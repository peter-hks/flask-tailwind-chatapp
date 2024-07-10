"""
HKS IT SC Chatbot
do not import this file; it's the entry point for the application
"""

# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=global-statement
from __future__ import annotations

import time
import logging
import mimetypes
import os
import pathlib
import tempfile
import threading
from typing import Any, Literal

import dotenv
from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_bcrypt import Bcrypt
from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.azure import make_azure_blueprint

# from flask_cache import Cache
from flask_login import LoginManager, current_user, login_required, logout_user
from flask_migrate import Migrate
from langchain_community.vectorstores.chroma import Chroma
from sqlalchemy.exc import NoResultFound
from werkzeug.utils import secure_filename

from flask_session import Session
from orms import *
from utils import *

# from flask_saml2.sp import ServiceProvider


dotenv.load_dotenv()

upload_progress: int = 0
current_user: User


def create_login_manager(_app: Flask) -> LoginManager:
    """Create a login manager for the Flask app.\
    \n
    instantiated with:
        ```py
        login_manager = create_login_manager(app)
        ```\
    \n
    if the `login_manager` variable is not used, the\
        function can be called without assigning it to a variable.

    Args:
        - `app (Flask)`: The Flask app instance. \n
    Returns:
        LoginManager: The login manager instance.
    """

    _login_manager = LoginManager(_app)
    # _login_manager.login_view = "azure.login"
    _login_manager.login_view = "azure.login"

    @_login_manager.user_loader
    def load_user(user_id: int | str):
        return User.query.get(int(user_id))

    @_login_manager.unauthorized_handler
    def unauthorized_callback():
        flash("You need to be logged in to access this page.", "warning")
        #    return redirect(url_for("azure.login"))
        return redirect(url_for("azure.login"))

    return _login_manager


def create_app(
    chromadb: Chroma, config: dict[str, Any] | None = None, **kwargs
) -> Flask:
    """Create a Flask app instance.

    Args:
        -  `chromadb (Chroma)`: The chromadb instance.
        -  `config (dict[str, Any])`: The configuration dictionary.
        -  `**kwargs (dict[str, Any])`: Additional keyword arguments to the `Flask` obj.\n
    Returns:
        - `Flask`: The Flask app instance.
    """
    _app = Flask(__name__, **kwargs)
    _app.config.update(config or {})
    _app.logger.setLevel(logging.DEBUG)
    _app.secret_key = os.urandom(24)
    session_id: int = None

    db.init_app(_app)
    with _app.app_context():
        db.create_all()
        Config.init_default_config(force=True)
        chain = Config.create_chain()
    create_login_manager(_app)
    #  blueprint = make_azure_blueprint()
    blueprint = make_azure_blueprint(
        client_id=os.getenv("AZURE_APP_CLIENT_ID"),
        client_secret=os.getenv("AZURE_APP_CLIENT_SECRET"),
        tenant=os.getenv("AZURE_TENANT_ID"),
    )
    blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)

    _app.register_blueprint(blueprint, url_prefix="/login")

    @_app.template_filter("ctime")
    def timectime(s):
        return time.ctime(s)  # datetime.datetime.fromtimestamp(s)

    @oauth_authorized.connect_via(blueprint)
    def azure_logged_in(
        _blueprint: OAuth2ConsumerBlueprint, token: list[dict] | None
    ) -> bool:
        """activates whenever a user logs in w/ oauth

        Args:
            - `_blueprint (OAuth2ConsumerBlueprint)`: blueprint from decorator
            - `token (list[dict])`: token provided by oauth \n
        Returns:
            - `bool`
        """

        if not token:
            flash("Failed to log in with azure.", category="error")
            return False
        # resp = _blueprint.session.get("/user")
        resp = _blueprint.session.get("/v1.0/me")
        if not resp.ok:
            flash("Failed to fetch user info from azure.", category="error")
            return False
        azure_info: dict = resp.json()
        try:
            oauth = OAuth.query.filter_by(
                provider=_blueprint.name, provider_user_id=str(azure_info["id"])
            ).one()
        except NoResultFound:
            oauth = OAuth(
                provider=_blueprint.name,
                provider_user_id=str(azure_info["id"]),
                token=token,
            )
        if oauth.user:
            oauth.user.login()
            flash("Successfully signed in with azure.")
            return False
            # Create a new local user account for this user
        user = User.from_oauth_info(
            azure_info,
            **{"mail": "email", "jobTitle": "job_title", "displayName": "name"},
        )
        oauth.user = user
        with db.session.begin_nested():
            db.session.add_all([user, oauth])
        user.login()
        flash("Successfully signed in with azure.")
        return False

    @_app.route("/", methods=["GET", "POST"])
    def index() -> Response:
        """index route

        Returns:
            Response: redirect to chat
        """
        # return render_template("index.html")
        return redirect(url_for("chat"))

    @_app.route("/login")
    def login() -> Response:
        """login route

        Returns:
            Response: redirect to azure login
        """
        return "login" "dsa"

    @_app.route("/logout")
    @login_required
    def logout() -> Response:
        """logout route

        Returns:
            Response: redirect to login
        """
        # if current_user.oauth:
        #     current_user.oauth.delete()
        logout_user()
        return redirect(url_for("login"))

    @_app.route("/chat")
    @login_required
    def chat() -> str | Response:
        """chat route

        Returns:
            str | Response: chat.html | redirect to login
        """
        # prompthistory.clear() # clears out history of chat when you refresh the page
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("azure.login"))
        return render_template("chat.html")

    @_app.route("/ai_settings", methods=["GET", "POST"])
    @login_required
    def ai_settings():
        nonlocal chromadb
        template = "ai_settings_documents.html"
        files = sorted(
            pathlib.Path(_app.config["UPLOAD_FOLDER"]).glob("*"),
            key=lambda x: x.stat().st_ctime,
        )
        if request.method != "POST":
            return render_template(template, files=files)
        if "delete" in request.form:
            deleted_files = []
            for file in files:
                if file.name in request.form:
                    file.unlink()
                    deleted_files.append(file.name)
            chromadb = create_chroma(
                get_most_recent_file(_app.config["UPLOAD_FOLDER"], "*.pdf"),
                replace=True,
            )
            return render_template(
                template,
                message=f"deleted {', '.join(deleted_files)}",
                files=sorted(
                    pathlib.Path(_app.config["UPLOAD_FOLDER"]).glob("*"),
                    key=lambda x: x.stat().st_ctime,
                ),
            )
        if "file" not in request.files:
            return render_template(template, message="No file part", files=files)
        file = request.files["file"]
        if not file.filename:
            return render_template(template, message="No selected file", files=files)
        file_ext: str = (
            mimetypes.guess_extension(file.content_type)
            or pathlib.Path(file.filename).suffix
        )
        if not file or file_ext not in _app.config["ALLOWED_EXTENSIONS"]:
            return render_template(
                template, message="File type not allowed", files=files
            )

        def _upload() -> None:
            """upload subfunc for threading"""
            nonlocal chromadb
            file_path = os.path.join(
                _app.config["UPLOAD_FOLDER"], secure_filename(file.filename)
            )
            try:
                file.save(file_path)
            except Exception:  # pylint: disable=broad-except
                pass
            if file_ext == ".zip":
                _temp_out = os.path.join(
                    tempfile.gettempdir(), file.filename.strip(file_ext)
                )
                unzip_file(file_path, _temp_out)
                file_path = os.path.join(
                    _app.config["UPLOAD_FOLDER"],
                    f"{secure_filename(file.filename)}.pdf",
                )
                combine_pdfs(_temp_out, output_path=file_path)
            chromadb = create_chroma(file_path, replace=True)

        # pylint: disable=assignment-from-no-return
        def _mutate_progress() -> None:
            """mutates upload progress global"""
            global upload_progress
            upload_progress = 0
            while upload_progress < 100:
                upload_progress += 1
                time.sleep(0.1)

        try:
            for thread in [
                threading.Thread(target=_upload),
                threading.Thread(target=_mutate_progress),
            ]:
                thread.start()
        except Exception as e:  # pylint: disable=broad-except
            return render_template(template, message=e, files=files)

        return render_template(
            template,
            message=f"{file} uploaded and embeddings updated",
            files=sorted(
                pathlib.Path(_app.config["UPLOAD_FOLDER"]).glob("*"),
                key=lambda x: x.stat().st_ctime,
            ),
        )

    @_app.route("/upload_progress")
    def progress() -> Response:
        """progress route

        Returns:
            - `jsonify`: upload_progress
        """
        return jsonify(upload_progress)

    @_app.route("/user_interaction", methods=["GET", "POST"])
    @login_required
    def ai_settings_userinteraction():
        nonlocal chain
        if not current_user.is_authenticated:
            flash("Please log in to access this page,", "warning")
            return redirect(url_for("azure.login"))
        template = "ai_settings_userinteraction.html"
        if not request.method == "POST":
            return render_template(template, current_settings=Config.query.all())
        config = Config.from_dict(request.form)
        if config.key.startswith("USER_TONE"):
            tones = ["USER_TONE_CASUAL", "USER_TONE_FORMAL"]
            for index, tone in enumerate(tones):
                _con: Config = config.query.filter_by(
                    key=tone, key_type="prompt"
                ).one_or_none()
                if not _con and tone == config.key:
                    config.toggle = "ON"
                    Config(
                        key=tones[1 if index == 0 else 0],
                        key_type="prompt",
                        toggle="OFF",
                        value="",
                    ).upsert()
                if _con and tone == config.key:
                    config.toggle = "ON" if _con.toggle == "OFF" else "OFF"
                    Config(
                        key=tones[1 if index == 0 else 0],
                        key_type="prompt",
                        toggle="OFF" if config.toggle == "ON" else "ON",
                        value="",
                    ).upsert()
        config.upsert()
        chain = Config.create_chain()
        return render_template(template, current_settings=Config.query.all())

    @_app.route("/content_management", methods=["GET", "POST"])
    @login_required
    def ai_settings_contentmanagement() -> str | Response:
        nonlocal chain
        if not current_user.is_authenticated:
            flash("Please log in to access this page,", "warning")
            return redirect(url_for("azure.login"))
        template = "ai_settings_contentmanagement.html"
        settings_query = Config.query.filter_by(key_type="compliance-prompt").order_by(
            Config.key_type
        )
        if not request.method == "POST":
            return render_template(template, current_settings=settings_query.all())
        if (del_key := "delete") in request.form:
            # if "delete" in request.form:
            to_delete = Config.from_dict(
                {k: v for k, v in request.form.items() if k not in {del_key, "value"}}
            )
            to_delete.delete()
            return render_template(template, current_settings=settings_query.all())
        Config.from_dict(request.form).upsert()
        chain = Config.create_chain()
        return render_template(template, current_settings=settings_query.all())

    @_app.route("/security_access")
    @login_required
    def ai_settings_securityaccess():
        if not current_user.is_authenticated:
            flash("Please log in to access this page,", "warning")
            return redirect(url_for("azure.login"))
        return render_template("ai_settings_security.html")

    @_app.route("/operational_settings")
    @login_required
    def ai_settings_operational():
        if not current_user.is_authenticated:
            flash("Please log in to access this page,", "warning")
            return redirect(url_for("azure.login"))
        return render_template("ai_settings_operational.html")

    @_app.route("/user-prompt", methods=["POST"])
    def user_prompt() -> (
        tuple[Literal["Error: prompt is None"], Literal[400]] | Response
    ):
        """route for user prompt

        Returns:
            str: Error: prompt is None | jsonify(answer=answer)
        """

        nonlocal session_id

        prompt = request.form.get("prompt")

        if prompt is None:
            return "Error: prompt is None", 400

        # Use Langchain for processing
        reg_simsearch = chromadb.similarity_search(prompt)
        res = chain({"input_documents": reg_simsearch, "question": prompt})
        answer: str = res["output_text"]

        # chain.llm_chain.prompt.messages[0].prompt.template

        # If it's the start of a new session (i.e., the first message), create a new session entry
        if session_id is None:
            logging.info("Creating new session...")  # Or use a proper logging method
            ChatSession(user_id=current_user.id).insert()
            session_id = (
                ChatSession.query.filter_by(user_id=current_user.id)
                .order_by(ChatSession.start_timestamp.desc())
                .first()
                .id
            )
        # Store chat in the database
        ChatMessage(
            session_id=session_id, user_message=prompt, ai_message=answer
        ).insert()
        return jsonify(answer=answer)

    @_app.route("/chat_history", methods=["GET"])
    @login_required
    def get_chat_history() -> str:
        """Get chat history route.

        Returns:
            str: chat_history.html
        """

        _app.logger.debug("Accessing chat history.")
        # Fetch all sessions for current user
        sessions: list[ChatSession] = (
            ChatSession.query.filter_by(user_id=current_user.id)
            .order_by(ChatSession.start_timestamp.desc())
            .all()
        )
        _app.logger.info("Sessions: %s", sessions)
        return render_template(
            "chat_history.html",
            chat_sessions=[sess for sess in sessions if sess.messages],
        )

    @_app.route("/account_management", methods=["GET", "POST"])
    @login_required
    @admin_required
    def manage_accounts() -> str | None:
        """manage accounts route

        Returns:
            str | None: account_management.html
        """
        if request.method != "POST":
            return render_template("account_management.html", users=User.query.all())
        action = request.form.get("action")
        if action == "delete":  # Delete a user account
            user: User = User.query.get(request.form.get("user_id"))
            if user:
                user.delete()
            return render_template("account_management.html", users=User.query.all())
        flash("Invalid action", "danger")
        return render_template("account_management.html", users=User.query.all())

    @_app.route("/bot_settings", methods=["GET", "POST"])
    @login_required
    @admin_required
    def bot_settings() -> str:
        """bot settings route"""
        nonlocal chain
        if request.method != "POST":
            return render_template("bot_settings.html", config=Config.query.all())
        for key, value in request.form.items():
            if key.startswith("delete-"):
                Config(
                    key=key.removeprefix("delete-"), key_type=request.form.get("action")
                ).delete()
                break  # could also use continue here in a diff context, but this is safer
            if key == "action" or not value:
                continue
            Config(key=key, key_type=request.form.get("action"), value=value).upsert()
        chain = Config.create_chain()
        return render_template("bot_settings.html", config=Config.query.all())

    @_app.route("/about")
    @login_required
    def about():
        if not current_user.is_authenticated:
            flash("Please log in to access this page,", "warning")
            return redirect(url_for("azure.login"))
        return render_template("about.html")

    return _app


UPLOADS_DIR: str = "uploads"
app: Flask = create_app(
    create_chroma(
        get_most_recent_file(UPLOADS_DIR, "*.pdf"),
        persist_to=os.path.join(tempfile.gettempdir(), "_default_embeddings"),
    ),
    config={
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_TYPE": "filesystem",
        "SECRET_KEY": os.urandom(24),
        "UPLOAD_FOLDER": UPLOADS_DIR,
        "ALLOWED_EXTENSIONS": {".pdf", ".zip"},
    },
)

# app.debug = True

Session(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
# cache = Cache(app)


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    if not os.path.exists(".env"):
        raise ValueError("create a .env file with the OPENAI_API_KEY=your_key")
    logging.getLogger().setLevel(logging.DEBUG)
    app.run(debug=True, host="localhost")

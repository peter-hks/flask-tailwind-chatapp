"""holds the Post class"""

import json
import logging
import os
from datetime import datetime
from typing import Literal, Optional, cast

import dotenv
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from sqlalchemy.orm import Mapped

from .base import Base, db

# from typing import override #requires python 3.12


class Config(Base):  # pylint: disable=too-few-public-methods
    """A class for the bot configuration.

    inherits:
        - `Base` \n
    attributes:
        - `key (str)`: the key for the configuration
        - `key_type (str)`: the type of the key
        - `key_datatype (str)`: the datatype of the key
        - `value (str)`: the value of the key
        - `created (datetime)`: the time the configuration was created \n
    """

    key: Mapped[str] = db.Column(db.String(80), primary_key=True)
    key_type: Mapped[str] = db.Column(db.String(80), primary_key=True)
    key_datatype: Mapped[str] = db.Column(db.String(80), default="str")
    value: Mapped[str] = db.Column(db.Text, nullable=False)
    toggle: Mapped[Optional[Literal["ON", "OFF"]]] = db.Column(db.String(3))
    created: Mapped[datetime] = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def init_default_config(cls, force: bool = False, **kwargs: dict[str]) -> None:
        """Create the default configuration for the bot. \
            the default config json file is `<bot_config.json>`.

        Args:
            - `force (bool, False)`: force the creation of the default configuration
            - `**kwargs`: keyword arguments to pass to `open()` \n
        Defaults:
            - `file (str)`: `"bot_config.json"`
            - `mode (str)`: `"r+"`
            - `encoding (str)`: `"utf-8"` \n
        """

        if not force and cls.query.count() > 0:
            logging.warning("Default configuration already exists.")
            return

        if force:
            cls.purge_all()

        for key, value in {
            "file": "bot_config.json",
            "mode": "r+",
            "encoding": "utf-8",
        }.items():
            kwargs[key] = kwargs.get(key) or value

        with open(**kwargs) as file:  # pylint: disable=unspecified-encoding
            for value in json.load(file):
                cls.from_dict(value).insert()

    def __str__(self) -> str:
        """Return the string representation of the configuration."""
        if self.toggle == "OFF":
            return ""
        if "prompt" in self.key_type and self.key not in {"header", "footer"}:
            return f"""{self.key}:\n{self.value}"""
        if self.key in {"header", "footer"}:
            return self.value
        return super().__str__()

    @classmethod
    def create_chain(
        cls,
        **kwargs,
    ) -> BaseCombineDocumentsChain:
        """Create the default configuration for the bot.

        Args:
            - `template_key_type (str)`: the name of the form for the template
            - `partial_vars_key_type (str)`: the name of the form for the partial variables
            - `**kwargs`: keyword arguments to pass to `open()` \n
        Returns:
            - `BaseCombineDocumentsChain`: the chain created from the configuration
        """

        return _create_chain(
            template="".join(
                str(x)
                for x in cls.query.where(
                    cls.key_type.in_(["compliance-prompt", "prompt"])
                )
                .order_by(cls.key_type)
                .all()
            ),
            partial_vars={
                x.key: x.value
                for x in cast(
                    list[Config],
                    cls.query.filter_by(key_type="partial_variable").all(),
                )
            },
            **kwargs,
        )


# pylint: disable=line-too-long


def _create_chain(
    template: str, partial_vars: dict[str, str], **kwargs
) -> BaseCombineDocumentsChain:
    """Get the chain instance for the chatbot.

    Args:
        - `template (str)`: The template for the system message prompt.
        - `partial_vars (dict[str, str])`: The partial variables for the user message prompt.
        - `**kwargs`: The keyword arguments to pass to the chatbot. \n
    Returns:
        - `BaseCombineDocumentsChain`: The chatbot chain instance.
    """
    dotenv.load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("please ask alex for the openai api key")
    _chat = AzureChatOpenAI(
        # deployment_name="gpt-35-turbo-16k",
        deployment_name="gpt-4o",
        openai_api_type="azure",
        openai_api_version="2023-08-01-preview",
        azure_endpoint="https://hks-dev-openai-service.openai.azure.com/",
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=0.8,
        max_tokens=4096,
        **kwargs,
    )

    # _chat = ChatOpenAI(
    #     name="gpt-4o",
    #     api_key=...,
    #     model="gpt-4o",
    #     temperature=0.8,
    #     max_tokens=150,
    # )

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    # # Define the prompt template(Langchain)
    # reg_prompt = PromptTemplate(template="{context}\n{question}\n{fmt}",
    #                             input_variables=["context", "question"],
    #                             partial_variables={"fmt": reg_pfi})

    # Define the user prompt template using the new custom_pfi
    _user_prompt = PromptTemplate(
        template="{context}\n{question}\n{custom_fmt}",
        input_variables=["context", "question"],
        partial_variables=partial_vars,
    )
    user_message_prompt = HumanMessagePromptTemplate(prompt=_user_prompt)
    # Combine (system, user) into a chat prompt template
    combined_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, user_message_prompt]
    )
    # Using Langchain's Stuff Chain
    return load_qa_chain(_chat, chain_type="stuff", prompt=combined_prompt)

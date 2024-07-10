# HKS-AgentAI_flask

## What does this project do?

This project is a web application built us that provides users with a chat interface to interact with an AI-powered chatbot which contains information about HKSIT Guide data. It features user authentication, session management, PDF document upload, Account Management, and chat history functionalities. The application is styled with Tailwind CSS and includes a responsive design for a seamless user experience on both desktop and mobile devices.

## Features

- User authentication with role-based access control for admins and regular users.
- Secure password handling with hashed passwords.
- PDF document upload and management.
- Account viewing and management.
- Persistent chat sessions with a history view.
- Search functionality within chat history.
- Integration with Langchain for AI responses.
- Responsive design using Tailwind CSS.

## How to use it?

- Firstly, you have to register an account to use AgentAI. If you already have an account, then simply login with your credentials.

- After you log in, it will take you to the Home page. and then ask AgentAI any questions you might have.

- On the left side of the screen, you will see a navbar where you will find the options Home, About, Documents, Chat History.

- About route contains information about the developers that worked on the project.

- (FOR ADMINS ONLY) Documents route contains an option to upload updated documents but it can be only accessed by admins-Alex and Barbara. If any other user tries to access the Documents route, then they will be redirected to the Home page.

- (FOR ADMINS ONLY) Account management route contains all the accounts currently stored in the computer. There is the ability to create an user, and delete an user from there. You also have the ability to choose if the user will be admin or a regular user when you create an user.

- When you ask questions to AgentAI and press the 'Ask' button, it will automatically store your session logs in the Chat History route. Simply go to the Chat History route to find all the session logs and all the interactions between AgentAI and you since the time you opened an account.

- On the top right corner, it will show you the name of the currently logged in user.

- You can also use the search bar in the home page to search anything in the chat.

- Once you are done with everything, you can log out of the app. Even if you accidentally log out, your chat history will be saved.

## Installation

### This project requires

- python3(Python 3.10.12)
- Docker engineI
- PostgresSQL

### To clone project and configure environment (current)

  1. While on Harvard VPN, clone the project:

      ```bash
      ssh-keygen -t rsa -b 4096 -C 
      git clone git@github.huit.harvard.edu:pdt150/HKS-AgentAI_flask.git
      ```

  2. In terminal, navigate to the project folder and create a new python virtual environment and activate it:
  
      ```bash
      python3 -m venv .flask_openai
      source .flask_openai/bin/activate
      ```

  3. Install python dependancies defined in requirements.txt file:

      ```bash
      pip install -r requirements.txt
      ```

  4. To debug locally, from the root of project run:

      ```bash
      python3 app.py
      ```

Now, you should have a running local instance of the web app that you can navigate to via: <http://localhost:5000/chat>

### Git workflow conventions

In short:

- please develop on a feature branch and use pull requests
- commit often!
- make useful comments to commits
- don't push static and local files, leverage the .gitignorefile!

### Basic Git Commands

#### Updated git policy documentation will be here soon :)

get status of project, see untracked and changed files, as well as what branch you are on

```bash
git status
```

add files to commit

```bash
git add file1 file2 directorya/* 
```

commit your changes with a message about what you did

```bash
git commit -m 'worked on stuff and things and made progress with that other item too'
```

while on vpn, push changes to github

```bash
git push origin main
```

_____________________

## Dev Environment configuration

### For developing in Windowns Environment

1. Open Powershell terminal and run following command to install Windows Subsystem for Linux.

    ```ps1
    wsl --install -d Ubuntu
    winget install --e --id Docker.DockerDesktop
    ```

Run through the prompts to accept terms and installation process, then reboot your machine.

### Configuring tailwindcss build environment

Install tailwindcss npm module if needed:
```
npm install -D tailwindcss
```
(Note: requires installing nodejs first: https://nodejs.org/en/download)

Install additional extension nodejs packages required for tailwind:

```
npm install @tailwindcss/typography @tailwindcss/aspect-ratio @tailwindcss/forms         
```                   
Note: If additional tailwindcss components require additional dependancies, please be sure to include them in this step for future developers.

To compile updated tailwind css and js, from the root directory of project run:
```
npx tailwindcss -i static/src/style.css -o static/css/main.css
```
(Note: only required if css values in the html or new tailwind html is added to project.)

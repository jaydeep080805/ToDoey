# ToDoey: A Flask-based Task Management Web Application
## Features
###### ToDoey is a task management web application built with Flask, a Python web framework. It offers features like user authentication, task creation and tracking, and customizable notifications.


*   User Authentication (Sign Up, Login, Logout)
*   Task Management (Add, Update, Complete)
*   Profile Management (Change Name, Email, Password, Profile Picture)
*   Email Notifications
*   Responsive Design for Mobile and Desktop

## Installation
### Prerequisites

*   Python 3.8 or above
*   Flask
*   SQLAlchemy
*   Flask-Login
*   Flask-WTF
*   Flask-Mail

### Environment Setup
```
git clone https://github.com/jaydeep080805/ToDoey.git
```
```
cd ToDoey
```
```
pip install -r requirements.txt
```
### Configuration
1. Create a .env file in the root directory.
2. Set the following environment variables:
```
SECRET_KEY=<your_secret_key>
DATABASE_URL=<your_database_url>
EMAIL=<your_email>
EMAIL_PASSWORD=<your_email_password>
```
### Usage
1. Start the Flask server:
```
flask run
```
2. Open a web browser and navigate to http://localhost:5000/ to use the application.

## Contributing
###### Contributions to ToDoey are welcome! Please follow the standard fork-clone-branch-pull request workflow.

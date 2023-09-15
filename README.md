# Watchdog Flask Backend

This is a Flask-based backend for the Watchdog svelte or vue frontend. It's a web scraper that fetches data from eBay and sends notifications to users via Telegram when new listings are found.

## Project Structure

The project is structured into several modules and files:

- app.py: This is the main application file where the Flask app is initialized and routes are defined.
- common/: This directory contains common utilities and models used across the application.
- resources/: This directory contains the resources for the Flask-RESTful API.
- tests/: This directory contains unit tests for the application.
- start.py: This file is used to start the Flask application.
- wsgi.py: This file is used for deploying the application with WSGI servers like Gunicorn.

## Dependencies

The project uses several Python libraries, which are listed in the pyproject.toml file. Some of the main dependencies include:

- Flask: For creating the web application.
- Flask-RESTful: For creating the RESTful API.
- Flask-JWT-Extended: For handling JSON Web Tokens (JWTs).
- Flask-SQLAlchemy: For database operations.
- BeautifulSoup4: For parsing HTML and extracting data.
- Telepot: For interacting with the Telegram API.

## Main Features

- User Authentication: Users can register, login, and manage their profiles. Passwords are hashed using bcrypt for security.
- Web Scraping: The application scrapes eBay for new listings based on URLs provided by the users. The scraping is done in a separate thread for each user.
- Notifications: When new listings are found, notifications are sent to users via Telegram.
- Admin Features: Admin users can view all users, listings, and URLs. They can also start all scrapers and delete users.

## Testing

The application includes unit tests, which are located in the tests/ directory. The tests cover user registration, login, URL management, and scraper control. (tests may be outdated)

## Running the Application

Before running the application, you need to set up the environment variables. These variables store sensitive data such as API keys and database credentials. Here's how you can do it:

1. Create a new file in the root directory of the project and name it `.env`.
2. Open the `.env` file and set your environment variables in the format `KEY=VALUE`. For example:

```env
BOT_TOKEN=your_telegram_bot_token
JWT_SECRET_KEY=your_jwt_secret_key
SQLALCHEMY_DATABASE_URI=your_database_url
```

Replace your_telegram_bot_token, your_jwt_secret_key, and your_database_url with your actual Telegram bot token, JWT secret key, and database URL respectively.

3. Save and close the `.env` file.
4. This project uses Poetry as the virtual environment manager. You can install Poetry by following the instructions [here](https://python-poetry.org/docs/#installation).
5. Run `poetry install` to install the dependencies.
6. Enter the virtual environment with `poetry shell`.
7. Now, you need to tell Flask where to find your `.env` file. You can do this by setting the `ENV_FILE_LOCATION` environment variable to the path of your `.env` file. If you're using a Unix-based system like Linux or macOS, you can do this in the terminal:

```bash
export ENV_FILE_LOCATION=/path/to/your/`.env`
```

If you're using Windows, you can do this in the Command Prompt:

```cmd
setx ENV_FILE_LOCATION C:\path\to\your\.env
```

Replace `/path/to/your/.env` or `C:\path\to\your\.env` with the actual path to your `.env` file.

8. Now you have to initalise the database, only do this step if there isn't already a database file in the instance folder. Run `flask shell`, and then run `db.create_all()` to initalise the database.
9. Now you can run the application with the command `python start.py`. The application will start on `0.0.0.0` and port `5123`.

## Future Work

The application is a work in progress and there are plans to add more features and improve the existing ones. Code is quite messy for now and is not really compliant with how an actual REST api should be structured.

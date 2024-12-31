# Wordle App

This is a simple Wordle-inspired web application built using Python's Flask framework. The app selects a daily word for users to guess and provides feedback on their guesses, similar to the original Wordle game from New York Times. It includes server-side logic, a SQLite database, and a basic frontend for interacting with the game.

---

## Features
- Daily word selection stored in a SQLite database.
- Six-character word guesses with feedback on correctness.
- Server-client communication via a RESTful API.
- Backend powered by Flask, with dependencies managed using Poetry.

---

## Prerequisites

1. **Python**: Install Python 3.12 or higher.
2. **Poetry**: Install [Poetry](https://python-poetry.org/docs/) for dependency management
3. **Docker (optional)**: To containerize and deploy the app.

---

## Local Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/jkoessle/woertle.git
cd woertle
```

### 2. Install Dependencies
Using Poetry:
```bash
poetry install
```

### 3. Create a `.env` File
Create a `.env` file in the root directory and add the following variables:
```
DATABASE=data/words.db # path to your local database
WORD_LIST_PATH="path-to-your-wordlist" # only needed to set up the game locally
LOG_LEVEL=INFO # optional, defaults to logging.info
```

### 4. Initialize the Database
Run the following to populate the SQLite database with words:
```bash
poetry run python -m app
```

### 5. Start the Application
Run the Flask development server:
```bash
poetry run python app.py
```

Access the app in your browser at `http://localhost:5000`.

---

## Running with Docker

### 1. Build the Docker Image
```bash
docker build -t woertle .
```

### 2. Run the Docker Container
```bash
docker run -p 8080:8080 --env-file .env woertle
```

Access the app in your browser at `http://localhost:8080`.

---

## How to Play
1. Open the app in your browser.
2. Guess the six-character daily word.
3. Receive feedback on each guess:
   - **Correct**: Letter is in the correct position.
   - **Present**: Letter is in the word but in the wrong position.
   - **Absent**: Letter is not in the word.
4. You have six attempts to guess the word correctly.

---

## License
This project is open-source and available under the MIT License.

---

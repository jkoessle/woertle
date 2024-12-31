import logging
import os
import random
import sqlite3
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from logging import getLogger

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request

logger = getLogger(__name__)
app = Flask(__name__)

WORD_LENGTH = 6


def load_word_list() -> list[str]:
    with open(os.getenv("WORD_LIST_PATH"), "r", encoding="utf-8") as file:
        words = {
            word.strip().lower()
            for word in file.readlines()
            if len(word.strip()) == WORD_LENGTH
        }
    return list(words)


def init_db(word_list: list[str]) -> None:
    conn = sqlite3.connect(os.getenv("DATABASE"))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS used_words (
            date TEXT PRIMARY KEY,
            word TEXT NOT NULL
        )
    """)
    conn.commit()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS words (
            word TEXT PRIMARY KEY,
            used INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    insert_many_list = [(word, 0) for word in word_list]
    cursor.executemany(
        "INSERT OR IGNORE INTO words (word, used) VALUES (?,?)", insert_many_list
    )
    conn.commit()
    conn.close()


def get_used_words() -> list[str]:
    conn = sqlite3.connect(os.getenv("DATABASE"))
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM used_words")
    used_words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return used_words


def get_unused_words() -> list[str]:
    conn = sqlite3.connect(os.getenv("DATABASE"))
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM words WHERE used = 0")
    available_words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return available_words


def get_all_words() -> list[str]:
    conn = sqlite3.connect(os.getenv("DATABASE"))
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM words")
    all_words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return all_words


def insert_used_word(date: str, word: str) -> None:
    conn = sqlite3.connect(os.getenv("DATABASE"))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO used_words (date, word) VALUES (?, ?)", (date, word))
    conn.commit()
    cursor.execute("UPDATE words SET used = 1 WHERE word = ?", (word,))
    conn.commit()
    conn.close()


def get_daily_word() -> str:
    today = datetime.now().date().isoformat()
    conn = sqlite3.connect(os.getenv("DATABASE"))
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM used_words WHERE date = ?", (today,))
    row = cursor.fetchone()
    if row:
        daily_word = row[0]
    else:
        available_words = get_unused_words()
        if not available_words:
            raise ValueError("No more available words to choose from.")
        random.seed(today)
        daily_word = random.choice(available_words)
        insert_used_word(today, daily_word)
    conn.close()
    logger.debug(f"Daily word: {daily_word}")
    return daily_word


@lru_cache
def get_target_char_count(word: str) -> dict[str, int]:
    char_count = defaultdict(int)
    for char in word:
        char_count[char] += 1
    return char_count


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/guess", methods=["POST"])
def guess() -> Response:
    target_word = get_daily_word()
    words = get_all_words()
    target_word = "gewebe"
    target_char_count = get_target_char_count(target_word)

    user_guess = request.json.get("guess", "").lower()
    attempts = request.json.get("attempts", 0)

    if len(user_guess) != WORD_LENGTH or user_guess not in words:
        return jsonify({"error": "Invalid word."}), 400

    attempts += 1
    feedback = []

    correct_char_count = defaultdict(int)

    for i, char in enumerate(user_guess):
        if char == target_word[i]:
            feedback.append("correct")
            correct_char_count[char] += 1
        elif char in target_word:
            feedback.append("present")
        else:
            feedback.append("absent")

    if user_guess == target_word:
        return jsonify(
            {
                "feedback": feedback,
                "win": True,
                "targetCount": target_char_count,
                "correctCount": correct_char_count,
            }
        )

    # each player has 6 attempts to guess the word
    if attempts >= 6:
        return jsonify(
            {
                "feedback": feedback,
                "win": False,
                "game_over": True,
                "target_word": target_word,
                "targetCount": target_char_count,
                "correctCount": correct_char_count,
            }
        )

    return jsonify(
        {
            "feedback": feedback,
            "win": False,
            "targetCount": target_char_count,
            "correctCount": correct_char_count,
        }
    )


if __name__ == "__main__":
    load_dotenv()
    logger.setLevel(os.getenv("LOG_LEVEL", logging.INFO))
    words = load_word_list()
    init_db(word_list=words)
    app.run(debug=True, host="localhost", port=8080)

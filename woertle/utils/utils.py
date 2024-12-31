import os
import random
import sqlite3
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from logging import Logger


def make_art(): ...


def load_word_list(word_list_path: str) -> list[str]:
    with open(word_list_path, "r", encoding="utf-8") as file:
        words = {
            word.strip().lower() for word in file.readlines() if len(word.strip()) == 5
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


def get_daily_word(logger: Logger) -> str:
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

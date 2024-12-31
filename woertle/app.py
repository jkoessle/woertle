import logging
import os
from collections import defaultdict
from logging import getLogger

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request

from woertle.utils.utils import get_all_words, get_daily_word, get_target_char_count

logger = getLogger(__name__)
app = Flask(__name__)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/guess", methods=["POST"])
def guess() -> Response:
    target_word = get_daily_word(logger=logger)
    words = get_all_words()
    # target_word = "gewebe"
    logger.info(words[:5])
    logger.info(target_word)
    target_char_count = get_target_char_count(target_word)

    user_guess = request.json.get("guess", "").lower()
    attempts = request.json.get("attempts", 0)

    if len(user_guess) != 5 or user_guess not in words:
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
    app.run(debug=True, host="localhost", port=8080)

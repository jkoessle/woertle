import os

from dotenv import load_dotenv

from woertle.utils.utils import init_db, load_word_list

if __name__ == "__main__":
    load_dotenv()
    init_db(word_list=load_word_list(word_list_path=os.getenv("WORD_LIST_PATH")))

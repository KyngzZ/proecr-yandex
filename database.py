import sqlite3
from datetime import datetime


def create_connection(db_file):
    """Создает соединение с базой данных SQLite."""
    conn = sqlite3.connect(db_file)
    return conn

conn = sqlite3.connect('words.db')
cursor = conn.cursor()

def create_tables(conn):
    """Создает таблицы в базе данных."""
    cursor = conn.cursor()

    # Таблица Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица Games
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            score INTEGER,
            duration INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            word_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users (user_id),
            FOREIGN KEY (word_id) REFERENCES Words (word_id)
        )
    ''')

    # Таблица Words
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Words (
            word_id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL
        )
    ''')

    conn.commit()

# Загрузка слов из файла
with open('words.txt', 'r') as file:
    for line in file:
        word = line.strip()
        if word:  # Проверка, что строка не пустая
            try:
                cursor.execute('INSERT INTO words (word) VALUES (?)', (word,))
            except sqlite3.IntegrityError:
                continue  # Игнорируем, если слово уже существует
conn.commit()
conn.close()


def add_user(conn, username):
    """Добавляет нового пользователя в таблицу Users."""
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Users (username) VALUES (?)', (username,))
    conn.commit()


def record_game(conn, user_id, score, duration, word_id):
    """Записывает результаты игры в таблицу Games."""
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Games (user_id, score, duration, word_id) VALUES (?, ?, ?, ?)',
                   (user_id, score, duration, word_id))
    conn.commit()


def add_word(conn, word):
    """Добавляет новое слово в таблицу Words."""
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Words (word) VALUES (?)', (word,))
    conn.commit()


def main():
    database = "word_game.db"
    conn = create_connection(database)

    if conn:
        create_tables(conn)

        # Добавление 300 простых английских слов в таблицу Words
        english_words = [
            'apple', 'banana', 'orange', 'grape', 'peach', 'pear',
            'plum', 'kiwi', 'mango', 'lemon', 'lime', 'cherry',
            'date', 'fig', 'apricot', 'cantaloupe', 'watermelon',
            'strawberry', 'blueberry', 'blackberry', 'raspberry',
            'coconut', 'jackfruit', 'papaya', 'passionfruit', 'quince',
            'carrot', 'potato', 'tomato', 'onion', 'garlic', 'pepper',
            'lettuce', 'spinach', 'cabbage', 'broccoli', 'cauliflower',
            'celery', 'zucchini', 'eggplant', 'beet', 'radish',
            'turnip', 'squash', 'pumpkin', 'asparagus', 'artichoke',
            'chickpea', 'bean', 'lentil', 'corn', 'rice',
            'pasta', 'bread', 'butter', 'cheese', 'milk',
            'yogurt', 'egg', 'chicken', 'beef', 'pork',
            'fish', 'shrimp', 'crab', 'lobster', 'nut',
            'seed', 'oil', 'vinegar', 'sugar', 'salt',
            'pepper', 'spice', 'herb', 'tea', 'coffee',
            'juice', 'soda', 'water', 'wine', 'beer',
            'cocktail', 'smoothie', 'shake', 'soup', 'stew',
            'salad', 'sandwich', 'wrap', 'taco', 'pizza',
            'burger', 'cake', 'cookie', 'pie', 'candy',
            'toy', 'book', 'pen', 'pencil', 'paper',
            'desk', 'chair', 'table', 'computer', 'phone',
            'mouse', 'keyboard', 'monitor', 'screen', 'printer',
            'notebook', 'folder', 'file', 'stapler', 'tape',
            'scissors', 'glue', 'ruler', 'marker', 'crayon',
            'paint', 'brush', 'canvas', 'picture', 'frame',
            'photo', 'album', 'music', 'song', 'dance',
            'game', 'play', 'sport', 'team', 'ball',
            'goal', 'score', 'win', 'lose', 'draw',
            'fan', 'coach', 'player', 'referee', 'field',
            'court', 'track', 'pool', 'ring', 'arena',
            'stadium', 'event', 'trophy', 'medal', 'prize',
            'champion', 'winner', 'loser', 'scoreboard', 'cheer',
            'crowd', 'audience', 'spectator', 'performance', 'show',
            'theater', 'movie', 'film', 'actor', 'actress',
            'director', 'script', 'scene', 'set', 'costume',
            'makeup', 'sound', 'music', 'score', 'dialogue',
            'plot', 'story', 'character', 'role', 'scene',
            'camera', 'shot', 'edit', 'cut', 'film',
            'cinema', 'screenplay', 'premiere', 'festival', 'award',
            'nomination', 'red carpet', 'celebrity', 'fame', 'glamour',
            'fashion', 'style', 'trend', 'design', 'model',
            'runway', 'collection', 'couture', 'accessory', 'jewelry',
            'bag', 'shoes', 'hat', 'scarf', 'gloves',
            'sunglasses', 'watch', 'belt', 'tie', 'socks',
            'shirt', 'blouse', 'skirt', 'dress', 'suit',
            'coat', 'jacket', 'hoodie', 'sweater', 'sweatshirt',
            'shorts', 'pants', 'jeans', 'leggings', 'pajamas',
            'red'
        ]

        for word in english_words:
            add_word(conn, word)

        conn.close()


if __name__ == '__main__':
    main()


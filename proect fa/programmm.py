import sys
import random
import sqlite3
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QTimer

class WordGame(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('word_game.ui', self)

        # Подключение к базе данных
        self.conn = sqlite3.connect('words.db')
        self.create_table()
        self.load_words()  # Загружаем слова при инициализации

        # Инициализация переменных
        self.current_letters = ""
        self.timer = QTimer()
        self.time_left = 120  # Время на игру в секундах
        self.correct_words_count = 0  # Счётчик правильных слов

        # Подключение кнопок к методам
        self.button_start.clicked.connect(self.start_game)
        self.button_check.clicked.connect(self.check_word)
        self.button_add_word.clicked.connect(self.add_word)

        # Настройка таймера
        self.timer.timeout.connect(self.update_timer)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                word TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()

    def load_words(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT word FROM words')
        self.valid_words = {row[0] for row in cursor.fetchall()}  # Загружаем слова в сет

    def start_game(self):
        self.current_letters = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 12))
        self.label_letters.setText(self.current_letters)
        self.label_result.setText("")
        self.lineEdit_word.clear()
        self.time_left = 120
        self.label_timer.setText(str(self.time_left))
        self.timer.start(1000)  # Обновление каждую секунду
        self.correct_words_count = 0  # Сбрасываем счётчик

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.label_timer.setText(str(self.time_left))
        else:
            self.timer.stop()
            self.label_result.setText(f"Время вышло! Найдено слов: {self.correct_words_count}")

    def check_word(self):
        user_word = self.lineEdit_word.text().strip()

        # Проверяем, что слово допустимо
        if user_word in self.valid_words:
            # Проверяем, может ли слово быть составлено из доступных букв
            if self.can_form_word(user_word):
                self.label_result.setText(f"Слово '{user_word}' корректно!")
                self.correct_words_count += 1  # Увеличиваем счётчик
                self.lineEdit_word.clear()  # Очищаем поле для ввода
            else:
                self.label_result.setText(f"Слово '{user_word}' некорректно! Используйте только буквы: {self.current_letters}")
        else:
            self.label_result.setText(f"Слово '{user_word}' не найдено в базе данных!")

    def can_form_word(self, word):
        # Проверяет, можно ли составить слово с использованием текущих букв
        for char in set(word):
            if word.count(char) > self.current_letters.count(char):
                return False
        return True

    def add_word(self):
        new_word = self.lineEdit_new_word.text().strip()
        if new_word:
            cursor = self.conn.cursor()
            try:
                cursor.execute('INSERT INTO words (word) VALUES (?)', (new_word,))
                self.conn.commit()
                self.valid_words.add(new_word)  # Добавляем новое слово в сет допустимых слов
                self.lineEdit_new_word.clear()
                self.label_result.setText(f"Слово '{new_word}' добавлено!")
            except sqlite3.IntegrityError:
                self.label_result.setText(f"Слово '{new_word}' уже существует!")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = WordGame()
    window.show()
    sys.exit(app.exec())
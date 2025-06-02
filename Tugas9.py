import sys
import csv
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QMenuBar, QMenu, QFileDialog, QDockWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard


DB_NAME = 'books.db'

class BookManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1D022087 - Putra Heryan Gagah Perkasa")

        self.all_books = []

        self.create_menu()
        self.create_ui()
        self.setup_db()
        self.load_data()
        self.create_dock()

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        export_action = file_menu.addAction("Simpan ke CSV")
        export_action.triggered.connect(self.export_csv)

    def create_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QLineEdit()

        paste_button = QPushButton("Paste from Clipboard")
        paste_button.clicked.connect(self.paste_from_clipboard)

        form_layout.addWidget(QLabel("Judul:"))
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(paste_button)
        form_layout.addWidget(QLabel("Pengarang:"))
        form_layout.addWidget(self.author_input)
        form_layout.addWidget(QLabel("Tahun:"))
        form_layout.addWidget(self.year_input)

        self.save_button = QPushButton("Simpan")
        self.save_button.clicked.connect(self.add_data)

        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        self.delete_button = QPushButton("Hapus Data")
        self.delete_button.setStyleSheet("background-color: orange")
        self.delete_button.clicked.connect(self.delete_data)
        layout.addWidget(self.delete_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def create_dock(self):
        dock = QDockWidget("Pencarian Judul", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        search_widget = QWidget()
        search_layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        search_widget.setLayout(search_layout)
        dock.setWidget(search_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.title_input.setText(clipboard.text())

    def setup_db(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def load_data(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM books")
        self.all_books = cur.fetchall()
        conn.close()
        self.display_books(self.all_books)

    def display_books(self, books):
        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(books):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def filter_table(self):
        keyword = self.search_input.text().lower()
        filtered = [row for row in self.all_books if keyword in row[1].lower()]
        self.display_books(filtered)

    def add_data(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        year = self.year_input.text().strip()

        if not (title and author and year.isdigit()):
            QMessageBox.warning(self, "Input Salah", "Lengkapi data dengan benar.")
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, int(year)))
        conn.commit()
        conn.close()

        self.title_input.clear()
        self.author_input.clear()
        self.year_input.clear()
        self.load_data()

    def delete_data(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Tidak ada data", "Pilih data terlebih dahulu")
            return

        book_id = int(self.table.item(selected_row, 0).text())
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()
        self.load_data()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if not path:
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM books")
        data = cur.fetchall()
        conn.close()

        with open(path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
            writer.writerows(data)

        QMessageBox.information(self, "Berhasil", "Data berhasil disimpan ke CSV.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookManager()
    window.resize(800, 500)
    window.show()
    sys.exit(app.exec())
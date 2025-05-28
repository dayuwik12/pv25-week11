import sys
import sqlite3
import csv
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QAction, QFileDialog, QInputDialog, QTabWidget, QScrollArea,
    QDockWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard


class BookManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku - Ida Ayu Dewi Purnama Anjani | F1D022050")
        self.setGeometry(100, 100, 900, 500)

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "books.db")
        self.conn = sqlite3.connect(db_path)

        self.create_table()
        self.setup_ui()
        self.load_data()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                year INTEGER
            )
        """)
        self.conn.commit()

    def setup_ui(self):
        # ====== Status Bar ======
        self.statusBar().showMessage("Ida Ayu Dewi Purnama Anjani | F1D022050")

        # ====== Menu Bar ======
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")

        save_action = QAction("Simpan", self)
        save_action.triggered.connect(self.save_data)
        export_action = QAction("Ekspor ke CSV", self)
        export_action.triggered.connect(self.export_to_csv)
        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(save_action)
        file_menu.addAction(export_action)
        file_menu.addAction(exit_action)

        search_action = QAction("Cari Judul", self)
        search_action.triggered.connect(self.search_by_menu)
        edit_menu.addAction(search_action)

        delete_action = QAction("Hapus Data", self)
        delete_action.triggered.connect(self.delete_data)
        edit_menu.addAction(delete_action)

        # ====== Form Input dan Tombol ======
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QLineEdit()

        paste_clip_btn = QPushButton("Paste Judul dari Clipboard")
        paste_clip_btn.clicked.connect(self.paste_from_clipboard)

        save_btn = QPushButton("Simpan")
        save_btn.clicked.connect(self.save_data)

        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Judul:"))
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(QLabel("Pengarang:"))
        form_layout.addWidget(self.author_input)
        form_layout.addWidget(QLabel("Tahun:"))
        form_layout.addWidget(self.year_input)
        form_layout.addWidget(save_btn)

        # ====== Table (dengan Scroll otomatis) ======
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.load_row_to_input)
        self.table.setMinimumHeight(200)

        # ScrollArea untuk Form dan Table
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addLayout(form_layout)
        paste_clip_layout = QHBoxLayout()
        paste_clip_layout.addStretch()
        paste_clip_layout.addWidget(paste_clip_btn)
        paste_clip_layout.addStretch()
        scroll_layout.addLayout(paste_clip_layout)

        scroll_layout.addWidget(self.table)

        delete_btn = QPushButton("Hapus Data")
        delete_btn.clicked.connect(self.delete_data)

        delete_layout = QHBoxLayout()
        delete_layout.addStretch()
        delete_layout.addWidget(delete_btn)
        delete_layout.addStretch()

        scroll_layout.addLayout(delete_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        # ====== Dock Widget (Pencarian) ======
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul...")
        self.search_input.textChanged.connect(self.search_data)

        search_dock = QDockWidget("Pencarian Buku", self)
        search_dock.setWidget(self.search_input)
        search_dock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, search_dock)

        # ====== Tab Widget ======
        self.tabs = QTabWidget()

        # Tab Data Buku
        data_tab = QWidget()
        data_tab.setLayout(QVBoxLayout())
        data_tab.layout().addWidget(scroll_area)

        # Tab Ekspor
        export_tab = QWidget()
        export_layout = QVBoxLayout()
        export_btn = QPushButton("Ekspor ke CSV")
        export_btn.clicked.connect(self.export_to_csv)
        export_layout.addWidget(export_btn)
        export_layout.addStretch()
        export_tab.setLayout(export_layout)

        self.tabs.addTab(data_tab, "Data Buku")
        self.tabs.addTab(export_tab, "Ekspor")

        self.setCentralWidget(self.tabs)

    def save_data(self):
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()

        if not title or not author or not year:
            QMessageBox.warning(self, "Peringatan", "Isi semua kolom terlebih dahulu.")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year))
        self.conn.commit()
        self.clear_inputs()
        self.load_data()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()

        self.table.setRowCount(0)
        for row_num, row_data in enumerate(rows):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def load_row_to_input(self, row, _column):
        self.selected_row_id = int(self.table.item(row, 0).text())
        self.title_input.setText(self.table.item(row, 1).text())
        self.author_input.setText(self.table.item(row, 2).text())
        self.year_input.setText(self.table.item(row, 3).text())

    def search_by_menu(self):
        search_text, ok = QInputDialog.getText(self, "Cari Judul", "Masukkan judul buku:")
        if ok and search_text:
            self.search_data(search_text)

    def delete_data(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih data yang ingin dihapus.")
            return

        row_id = int(self.table.item(selected, 0).text())
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM books WHERE id=?", (row_id,))
        self.conn.commit()
        self.load_data()

    def search_data(self, text):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + text + '%',))
        rows = cursor.fetchall()
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(rows):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File", "", "CSV Files (*.csv)")
        if path:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM books")
            rows = cursor.fetchall()
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(rows)
            QMessageBox.information(self, "Berhasil", "Data berhasil diekspor ke CSV.")

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.title_input.setText(clipboard.text())

    def clear_inputs(self):
        self.title_input.clear()
        self.author_input.clear()
        self.year_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec_())

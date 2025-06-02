"""
Main window for the Woodcut application.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QWizard, QWizardPage, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from .specification_dialog import SpecificationDialog
from specification_manager import SpecificationManager, WoodElement
from pdf_parser import PDFParser

class ProjectWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project Wizard")
        self.pdf_spec_data = None  # Сохраняем результат анализа PDF
        self.spec_dialog = SpecificationDialog()  # Создаём один раз
        self.setup_pages()
        
    def setup_pages(self):
        # Page 1: Load PDF
        pdf_page = QWizardPage()
        pdf_page.setTitle("Load Project PDF")
        pdf_layout = QVBoxLayout()
        pdf_page.setLayout(pdf_layout)
        
        pdf_label = QLabel("Select the project PDF file to analyze:")
        pdf_layout.addWidget(pdf_label)
        
        pdf_btn = QPushButton("Browse PDF...")
        pdf_btn.clicked.connect(self.browse_pdf)
        pdf_layout.addWidget(pdf_btn)
        pdf_layout.addStretch()
        self.addPage(pdf_page)
        
        # Page 2: Specification
        spec_page = QWizardPage()
        spec_page.setTitle("Wood Specification")
        spec_layout = QVBoxLayout()
        spec_layout.addWidget(self.spec_dialog)  # Используем уже созданный экземпляр
        spec_page.setLayout(spec_layout)
        self.addPage(spec_page)
        
        # Page 3: Stock Configuration
        stock_page = QWizardPage()
        stock_page.setTitle("Stock Configuration")
        stock_layout = QVBoxLayout()
        stock_page.setLayout(stock_layout)
        
        stock_label = QLabel("Configure available wood stock:")
        stock_layout.addWidget(stock_label)
        stock_layout.addStretch()
        self.addPage(stock_page)
        
        # Page 4: Review
        review_page = QWizardPage()
        review_page.setTitle("Review and Generate")
        review_layout = QVBoxLayout()
        review_page.setLayout(review_layout)
        
        review_label = QLabel("Review cutting plan and generate output:")
        review_layout.addWidget(review_label)
        review_layout.addStretch()
        self.addPage(review_page)

    def browse_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_name:
            print("Выбран файл:", file_name)
            parser = PDFParser(file_name)
            spec = parser.extract_specification()
            print(f"[DEBUG] extract_specification() вернул: {spec}")
            self.pdf_spec_data = spec['specifications']
            # Автоматически заполняем таблицу спецификаций
            self.fill_specification_from_pdf()

    def fill_specification_from_pdf(self):
        """Заполняет таблицу спецификаций из данных PDF."""
        if not self.pdf_spec_data:
            print("[DEBUG] Нет данных PDF для заполнения спецификации")
            return
        print(f"[DEBUG] Ключи первой строки: {list(self.pdf_spec_data[0].keys())}")
        print(f"[DEBUG] Значения первой строки: {self.pdf_spec_data[0]}")
        self.spec_dialog.spec_manager.elements.clear()
        used_ids = set()
        for idx, row in enumerate(self.pdf_spec_data):
            raw_id = row.get('Поз', '').strip()
            if not raw_id or raw_id in used_ids:
                element_id = str(idx+1)
            else:
                element_id = raw_id
                used_ids.add(element_id)
            # Парсим длину с удалением пробелов
            raw_length = str(row.get('Длина, мм', '0')).replace(' ', '').replace('\u00A0', '')
            try:
                length = float(raw_length)
            except Exception:
                length = 0.0
            element = WoodElement(
                id=element_id,
                description=row.get('Наименование', ''),
                length=length,
                width=float(row.get('Ширина, мм', 0)),
                height=float(row.get('Толщина, мм', row.get('Высота, мм', 0))),
                quantity=int(row.get('Кол-во, шт.', 1)),
                is_rectangular=True,
                notes=''
            )
            self.spec_dialog.spec_manager.add_element(element)
        print(f"[DEBUG] Всего элементов после импорта из PDF: {len(self.spec_dialog.spec_manager.elements)}")
        for el in self.spec_dialog.spec_manager.elements.values():
            print(f"[DEBUG] {el}")
        self.spec_dialog.update_table()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("Woodcut - Wood Cutting Optimization")
        self.setMinimumSize(1024, 768)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Welcome message
        welcome_label = QLabel("Welcome to Woodcut")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.start_new_project)
        btn_layout.addWidget(new_project_btn)
        
        open_project_btn = QPushButton("Open Project")
        open_project_btn.clicked.connect(self.open_project)
        btn_layout.addWidget(open_project_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.start_new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def start_new_project(self):
        """Start a new project wizard."""
        wizard = ProjectWizard(self)
        wizard.exec()
    
    def open_project(self):
        """Open an existing project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "Woodcut Projects (*.woodcut);;All Files (*.*)"
        )
        if file_path:
            # TODO: Implement project loading
            pass
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Woodcut",
            "Woodcut - Wood Cutting Optimization System\n\n"
            "Version: 0.1.0\n"
            "A tool for optimizing wood cutting patterns from architectural drawings."
        ) 
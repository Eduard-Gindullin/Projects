"""
Dialog for manual specification input and import.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QLabel, QSpinBox,
    QDoubleSpinBox, QLineEdit, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from specification_manager import SpecificationManager, WoodElement

class SpecificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spec_manager = SpecificationManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Wood Specification")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Project info
        project_group = QGroupBox("Project Information")
        project_layout = QHBoxLayout()
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Project Name")
        project_layout.addWidget(QLabel("Project Name:"))
        project_layout.addWidget(self.project_name)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Поз.", "Наименование", "Length (mm)", "Width (mm)", "Thickness (mm)",
            "Quantity", "Rectangular", "Notes"
        ])
        layout.addWidget(self.table)
        
        # Input group
        input_group = QGroupBox("Add New Element")
        input_layout = QHBoxLayout()
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description")
        
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(0, 10000)
        self.length_input.setSuffix(" mm")
        
        self.width_input = QDoubleSpinBox()
        self.width_input.setRange(0, 1000)
        self.width_input.setSuffix(" mm")
        
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(0, 1000)
        self.height_input.setSuffix(" mm")
        self.height_input.setPrefix("")
        self.height_input.setToolTip("Толщина (мм)")
        
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 1000)
        
        self.rect_input = QCheckBox("Rectangular")
        self.rect_input.setChecked(True)
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Notes")
        
        input_layout.addWidget(self.id_input)
        input_layout.addWidget(self.desc_input)
        input_layout.addWidget(self.length_input)
        input_layout.addWidget(self.width_input)
        input_layout.addWidget(self.height_input)
        input_layout.addWidget(self.qty_input)
        input_layout.addWidget(self.rect_input)
        input_layout.addWidget(self.notes_input)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_element)
        input_layout.addWidget(add_btn)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        import_excel_btn = QPushButton("Import Excel")
        import_excel_btn.clicked.connect(self.import_excel)
        btn_layout.addWidget(import_excel_btn)
        
        import_csv_btn = QPushButton("Import CSV")
        import_csv_btn.clicked.connect(self.import_csv)
        btn_layout.addWidget(import_csv_btn)
        
        export_excel_btn = QPushButton("Export Excel")
        export_excel_btn.clicked.connect(self.export_excel)
        btn_layout.addWidget(export_excel_btn)
        
        btn_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def add_element(self):
        """Add new element to the specification."""
        try:
            element = WoodElement(
                id=self.id_input.text(),
                description=self.desc_input.text(),
                length=self.length_input.value(),
                width=self.width_input.value(),
                height=self.height_input.value() if hasattr(self, 'height_input') else 0.0,
                quantity=self.qty_input.value(),
                is_rectangular=self.rect_input.isChecked(),
                notes=self.notes_input.text()
            )
            
            self.spec_manager.add_element(element)
            self.update_table()
            self.clear_inputs()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def clear_inputs(self):
        """Clear input fields."""
        self.id_input.clear()
        self.desc_input.clear()
        self.length_input.setValue(0)
        self.width_input.setValue(0)
        self.height_input.setValue(0)
        self.qty_input.setValue(1)
        self.rect_input.setChecked(True)
        self.notes_input.clear()
    
    def update_table(self):
        """Update the table with current specification."""
        print(f"[DEBUG] update_table: элементов в spec_manager: {len(self.spec_manager.elements)}")
        self.table.setRowCount(0)
        for element in self.spec_manager.elements.values():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(element.id))
            self.table.setItem(row, 1, QTableWidgetItem(element.description))
            self.table.setItem(row, 2, QTableWidgetItem(str(element.length)))
            self.table.setItem(row, 3, QTableWidgetItem(str(element.width)))
            self.table.setItem(row, 4, QTableWidgetItem(str(getattr(element, 'height', 0.0))))
            self.table.setItem(row, 5, QTableWidgetItem(str(element.quantity)))
            self.table.setItem(row, 6, QTableWidgetItem("Yes" if element.is_rectangular else "No"))
            self.table.setItem(row, 7, QTableWidgetItem(element.notes))
    
    def import_excel(self):
        """Import specification from Excel file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            try:
                self.spec_manager.import_from_excel(file_path)
                self.update_table()
            except Exception as e:
                QMessageBox.warning(self, "Import Error", str(e))
    
    def import_csv(self):
        """Import specification from CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                self.spec_manager.import_from_csv(file_path)
                self.update_table()
            except Exception as e:
                QMessageBox.warning(self, "Import Error", str(e))
    
    def export_excel(self):
        """Export specification to Excel file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Excel", "", "Excel Files (*.xlsx)"
        )
        if file_path:
            try:
                self.spec_manager.export_to_excel(file_path)
                QMessageBox.information(self, "Success", "Specification exported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))
    
    def get_specification(self) -> SpecificationManager:
        """Get the current specification."""
        return self.spec_manager 
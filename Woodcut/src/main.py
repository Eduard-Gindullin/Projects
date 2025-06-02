"""
Main entry point for the Woodcut application.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("Woodcut")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Woodcut")
    app.setOrganizationDomain("woodcut.local")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from src.MainWindow import MainWindow

def main():
    """
    Main entry point for the application
    """
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.showMaximized()
    
    # Start the event loop
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
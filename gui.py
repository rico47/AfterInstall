
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLabel
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal

import app

class Worker(QObject):
    """Pracownik do uruchamiania procesu w osobnym wątku."""
    finished = pyqtSignal()
    log_updated = pyqtSignal(str)

    def __init__(self, package_manager):
        super().__init__()
        self.package_manager = package_manager

    def run(self):
        """Uruchamia proces instalacji."""
        try:
            # Listy programów i usług są zdefiniowane w app.py
            app.run_installation_process(
                app.PROGRAMY_DO_INSTALACJI,
                app.USLUGI_DO_ZARZADZANIA,
                self.log_updated.emit,
                self.package_manager
            )
        except Exception as e:
            self.log_updated.emit(f"Wystąpił nieoczekiwany błąd: {e}")
        finally:
            self.finished.emit()

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instalator")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Wybór systemu
        system_layout = QHBoxLayout()
        system_label = QLabel("Wybierz menedżer pakietów:")
        self.pm_combo = QComboBox()
        self.pm_combo.addItems(["pacman", "apt", "dnf"])
        
        system_layout.addWidget(system_label)
        system_layout.addWidget(self.pm_combo)
        layout.addLayout(system_layout)

        # Przycisk Start
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_installation)
        layout.addWidget(self.start_button)

        self.resize(350, 100)

    def start_installation(self):
        """Uruchamia proces instalacji w osobnym wątku."""
        self.start_button.setEnabled(False)
        package_manager = self.pm_combo.currentText()
        
        print(f"--- Rozpoczynam instalację dla systemu: {package_manager} ---")

        self.thread = QThread()
        self.worker = Worker(package_manager)
        self.worker.moveToThread(self.thread)

        # Łączenie sygnałów
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.log_updated.connect(lambda msg: print(msg))
        self.thread.finished.connect(lambda: self.start_button.setEnabled(True))
        self.thread.finished.connect(lambda: print("--- Zakończono ---"))

        self.thread.start()

if __name__ == "__main__":
    app_instance = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app_instance.exec())

import sys
import matplotlib
matplotlib.use('QtAgg')

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 11))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

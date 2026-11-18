"""Launch the LIFE Appearance application in the Qt desktop."""

import sys
from PySide6.QtWidgets import QApplication
from lifeos.ui.pages.appearance_page import AppearancePage


def main():
    app = QApplication(sys.argv)
    window = AppearancePage()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

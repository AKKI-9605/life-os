"""LIFE OS desktop companion."""
import sys

from PySide6.QtWidgets import QApplication

from lifeos.ui.main_window import LifeOSWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("LIFE OS")
    app.setOrganizationName("AKKI-9605")

    window = LifeOSWindow(app)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

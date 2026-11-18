from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class NavigationSidebar(QFrame):
    page_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setObjectName("sidebar")
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(8)

        brand = QLabel("LIFE OS")
        brand.setObjectName("brand")
        layout.addWidget(brand)

        layout.addSpacing(28)

        section = QLabel("WORKSPACE")
        section.setObjectName("eyebrow")
        layout.addWidget(section)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.buttons = {}

        for index, name in enumerate(("Overview", "Notes")):
            button = QPushButton(name)
            button.setCheckable(True)
            button.setObjectName("navigationButton")

            self.button_group.addButton(button, index)
            self.buttons[name] = button

            layout.addWidget(button)

        self.button_group.idClicked.connect(self.page_selected.emit)

        self.buttons["Overview"].setChecked(True)

        layout.addStretch()

        footer = QLabel("A little space to think.")
        footer.setObjectName("muted")
        layout.addWidget(footer)

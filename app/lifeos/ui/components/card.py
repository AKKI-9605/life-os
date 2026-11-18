from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget


class LifeCard(QFrame):
    def __init__(
        self,
        title: str,
        description: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.setObjectName("lifeCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        layout.addWidget(self.title_label)

        self.description_label = QLabel(description)
        self.description_label.setObjectName("cardDescription")
        self.description_label.setWordWrap(True)

        if description:
            layout.addWidget(self.description_label)

        self.setStyleSheet("""
            QFrame#lifeCard {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 14px;
            }

            QLabel#cardTitle {
                font-size: 16px;
                font-weight: 600;
                color: palette(text);
            }

            QLabel#cardDescription {
                font-size: 13px;
                color: palette(mid);
            }
        """)

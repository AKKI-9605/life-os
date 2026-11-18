from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)


class DashboardPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(12)

        eyebrow = QLabel("YOUR SPACE")
        eyebrow.setObjectName("eyebrow")
        layout.addWidget(eyebrow)

        title = QLabel("A calmer way to work.")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        description = QLabel(
            "A little space to think, organise, and get things done."
        )
        description.setObjectName("muted")
        layout.addWidget(description)

        layout.addStretch()

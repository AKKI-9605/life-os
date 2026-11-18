import json
from pathlib import Path

from platformdirs import user_config_path

from lifeos.config import APP_NAME, APP_AUTHOR, DEFAULT_THEME, SUPPORTED_THEMES


class Settings:
    def __init__(self, config_file: Path | None = None):
        self.config_file = config_file or (
            user_config_path(APP_NAME, APP_AUTHOR) / "settings.json"
        )
        self._data = {
            "theme": DEFAULT_THEME,
        }
        self.load()

    def load(self) -> None:
        if not self.config_file.exists():
            return

        try:
            data = json.loads(self.config_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        if isinstance(data, dict):
            theme = data.get("theme")
            if theme in SUPPORTED_THEMES:
                self._data["theme"] = theme

    def save(self) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(
            json.dumps(self._data, indent=4),
            encoding="utf-8",
        )

    def get_theme(self) -> str:
        return self._data["theme"]

    def set_theme(self, theme: str) -> None:
        if theme not in SUPPORTED_THEMES:
            raise ValueError(f"Unsupported theme: {theme}")

        self._data["theme"] = theme
        self.save()

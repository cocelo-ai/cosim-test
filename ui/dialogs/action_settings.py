# ui/dialogs/action_settings.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLabel, QDialogButtonBox, QGroupBox
)
from PyQt5.QtGui import QDoubleValidator

from ui.custom_widgets import NoWheelComboBox
from ui.utils import to_float, to_int


class ActionSettingsDialog(QDialog):
    def __init__(self, settings, parent):
        super().__init__(parent)
        self.setWindowTitle("Action Settings")
        self.settings = settings if isinstance(settings, dict) else {}
        self.parent_widget = parent
        self.scale_cbs = []

        self._setup_ui()
        self.resize(420, min(720, 120 + self.action_dim * 34))

    def _scale_options(self):
        return [
            "0", "0.01", "0.05", "0.1", "0.15", "0.25", "0.5", "0.75",
            "1.0", "1.5", "2.0", "2.5", "5.0", "10.0", "20.0", "40.0"
        ]

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        env_id = self.parent_widget.env_id_cb.currentText()
        env_cfg = self.parent_widget.env_config.get(env_id, {}) or {}
        hw_cfg = env_cfg.get("hardware", {}) if isinstance(env_cfg.get("hardware", {}), dict) else {}
        self.action_dim = to_int(self.settings.get("action_dim", hw_cfg.get("action_dim", 0)), 0)

        raw_scales = self.settings.get("action_scales", env_cfg.get("action_scales", []))
        if not isinstance(raw_scales, (list, tuple)) or len(raw_scales) != self.action_dim:
            raw_scales = [1.0] * self.action_dim

        group = QGroupBox("Action Scales")
        grid = QGridLayout(group)
        grid.addWidget(QLabel("Index"), 0, 0)
        grid.addWidget(QLabel("Scale"), 0, 1)

        validator = QDoubleValidator(0.0, 1e6, 6)
        validator.setNotation(QDoubleValidator.StandardNotation)
        options = self._scale_options()

        for i in range(self.action_dim):
            grid.addWidget(QLabel(f"action[{i}]"), i + 1, 0)
            cb = NoWheelComboBox()
            cb.setEditable(True)
            cb.addItems(options)
            cb.lineEdit().setValidator(validator)

            value = to_float(raw_scales[i], 1.0)
            text = str(value)
            cb.setCurrentText(text if text in options else text)
            grid.addWidget(cb, i + 1, 1)
            self.scale_cbs.append(cb)

        layout.addWidget(group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self):
        return {
            "action_dim": self.action_dim,
            "action_scales": [to_float(cb.currentText(), 1.0) for cb in self.scale_cbs],
        }

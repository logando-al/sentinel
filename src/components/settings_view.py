"""
PDF Sentinel - Settings View Widget
Settings panel for customizing app behavior and seal options.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QFrame, QLineEdit,
    QComboBox, QCheckBox, QColorDialog, QGroupBox,
    QFormLayout, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor
import qtawesome as qta

from core.settings_manager import settings


ICON_COLOR = "#88A9C3"


class SettingsViewWidget(QWidget):
    """Settings panel for app configuration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Initialize the UI."""
        # Main layout for scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Header
        header = QLabel("Settings")
        header.setObjectName("pageHeader")
        layout.addWidget(header)
        
        subtitle = QLabel("Customize PDF Sentinel behavior and seal appearance")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)
        
        # Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_group.setObjectName("settingsGroup")
        output_layout = QFormLayout(output_group)
        
        # Output folder
        folder_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setPlaceholderText("Same as input file")
        self.output_folder_input.setReadOnly(True)
        folder_layout.addWidget(self.output_folder_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondaryButton")
        browse_btn.clicked.connect(self._browse_output_folder)
        folder_layout.addWidget(browse_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("textButton")
        clear_btn.clicked.connect(self._clear_output_folder)
        folder_layout.addWidget(clear_btn)
        
        output_layout.addRow("Output Folder:", folder_layout)
        layout.addWidget(output_group)
        
        # Seal Settings Group
        seal_group = QGroupBox("Seal Settings")
        seal_group.setObjectName("settingsGroup")
        seal_layout = QVBoxLayout(seal_group)
        seal_layout.setSpacing(8)
        
        # Enable seal checkbox
        self.seal_enabled_check = QCheckBox("Add visual seal to stamped PDFs")
        self.seal_enabled_check.stateChanged.connect(self._on_seal_enabled_changed)
        seal_layout.addWidget(self.seal_enabled_check)
        seal_layout.addSpacing(30)
        
        # Seal position row
        position_row = QHBoxLayout()
        position_label = QLabel("Position:")
        position_label.setFixedWidth(80)
        position_row.addWidget(position_label)
        self.seal_position_combo = QComboBox()
        self.seal_position_combo.addItems([
            "Top Right",
            "Top Left", 
            "Bottom Right",
            "Bottom Left"
        ])
        self.seal_position_combo.setObjectName("settingsCombo")
        position_row.addWidget(self.seal_position_combo)
        position_row.addStretch()
        seal_layout.addLayout(position_row)
        seal_layout.addSpacing(8)
        
        # Seal color row
        color_row = QHBoxLayout()
        color_label = QLabel("Color:")
        color_label.setFixedWidth(80)
        color_row.addWidget(color_label)
        self.seal_color_preview = QLabel()
        self.seal_color_preview.setFixedSize(32, 32)
        self.seal_color_preview.setObjectName("colorPreview")
        color_row.addWidget(self.seal_color_preview)
        self.seal_color_btn = QPushButton("  Choose Color")
        self.seal_color_btn.setIcon(qta.icon("fa5s.palette", color=ICON_COLOR))
        self.seal_color_btn.setIconSize(QSize(14, 14))
        self.seal_color_btn.setObjectName("secondaryButton")
        self.seal_color_btn.clicked.connect(self._choose_seal_color)
        color_row.addWidget(self.seal_color_btn)
        color_row.addStretch()
        seal_layout.addLayout(color_row)
        seal_layout.addSpacing(8)
        
        # Seal text row
        text_row = QHBoxLayout()
        text_label = QLabel("Seal Text:")
        text_label.setFixedWidth(80)
        text_row.addWidget(text_label)
        self.seal_text_input = QLineEdit()
        self.seal_text_input.setPlaceholderText("SENTINEL VERIFIED")
        self.seal_text_input.setMaxLength(30)
        text_row.addWidget(self.seal_text_input)
        seal_layout.addLayout(text_row)
        
        layout.addWidget(seal_group)
        
        # App Settings Group
        app_group = QGroupBox("App Settings")
        app_group.setObjectName("settingsGroup")
        app_layout = QFormLayout(app_group)
        
        # Theme toggle
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setObjectName("settingsCombo")
        app_layout.addRow("Theme:", self.theme_combo)
        
        # Sound enabled
        self.sound_check = QCheckBox("Enable sound feedback")
        app_layout.addRow("", self.sound_check)
        
        layout.addWidget(app_group)
        
        layout.addStretch()
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        reset_btn = QPushButton("  Reset to Defaults")
        reset_btn.setIcon(qta.icon("fa5s.undo", color=ICON_COLOR))
        reset_btn.setIconSize(QSize(14, 14))
        reset_btn.setObjectName("secondaryButton")
        reset_btn.clicked.connect(self._reset_defaults)
        btn_layout.addWidget(reset_btn)
        
        save_btn = QPushButton("  Save Settings")
        save_btn.setIcon(qta.icon("fa5s.save", color="#000000"))
        save_btn.setIconSize(QSize(14, 14))
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Store current color
        self._current_color = "#88A9C3"
    
    def _load_settings(self):
        """Load current settings into UI."""
        # Output folder
        self.output_folder_input.setText(settings.output_folder)
        
        # Seal enabled
        self.seal_enabled_check.setChecked(settings.seal_enabled)
        
        # Seal position
        position_map = {
            "top-right": 0,
            "top-left": 1,
            "bottom-right": 2,
            "bottom-left": 3
        }
        self.seal_position_combo.setCurrentIndex(position_map.get(settings.seal_position, 0))
        
        # Seal color
        self._current_color = settings.seal_color
        self._update_color_preview()
        
        # Seal text
        self.seal_text_input.setText(settings.seal_text)
        
        # Theme
        self.theme_combo.setCurrentIndex(0 if settings.theme == "dark" else 1)
        
        # Sound
        self.sound_check.setChecked(settings.sound_enabled)
        
        # Update enabled state
        self._on_seal_enabled_changed()
    
    def _save_settings(self):
        """Save current UI values to settings."""
        # Output folder
        settings.output_folder = self.output_folder_input.text()
        
        # Seal enabled
        settings.seal_enabled = self.seal_enabled_check.isChecked()
        
        # Seal position
        position_values = ["top-right", "top-left", "bottom-right", "bottom-left"]
        settings.seal_position = position_values[self.seal_position_combo.currentIndex()]
        
        # Seal color
        settings.seal_color = self._current_color
        
        # Seal text
        text = self.seal_text_input.text().strip()
        settings.seal_text = text if text else "SENTINEL VERIFIED"
        
        # Theme
        new_theme = "dark" if self.theme_combo.currentIndex() == 0 else "light"
        if new_theme != settings.theme:
            settings.theme = new_theme
            self._apply_theme(new_theme)
        
        # Sound
        settings.sound_enabled = self.sound_check.isChecked()
        
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved.")
    
    def _apply_theme(self, theme_name: str):
        """Apply the selected theme to the application."""
        import sys
        from pathlib import Path
        from PyQt6.QtWidgets import QApplication
        
        # Get resource path
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent
        
        if theme_name == "light":
            style_file = base_path / "assets" / "styles_light.qss"
        else:
            style_file = base_path / "assets" / "styles.qss"
        
        try:
            with open(style_file, "r", encoding="utf-8") as f:
                QApplication.instance().setStyleSheet(f.read())
        except FileNotFoundError:
            pass
    
    def _browse_output_folder(self):
        """Open folder dialog for output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_input.setText(folder)
    
    def _clear_output_folder(self):
        """Clear output folder (use same as input)."""
        self.output_folder_input.clear()
    
    def _choose_seal_color(self):
        """Open color picker for seal color."""
        current = QColor(self._current_color)
        color = QColorDialog.getColor(current, self, "Choose Seal Color")
        if color.isValid():
            self._current_color = color.name()
            self._update_color_preview()
    
    def _update_color_preview(self):
        """Update the color preview label."""
        self.seal_color_preview.setStyleSheet(
            f"background-color: {self._current_color}; "
            f"border: 1px solid #333; border-radius: 4px;"
        )
    
    def _on_seal_enabled_changed(self):
        """Handle seal enabled checkbox change."""
        enabled = self.seal_enabled_check.isChecked()
        self.seal_position_combo.setEnabled(enabled)
        self.seal_color_btn.setEnabled(enabled)
        self.seal_text_input.setEnabled(enabled)
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            settings.reset_defaults()
            self._load_settings()
            QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults.")

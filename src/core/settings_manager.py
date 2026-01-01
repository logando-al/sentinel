"""
PDF Sentinel - Settings Manager
Handles persistent settings using QSettings.
"""

from PyQt6.QtCore import QSettings
from pathlib import Path
from typing import Any, Optional


# Default settings values
DEFAULTS = {
    # Output settings
    "output_folder": "",  # Empty = same folder as input
    
    # Seal settings
    "seal_enabled": True,
    "seal_position": "top-right",  # top-right, top-left, bottom-right, bottom-left
    "seal_color": "#88A9C3",  # Accent color
    "seal_text": "SENTINEL VERIFIED",  # Custom text on seal
    
    # App settings
    "last_folder": "",
    "theme": "dark",  # dark or light
    "sound_enabled": True,
}


class SettingsManager:
    """Manages application settings persistence."""
    
    _instance: Optional["SettingsManager"] = None
    
    def __new__(cls):
        """Singleton pattern - only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._settings = QSettings("Sentinel", "PDFSentinel")
        self._initialized = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key name
            default: Default value if not set (uses DEFAULTS if None)
            
        Returns:
            The setting value
        """
        if default is None:
            default = DEFAULTS.get(key, None)
        
        value = self._settings.value(key, default)
        
        # Handle boolean conversion (QSettings returns strings)
        if isinstance(default, bool):
            if isinstance(value, str):
                return value.lower() == "true"
            return bool(value)
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set a setting value.
        
        Args:
            key: Setting key name
            value: Value to store
        """
        self._settings.setValue(key, value)
        self._settings.sync()
    
    def reset_defaults(self):
        """Reset all settings to default values."""
        for key, value in DEFAULTS.items():
            self._settings.setValue(key, value)
        self._settings.sync()
    
    def get_all(self) -> dict:
        """Get all settings as a dictionary."""
        return {key: self.get(key) for key in DEFAULTS.keys()}
    
    # Convenience properties for common settings
    @property
    def output_folder(self) -> str:
        return self.get("output_folder", "")
    
    @output_folder.setter
    def output_folder(self, value: str):
        self.set("output_folder", value)
    
    @property
    def seal_enabled(self) -> bool:
        return self.get("seal_enabled", True)
    
    @seal_enabled.setter
    def seal_enabled(self, value: bool):
        self.set("seal_enabled", value)
    
    @property
    def seal_position(self) -> str:
        return self.get("seal_position", "top-right")
    
    @seal_position.setter
    def seal_position(self, value: str):
        self.set("seal_position", value)
    
    @property
    def seal_color(self) -> str:
        return self.get("seal_color", "#88A9C3")
    
    @seal_color.setter
    def seal_color(self, value: str):
        self.set("seal_color", value)
    
    @property
    def seal_text(self) -> str:
        return self.get("seal_text", "SENTINEL VERIFIED")
    
    @seal_text.setter
    def seal_text(self, value: str):
        self.set("seal_text", value)
    
    @property
    def theme(self) -> str:
        return self.get("theme", "dark")
    
    @theme.setter
    def theme(self, value: str):
        self.set("theme", value)
    
    @property
    def sound_enabled(self) -> bool:
        return self.get("sound_enabled", True)
    
    @sound_enabled.setter
    def sound_enabled(self, value: bool):
        self.set("sound_enabled", value)


# Global settings instance
settings = SettingsManager()

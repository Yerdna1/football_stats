import json
import os
import logging
from typing import Dict, List, Any, Optional
import customtkinter as ctk

from modules.config import DEFAULT_SETTINGS, THEMES

logger = logging.getLogger(__name__)

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or use defaults"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                logger.info(f"Settings loaded from {self.settings_file}")
                return settings
            else:
                logger.info(f"Settings file {self.settings_file} not found using defaults")
                return DEFAULT_SETTINGS.copy()
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            return DEFAULT_SETTINGS.copy()
            
    def _save_settings(self) -> bool:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logger.info(f"Settings saved to {self.settings_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            return False
            
    def get_setting(self, key: str) -> Any:
        """Get a setting value"""
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))
        
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value"""
        self.settings[key] = value
        return self._save_settings()
        
    def get_leagues(self) -> List[int]:
        """Get selected leagues"""
        return self.settings.get("leagues", DEFAULT_SETTINGS.get("leagues"))
        
    def get_form_length(self) -> int:
        """Get form length"""
        return self.settings.get("form_length", DEFAULT_SETTINGS.get("form_length"))
        
    def get_threshold(self) -> float:
        """Get performance difference threshold"""
        return self.settings.get("threshold", DEFAULT_SETTINGS.get("threshold"))
        
    def get_auto_refresh(self) -> bool:
        """Get auto refresh setting"""
        return self.settings.get("auto_refresh", DEFAULT_SETTINGS.get("auto_refresh"))
        
    def get_refresh_interval(self) -> int:
        """Get refresh interval in minutes"""
        return self.settings.get("refresh_interval", DEFAULT_SETTINGS.get("refresh_interval"))
        
    def get_appearance_mode(self) -> str:
        """Get appearance mode"""
        return self.settings.get("appearance_mode", DEFAULT_SETTINGS.get("appearance_mode"))
        
    def get_color_theme(self) -> str:
        """Get color theme"""
        return self.settings.get("color_theme", DEFAULT_SETTINGS.get("color_theme"))
        
    def get_theme(self) -> Dict[str, str]:
        """Get theme colors"""
        theme_name = self.get_color_theme()
        return THEMES.get(theme_name, THEMES["blue"])
        
    def get_available_themes(self) -> List[str]:
        """Get list of available themes"""
        return list(THEMES.keys())
        
    def get_font_size(self) -> int:
        """Get font size for tables and detail windows"""
        return self.settings.get("font_size", DEFAULT_SETTINGS.get("font_size"))
        
    def reset_to_defaults(self) -> bool:
        """Reset settings to defaults"""
        self.settings = DEFAULT_SETTINGS.copy()
        return self._save_settings()
        
    def apply_appearance_settings(self):
        """Apply appearance settings to CustomTkinter"""
        # Set appearance mode
        appearance_mode = self.get_appearance_mode()
        ctk.set_appearance_mode(appearance_mode)
        
        # Set color theme
        # Note: CustomTkinter doesn't support custom color themes directly
        # We're using our own theme system

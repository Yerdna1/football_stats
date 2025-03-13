import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog
import logging
from typing import Dict, List, Any, Optional, Callable

from modules.settings_manager import SettingsManager
from modules.league_names import LEAGUE_NAMES, get_league_options, ALL_LEAGUES
from modules.config import THEMES, PREDICTION_THRESHOLD_LEVEL1, PREDICTION_THRESHOLD_LEVEL2
from modules.translations import translate

logger = logging.getLogger(__name__)

class SettingsTab:
    def __init__(self, parent, settings_manager: SettingsManager, on_settings_changed: Callable, db_manager=None):
        self.parent = parent
        self.settings_manager = settings_manager
        self.on_settings_changed = on_settings_changed
        self.db_manager = db_manager
        
        # Get theme colors
        self.theme = self.settings_manager.get_theme()
        
        # Create UI elements
        self._create_ui()
        
    def _create_ui(self):
        """Create the settings tab UI elements"""
        # Main container with padding
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header section
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.pack(fill="x", padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Settings", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=10)
        
        # Create notebook for settings categories
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Appearance Tab
        self.appearance_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.appearance_frame, text="Appearance")
        self._create_appearance_settings()
        
        # Data Tab
        self.data_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.data_frame, text="Data Settings")
        self._create_data_settings()
        
        # Leagues Tab
        self.leagues_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.leagues_frame, text="Leagues")
        self._create_leagues_settings()
        
        # Predictions Tab
        self.predictions_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.predictions_frame, text="Predictions")
        self._create_predictions_settings()
        
        # Save and Reset Buttons
        self.buttons_frame = ctk.CTkFrame(self.main_frame)
        self.buttons_frame.pack(fill="x", padx=10, pady=10)
        
        self.save_button = ctk.CTkButton(
            self.buttons_frame,
            text="Save Settings",
            command=self._save_settings,
            width=150,
            height=32,
            corner_radius=8,
            border_width=0,
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"],
            text_color="white"
        )
        self.save_button.pack(side="right", padx=10, pady=10)
        
        self.reset_button = ctk.CTkButton(
            self.buttons_frame,
            text="Reset to Defaults",
            command=self._reset_settings,
            width=150,
            height=32,
            corner_radius=8,
            border_width=0,
            fg_color=self.theme["secondary"],
            hover_color=self.theme["primary"],
            text_color="white"
        )
        self.reset_button.pack(side="right", padx=10, pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.buttons_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=10)
        
    def _create_appearance_settings(self):
        """Create appearance settings UI"""
        # Main container with grid layout for better space usage
        self.appearance_container = ctk.CTkFrame(self.appearance_frame)
        self.appearance_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid layout
        self.appearance_container.columnconfigure(0, weight=1)
        self.appearance_container.columnconfigure(1, weight=1)
        
        # Appearance Mode (Left column)
        self.appearance_mode_frame = ctk.CTkFrame(self.appearance_container)
        self.appearance_mode_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.appearance_mode_label = ctk.CTkLabel(
            self.appearance_mode_frame,
            text="Appearance Mode:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.appearance_mode_label.pack(anchor="w", padx=10, pady=(10, 15))
        
        self.appearance_mode_var = tk.StringVar(value=self.settings_manager.get_appearance_mode())
        
        # Create radio buttons for appearance modes
        modes_frame = ctk.CTkFrame(self.appearance_mode_frame, fg_color="transparent")
        modes_frame.pack(fill="x", padx=10, pady=5)
        
        for mode in ["System", "Light", "Dark"]:
            mode_radio = ctk.CTkRadioButton(
                modes_frame,
                text=mode,
                variable=self.appearance_mode_var,
                value=mode,
                font=ctk.CTkFont(size=14)
            )
            mode_radio.pack(anchor="w", padx=20, pady=8)
        
        # Font Size (Right column)
        self.font_size_frame = ctk.CTkFrame(self.appearance_container)
        self.font_size_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.font_size_label = ctk.CTkLabel(
            self.font_size_frame,
            text="Font Size (Tables & Details):",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.font_size_label.pack(anchor="w", padx=10, pady=(10, 15))
        
        self.font_size_var = tk.IntVar(value=self.settings_manager.get_font_size())
        
        # Create slider controls frame
        slider_frame = ctk.CTkFrame(self.font_size_frame, fg_color="transparent")
        slider_frame.pack(fill="x", padx=10, pady=5)
        
        # Font size slider
        self.font_size_slider = ctk.CTkSlider(
            slider_frame,
            from_=12,
            to=80,
            number_of_steps=68,
            variable=self.font_size_var
        )
        self.font_size_slider.pack(fill="x", padx=10, pady=10)
        
        # Value and apply button in same row
        controls_frame = ctk.CTkFrame(slider_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        self.font_size_value_label = ctk.CTkLabel(
            controls_frame,
            text=f"Size: {self.font_size_var.get()} px",
            font=ctk.CTkFont(size=14)
        )
        self.font_size_value_label.pack(side="left", padx=10)
        
        # Apply button for immediate font size change
        self.apply_font_button = ctk.CTkButton(
            controls_frame,
            text="Apply",
            command=self._apply_font_size,
            width=100,
            height=30,
            corner_radius=8,
            border_width=0,
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"],
            text_color="white"
        )
        self.apply_font_button.pack(side="right", padx=10)
        
        # Update label when slider changes
        self.font_size_slider.configure(
            command=lambda value: self.font_size_value_label.configure(
                text=f"Size: {int(value)} px"
            )
        )
        
        # Color Theme (Full width, below other settings)
        self.color_theme_frame = ctk.CTkFrame(self.appearance_container)
        self.color_theme_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.color_theme_label = ctk.CTkLabel(
            self.color_theme_frame,
            text="Color Theme:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.color_theme_label.pack(anchor="w", padx=10, pady=(10, 15))
        
        self.color_theme_var = tk.StringVar(value=self.settings_manager.get_setting("color_theme"))
        
        # Create theme grid layout (2 columns)
        themes_frame = ctk.CTkFrame(self.color_theme_frame, fg_color="transparent")
        themes_frame.pack(fill="x", padx=10, pady=10)
        
        themes_frame.columnconfigure(0, weight=1)
        themes_frame.columnconfigure(1, weight=1)
        
        # Create a radio button for each theme with a color preview
        row = 0
        col = 0
        for i, theme_name in enumerate(self.settings_manager.get_available_themes()):
            theme_colors = THEMES[theme_name]
            
            theme_frame = ctk.CTkFrame(themes_frame)
            theme_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # Create color preview
            preview_frame = ctk.CTkFrame(theme_frame, width=30, height=30, fg_color=theme_colors["primary"])
            preview_frame.pack(side="left", padx=10, pady=10)
            
            # Create radio button
            theme_radio = ctk.CTkRadioButton(
                theme_frame,
                text=theme_name.capitalize(),
                variable=self.color_theme_var,
                value=theme_name,
                font=ctk.CTkFont(size=14)
            )
            theme_radio.pack(side="left", padx=10, pady=10)
            
            # Add accent color preview
            accent_frame = ctk.CTkFrame(theme_frame, width=20, height=20, fg_color=theme_colors["accent"])
            accent_frame.pack(side="left", padx=5, pady=10)
            
            # Move to next column or row
            col += 1
            if col > 1:
                col = 0
                row += 1
            
    def _create_data_settings(self):
        """Create data settings UI"""
        # Form Length
        self.form_length_frame = ctk.CTkFrame(self.data_frame)
        self.form_length_frame.pack(fill="x", padx=20, pady=20)
        
        self.form_length_label = ctk.CTkLabel(
            self.form_length_frame,
            text="Form Analysis Length:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.form_length_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.form_length_var = tk.IntVar(value=self.settings_manager.get_form_length())
        
        self.form_length_slider = ctk.CTkSlider(
            self.form_length_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            variable=self.form_length_var
        )
        self.form_length_slider.pack(fill="x", padx=10, pady=5)
        
        self.form_length_value_label = ctk.CTkLabel(
            self.form_length_frame,
            text=f"Current value: {self.form_length_var.get()} matches",
            font=ctk.CTkFont(size=12)
        )
        self.form_length_value_label.pack(anchor="w", padx=10, pady=5)
        
        # Update label when slider changes
        self.form_length_slider.configure(
            command=lambda value: self.form_length_value_label.configure(
                text=f"Current value: {int(value)} matches"
            )
        )
        
        # Performance Difference Threshold
        self.threshold_frame = ctk.CTkFrame(self.data_frame)
        self.threshold_frame.pack(fill="x", padx=20, pady=20)
        
        self.threshold_label = ctk.CTkLabel(
            self.threshold_frame,
            text="Performance Difference Threshold:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.threshold_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.threshold_var = tk.DoubleVar(value=self.settings_manager.get_threshold())
        
        self.threshold_slider = ctk.CTkSlider(
            self.threshold_frame,
            from_=0.1,
            to=2.0,
            variable=self.threshold_var
        )
        self.threshold_slider.pack(fill="x", padx=10, pady=5)
        
        self.threshold_value_label = ctk.CTkLabel(
            self.threshold_frame,
            text=f"Current value: {self.threshold_var.get():.2f}",
            font=ctk.CTkFont(size=12)
        )
        self.threshold_value_label.pack(anchor="w", padx=10, pady=5)
        
        # Update label when slider changes
        self.threshold_slider.configure(
            command=lambda value: self.threshold_value_label.configure(
                text=f"Current value: {value:.2f}"
            )
        )
        
        # Auto Refresh
        self.auto_refresh_frame = ctk.CTkFrame(self.data_frame)
        self.auto_refresh_frame.pack(fill="x", padx=20, pady=20)
        
        self.auto_refresh_label = ctk.CTkLabel(
            self.auto_refresh_frame,
            text="Auto Refresh Data:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.auto_refresh_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.auto_refresh_var = tk.BooleanVar(value=self.settings_manager.get_auto_refresh())
        
        self.auto_refresh_switch = ctk.CTkSwitch(
            self.auto_refresh_frame,
            text="Enable Auto Refresh",
            variable=self.auto_refresh_var,
            onvalue=True,
            offvalue=False
        )
        self.auto_refresh_switch.pack(anchor="w", padx=10, pady=5)
        
        # Refresh Interval
        self.refresh_interval_frame = ctk.CTkFrame(self.auto_refresh_frame)
        self.refresh_interval_frame.pack(fill="x", padx=10, pady=10)
        
        self.refresh_interval_label = ctk.CTkLabel(
            self.refresh_interval_frame,
            text="Refresh Interval (minutes):",
            font=ctk.CTkFont(size=12)
        )
        self.refresh_interval_label.pack(anchor="w", padx=10, pady=5)
        
        self.refresh_interval_var = tk.IntVar(value=self.settings_manager.get_refresh_interval())
        
        self.refresh_interval_slider = ctk.CTkSlider(
            self.refresh_interval_frame,
            from_=5,
            to=120,
            number_of_steps=23,
            variable=self.refresh_interval_var
        )
        self.refresh_interval_slider.pack(fill="x", padx=10, pady=5)
        
        self.refresh_interval_value_label = ctk.CTkLabel(
            self.refresh_interval_frame,
            text=f"Current value: {self.refresh_interval_var.get()} minutes",
            font=ctk.CTkFont(size=10)
        )
        self.refresh_interval_value_label.pack(anchor="w", padx=10, pady=5)
        
        # Update label when slider changes
        self.refresh_interval_slider.configure(
            command=lambda value: self.refresh_interval_value_label.configure(
                text=f"Current value: {int(value)} minutes"
            )
        )
        
    def _create_leagues_settings(self):
        """Create leagues settings UI"""
        # Leagues Selection
        self.leagues_selection_frame = ctk.CTkScrollableFrame(self.leagues_frame)
        self.leagues_selection_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create header with league count
        self.leagues_header_frame = ctk.CTkFrame(self.leagues_selection_frame)
        self.leagues_header_frame.pack(fill="x", padx=10, pady=(10, 20))
        
        self.leagues_label = ctk.CTkLabel(
            self.leagues_header_frame,
            text=translate("Select Leagues to Analyze:"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.leagues_label.pack(side="left", padx=10)
        
        # Add league count label
        self.leagues_count_label = ctk.CTkLabel(
            self.leagues_header_frame,
            text="",
            font=ctk.CTkFont(size=16)
        )
        self.leagues_count_label.pack(side="right", padx=10)
        
        # Get all leagues (default to all leagues selected)
        all_leagues = [league_id for league_id in LEAGUE_NAMES.keys() if league_id != ALL_LEAGUES]
        selected_leagues = self.settings_manager.get_leagues()
        
        # If no leagues are selected, select all leagues
        if not selected_leagues:
            selected_leagues = all_leagues
        
        # Create checkboxes for each league
        self.league_vars = {}
        
        # Group leagues by country
        leagues_by_country = {}
        for league_id, league_info in LEAGUE_NAMES.items():
            if league_id == -1:  # Skip ALL_LEAGUES
                continue
                
            country = league_info["country"]
            if country not in leagues_by_country:
                leagues_by_country[country] = []
                
            leagues_by_country[country].append((league_id, league_info))
        
        # Create a grid layout with 6 columns
        grid_frame = ctk.CTkFrame(self.leagues_selection_frame)
        grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid columns
        for i in range(6):
            grid_frame.columnconfigure(i, weight=1)
            
        # Add select all/none buttons
        self.select_buttons_frame = ctk.CTkFrame(self.leagues_selection_frame)
        self.select_buttons_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.select_all_button = ctk.CTkButton(
            self.select_buttons_frame,
            text=translate("Select All"),
            command=self._select_all_leagues,
            width=150,
            height=32,
            corner_radius=8,
            border_width=0,
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"],
            text_color="white",
            font=ctk.CTkFont(size=14)
        )
        self.select_all_button.pack(side="left", padx=10, pady=5)
        
        self.select_none_button = ctk.CTkButton(
            self.select_buttons_frame,
            text=translate("Select None"),
            command=self._select_no_leagues,
            width=150,
            height=32,
            corner_radius=8,
            border_width=0,
            fg_color=self.theme["secondary"],
            hover_color=self.theme["primary"],
            text_color="white",
            font=ctk.CTkFont(size=14)
        )
        self.select_none_button.pack(side="left", padx=10, pady=5)
        
        # Place countries in a grid (6 columns)
        col = 0
        row = 0
        
        for country, leagues in sorted(leagues_by_country.items()):
            country_frame = ctk.CTkFrame(grid_frame)
            country_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            country_label = ctk.CTkLabel(
                country_frame,
                text=f"{leagues[0][1]['flag']} {country}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            country_label.pack(anchor="w", padx=10, pady=5)
            
            # Create checkboxes for each league in the country
            for league_id, league_info in leagues:
                self.league_vars[league_id] = tk.BooleanVar(value=league_id in selected_leagues)
                
                league_checkbox = ctk.CTkCheckBox(
                    country_frame,
                    text=f"{league_info['name']}",
                    variable=self.league_vars[league_id],
                    font=ctk.CTkFont(size=14)
                )
                league_checkbox.pack(anchor="w", padx=20, pady=2)
            
            # Move to next column, or next row if we've filled all columns
            col += 1
            if col >= 6:
                col = 0
                row += 1
                
        # Update league count
        self._update_league_count()
        
    def _create_predictions_settings(self):
        """Create predictions settings UI"""
        # Prediction Thresholds
        self.prediction_thresholds_frame = ctk.CTkFrame(self.predictions_frame)
        self.prediction_thresholds_frame.pack(fill="x", padx=20, pady=20)
        
        self.prediction_thresholds_label = ctk.CTkLabel(
            self.prediction_thresholds_frame,
            text="Prediction Thresholds:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.prediction_thresholds_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Level 1 Threshold
        self.level1_frame = ctk.CTkFrame(self.prediction_thresholds_frame)
        self.level1_frame.pack(fill="x", padx=10, pady=10)
        
        self.level1_label = ctk.CTkLabel(
            self.level1_frame,
            text="Level 1 (Win/Loss):",
            font=ctk.CTkFont(size=12)
        )
        self.level1_label.pack(anchor="w", padx=10, pady=5)
        
        self.level1_var = tk.DoubleVar(value=PREDICTION_THRESHOLD_LEVEL1)
        
        self.level1_slider = ctk.CTkSlider(
            self.level1_frame,
            from_=0.1,
            to=1.0,
            variable=self.level1_var
        )
        self.level1_slider.pack(fill="x", padx=10, pady=5)
        
        self.level1_value_label = ctk.CTkLabel(
            self.level1_frame,
            text=f"Current value: {self.level1_var.get():.2f}",
            font=ctk.CTkFont(size=10)
        )
        self.level1_value_label.pack(anchor="w", padx=10, pady=5)
        
        # Update label when slider changes
        self.level1_slider.configure(
            command=lambda value: self.level1_value_label.configure(
                text=f"Current value: {value:.2f}"
            )
        )
        
        # Level 2 Threshold
        self.level2_frame = ctk.CTkFrame(self.prediction_thresholds_frame)
        self.level2_frame.pack(fill="x", padx=10, pady=10)
        
        self.level2_label = ctk.CTkLabel(
            self.level2_frame,
            text="Level 2 (Big Win/Big Loss):",
            font=ctk.CTkFont(size=12)
        )
        self.level2_label.pack(anchor="w", padx=10, pady=5)
        
        self.level2_var = tk.DoubleVar(value=PREDICTION_THRESHOLD_LEVEL2)
        
        self.level2_slider = ctk.CTkSlider(
            self.level2_frame,
            from_=0.5,
            to=2.0,
            variable=self.level2_var
        )
        self.level2_slider.pack(fill="x", padx=10, pady=5)
        
        self.level2_value_label = ctk.CTkLabel(
            self.level2_frame,
            text=f"Current value: {self.level2_var.get():.2f}",
            font=ctk.CTkFont(size=10)
        )
        self.level2_value_label.pack(anchor="w", padx=10, pady=5)
        
        # Update label when slider changes
        self.level2_slider.configure(
            command=lambda value: self.level2_value_label.configure(
                text=f"Current value: {value:.2f}"
            )
        )
        
        # Export Predictions
        self.export_frame = ctk.CTkFrame(self.predictions_frame)
        self.export_frame.pack(fill="x", padx=20, pady=20)
        
        self.export_label = ctk.CTkLabel(
            self.export_frame,
            text="Export Predictions:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.export_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.export_button = ctk.CTkButton(
            self.export_frame,
            text="Export to CSV",
            command=self._export_predictions,
            width=150,
            height=32,
            corner_radius=8,
            border_width=0,
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"],
            text_color="white"
        )
        self.export_button.pack(anchor="w", padx=10, pady=10)
        
    def _select_all_leagues(self):
        """Select all leagues"""
        for league_id, var in self.league_vars.items():
            var.set(True)
        self._update_league_count()
        
    def _select_no_leagues(self):
        """Deselect all leagues"""
        for league_id, var in self.league_vars.items():
            var.set(False)
        self._update_league_count()
        
    def _update_league_count(self):
        """Update the league count label"""
        selected_count = sum(1 for var in self.league_vars.values() if var.get())
        total_count = len(self.league_vars)
        self.leagues_count_label.configure(
            text=f"{translate('Selected')}: {selected_count}/{total_count}"
        )
    
    def _save_settings(self):
        """Save settings to settings manager"""
        try:
            # Appearance settings
            self.settings_manager.set_setting("appearance_mode", self.appearance_mode_var.get())
            self.settings_manager.set_setting("color_theme", self.color_theme_var.get())
            self.settings_manager.set_setting("font_size", int(self.font_size_var.get()))
            
            # Data settings
            self.settings_manager.set_setting("form_length", int(self.form_length_var.get()))
            self.settings_manager.set_setting("threshold", float(self.threshold_var.get()))
            self.settings_manager.set_setting("auto_refresh", bool(self.auto_refresh_var.get()))
            self.settings_manager.set_setting("refresh_interval", int(self.refresh_interval_var.get()))
            
            # Leagues settings
            selected_leagues = [
                league_id for league_id, var in self.league_vars.items()
                if var.get()
            ]
            self.settings_manager.set_setting("leagues", selected_leagues)
            
            # Update league count
            self._update_league_count()
            
            # Prediction settings
            self.settings_manager.set_setting("prediction_threshold_level1", float(self.level1_var.get()))
            self.settings_manager.set_setting("prediction_threshold_level2", float(self.level2_var.get()))
            
            # Apply appearance settings
            ctk.set_appearance_mode(self.appearance_mode_var.get())
            
            # Show success message
            self.status_label.configure(text="Settings saved successfully!")
            self.parent.after(2000, lambda: self.status_label.configure(text=""))
            
            # Call the callback
            self.on_settings_changed()
            
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            self.status_label.configure(text=f"Error: {str(e)}")
            self.parent.after(2000, lambda: self.status_label.configure(text=""))
            
    def _reset_settings(self):
        """Reset settings to defaults"""
        try:
            # Reset settings in settings manager
            self.settings_manager.reset_to_defaults()
            
            # Update UI elements
            self.appearance_mode_var.set(self.settings_manager.get_appearance_mode())
            self.color_theme_var.set(self.settings_manager.get_setting("color_theme"))
            self.font_size_var.set(self.settings_manager.get_font_size())
            self.form_length_var.set(self.settings_manager.get_form_length())
            self.threshold_var.set(self.settings_manager.get_threshold())
            self.auto_refresh_var.set(self.settings_manager.get_auto_refresh())
            self.refresh_interval_var.set(self.settings_manager.get_refresh_interval())
            
            # Update league checkboxes
            selected_leagues = self.settings_manager.get_leagues()
            for league_id, var in self.league_vars.items():
                var.set(league_id in selected_leagues)
                
            # Update prediction thresholds
            self.level1_var.set(PREDICTION_THRESHOLD_LEVEL1)
            self.level2_var.set(PREDICTION_THRESHOLD_LEVEL2)
            
            # Update labels
            self.font_size_value_label.configure(text=f"Size: {self.font_size_var.get()} px")
            self.form_length_value_label.configure(text=f"Current value: {self.form_length_var.get()} matches")
            self.threshold_value_label.configure(text=f"Current value: {self.threshold_var.get():.2f}")
            self.refresh_interval_value_label.configure(text=f"Current value: {self.refresh_interval_var.get()} minutes")
            self.level1_value_label.configure(text=f"Current value: {self.level1_var.get():.2f}")
            self.level2_value_label.configure(text=f"Current value: {self.level2_var.get():.2f}")
            
            # Show success message
            self.status_label.configure(text="Settings reset to defaults!")
            self.parent.after(2000, lambda: self.status_label.configure(text=""))
            
            # Call the callback
            self.on_settings_changed()
            
        except Exception as e:
            logger.error(f"Error resetting settings: {str(e)}")
            self.status_label.configure(text=f"Error: {str(e)}")
            self.parent.after(2000, lambda: self.status_label.configure(text=""))
            
    def _apply_font_size(self):
        """Apply font size setting without saving other settings"""
        try:
            # Get the current font size from the slider
            font_size = int(self.font_size_var.get())
            
            # Save only the font size setting
            self.settings_manager.set_setting("font_size", font_size)
            
            # Call the callback to update all tabs
            self.on_settings_changed()
            
            # Show success message
            self.status_label.configure(text=f"Font size updated to {font_size}px")
            self.parent.after(2000, lambda: self.status_label.configure(text=""))
            
        except Exception as e:
            logger.error(f"Error applying font size: {str(e)}")
            self.status_label.configure(text=f"Error: {str(e)}")
            self.parent.after(2000, lambda: self.status_label.configure(text=""))
    
    def _export_predictions(self):
        """Export predictions to CSV"""
        try:
            # Open file dialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Export Predictions"
            )
            
            if not filepath:
                return
                
            # Export predictions using the existing db_manager
            success = self.db_manager.export_predictions_to_csv(filepath)
            
            if success:
                self.status_label.configure(text=f"Predictions exported to {filepath}")
            else:
                self.status_label.configure(text="No predictions to export")
                
            self.parent.after(2000, lambda: self.status_label.configure(text=""))
            
        except Exception as e:
            logger.error(f"Error exporting predictions: {str(e)}")
            self.status_label.configure(text=f"Error: {str(e)}")
            self.parent.after(2000, lambda: self.status_label.configure(text=""))

import os
import json
import logging
import sqlite3
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Import modules
from modules.api_client import FootballAPI
from modules.config import API_KEY, BASE_URL, ALL_LEAGUES, PERF_DIFF_THRESHOLD
from modules.league_names import LEAGUE_NAMES
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.translations import translate

# Import tabs
from tabs.form_tab import FormTab
from tabs.settings_tab import SettingsTab
from tabs.stats_tab import StatsTab
from tabs.winless_tab import WinlessTab
from tabs.team_tab import TeamTab
from tabs.next_round_tab import NextRoundTab
from tabs.league_stats_tab import LeagueStatsTab
from tabs.data_collection_tab import DataCollectionTab
from tabs.firebase_tab import FirebaseTab
from tabs.db_view_tab import DbViewTab
from tabs.about_tab import AboutTab
from tabs.logs_tab import LogsTab

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class FootballStatsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize API client
        self.api = FootballAPI(API_KEY, BASE_URL)
        
        # Initialize database manager
        self.db_manager = DatabaseManager("football_stats.db")
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Configure window
        self.title(translate("Football Statistics Analyzer"))
        self.geometry("1200x800")
        
        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure notebook style for larger font
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=('Helvetica', 36))  # Increased font size from 28 to 36
        style.configure("TNotebook", font=('Helvetica', 36))  # Add font configuration for the notebook itself
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True)
        
        # Add tabs with Slovak translations
        self.winless_tab = self.tabview.add(translate("Winless Streaks"))
        self.team_tab = self.tabview.add(translate("Team Analysis"))
        self.next_round_tab = self.tabview.add(translate("Next Round"))
        self.league_stats_tab = self.tabview.add(translate("League Stats"))
        self.form_tab = self.tabview.add(translate("Form Analysis"))
        self.data_collection_tab = self.tabview.add(translate("Data Collection"))
        self.firebase_tab = self.tabview.add(translate("Firebase Analysis"))
        self.stats_tab = self.tabview.add(translate("Statistics"))
        self.db_view_tab = self.tabview.add(translate("Database View"))
        self.logs_tab = self.tabview.add(translate("Logs"))
        self.about_tab = self.tabview.add(translate("About"))
        self.settings_tab = self.tabview.add(translate("Settings"))
        
        # Initialize tab contents
        self.winless_tab_content = WinlessTab(self.winless_tab, self.api, self.db_manager, self.settings_manager)
        self.team_tab_content = TeamTab(self.team_tab, self.api, self.db_manager, self.settings_manager)
        self.next_round_tab_content = NextRoundTab(self.next_round_tab, self.api, self.db_manager, self.settings_manager)
        self.league_stats_tab_content = LeagueStatsTab(self.league_stats_tab, self.api, self.db_manager, self.settings_manager)
        self.form_tab_content = FormTab(self.form_tab, self.api, self.db_manager, self.settings_manager)
        self.data_collection_tab_content = DataCollectionTab(self.data_collection_tab, self.api, self.db_manager, self.settings_manager)
        self.firebase_tab_content = FirebaseTab(self.firebase_tab, self.api, self.db_manager, self.settings_manager)
        self.stats_tab_content = StatsTab(self.stats_tab, self.db_manager)
        self.db_view_tab_content = DbViewTab(self.db_view_tab, self.api, self.db_manager, self.settings_manager)
        self.logs_tab_content = LogsTab(self.logs_tab, self.api, self.db_manager, self.settings_manager)
        self.about_tab_content = AboutTab(self.about_tab, self.api, self.db_manager, self.settings_manager)
        self.settings_tab_content = SettingsTab(self.settings_tab, self.settings_manager, self.on_settings_changed, self.db_manager)
        
        # Set default tab
        self.tabview.set(translate("Winless Streaks"))
        
        # Create status bar
        self.status_bar = ctk.CTkLabel(self, text=translate("Ready"), anchor="w", font=ctk.CTkFont(size=14))
        self.status_bar.pack(fill="x", padx=10, pady=(0, 10))
        
    def on_settings_changed(self):
        """Callback when settings are changed"""
        # Update tabs with new settings
        self.winless_tab_content.update_settings()
        self.team_tab_content.update_settings()
        self.next_round_tab_content.update_settings()
        self.league_stats_tab_content.update_settings()
        self.form_tab_content.update_settings()
        self.data_collection_tab_content.update_settings()
        self.firebase_tab_content.update_settings()
        self.stats_tab_content.update_settings()
        self.db_view_tab_content.update_settings()
        self.logs_tab_content.update_settings()
        self.about_tab_content.update_settings()
        
        # Update appearance
        ctk.set_appearance_mode(self.settings_manager.get_setting("appearance_mode"))
        ctk.set_default_color_theme(self.settings_manager.get_setting("color_theme"))
        
        # Update status
        self.status_bar.configure(text=f"{translate('Settings updated at')} {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    app = FootballStatsApp()
    app.mainloop()

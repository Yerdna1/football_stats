import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable

from tabs.base_tab import BaseTab
from modules.api_client import FootballAPI
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.league_names import get_league_options, get_league_display_name

logger = logging.getLogger(__name__)

class WinlessTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Initialize variables
        self.winless_data = []
        
        # Get leagues from settings, use default if empty
        leagues = self.settings_manager.get_leagues()
        default_league = 39  # Premier League
        
        # Set selected league with fallback to default
        if leagues and len(leagues) > 0:
            self.selected_league = tk.IntVar(value=leagues[0])
        else:
            self.selected_league = tk.IntVar(value=default_league)
            # Update settings with default league
            self.settings_manager.set_setting("leagues", [default_league])
        
        # Create UI elements
        self._create_ui()
        
    def _create_ui(self):
        """Create the winless tab UI elements"""
        # Title
        self._create_title("Winless Streaks Analysis")
        
        # Controls section
        self.controls_frame = ctk.CTkFrame(self.content_frame)
        self.controls_frame.pack(fill="x", padx=10, pady=10)
        
        # League selection
        self.league_frame = ctk.CTkFrame(self.controls_frame)
        self.league_frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.league_label = ctk.CTkLabel(
            self.league_frame, 
            text="Select League:",
            font=ctk.CTkFont(size=14)
        )
        self.league_label.pack(pady=(0, 5))
        
        # Get league options
        league_options = get_league_options()
        
        # Create dropdown for leagues
        self.league_dropdown = ctk.CTkOptionMenu(
            self.league_frame,
            values=[option["text"] for option in league_options],
            command=self._on_league_changed,
            font=ctk.CTkFont(size=12)
        )
        self.league_dropdown.pack(fill="x", padx=10, pady=5)
        
        # Streak type selection
        self.streak_frame = ctk.CTkFrame(self.controls_frame)
        self.streak_frame.pack(side="right", padx=10, pady=10, fill="x", expand=True)
        
        self.streak_label = ctk.CTkLabel(
            self.streak_frame, 
            text="Streak Type:",
            font=ctk.CTkFont(size=14)
        )
        self.streak_label.pack(pady=(0, 5))
        
        self.streak_var = tk.StringVar(value="Winless")
        
        self.streak_segment = ctk.CTkSegmentedButton(
            self.streak_frame,
            values=["Winless", "Lossless"],
            command=self._on_streak_changed,
            variable=self.streak_var,
            font=ctk.CTkFont(size=12)
        )
        self.streak_segment.pack(fill="x", padx=10, pady=5)
        
        # Refresh button with animation
        self.refresh_button = self._create_button(
            self.controls_frame,
            text="Refresh Data",
            command=self._refresh_data,
            width=120,
            height=32
        )
        self.refresh_button.pack(side="right", padx=20, pady=10)
        
        # Create tables
        self.tables_frame = ctk.CTkFrame(self.content_frame)
        self.tables_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create winless streaks table
        self.winless_table = self._create_table(
            self.tables_frame,
            columns=[
                {"text": "Team", "width": 150},
                {"text": "League", "width": 150},
                {"text": "Streak", "width": 80},
                {"text": "Last Win", "width": 100},
                {"text": "Days Since Win", "width": 100},
                {"text": "Next Opponent", "width": 150},
                {"text": "Match Date", "width": 100},
                {"text": "Venue", "width": 100}
            ]
        )
        
        # Initial data load
        self._refresh_data()
        
    def _on_league_changed(self, selection):
        """Handle league selection change"""
        # Find the league ID from the selection text
        league_options = get_league_options()
        for option in league_options:
            if option["text"] == selection:
                self.selected_league.set(option["id"])
                break
        
        # Save to settings
        self.settings_manager.set_setting("leagues", [self.selected_league.get()])
        
        # Refresh data
        self._refresh_data()
        
    def _on_streak_changed(self, selection):
        """Handle streak type selection change"""
        # Refresh data
        self._refresh_data()
        
    def _refresh_data(self):
        """Refresh data from API"""
        # Show loading animation
        self._show_loading_animation(self.refresh_button, "Refresh Data")
        
        # Get data in a separate thread
        self.parent.after(100, self._fetch_data)
            
    def _fetch_data(self):
        """Fetch data from API"""
        try:
            # Get league ID
            league_id = self.selected_league.get()
            
            # Get streak type
            streak_type = self.streak_var.get()
            
            # Fetch standings
            standings = self.api.fetch_standings(league_id)
            
            if not standings or not standings.get('response'):
                logger.warning(f"No standings for league {league_id}")
                self.refresh_button.configure(text="Refresh Data", state="normal")
                return
                
            standings_data = standings['response'][0]['league']['standings'][0]
            
            # Fetch fixtures
            fixtures = self.api.fetch_fixtures(league_id)
            
            # Process data (placeholder)
            self.winless_data = []
            
            # In a real implementation, we would analyze the fixtures to find winless streaks
            # For now, just use placeholder data
            for i, team in enumerate(standings_data[:10]):
                team_name = team['team']['name']
                team_id = team['team']['id']
                
                # Add placeholder data
                self.winless_data.append({
                    'team': team_name,
                    'team_id': team_id,
                    'league': get_league_display_name(league_id),
                    'streak': i + 1,
                    'last_win': '2024-01-01',
                    'days_since_win': (i + 1) * 7,
                    'next_opponent': 'Opponent ' + str(i + 1),
                    'match_date': '2024-03-15',
                    'venue': 'Home' if i % 2 == 0 else 'Away'
                })
            
            # Update table
            self._update_table()
            
            # Reset refresh button
            self.refresh_button.configure(text="Refresh Data", state="normal")
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            self.refresh_button.configure(text="Refresh Failed", state="normal")
            self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data"))
            
    def _update_table(self):
        """Update the winless streaks table"""
        # Clear table
        for item in self.winless_table.get_children():
            self.winless_table.delete(item)
            
        # Add data
        for i, team in enumerate(self.winless_data):
            # Add row
            self.winless_table.insert(
                "", "end",
                values=(
                    team.get('team', ''),
                    team.get('league', ''),
                    team.get('streak', ''),
                    team.get('last_win', ''),
                    team.get('days_since_win', ''),
                    team.get('next_opponent', ''),
                    team.get('match_date', ''),
                    team.get('venue', '')
                ),
                tags=('streak',)
            )
            
        # Configure tags
        self.winless_table.tag_configure('streak', foreground='red')
    
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update UI elements with new theme
        self.refresh_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )

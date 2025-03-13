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

class TeamTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Initialize variables
        self.team_data = []
        self.player_data = []
        
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
            
        self.selected_team = tk.StringVar()
        
        # Create UI elements
        self._create_ui()
        
    def _create_ui(self):
        """Create the team tab UI elements"""
        # Title
        self._create_title("Team Analysis")
        
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
        
        # Team selection
        self.team_frame = ctk.CTkFrame(self.controls_frame)
        self.team_frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.team_label = ctk.CTkLabel(
            self.team_frame, 
            text="Select Team:",
            font=ctk.CTkFont(size=14)
        )
        self.team_label.pack(pady=(0, 5))
        
        # Create dropdown for teams (will be populated later)
        self.team_dropdown = ctk.CTkOptionMenu(
            self.team_frame,
            values=["Select a league first"],
            command=self._on_team_changed,
            font=ctk.CTkFont(size=12)
        )
        self.team_dropdown.pack(fill="x", padx=10, pady=5)
        
        # Refresh button with animation
        self.refresh_button = self._create_button(
            self.controls_frame,
            text="Refresh Data",
            command=self._refresh_data,
            width=120,
            height=32
        )
        self.refresh_button.pack(side="right", padx=20, pady=10)
        
        # Create notebook for team data
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Team Overview Tab
        self.overview_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.overview_frame, text="Team Overview")
        
        # Create team info section
        self.team_info_frame = ctk.CTkFrame(self.overview_frame)
        self.team_info_frame.pack(fill="x", padx=10, pady=10)
        
        # Team name
        self.team_name_label = ctk.CTkLabel(
            self.team_info_frame,
            text="Team: ",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.team_name_label.pack(anchor="w", padx=10, pady=5)
        
        # Team stats
        self.team_stats_frame = ctk.CTkFrame(self.team_info_frame)
        self.team_stats_frame.pack(fill="x", padx=10, pady=10)
        
        # Create grid layout for stats
        self.team_stats_frame.columnconfigure(0, weight=1)
        self.team_stats_frame.columnconfigure(1, weight=1)
        self.team_stats_frame.columnconfigure(2, weight=1)
        self.team_stats_frame.columnconfigure(3, weight=1)
        
        # Create stat labels
        self.position_label = self._create_stat_label(self.team_stats_frame, "Position:", "0", 0, 0)
        self.points_label = self._create_stat_label(self.team_stats_frame, "Points:", "0", 0, 1)
        self.wins_label = self._create_stat_label(self.team_stats_frame, "Wins:", "0", 0, 2)
        self.draws_label = self._create_stat_label(self.team_stats_frame, "Draws:", "0", 0, 3)
        self.losses_label = self._create_stat_label(self.team_stats_frame, "Losses:", "0", 1, 0)
        self.goals_for_label = self._create_stat_label(self.team_stats_frame, "Goals For:", "0", 1, 1)
        self.goals_against_label = self._create_stat_label(self.team_stats_frame, "Goals Against:", "0", 1, 2)
        self.goal_diff_label = self._create_stat_label(self.team_stats_frame, "Goal Diff:", "0", 1, 3)
        
        # Squad Tab
        self.squad_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.squad_frame, text="Squad")
        
        # Create squad table
        self.squad_table = self._create_table(
            self.squad_frame,
            columns=[
                {"text": "Player", "width": 150},
                {"text": "Position", "width": 100},
                {"text": "Age", "width": 50},
                {"text": "Nationality", "width": 100},
                {"text": "Appearances", "width": 100},
                {"text": "Goals", "width": 50},
                {"text": "Assists", "width": 50},
                {"text": "Yellow Cards", "width": 100},
                {"text": "Red Cards", "width": 100}
            ]
        )
        
        # Fixtures Tab
        self.fixtures_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.fixtures_frame, text="Fixtures")
        
        # Create fixtures table
        self.fixtures_table = self._create_table(
            self.fixtures_frame,
            columns=[
                {"text": "Date", "width": 100},
                {"text": "Home", "width": 150},
                {"text": "Away", "width": 150},
                {"text": "Score", "width": 100},
                {"text": "Status", "width": 100},
                {"text": "Venue", "width": 150}
            ]
        )
        
        # Initial data load
        self._refresh_data()
        
    def _create_stat_label(self, parent, title, value, row, col):
        """Create a stat label with title and value"""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=12)
        )
        title_label.pack(pady=(5, 0))
        
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        value_label.pack(pady=(0, 5))
        
        return {
            "title": title_label,
            "value": value_label
        }
        
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
        
    def _on_team_changed(self, selection):
        """Handle team selection change"""
        self.selected_team.set(selection)
        
        # Refresh team data
        self._fetch_team_data()
        
    def _refresh_data(self):
        """Refresh data from API"""
        # Show loading animation
        self._show_loading_animation(self.refresh_button, "Refresh Data")
        
        # Get data in a separate thread
        self.parent.after(100, self._fetch_league_data)
            
    def _fetch_league_data(self):
        """Fetch league data from API"""
        try:
            # Get league ID
            league_id = self.selected_league.get()
            
            # Fetch standings
            standings = self.api.fetch_standings(league_id)
            
            if not standings or not standings.get('response'):
                logger.warning(f"No standings for league {league_id}")
                self.refresh_button.configure(text="Refresh Data", state="normal")
                return
                
            standings_data = standings['response'][0]['league']['standings'][0]
            
            # Get team names
            team_names = [team['team']['name'] for team in standings_data]
            
            # Update team dropdown
            self.team_dropdown.configure(values=team_names)
            
            # If no team is selected, select the first one
            if not self.selected_team.get() or self.selected_team.get() not in team_names:
                self.selected_team.set(team_names[0])
                self.team_dropdown.set(team_names[0])
            
            # Fetch team data
            self._fetch_team_data()
            
        except Exception as e:
            logger.error(f"Error fetching league data: {str(e)}")
            self.refresh_button.configure(text="Refresh Failed", state="normal")
            self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data"))
            
    def _fetch_team_data(self):
        """Fetch team data from API"""
        try:
            # Get league ID
            league_id = self.selected_league.get()
            
            # Get team name
            team_name = self.selected_team.get()
            
            # Fetch standings
            standings = self.api.fetch_standings(league_id)
            
            if not standings or not standings.get('response'):
                logger.warning(f"No standings for league {league_id}")
                self.refresh_button.configure(text="Refresh Data", state="normal")
                return
                
            standings_data = standings['response'][0]['league']['standings'][0]
            
            # Find team data
            team_data = None
            for team in standings_data:
                if team['team']['name'] == team_name:
                    team_data = team
                    break
                    
            if not team_data:
                logger.warning(f"Team {team_name} not found in standings")
                self.refresh_button.configure(text="Refresh Data", state="normal")
                return
                
            # Update team info
            self.team_name_label.configure(text=f"Team: {team_data['team']['name']}")
            
            # Update team stats
            self.position_label["value"].configure(text=str(team_data['rank']))
            self.points_label["value"].configure(text=str(team_data['points']))
            self.wins_label["value"].configure(text=str(team_data['all']['win']))
            self.draws_label["value"].configure(text=str(team_data['all']['draw']))
            self.losses_label["value"].configure(text=str(team_data['all']['lose']))
            self.goals_for_label["value"].configure(text=str(team_data['all']['goals']['for']))
            self.goals_against_label["value"].configure(text=str(team_data['all']['goals']['against']))
            self.goal_diff_label["value"].configure(text=str(team_data['goalsDiff']))
            
            # Fetch fixtures
            team_id = team_data['team']['id']
            fixtures = self.api.fetch_fixtures(league_id, team_id=team_id)
            
            # Update fixtures table
            self._update_fixtures_table(fixtures)
            
            # Fetch squad (placeholder)
            self._update_squad_table(team_id)
            
            # Reset refresh button
            self.refresh_button.configure(text="Refresh Data", state="normal")
            
        except Exception as e:
            logger.error(f"Error fetching team data: {str(e)}")
            self.refresh_button.configure(text="Refresh Failed", state="normal")
            self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data"))
            
    def _update_fixtures_table(self, fixtures):
        """Update the fixtures table"""
        # Clear table
        for item in self.fixtures_table.get_children():
            self.fixtures_table.delete(item)
            
        # Add data
        for fixture in fixtures:
            # Get fixture data
            date = fixture['fixture']['date'].split('T')[0]
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            
            # Get score
            if fixture['fixture']['status']['short'] == 'FT':
                score = f"{fixture['goals']['home']} - {fixture['goals']['away']}"
            else:
                score = "vs"
                
            status = fixture['fixture']['status']['long']
            venue = fixture['fixture']['venue']['name'] if fixture['fixture']['venue']['name'] else "Unknown"
            
            # Add row
            self.fixtures_table.insert(
                "", "end",
                values=(
                    date,
                    home_team,
                    away_team,
                    score,
                    status,
                    venue
                )
            )
            
    def _update_squad_table(self, team_id):
        """Update the squad table with placeholder data"""
        # Clear table
        for item in self.squad_table.get_children():
            self.squad_table.delete(item)
            
        # Add placeholder data
        positions = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
        nationalities = ["England", "Spain", "Germany", "France", "Italy"]
        
        for i in range(20):
            position = positions[i % len(positions)]
            nationality = nationalities[i % len(nationalities)]
            
            # Add row
            self.squad_table.insert(
                "", "end",
                values=(
                    f"Player {i+1}",
                    position,
                    20 + (i % 15),
                    nationality,
                    i + 10,
                    i % 5,
                    i % 3,
                    i % 4,
                    0 if i % 10 != 0 else 1
                )
            )
    
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update UI elements with new theme
        self.refresh_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )

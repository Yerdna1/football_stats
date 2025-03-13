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

class NextRoundTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Initialize variables
        self.fixtures_data = []
        
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
        """Create the next round tab UI elements"""
        # Title
        self._create_title("Next Round Fixtures")
        
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
        
        # Refresh button with animation
        self.refresh_button = self._create_button(
            self.controls_frame,
            text="Refresh Data",
            command=self._refresh_data,
            width=120,
            height=32
        )
        self.refresh_button.pack(side="right", padx=20, pady=10)
        
        # Create fixtures section
        self.fixtures_frame = ctk.CTkFrame(self.content_frame)
        self.fixtures_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Round info
        self.round_label = ctk.CTkLabel(
            self.fixtures_frame,
            text="Round: ",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.round_label.pack(anchor="w", padx=10, pady=5)
        
        # Create fixtures table
        self.fixtures_table = self._create_table(
            self.fixtures_frame,
            columns=[
                {"text": "Date", "width": 100},
                {"text": "Time", "width": 80},
                {"text": "Home", "width": 150},
                {"text": "Away", "width": 150},
                {"text": "Venue", "width": 150},
                {"text": "Home Form", "width": 100},
                {"text": "Away Form", "width": 100},
                {"text": "Prediction", "width": 150}
            ]
        )
        
        # Create details section
        self.details_frame = ctk.CTkFrame(self.content_frame)
        self.details_frame.pack(fill="x", padx=10, pady=10)
        
        # Match details label
        self.details_label = ctk.CTkLabel(
            self.details_frame,
            text="Select a match to view details",
            font=ctk.CTkFont(size=14)
        )
        self.details_label.pack(pady=10)
        
        # Match details content
        self.details_content = ctk.CTkTextbox(
            self.details_frame,
            height=250,  # Increased height to accommodate larger font
            font=ctk.CTkFont(size=self.settings_manager.get_font_size())  # Use font size from settings
        )
        self.details_content.pack(fill="x", padx=10, pady=10)
        
        # Bind selection event
        self.fixtures_table.bind("<<TreeviewSelect>>", self._on_fixture_selected)
        
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
        
    def _refresh_data(self):
        """Refresh data from API"""
        # Show loading animation
        self._show_loading_animation(self.refresh_button, "Refresh Data")
        
        # Show loading indicator overlay
        self.show_loading_indicator()
        
        # Get data in a separate thread
        self.parent.after(100, self._fetch_data)
            
    def _fetch_data(self):
        """Fetch data from API"""
        try:
            # Get league ID
            league_id = self.selected_league.get()
            
            # Show status message
            self.refresh_button.configure(text="Fetching fixtures...", state="disabled")
            
            try:
                # Fetch next fixtures with timeout handling
                fixtures = self.api.fetch_next_fixtures(league_id)
                
                if not fixtures:
                    logger.warning(f"No fixtures for league {league_id}")
                    self.refresh_button.configure(text="No Fixtures Found", state="normal")
                    self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data", state="normal"))
                    return
            except KeyboardInterrupt:
                logger.warning("Fixtures fetch interrupted by user")
                self.refresh_button.configure(text="Fetch Interrupted", state="normal")
                self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data", state="normal"))
                return
            except Exception as e:
                logger.error(f"Error fetching fixtures: {str(e)}")
                self.refresh_button.configure(text="Fixtures Error", state="normal")
                self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data", state="normal"))
                return
                
            # Store fixtures data
            self.fixtures_data = fixtures
            
            # Get round info
            round_name = fixtures[0]['league']['round'] if fixtures else "Unknown"
            self.round_label.configure(text=f"Round: {round_name}")
            
            # Update status
            self.refresh_button.configure(text="Updating table...", state="disabled")
            
            # Update fixtures table
            self._update_fixtures_table()
            
            # Reset refresh button
            self.refresh_button.configure(text="Refresh Data", state="normal")
            
            # Hide loading indicator
            self.hide_loading_indicator()
            
        except KeyboardInterrupt:
            logger.warning("Data fetch interrupted by user")
            self.refresh_button.configure(text="Interrupted", state="normal")
            self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data", state="normal"))
            # Hide loading indicator
            self.hide_loading_indicator()
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            self.refresh_button.configure(text="Refresh Failed", state="normal")
            self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data", state="normal"))
            # Hide loading indicator
            self.hide_loading_indicator()
            
    def _update_fixtures_table(self):
        """Update the fixtures table"""
        # Clear table
        for item in self.fixtures_table.get_children():
            self.fixtures_table.delete(item)
            
        # Add data
        for fixture in self.fixtures_data:
            try:
                # Get fixture data
                date = fixture['fixture']['date'].split('T')[0]
                time = fixture['fixture']['date'].split('T')[1].split('+')[0][:-3]  # Extract HH:MM
                home_team = fixture['teams']['home']['name']
                away_team = fixture['teams']['away']['name']
                venue = fixture['fixture']['venue']['name'] if fixture['fixture']['venue']['name'] else "Unknown"
                
                # Get real form data from API
                home_team_id = fixture['teams']['home']['id']
                away_team_id = fixture['teams']['away']['id']
                league_id = fixture['league']['id']
                
                # Default values in case API calls fail
                home_form = 'N/A'
                away_form = 'N/A'
                prediction = "Unknown"
                
                try:
                    # Fetch team statistics with error handling
                    home_stats = self.api.fetch_team_statistics(league_id, home_team_id)
                    away_stats = self.api.fetch_team_statistics(league_id, away_team_id)
                    
                    # Extract form data
                    home_form = home_stats.get('form', 'N/A')
                    away_form = away_stats.get('form', 'N/A')
                    
                    # Generate prediction based on form
                    home_wins = home_form.count('W')
                    away_wins = away_form.count('W')
                    
                    if home_wins > away_wins:
                        prediction = "Home Win"
                    elif away_wins > home_wins:
                        prediction = "Away Win"
                    else:
                        prediction = "Draw"
                except KeyboardInterrupt:
                    logger.warning("Team statistics fetch interrupted by user")
                    # Use default values
                except Exception as e:
                    logger.error(f"Error fetching team statistics: {str(e)}")
                    # Use default values
                
                # Add row
                self.fixtures_table.insert(
                    "", "end",
                    values=(
                        date,
                        time,
                        home_team,
                        away_team,
                        venue,
                        home_form,
                        away_form,
                        prediction
                    ),
                    tags=(fixture['fixture']['id'],)
                )
            except Exception as e:
                logger.error(f"Error processing fixture: {str(e)}")
                continue
            
    def _on_fixture_selected(self, event):
        """Handle fixture selection"""
        # Get selected item
        selection = self.fixtures_table.selection()
        if not selection:
            return
            
        # Get fixture ID from tags
        fixture_id = self.fixtures_table.item(selection[0], "tags")[0]
        
        # Find fixture data
        fixture_data = None
        for fixture in self.fixtures_data:
            if fixture['fixture']['id'] == fixture_id:
                fixture_data = fixture
                break
                
        if not fixture_data:
            return
            
        # Update details
        home_team = fixture_data['teams']['home']['name']
        away_team = fixture_data['teams']['away']['name']
        
        # Get real team statistics from API
        home_team_id = fixture_data['teams']['home']['id']
        away_team_id = fixture_data['teams']['away']['id']
        league_id = fixture_data['league']['id']
        
        # Fetch team statistics
        try:
            home_stats = self.api.fetch_team_statistics(league_id, home_team_id)
            away_stats = self.api.fetch_team_statistics(league_id, away_team_id)
            
            # Extract form data
            home_form = home_stats.get('form', 'N/A')
            away_form = away_stats.get('form', 'N/A')
            
            # Extract home/away records
            home_record = f"{home_stats.get('fixtures', {}).get('wins', {}).get('home', 0)}W "
            home_record += f"{home_stats.get('fixtures', {}).get('draws', {}).get('home', 0)}D "
            home_record += f"{home_stats.get('fixtures', {}).get('loses', {}).get('home', 0)}L"
            
            away_record = f"{away_stats.get('fixtures', {}).get('wins', {}).get('away', 0)}W "
            away_record += f"{away_stats.get('fixtures', {}).get('draws', {}).get('away', 0)}D "
            away_record += f"{away_stats.get('fixtures', {}).get('loses', {}).get('away', 0)}L"
            
            # Generate prediction based on form
            home_wins = home_form.count('W')
            away_wins = away_form.count('W')
            
            if home_wins > away_wins:
                prediction = "Home Win"
                probability = int((home_wins / (home_wins + away_wins)) * 100) if (home_wins + away_wins) > 0 else 50
            elif away_wins > home_wins:
                prediction = "Away Win"
                probability = int((away_wins / (home_wins + away_wins)) * 100) if (home_wins + away_wins) > 0 else 50
            else:
                prediction = "Draw"
                probability = 50
        except Exception as e:
            logger.error(f"Error fetching team statistics: {str(e)}")
            home_form = away_form = "N/A"
            home_record = away_record = "N/A"
            prediction = "Unknown"
            probability = 0
        
        # Create details text
        details = f"Match: {home_team} vs {away_team}\n\n"
        details += f"Date: {fixture_data['fixture']['date'].split('T')[0]}\n"
        details += f"Time: {fixture_data['fixture']['date'].split('T')[1].split('+')[0][:-3]}\n"
        details += f"Venue: {fixture_data['fixture']['venue']['name'] if fixture_data['fixture']['venue']['name'] else 'Unknown'}\n"
        details += f"City: {fixture_data['fixture']['venue']['city'] if fixture_data['fixture']['venue']['city'] else 'Unknown'}\n\n"
        
        details += "Team Statistics:\n"
        details += f"{home_team} (Home):\n"
        details += f"- Recent Form: {home_form}\n"
        details += f"- Home Record: {home_record}\n\n"
        
        details += f"{away_team} (Away):\n"
        details += f"- Recent Form: {away_form}\n"
        details += f"- Away Record: {away_record}\n\n"
        
        if prediction != "Unknown":
            details += f"Prediction: {prediction} ({probability}% probability)"
        else:
            details += "Prediction: Not available"
        
        # Update details content
        self.details_content.delete("1.0", tk.END)
        self.details_content.insert("1.0", details)
        
        # Update details label
        self.details_label.configure(text=f"Match Details: {home_team} vs {away_team}")
    
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update UI elements with new theme
        self.refresh_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )
        
        # Update font size for details content
        self.details_content.configure(
            font=ctk.CTkFont(size=self.settings_manager.get_font_size())
        )

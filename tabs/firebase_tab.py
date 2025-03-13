import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable
import json
from datetime import datetime

from tabs.base_tab import BaseTab
from modules.api_client import FootballAPI
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.league_names import get_league_options, get_league_display_name

logger = logging.getLogger(__name__)

class FirebaseTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Initialize variables
        self.form_changes_data = []
        
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
            
        self.threshold = tk.DoubleVar(value=self.settings_manager.get_threshold())
        
        # Create UI elements
        self._create_ui()
        
    def _create_ui(self):
        """Create the firebase tab UI elements"""
        # Title
        self._create_title("Form Changes Analysis")
        
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
        
        # Threshold selection
        self.threshold_frame = ctk.CTkFrame(self.controls_frame)
        self.threshold_frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.threshold_label = ctk.CTkLabel(
            self.threshold_frame, 
            text=f"Threshold: {self.threshold.get()}",
            font=ctk.CTkFont(size=14)
        )
        self.threshold_label.pack(pady=(0, 5))
        
        # Create slider for threshold
        self.threshold_slider = ctk.CTkSlider(
            self.threshold_frame,
            from_=0.1,
            to=2.0,
            number_of_steps=19,
            command=self._on_threshold_changed,
            variable=self.threshold
        )
        self.threshold_slider.pack(fill="x", padx=10, pady=5)
        
        # Refresh button with animation
        self.refresh_button = self._create_button(
            self.controls_frame,
            text="Refresh Data",
            command=self._refresh_data,
            width=120,
            height=32
        )
        self.refresh_button.pack(side="right", padx=20, pady=10)
        
        # Create notebook for tables
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Form Changes Tab
        self.form_changes_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.form_changes_frame, text="Form Changes")
        
        # Create form changes table
        self.form_changes_table = self._create_table(
            self.form_changes_frame,
            columns=[
                {"text": "Team", "width": 150},
                {"text": "League", "width": 150},
                {"text": "Perf. Diff", "width": 80},
                {"text": "Prediction", "width": 150},
                {"text": "Opponent", "width": 150},
                {"text": "Date", "width": 100},
                {"text": "Time", "width": 80},
                {"text": "Venue", "width": 100}
            ]
        )
        
        # Upcoming Fixtures Tab
        self.fixtures_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.fixtures_frame, text="Upcoming Fixtures")
        
        # Create upcoming fixtures table
        self.fixtures_table = self._create_table(
            self.fixtures_frame,
            columns=[
                {"text": "Team", "width": 150},
                {"text": "Perf. Diff", "width": 80},
                {"text": "Prediction", "width": 150},
                {"text": "Opponent", "width": 150},
                {"text": "Date", "width": 100},
                {"text": "Time", "width": 80},
                {"text": "Venue", "width": 100},
                {"text": "Status", "width": 100}
            ]
        )
        
        # Results Tab
        self.results_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")
        
        # Create results table
        self.results_table = self._create_table(
            self.results_frame,
            columns=[
                {"text": "Team", "width": 150},
                {"text": "Perf. Diff", "width": 80},
                {"text": "Prediction", "width": 150},
                {"text": "Opponent", "width": 150},
                {"text": "Date", "width": 100},
                {"text": "Result", "width": 100},
                {"text": "Correct", "width": 80}
            ]
        )
        
        # Create actions section
        self.actions_frame = ctk.CTkFrame(self.content_frame)
        self.actions_frame.pack(fill="x", padx=10, pady=10)
        
        # Save to database button
        self.save_button = self._create_button(
            self.actions_frame,
            text="Save to Database",
            command=self._save_to_database,
            width=150,
            height=32
        )
        self.save_button.pack(side="left", padx=20, pady=10)
        
        # Check results button
        self.check_button = self._create_button(
            self.actions_frame,
            text="Check Results",
            command=self._check_results,
            width=150,
            height=32
        )
        self.check_button.pack(side="right", padx=20, pady=10)
        
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
        
    def _on_threshold_changed(self, value):
        """Handle threshold selection change"""
        # Update label
        self.threshold_label.configure(text=f"Threshold: {self.threshold.get():.2f}")
        
        # Save to settings
        self.settings_manager.set_setting("threshold", self.threshold.get())
        
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
            
            # Get threshold
            threshold = self.threshold.get()
            
            # Fetch form data
            form_data = self.api.fetch_all_teams({league_id: {"name": "", "flag": ""}}, 5)
            
            # Filter teams with significant form changes
            self.form_changes_data = []
            
            for team_data in form_data:
                if abs(team_data.get('performance_diff', 0)) >= threshold:
                    # Get upcoming matches
                    fixtures = self.api.fetch_fixtures(league_id)
                    upcoming_matches = self._get_upcoming_matches(fixtures, team_data['team_id'])
                    
                    if upcoming_matches:
                        for match in upcoming_matches:
                            # Create prediction
                            prediction, prediction_level = self._generate_prediction(team_data['performance_diff'])
                            
                            # Add to form changes data
                            self.form_changes_data.append({
                                'team_id': team_data['team_id'],
                                'team': team_data['team'],
                                'league_id': league_id,
                                'league_name': get_league_display_name(league_id),
                                'performance_diff': team_data['performance_diff'],
                                'prediction': prediction,
                                'prediction_level': prediction_level,
                                'opponent_id': match['opponent_id'],
                                'opponent': match['opponent'],
                                'fixture_id': match['fixture_id'],
                                'date': match['date'],
                                'time': match['time'],
                                'venue': match['venue'],
                                'status': match['status']
                            })
            
            # Update tables
            self._update_form_changes_table()
            self._update_fixtures_table()
            self._update_results_table()
            
            # Reset refresh button
            self.refresh_button.configure(text="Refresh Data", state="normal")
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            self.refresh_button.configure(text="Refresh Failed", state="normal")
            self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data"))
            
    def _get_upcoming_matches(self, fixtures, team_id, top_n=1):
        """Get upcoming matches for a team"""
        from modules.form_analyzer import FormAnalyzer
        return FormAnalyzer.get_upcoming_opponents(fixtures, team_id, top_n)
            
    def _update_form_changes_table(self):
        """Update the form changes table"""
        # Clear table
        for item in self.form_changes_table.get_children():
            self.form_changes_table.delete(item)
            
        # Add data
        for i, team in enumerate(self.form_changes_data):
            # Add row
            self.form_changes_table.insert(
                "", "end",
                values=(
                    team.get('team', ''),
                    team.get('league_name', ''),
                    team.get('performance_diff', ''),
                    team.get('prediction', ''),
                    team.get('opponent', ''),
                    team.get('date', ''),
                    team.get('time', ''),
                    team.get('venue', '')
                ),
                tags=('positive' if team.get('performance_diff', 0) > 0 else 'negative',)
            )
            
        # Configure tags
        self.form_changes_table.tag_configure('positive', foreground='green')
        self.form_changes_table.tag_configure('negative', foreground='red')
            
    def _update_fixtures_table(self):
        """Update the upcoming fixtures table"""
        # Clear table
        for item in self.fixtures_table.get_children():
            self.fixtures_table.delete(item)
            
        # Get fixtures from database
        fixtures = self.db_manager.get_upcoming_fixtures()
        
        # Add data
        for fixture in fixtures:
            # Add row
            self.fixtures_table.insert(
                "", "end",
                values=(
                    fixture.get('team_name', ''),
                    fixture.get('performance_diff', ''),
                    fixture.get('prediction', ''),
                    fixture.get('opponent_name', ''),
                    fixture.get('match_date', ''),
                    fixture.get('match_time', ''),
                    fixture.get('venue', ''),
                    fixture.get('status', '')
                ),
                tags=('positive' if fixture.get('performance_diff', 0) > 0 else 'negative',)
            )
            
        # Configure tags
        self.fixtures_table.tag_configure('positive', foreground='green')
        self.fixtures_table.tag_configure('negative', foreground='red')
            
    def _update_results_table(self):
        """Update the results table"""
        # Clear table
        for item in self.results_table.get_children():
            self.results_table.delete(item)
            
        # Get results from database
        results = self.db_manager.get_completed_predictions()
        
        # Add data
        for result in results:
            # Add row
            self.results_table.insert(
                "", "end",
                values=(
                    result.get('team_name', ''),
                    result.get('performance_diff', ''),
                    result.get('prediction', ''),
                    result.get('opponent_name', ''),
                    result.get('match_date', ''),
                    result.get('result', ''),
                    "Yes" if result.get('correct', 0) == 1 else "No"
                ),
                tags=('correct' if result.get('correct', 0) == 1 else 'incorrect',)
            )
            
        # Configure tags
        self.results_table.tag_configure('correct', foreground='green')
        self.results_table.tag_configure('incorrect', foreground='red')
    
    def _generate_prediction(self, performance_diff):
        """Generate prediction based on performance difference"""
        from modules.config import PREDICTION_THRESHOLD_LEVEL1, PREDICTION_THRESHOLD_LEVEL2
        
        prediction_level = 1
        
        if abs(performance_diff) >= PREDICTION_THRESHOLD_LEVEL2:
            prediction_level = 2
            
        if performance_diff > 0:
            if prediction_level == 2:
                prediction = "BIG WIN"
            else:
                prediction = "WIN"
        else:
            if prediction_level == 2:
                prediction = "BIG LOSS"
            else:
                prediction = "LOSS"
                
        return prediction, prediction_level
    
    def _save_to_database(self):
        """Save form changes to database"""
        try:
            saved_count = 0
            
            for fixture in self.form_changes_data:
                # Create prediction data
                prediction_data = {
                    'team_id': fixture['team_id'],
                    'team_name': fixture['team'],
                    'league_id': fixture['league_id'],
                    'league_name': fixture['league_name'],
                    'fixture_id': fixture['fixture_id'],
                    'opponent_id': fixture['opponent_id'],
                    'opponent_name': fixture['opponent'],
                    'match_date': fixture['date'],
                    'venue': fixture['venue'],
                    'performance_diff': fixture['performance_diff'],
                    'prediction': fixture['prediction'],
                    'prediction_level': fixture['prediction_level']
                }
                
                # Save to database
                prediction_id = self.db_manager.save_prediction(prediction_data)
                if prediction_id > 0:
                    saved_count += 1
            
            # Show success message
            if saved_count > 0:
                self.save_button.configure(text=f"Saved {saved_count} Predictions")
                self.parent.after(2000, lambda: self.save_button.configure(text="Save to Database"))
            else:
                self.save_button.configure(text="No New Predictions")
                self.parent.after(2000, lambda: self.save_button.configure(text="Save to Database"))
                
            # Update fixtures table
            self._update_fixtures_table()
                
        except Exception as e:
            logger.error(f"Error saving predictions: {str(e)}")
            self.save_button.configure(text="Save Failed")
            self.parent.after(2000, lambda: self.save_button.configure(text="Save to Database"))
            
    def _check_results(self):
        """Check results of predictions"""
        try:
            # Show loading animation
            self._show_loading_animation(self.check_button, "Check Results")
            
            # Check results in a separate thread
            self.parent.after(100, self._check_results_thread)
                
        except Exception as e:
            logger.error(f"Error checking results: {str(e)}")
            self.check_button.configure(text="Check Failed", state="normal")
            self.parent.after(2000, lambda: self.check_button.configure(text="Check Results"))
            
    def _check_results_thread(self):
        """Check results in a separate thread"""
        try:
            # Get predictions from database
            predictions = self.db_manager.get_predictions_to_check()
            
            checked_count = 0
            correct_count = 0
            
            for prediction in predictions:
                # Get fixture result
                fixture_id = prediction['fixture_id']
                fixture = self.api.fetch_fixture(fixture_id)
                
                if fixture and fixture['fixture']['status']['short'] == 'FT':
                    # Get result
                    home_score = fixture['goals']['home']
                    away_score = fixture['goals']['away']
                    
                    # Determine winner
                    if home_score > away_score:
                        result = "HOME_WIN"
                    elif away_score > home_score:
                        result = "AWAY_WIN"
                    else:
                        result = "DRAW"
                        
                    # Check if prediction was correct
                    team_id = prediction['team_id']
                    is_home = fixture['teams']['home']['id'] == team_id
                    
                    prediction_correct = False
                    
                    if prediction['prediction'] in ["WIN", "BIG WIN"]:
                        if (is_home and result == "HOME_WIN") or (not is_home and result == "AWAY_WIN"):
                            prediction_correct = True
                    elif prediction['prediction'] in ["LOSS", "BIG LOSS"]:
                        if (is_home and result == "AWAY_WIN") or (not is_home and result == "HOME_WIN"):
                            prediction_correct = True
                            
                    # Update prediction in database
                    self.db_manager.update_prediction_result(
                        prediction['id'],
                        result,
                        1 if prediction_correct else 0
                    )
                    
                    checked_count += 1
                    if prediction_correct:
                        correct_count += 1
            
            # Show success message
            if checked_count > 0:
                self.check_button.configure(
                    text=f"Checked {checked_count} ({correct_count} correct)",
                    state="normal"
                )
                self.parent.after(3000, lambda: self.check_button.configure(text="Check Results"))
            else:
                self.check_button.configure(text="No New Results", state="normal")
                self.parent.after(2000, lambda: self.check_button.configure(text="Check Results"))
                
            # Update results table
            self._update_results_table()
                
        except Exception as e:
            logger.error(f"Error checking results: {str(e)}")
            self.check_button.configure(text="Check Failed", state="normal")
            self.parent.after(2000, lambda: self.check_button.configure(text="Check Results"))
    
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update threshold
        self.threshold.set(self.settings_manager.get_threshold())
        self.threshold_label.configure(text=f"Threshold: {self.threshold.get():.2f}")
        
        # Update UI elements with new theme
        self.refresh_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )
        
        self.save_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )
        
        self.check_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )

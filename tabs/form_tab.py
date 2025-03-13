import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional, Callable

from tabs.base_tab import BaseTab
from modules.api_client import FootballAPI
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.league_names import get_league_options, get_league_display_name
from modules.config import PREDICTION_THRESHOLD_LEVEL1, PREDICTION_THRESHOLD_LEVEL2

logger = logging.getLogger(__name__)

class FormTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Initialize variables
        self.form_data = []
        self.upcoming_fixtures_data = []
        
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
            
        self.form_length = tk.IntVar(value=self.settings_manager.get_form_length())
        
        # Create UI elements
        self._create_ui()
        
    def _create_ui(self):
        """Create the form tab UI elements"""
        # Title
        self._create_title("Form Analysis")
        
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
        
        # Form length selection
        self.form_length_frame = ctk.CTkFrame(self.controls_frame)
        self.form_length_frame.pack(side="right", padx=10, pady=10, fill="x", expand=True)
        
        self.form_length_label = ctk.CTkLabel(
            self.form_length_frame, 
            text="Form Length:",
            font=ctk.CTkFont(size=14)
        )
        self.form_length_label.pack(pady=(0, 5))
        
        self.form_length_segment = ctk.CTkSegmentedButton(
            self.form_length_frame,
            values=["3 Matches", "5 Matches"],
            command=self._on_form_length_changed,
            font=ctk.CTkFont(size=12)
        )
        self.form_length_segment.pack(fill="x", padx=10, pady=5)
        self.form_length_segment.set("3 Matches" if self.form_length.get() == 3 else "5 Matches")
        
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
        
        # Form Analysis Tab
        self.form_analysis_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.form_analysis_frame, text="Form Analysis")
        
        # Create form analysis table
        self.form_analysis_table = self._create_table(
            self.form_analysis_frame,
            columns=[
                {"text": "Team", "width": 150},
                {"text": "League", "width": 150},
                {"text": "Position", "width": 80},
                {"text": "Points", "width": 80},
                {"text": "PPG", "width": 80},
                {"text": "Form", "width": 100},
                {"text": "Form Points", "width": 100},
                {"text": "Form PPG", "width": 80},
                {"text": "Perf. Diff", "width": 80}
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
                {"text": "Venue", "width": 150},
                {"text": "Status", "width": 100}
            ]
        )
        
        # Enable sorting for the fixtures table
        for col_idx, col in enumerate(["Team", "Perf. Diff", "Prediction", "Opponent", "Date", "Time", "Venue", "Status"]):
            self.fixtures_table.heading(f"col{col_idx}", 
                                       text=col,
                                       command=lambda c=col_idx: self._sort_fixtures_table(c))
        
        # Add save button for predictions
        self.save_button = self._create_button(
            self.fixtures_frame,
            text="Save Predictions to Database",
            command=self._save_predictions,
            width=200,
            height=32
        )
        self.save_button.pack(pady=10)
        
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
        
    def _on_form_length_changed(self, selection):
        """Handle form length selection change"""
        form_length = 3 if selection == "3 Matches" else 5
        self.form_length.set(form_length)
        
        # Save to settings
        self.settings_manager.set_setting("form_length", form_length)
        
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
            # Get form data
            league_id = self.selected_league.get()
            form_length = self.form_length.get()
            
            try:
                # Fetch data from API with timeout handling
                self.form_data = self.api.fetch_all_teams({league_id: {"name": "", "flag": ""}}, form_length)
                
                if not self.form_data:
                    logger.warning(f"No form data returned for league {league_id}")
                    self.refresh_button.configure(text="No Data Found", state="normal")
                    self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data", state="normal"))
                    return
            except KeyboardInterrupt:
                logger.warning("Team data fetch interrupted by user")
                self.refresh_button.configure(text="Fetch Interrupted", state="normal")
                self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data", state="normal"))
                return
            except Exception as e:
                logger.error(f"Error fetching team data: {str(e)}")
                self.refresh_button.configure(text="Team Data Error", state="normal")
                self.parent.after(2000, lambda: self.refresh_button.configure(text="Refresh Data", state="normal"))
                return
            
            # Update status
            self.refresh_button.configure(text="Fetching fixtures...", state="disabled")
            
            # Get upcoming fixtures for teams with significant form changes
            self.upcoming_fixtures_data = []
            threshold = self.settings_manager.get_threshold()
            
            try:
                # Fetch fixtures once for the league
                fixtures = self.api.fetch_fixtures(league_id)
                
                for team_data in self.form_data:
                    if abs(team_data.get('performance_diff', 0)) >= threshold:
                        # Get upcoming matches
                        upcoming_matches = self._get_upcoming_matches(fixtures, team_data['team_id'])
                        
                        if upcoming_matches:
                            for match in upcoming_matches:
                                # Create prediction
                                prediction, prediction_level = self._generate_prediction(team_data['performance_diff'])
                                
                                # Add to upcoming fixtures data
                                self.upcoming_fixtures_data.append({
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
            except KeyboardInterrupt:
                logger.warning("Fixtures fetch interrupted by user")
                # Continue with whatever data we have
            except Exception as e:
                logger.error(f"Error fetching fixtures: {str(e)}")
                # Continue with whatever data we have
            
            # Update tables
            self._update_form_table()
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
            
    def _get_upcoming_matches(self, fixtures, team_id, top_n=1):
        """Get upcoming matches for a team"""
        from modules.form_analyzer import FormAnalyzer
        return FormAnalyzer.get_upcoming_opponents(fixtures, team_id, top_n)
            
    def _update_form_table(self):
        """Update the form analysis table"""
        # Clear table
        for item in self.form_analysis_table.get_children():
            self.form_analysis_table.delete(item)
            
        # Add data
        for i, team in enumerate(self.form_data):
            # Format form string
            form_str = self._format_form_string(team.get('form', ''))
            
            # Add row
            self.form_analysis_table.insert(
                "", "end",
                values=(
                    team.get('team', ''),
                    team.get('league', ''),
                    team.get('current_position', ''),
                    team.get('current_points', ''),
                    team.get('current_ppg', ''),
                    form_str,
                    team.get('form_points', ''),
                    team.get('form_ppg', ''),
                    team.get('performance_diff', '')
                ),
                tags=('positive' if team.get('performance_diff', 0) > 0 else 'negative',)
            )
            
        # Configure tags
        self.form_analysis_table.tag_configure('positive', foreground='green')
        self.form_analysis_table.tag_configure('negative', foreground='red')
            
    def _update_fixtures_table(self):
        """Update the upcoming fixtures table"""
        # Clear table
        for item in self.fixtures_table.get_children():
            self.fixtures_table.delete(item)
            
        # Filter out past matches
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')
            future_fixtures = []
            
            for fixture in self.upcoming_fixtures_data:
                fixture_date = fixture.get('date', '')
                
                # Skip fixtures with no date
                if not fixture_date:
                    continue
                    
                # Handle ISO format dates
                if 'T' in fixture_date:
                    fixture_date = fixture_date.split('T')[0]
                
                # Only include future fixtures
                if fixture_date >= current_date:
                    future_fixtures.append(fixture)
                    
            logger.debug(f"Filtered {len(self.upcoming_fixtures_data)} fixtures to {len(future_fixtures)} future fixtures")
        except Exception as e:
            logger.error(f"Error filtering fixtures: {str(e)}")
            # Fall back to all fixtures if filtering fails
            future_fixtures = self.upcoming_fixtures_data
        
        # Sort by date
        future_fixtures.sort(key=lambda x: x['date'])
        
        # Group fixtures by date
        fixtures_by_date = {}
        for fixture in future_fixtures:
            # Convert date from YYYY-MM-DD to DD.MM.YYYY
            original_date = fixture.get('date', '')
            if original_date:
                try:
                    # Handle different date formats
                    if 'T' in original_date:
                        # ISO format with time component
                        date_part = original_date.split('T')[0]
                        date_obj = datetime.strptime(date_part, '%Y-%m-%d')
                    else:
                        # Just date
                        date_obj = datetime.strptime(original_date, '%Y-%m-%d')
                    
                    # Format as DD.MM.YYYY
                    formatted_date = date_obj.strftime('%d.%m.%Y')
                    fixture['formatted_date'] = formatted_date
                except ValueError as e:
                    logger.warning(f"Error formatting date '{original_date}': {str(e)}")
                    fixture['formatted_date'] = original_date
            else:
                fixture['formatted_date'] = 'Unknown'
                
            # Group by original date for sorting purposes
            if original_date not in fixtures_by_date:
                fixtures_by_date[original_date] = []
            fixtures_by_date[original_date].append(fixture)
        
        # Add data with date separators
        for date, fixtures in fixtures_by_date.items():
            # Get formatted date for display (from the first fixture in this group)
            formatted_date = fixtures[0].get('formatted_date', date) if fixtures else date
            
            # Add date separator
            separator_id = self.fixtures_table.insert(
                "", "end",
                values=("", "", "", "", f"--- {formatted_date} ---", "", "", ""),
                tags=('date_separator',)
            )
            
            # Add fixtures for this date
            for fixture in fixtures:
                # Add row as child of date separator
                self.fixtures_table.insert(
                    separator_id, "end",
                    values=(
                        fixture.get('team', ''),
                        fixture.get('performance_diff', ''),
                        fixture.get('prediction', ''),
                        fixture.get('opponent', ''),
                        fixture.get('formatted_date', ''),
                        fixture.get('time', ''),
                        fixture.get('venue', ''),
                        fixture.get('status', '')
                    ),
                    tags=('positive' if fixture.get('performance_diff', 0) > 0 else 'negative',)
                )
            
            # Expand the date separator by default
            self.fixtures_table.item(separator_id, open=True)
            
        # Configure tags
        self.fixtures_table.tag_configure('positive', foreground='green')
        self.fixtures_table.tag_configure('negative', foreground='red')
        self.fixtures_table.tag_configure('date_separator', background='#E0E0E0', font=('Helvetica', self.settings_manager.get_font_size(), 'bold'))
            
    def _format_form_string(self, form_str):
        """Format form string with colors"""
        # This is just for display in the table
        # In a real implementation, we would use custom cell rendering
        return form_str
    
    def _generate_prediction(self, performance_diff):
        """Generate prediction based on performance difference"""
        prediction_level = 1
        
        if abs(performance_diff) >= PREDICTION_THRESHOLD_LEVEL2:
            prediction_level = 2
            
        if performance_diff > 0:
            if prediction_level == 2:
                prediction = "VEĽKÁ PREHRA S"
            else:
                prediction = "PREHRA s"
        else:
            if prediction_level == 2:
                prediction = "VEĽKÁ VÝHRA s"
            else:
                prediction = "VÝHRA s"
                
        return prediction, prediction_level
    
    def _save_predictions(self):
        """Save predictions to database"""
        try:
            saved_count = 0
            
            for fixture in self.upcoming_fixtures_data:
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
                self.parent.after(2000, lambda: self.save_button.configure(text="Save Predictions to Database"))
            else:
                self.save_button.configure(text="No New Predictions")
                self.parent.after(2000, lambda: self.save_button.configure(text="Save Predictions to Database"))
                
        except Exception as e:
            logger.error(f"Error saving predictions: {str(e)}")
            self.save_button.configure(text="Save Failed")
            self.parent.after(2000, lambda: self.save_button.configure(text="Save Predictions to Database"))
    
    def _sort_fixtures_table(self, col_idx):
        """Sort the fixtures table by the specified column"""
        try:
            # Store current sort column and order
            if hasattr(self, 'sort_col') and self.sort_col == col_idx:
                # If already sorting by this column, reverse the order
                self.sort_reverse = not self.sort_reverse
            else:
                # New sort column
                self.sort_col = col_idx
                self.sort_reverse = False
                
            # Get all date separators
            date_separators = []
            for item_id in self.fixtures_table.get_children():
                if self.fixtures_table.item(item_id, 'tags') and 'date_separator' in self.fixtures_table.item(item_id, 'tags'):
                    date_separators.append(item_id)
                    
            # If no date separators, sort the entire table
            if not date_separators:
                # Get all items
                items = []
                for item_id in self.fixtures_table.get_children():
                    values = self.fixtures_table.item(item_id, 'values')
                    tags = self.fixtures_table.item(item_id, 'tags')
                    items.append((values, tags, item_id))
                    
                # Sort items by the selected column
                items.sort(key=lambda x: x[0][col_idx] if x[0][col_idx] else "", reverse=self.sort_reverse)
                
                # Reorder items in the treeview
                for idx, (values, tags, item_id) in enumerate(items):
                    self.fixtures_table.move(item_id, "", idx)
            else:
                # Sort each date group separately
                for separator_id in date_separators:
                    # Get all children of this separator
                    children = self.fixtures_table.get_children(separator_id)
                    if not children:
                        continue
                        
                    # Get values for each child
                    items = []
                    for child_id in children:
                        values = self.fixtures_table.item(child_id, 'values')
                        tags = self.fixtures_table.item(child_id, 'tags')
                        items.append((values, tags, child_id))
                        
                    # Sort items by the selected column
                    items.sort(key=lambda x: x[0][col_idx] if x[0][col_idx] else "", reverse=self.sort_reverse)
                    
                    # Reorder items in the treeview
                    for idx, (values, tags, item_id) in enumerate(items):
                        self.fixtures_table.move(item_id, separator_id, idx)
                    
            # Update column headers to show sort direction
            for i in range(8):  # 8 columns
                if i == col_idx:
                    # Add arrow to indicate sort direction
                    arrow = "▼" if self.sort_reverse else "▲"
                    text = self.fixtures_table.heading(f"col{i}")["text"].rstrip("▲▼ ")
                    self.fixtures_table.heading(f"col{i}", text=f"{text} {arrow}")
                else:
                    # Remove arrow from other columns
                    text = self.fixtures_table.heading(f"col{i}")["text"].rstrip("▲▼ ")
                    self.fixtures_table.heading(f"col{i}", text=text)
        except Exception as e:
            logger.error(f"Error sorting fixtures table: {str(e)}")
    
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update UI elements with new theme
        self.refresh_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )
        
        self.save_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog
import logging
import csv
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

from tabs.base_tab import BaseTab
from modules.api_client import FootballAPI
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.league_names import get_league_options, get_league_display_name

logger = logging.getLogger(__name__)

class DataCollectionTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Initialize variables
        self.collected_data = []
        self.selected_league = tk.IntVar(value=self.settings_manager.get_leagues()[0])
        self.selected_data_type = tk.StringVar(value="Fixtures")
        
        # Create UI elements
        self._create_ui()
        
    def _create_ui(self):
        """Create the data collection tab UI elements"""
        # Title
        self._create_title("Data Collection")
        
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
        
        # Data type selection
        self.data_type_frame = ctk.CTkFrame(self.controls_frame)
        self.data_type_frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.data_type_label = ctk.CTkLabel(
            self.data_type_frame, 
            text="Data Type:",
            font=ctk.CTkFont(size=14)
        )
        self.data_type_label.pack(pady=(0, 5))
        
        # Create dropdown for data types
        self.data_type_dropdown = ctk.CTkOptionMenu(
            self.data_type_frame,
            values=["Fixtures", "Teams", "Players", "Standings"],
            command=self._on_data_type_changed,
            variable=self.selected_data_type,
            font=ctk.CTkFont(size=12)
        )
        self.data_type_dropdown.pack(fill="x", padx=10, pady=5)
        
        # Season selection
        self.season_frame = ctk.CTkFrame(self.controls_frame)
        self.season_frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.season_label = ctk.CTkLabel(
            self.season_frame, 
            text="Season:",
            font=ctk.CTkFont(size=14)
        )
        self.season_label.pack(pady=(0, 5))
        
        # Create dropdown for seasons
        current_year = datetime.now().year
        seasons = [str(year) for year in range(current_year, current_year - 5, -1)]
        
        self.season_dropdown = ctk.CTkOptionMenu(
            self.season_frame,
            values=seasons,
            font=ctk.CTkFont(size=12)
        )
        self.season_dropdown.pack(fill="x", padx=10, pady=5)
        
        # Fetch button
        self.fetch_button = self._create_button(
            self.controls_frame,
            text="Fetch Data",
            command=self._fetch_data,
            width=120,
            height=32
        )
        self.fetch_button.pack(side="right", padx=20, pady=10)
        
        # Create data display section
        self.data_frame = ctk.CTkFrame(self.content_frame)
        self.data_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create data table
        self.data_table = self._create_table(
            self.data_frame,
            columns=[
                {"text": "ID", "width": 80},
                {"text": "Name", "width": 150},
                {"text": "Type", "width": 100},
                {"text": "Date", "width": 100},
                {"text": "Status", "width": 100},
                {"text": "Details", "width": 300}
            ]
        )
        
        # Create export section
        self.export_frame = ctk.CTkFrame(self.content_frame)
        self.export_frame.pack(fill="x", padx=10, pady=10)
        
        # Export format selection
        self.export_format_var = tk.StringVar(value="CSV")
        
        self.csv_radio = ctk.CTkRadioButton(
            self.export_frame,
            text="CSV",
            variable=self.export_format_var,
            value="CSV",
            font=ctk.CTkFont(size=12)
        )
        self.csv_radio.pack(side="left", padx=20, pady=10)
        
        self.json_radio = ctk.CTkRadioButton(
            self.export_frame,
            text="JSON",
            variable=self.export_format_var,
            value="JSON",
            font=ctk.CTkFont(size=12)
        )
        self.json_radio.pack(side="left", padx=20, pady=10)
        
        # Export button
        self.export_button = self._create_button(
            self.export_frame,
            text="Export Data",
            command=self._export_data,
            width=120,
            height=32
        )
        self.export_button.pack(side="right", padx=20, pady=10)
        
        # Save to database button
        self.save_button = self._create_button(
            self.export_frame,
            text="Save to Database",
            command=self._save_to_database,
            width=150,
            height=32
        )
        self.save_button.pack(side="right", padx=20, pady=10)
        
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
        
    def _on_data_type_changed(self, selection):
        """Handle data type selection change"""
        # Update columns based on data type
        if selection == "Fixtures":
            columns = [
                {"text": "ID", "width": 80},
                {"text": "Home", "width": 150},
                {"text": "Away", "width": 150},
                {"text": "Date", "width": 100},
                {"text": "Status", "width": 100},
                {"text": "Score", "width": 100}
            ]
        elif selection == "Teams":
            columns = [
                {"text": "ID", "width": 80},
                {"text": "Name", "width": 150},
                {"text": "Country", "width": 100},
                {"text": "Founded", "width": 100},
                {"text": "Stadium", "width": 150},
                {"text": "Capacity", "width": 100}
            ]
        elif selection == "Players":
            columns = [
                {"text": "ID", "width": 80},
                {"text": "Name", "width": 150},
                {"text": "Team", "width": 150},
                {"text": "Position", "width": 100},
                {"text": "Age", "width": 80},
                {"text": "Nationality", "width": 100}
            ]
        else:  # Standings
            columns = [
                {"text": "Pos", "width": 50},
                {"text": "Team", "width": 150},
                {"text": "P", "width": 50},
                {"text": "W", "width": 50},
                {"text": "D", "width": 50},
                {"text": "L", "width": 50},
                {"text": "GF", "width": 50},
                {"text": "GA", "width": 50},
                {"text": "Pts", "width": 50}
            ]
            
        # Recreate table with new columns
        for item in self.data_table.get_children():
            self.data_table.delete(item)
            
        # Update table columns
        for i, col in enumerate(self.data_table["columns"]):
            self.data_table.heading(col, text="")
            self.data_table.column(col, width=0)
            
        for i, col in enumerate(columns):
            if i < len(self.data_table["columns"]):
                self.data_table.heading(f"col{i}", text=col["text"])
                self.data_table.column(f"col{i}", width=col["width"])
        
    def _fetch_data(self):
        """Fetch data from API"""
        # Show loading animation
        self._show_loading_animation(self.fetch_button, "Fetch Data")
        
        # Get data in a separate thread
        self.parent.after(100, self._fetch_data_thread)
        
    def _fetch_data_thread(self):
        """Fetch data from API in a separate thread"""
        try:
            # Get parameters
            league_id = self.selected_league.get()
            data_type = self.selected_data_type.get()
            season = self.season_dropdown.get()
            
            # Fetch data based on type
            if data_type == "Fixtures":
                data = self.api.fetch_fixtures(league_id, season=season)
            elif data_type == "Teams":
                data = self.api.fetch_teams(league_id, season=season)
            elif data_type == "Players":
                data = self.api.fetch_players(league_id, season=season)
            else:  # Standings
                data = self.api.fetch_standings(league_id, season=season)
                
            # Store data
            self.collected_data = data
            
            # Update table
            self._update_data_table()
            
            # Reset fetch button
            self.fetch_button.configure(text="Fetch Data", state="normal")
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            self.fetch_button.configure(text="Fetch Failed", state="normal")
            self.parent.after(2000, lambda: self.fetch_button.configure(text="Fetch Data"))
            
    def _update_data_table(self):
        """Update the data table with fetched data"""
        # Clear table
        for item in self.data_table.get_children():
            self.data_table.delete(item)
            
        # Get data type
        data_type = self.selected_data_type.get()
        
        # Add data based on type
        if data_type == "Fixtures":
            for fixture in self.collected_data:
                # Get fixture data
                fixture_id = fixture['fixture']['id']
                home_team = fixture['teams']['home']['name']
                away_team = fixture['teams']['away']['name']
                date = fixture['fixture']['date'].split('T')[0]
                status = fixture['fixture']['status']['long']
                
                # Get score
                if fixture['fixture']['status']['short'] == 'FT':
                    score = f"{fixture['goals']['home']} - {fixture['goals']['away']}"
                else:
                    score = "vs"
                    
                # Add row
                self.data_table.insert(
                    "", "end",
                    values=(
                        fixture_id,
                        home_team,
                        away_team,
                        date,
                        status,
                        score
                    )
                )
        elif data_type == "Teams":
            for team in self.collected_data:
                # Get team data (placeholder)
                team_id = team['team']['id']
                name = team['team']['name']
                country = "England"  # Placeholder
                founded = "1900"  # Placeholder
                stadium = "Stadium"  # Placeholder
                capacity = "50000"  # Placeholder
                
                # Add row
                self.data_table.insert(
                    "", "end",
                    values=(
                        team_id,
                        name,
                        country,
                        founded,
                        stadium,
                        capacity
                    )
                )
        elif data_type == "Players":
            for player in self.collected_data:
                # Get player data (placeholder)
                player_id = player['player']['id']
                name = player['player']['name']
                team = "Team"  # Placeholder
                position = "Position"  # Placeholder
                age = "25"  # Placeholder
                nationality = "England"  # Placeholder
                
                # Add row
                self.data_table.insert(
                    "", "end",
                    values=(
                        player_id,
                        name,
                        team,
                        position,
                        age,
                        nationality
                    )
                )
        else:  # Standings
            for team in self.collected_data:
                # Get team data
                position = team['rank']
                team_name = team['team']['name']
                played = team['all']['played']
                wins = team['all']['win']
                draws = team['all']['draw']
                losses = team['all']['lose']
                goals_for = team['all']['goals']['for']
                goals_against = team['all']['goals']['against']
                points = team['points']
                
                # Add row
                self.data_table.insert(
                    "", "end",
                    values=(
                        position,
                        team_name,
                        played,
                        wins,
                        draws,
                        losses,
                        goals_for,
                        goals_against,
                        points
                    )
                )
                
    def _export_data(self):
        """Export data to file"""
        if not self.collected_data:
            return
            
        # Get export format
        export_format = self.export_format_var.get()
        
        # Get file path
        file_types = [("CSV files", "*.csv")] if export_format == "CSV" else [("JSON files", "*.json")]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv" if export_format == "CSV" else ".json",
            filetypes=file_types
        )
        
        if not file_path:
            return
            
        try:
            # Export based on format
            if export_format == "CSV":
                self._export_to_csv(file_path)
            else:
                self._export_to_json(file_path)
                
            # Show success message
            self.export_button.configure(text="Export Successful")
            self.parent.after(2000, lambda: self.export_button.configure(text="Export Data"))
            
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            self.export_button.configure(text="Export Failed")
            self.parent.after(2000, lambda: self.export_button.configure(text="Export Data"))
            
    def _export_to_csv(self, file_path):
        """Export data to CSV file"""
        # Get data type
        data_type = self.selected_data_type.get()
        
        # Define headers based on data type
        if data_type == "Fixtures":
            headers = ["ID", "Home", "Away", "Date", "Status", "Score"]
        elif data_type == "Teams":
            headers = ["ID", "Name", "Country", "Founded", "Stadium", "Capacity"]
        elif data_type == "Players":
            headers = ["ID", "Name", "Team", "Position", "Age", "Nationality"]
        else:  # Standings
            headers = ["Position", "Team", "Played", "Wins", "Draws", "Losses", "Goals For", "Goals Against", "Points"]
            
        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write headers
            writer.writerow(headers)
            
            # Write data
            for item in self.data_table.get_children():
                values = self.data_table.item(item, "values")
                writer.writerow(values)
                
    def _export_to_json(self, file_path):
        """Export data to JSON file"""
        # Get data type
        data_type = self.selected_data_type.get()
        
        # Create JSON data
        json_data = {
            "data_type": data_type,
            "league_id": self.selected_league.get(),
            "league_name": get_league_display_name(self.selected_league.get()),
            "season": self.season_dropdown.get(),
            "export_date": datetime.now().isoformat(),
            "items": []
        }
        
        # Add items based on data type
        if data_type == "Fixtures":
            for item in self.data_table.get_children():
                values = self.data_table.item(item, "values")
                json_data["items"].append({
                    "id": values[0],
                    "home_team": values[1],
                    "away_team": values[2],
                    "date": values[3],
                    "status": values[4],
                    "score": values[5]
                })
        elif data_type == "Teams":
            for item in self.data_table.get_children():
                values = self.data_table.item(item, "values")
                json_data["items"].append({
                    "id": values[0],
                    "name": values[1],
                    "country": values[2],
                    "founded": values[3],
                    "stadium": values[4],
                    "capacity": values[5]
                })
        elif data_type == "Players":
            for item in self.data_table.get_children():
                values = self.data_table.item(item, "values")
                json_data["items"].append({
                    "id": values[0],
                    "name": values[1],
                    "team": values[2],
                    "position": values[3],
                    "age": values[4],
                    "nationality": values[5]
                })
        else:  # Standings
            for item in self.data_table.get_children():
                values = self.data_table.item(item, "values")
                json_data["items"].append({
                    "position": values[0],
                    "team": values[1],
                    "played": values[2],
                    "wins": values[3],
                    "draws": values[4],
                    "losses": values[5],
                    "goals_for": values[6],
                    "goals_against": values[7],
                    "points": values[8]
                })
                
        # Write to JSON file
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=4, ensure_ascii=False)
            
    def _save_to_database(self):
        """Save data to database"""
        if not self.collected_data:
            return
            
        try:
            # Get data type
            data_type = self.selected_data_type.get()
            
            # Save based on data type
            if data_type == "Fixtures":
                saved_count = self.db_manager.save_fixtures(self.collected_data)
            elif data_type == "Teams":
                saved_count = self.db_manager.save_teams(self.collected_data)
            elif data_type == "Players":
                saved_count = self.db_manager.save_players(self.collected_data)
            else:  # Standings
                saved_count = self.db_manager.save_standings(self.collected_data)
                
            # Show success message
            self.save_button.configure(text=f"Saved {saved_count} Items")
            self.parent.after(2000, lambda: self.save_button.configure(text="Save to Database"))
            
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            self.save_button.configure(text="Save Failed")
            self.parent.after(2000, lambda: self.save_button.configure(text="Save to Database"))
    
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update UI elements with new theme
        self.fetch_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )
        
        self.export_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )
        
        self.save_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )

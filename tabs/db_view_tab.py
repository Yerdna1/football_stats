import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable
import sqlite3
import pandas as pd
from datetime import datetime

from tabs.base_tab import BaseTab
from modules.api_client import FootballAPI
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.translations import translate

logger = logging.getLogger(__name__)

class DbViewTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Initialize variables
        self.current_table = tk.StringVar(value="predictions")
        self.tables = ["predictions", "fixtures", "teams", "leagues", "form_changes"]
        
        # Create UI elements
        self._create_ui()
        
        # Load initial data
        self._load_data()
        
    def _create_ui(self):
        """Create the database view tab UI elements"""
        # Title
        self._create_title(translate("Database View"))
        
        # Controls section
        self.controls_frame = ctk.CTkFrame(self.content_frame)
        self.controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Table selection
        self.table_label = ctk.CTkLabel(
            self.controls_frame,
            text=translate("Select Table:"),
            font=ctk.CTkFont(size=18)
        )
        self.table_label.pack(side="left", padx=(10, 5))
        
        self.table_dropdown = ctk.CTkOptionMenu(
            self.controls_frame,
            values=[translate(table) for table in self.tables],
            variable=self.current_table,
            command=self._on_table_changed,
            font=ctk.CTkFont(size=18)
        )
        self.table_dropdown.pack(side="left", padx=5)
        
        # Filter section
        self.filter_frame = ctk.CTkFrame(self.controls_frame)
        self.filter_frame.pack(side="left", padx=20)
        
        # For predictions table
        self.prediction_filter_var = tk.StringVar(value=translate("All"))
        
        self.prediction_filter_label = ctk.CTkLabel(
            self.filter_frame,
            text=translate("Filter:"),
            font=ctk.CTkFont(size=18)
        )
        self.prediction_filter_label.pack(side="left", padx=(10, 5))
        
        self.prediction_filter_dropdown = ctk.CTkOptionMenu(
            self.filter_frame,
            values=[
                translate("All"), 
                translate("Correct"), 
                translate("Incorrect"),
                translate("WAITING"),
                translate("COMPLETED")
            ],
            variable=self.prediction_filter_var,
            command=self._on_filter_changed,
            font=ctk.CTkFont(size=18)
        )
        self.prediction_filter_dropdown.pack(side="left", padx=5)
        
        # Refresh button
        self.refresh_button = self._create_button(
            self.controls_frame,
            text=translate("Refresh Data"),
            command=self._load_data,
            width=150,
            height=40
        )
        self.refresh_button.pack(side="right", padx=10)
        
        # Export button
        self.export_button = self._create_button(
            self.controls_frame,
            text=translate("Export to CSV"),
            command=self._export_data,
            width=150,
            height=40
        )
        self.export_button.pack(side="right", padx=10)
        
        # Create notebook for different views
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=('Helvetica', 36))  # Increased font size from 28 to 36
        style.configure("TNotebook", font=('Helvetica', 36))  # Add font configuration for the notebook itself
        
        self.notebook = ttk.Notebook(self.content_frame, style="TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Table View Tab
        self.table_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.table_frame, text=translate("Table View"))
        
        # Create table
        self.data_table = self._create_table(
            self.table_frame,
            columns=[
                {"text": "ID", "width": 50},
                {"text": translate("Team"), "width": 150},
                {"text": translate("League"), "width": 150},
                {"text": translate("Opponent"), "width": 150},
                {"text": translate("Date"), "width": 100},
                {"text": translate("Prediction"), "width": 120},
                {"text": translate("Perf. Diff"), "width": 100},
                {"text": translate("Status"), "width": 100},
                {"text": translate("Result"), "width": 100},
                {"text": translate("Correct"), "width": 100}
            ]
        )
        
        # Stats View Tab
        self.stats_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.stats_frame, text=translate("Statistics"))
        
        # Create stats grid
        self.stats_grid = ctk.CTkFrame(self.stats_frame)
        self.stats_grid.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        self.stats_grid.columnconfigure(0, weight=1)
        self.stats_grid.columnconfigure(1, weight=1)
        self.stats_grid.rowconfigure(0, weight=1)
        self.stats_grid.rowconfigure(1, weight=1)
        
        # Create stat cards
        self.total_card = self._create_stat_card(self.stats_grid, translate("Total Records"), "0", 0, 0)
        self.completed_card = self._create_stat_card(self.stats_grid, translate("Completed"), "0", 0, 1)
        self.correct_card = self._create_stat_card(self.stats_grid, translate("Correct"), "0", 1, 0)
        self.accuracy_card = self._create_stat_card(self.stats_grid, translate("Accuracy"), "0%", 1, 1)
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self.footer_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=5)
        
    def _create_stat_card(self, parent, title, value, row, col):
        """Create a stat card with title and value"""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=24)
        )
        value_label.pack(pady=(10, 20))
        
        return {
            "title": title_label,
            "value": value_label
        }
        
    def _on_table_changed(self, selection):
        """Handle table selection change"""
        # Get the English table name from the translated selection
        for table in self.tables:
            if translate(table) == selection:
                self.current_table.set(table)
                break
        
        # Show/hide prediction filter based on selected table
        if self.current_table.get() == "predictions":
            self.filter_frame.pack(side="left", padx=20)
        else:
            self.filter_frame.pack_forget()
        
        # Reload data
        self._load_data()
        
    def _on_filter_changed(self, selection):
        """Handle filter selection change"""
        self._load_data()
        
    def _load_data(self):
        """Load data from database"""
        # Show loading animation on button
        self._show_loading_animation(self.refresh_button, translate("Refresh Data"))
        
        # Show loading indicator overlay
        self.show_loading_indicator()
        
        # Get data in a separate thread
        self.parent.after(100, self._fetch_data)
        
    def _fetch_data(self):
        """Fetch data from database"""
        try:
            table = self.current_table.get()
            
            # Clear table
            for item in self.data_table.get_children():
                self.data_table.delete(item)
                
            # Configure columns based on selected table
            if table == "predictions":
                self._configure_predictions_table()
            elif table == "fixtures":
                self._configure_fixtures_table()
            elif table == "teams":
                self._configure_teams_table()
            elif table == "leagues":
                self._configure_leagues_table()
            elif table == "form_changes":
                self._configure_form_changes_table()
                
            # Update status
            self.status_label.configure(text=f"{translate('Data loaded at')} {datetime.now().strftime('%H:%M:%S')}")
            
            # Reset refresh button
            self.refresh_button.configure(text=translate("Refresh Data"), state="normal")
            
            # Hide loading indicator
            self.hide_loading_indicator()
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            self.refresh_button.configure(text=translate("Refresh Failed"), state="normal")
            self.parent.after(2000, lambda: self.refresh_button.configure(text=translate("Refresh Data")))
            
            # Hide loading indicator
            self.hide_loading_indicator()
            
    def _configure_predictions_table(self):
        """Configure and load predictions table"""
        # Configure columns
        self.data_table["columns"] = (
            "id", "team", "league", "opponent", "date", "prediction",
            "performance_diff", "status", "result", "correct"
        )
        
        # Clear existing columns
        for col in self.data_table["columns"]:
            self.data_table.heading(col, text="")
            self.data_table.column(col, width=0)
            
        # Set new column headings
        self.data_table.heading("id", text="ID")
        self.data_table.heading("team", text=translate("Team"))
        self.data_table.heading("league", text=translate("League"))
        self.data_table.heading("opponent", text=translate("Opponent"))
        self.data_table.heading("date", text=translate("Date"))
        self.data_table.heading("prediction", text=translate("Prediction"))
        self.data_table.heading("performance_diff", text=translate("Perf. Diff"))
        self.data_table.heading("status", text=translate("Status"))
        self.data_table.heading("result", text=translate("Result"))
        self.data_table.heading("correct", text=translate("Correct"))
        
        # Set column widths
        self.data_table.column("id", width=50)
        self.data_table.column("team", width=150)
        self.data_table.column("league", width=150)
        self.data_table.column("opponent", width=150)
        self.data_table.column("date", width=100)
        self.data_table.column("prediction", width=120)
        self.data_table.column("performance_diff", width=100)
        self.data_table.column("status", width=100)
        self.data_table.column("result", width=100)
        self.data_table.column("correct", width=100)
        
        # Get predictions
        predictions = self.db_manager.get_predictions()
        
        # Apply filter
        filter_value = self.prediction_filter_var.get()
        
        if filter_value == translate("Correct"):
            predictions = [p for p in predictions if p["correct"] == 1]
        elif filter_value == translate("Incorrect"):
            predictions = [p for p in predictions if p["correct"] == 0 and p["status"] == "COMPLETED"]
        elif filter_value == translate("WAITING"):
            predictions = [p for p in predictions if p["status"] == "WAITING"]
        elif filter_value == translate("COMPLETED"):
            predictions = [p for p in predictions if p["status"] == "COMPLETED"]
        
        # Add data to table
        for prediction in predictions:
            # Determine tag
            if prediction["status"] == "WAITING":
                tag = "waiting"
            elif prediction["correct"] == 1:
                tag = "correct"
            else:
                tag = "incorrect"
                
            # Add row
            self.data_table.insert(
                "", "end",
                values=(
                    prediction["id"],
                    prediction["team_name"],
                    prediction["league_name"],
                    prediction["opponent_name"],
                    prediction["match_date"],
                    translate(prediction["prediction"]),
                    prediction["performance_diff"],
                    translate(prediction["status"]),
                    prediction["result"] or "",
                    translate("Yes") if prediction["correct"] == 1 else translate("No") if prediction["status"] == "COMPLETED" else ""
                ),
                tags=(tag,)
            )
            
        # Configure tags
        self.data_table.tag_configure("correct", foreground="green")
        self.data_table.tag_configure("incorrect", foreground="red")
        self.data_table.tag_configure("waiting", foreground="blue")
        
        # Update stats
        stats = self.db_manager.get_prediction_stats()
        
        self.total_card["value"].configure(text=str(stats["total"]))
        self.completed_card["value"].configure(text=str(stats["completed"]))
        self.correct_card["value"].configure(text=str(stats["correct"]))
        self.accuracy_card["value"].configure(text=f"{stats['accuracy']:.1f}%")
        
    def _configure_fixtures_table(self):
        """Configure and load fixtures table"""
        # Configure columns
        self.data_table["columns"] = (
            "id", "league", "home_team", "away_team", "date", "status", "score"
        )
        
        # Clear existing columns
        for col in self.data_table["columns"]:
            self.data_table.heading(col, text="")
            self.data_table.column(col, width=0)
            
        # Set new column headings
        self.data_table.heading("id", text="ID")
        self.data_table.heading("league", text=translate("League"))
        self.data_table.heading("home_team", text=translate("Home"))
        self.data_table.heading("away_team", text=translate("Away"))
        self.data_table.heading("date", text=translate("Date"))
        self.data_table.heading("status", text=translate("Status"))
        self.data_table.heading("score", text=translate("Score"))
        
        # Set column widths
        self.data_table.column("id", width=50)
        self.data_table.column("league", width=150)
        self.data_table.column("home_team", width=150)
        self.data_table.column("away_team", width=150)
        self.data_table.column("date", width=150)
        self.data_table.column("status", width=100)
        self.data_table.column("score", width=100)
        
        # Get fixtures
        fixtures = self.db_manager.get_fixtures()
        
        # Add data to table
        for fixture in fixtures:
            try:
                # Create score string
                score = "-"
                if fixture.get("home_score") is not None and fixture.get("away_score") is not None:
                    score = f"{fixture['home_score']}-{fixture['away_score']}"
                
                self.data_table.insert(
                    "", "end",
                    values=(
                        fixture["id"],
                        fixture.get("league_name", ""),
                        fixture["home_team_name"],
                        fixture["away_team_name"],
                        fixture["match_date"],
                        fixture["status"],
                        score
                    )
                )
            except Exception as e:
                logger.error(f"Error adding fixture to table: {str(e)}")
            
        # Update stats
        total = len(fixtures)
        completed = sum(1 for f in fixtures if f["status"] == "COMPLETED")
        
        self.total_card["value"].configure(text=str(total))
        self.completed_card["value"].configure(text=str(completed))
        self.correct_card["value"].configure(text="-")
        self.accuracy_card["value"].configure(text="-")
        
    def _configure_teams_table(self):
        """Configure and load teams table"""
        # Configure columns
        self.data_table["columns"] = (
            "id", "name", "league", "country"
        )
        
        # Clear existing columns
        for col in self.data_table["columns"]:
            self.data_table.heading(col, text="")
            self.data_table.column(col, width=0)
            
        # Set new column headings
        self.data_table.heading("id", text="ID")
        self.data_table.heading("name", text=translate("Team"))
        self.data_table.heading("league", text=translate("League"))
        self.data_table.heading("country", text=translate("Country"))
        
        # Set column widths
        self.data_table.column("id", width=50)
        self.data_table.column("name", width=200)
        self.data_table.column("league", width=200)
        self.data_table.column("country", width=150)
        
        # Get teams
        teams = self.db_manager.get_teams()
        
        # Add data to table
        for team in teams:
            try:
                self.data_table.insert(
                    "", "end",
                    values=(
                        team["id"],
                        team["name"],
                        team.get("league_name", ""),
                        team.get("country", "")
                    )
                )
            except Exception as e:
                logger.error(f"Error adding team to table: {str(e)}")
            
        # Update stats
        total = len(teams)
        
        self.total_card["value"].configure(text=str(total))
        self.completed_card["value"].configure(text="-")
        self.correct_card["value"].configure(text="-")
        self.accuracy_card["value"].configure(text="-")
        
    def _configure_leagues_table(self):
        """Configure and load leagues table"""
        # Configure columns
        self.data_table["columns"] = (
            "id", "name", "country", "logo", "season"
        )
        
        # Clear existing columns
        for col in self.data_table["columns"]:
            self.data_table.heading(col, text="")
            self.data_table.column(col, width=0)
            
        # Set new column headings
        self.data_table.heading("id", text="ID")
        self.data_table.heading("name", text=translate("League"))
        self.data_table.heading("country", text=translate("Country"))
        self.data_table.heading("logo", text=translate("Logo URL"))
        self.data_table.heading("season", text=translate("Season"))
        
        # Set column widths
        self.data_table.column("id", width=50)
        self.data_table.column("name", width=200)
        self.data_table.column("country", width=150)
        self.data_table.column("logo", width=300)
        self.data_table.column("season", width=100)
        
        # Get leagues
        leagues = self.db_manager.get_leagues()
        
        # Add data to table
        for league in leagues:
            self.data_table.insert(
                "", "end",
                values=(
                    league["id"],
                    league["name"],
                    league["country"],
                    league["logo"],
                    league["season"]
                )
            )
            
        # Update stats
        total = len(leagues)
        
        self.total_card["value"].configure(text=str(total))
        self.completed_card["value"].configure(text="-")
        self.correct_card["value"].configure(text="-")
        self.accuracy_card["value"].configure(text="-")
        
    def _configure_form_changes_table(self):
        """Configure and load form changes table"""
        # Configure columns
        self.data_table["columns"] = (
            "id", "team", "league", "date", "performance_diff", "fixture_id"
        )
        
        # Clear existing columns
        for col in self.data_table["columns"]:
            self.data_table.heading(col, text="")
            self.data_table.column(col, width=0)
            
        # Set new column headings
        self.data_table.heading("id", text="ID")
        self.data_table.heading("team", text=translate("Team"))
        self.data_table.heading("league", text=translate("League"))
        self.data_table.heading("date", text=translate("Date"))
        self.data_table.heading("performance_diff", text=translate("Perf. Diff"))
        self.data_table.heading("fixture_id", text=translate("Fixture ID"))
        
        # Set column widths
        self.data_table.column("id", width=50)
        self.data_table.column("team", width=200)
        self.data_table.column("league", width=200)
        self.data_table.column("date", width=150)
        self.data_table.column("performance_diff", width=100)
        self.data_table.column("fixture_id", width=100)
        
        # Get form changes
        form_changes = self.db_manager.get_form_changes()
        
        # Add data to table
        for change in form_changes:
            self.data_table.insert(
                "", "end",
                values=(
                    change["id"],
                    change["team_name"],
                    change["league_name"],
                    change["date"],
                    change["performance_diff"],
                    change["fixture_id"]
                )
            )
            
        # Update stats
        total = len(form_changes)
        
        self.total_card["value"].configure(text=str(total))
        self.completed_card["value"].configure(text="-")
        self.correct_card["value"].configure(text="-")
        self.accuracy_card["value"].configure(text="-")
        
    def _export_data(self):
        """Export current table data to CSV"""
        try:
            from tkinter import filedialog
            
            # Get file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title=f"{translate('Export')} {self.current_table.get()}"
            )
            
            if not file_path:
                return
                
            # Get data
            table = self.current_table.get()
            
            if table == "predictions":
                data = self.db_manager.get_predictions()
                if self.prediction_filter_var.get() == translate("Correct"):
                    data = [p for p in data if p["correct"] == 1]
                elif self.prediction_filter_var.get() == translate("Incorrect"):
                    data = [p for p in data if p["correct"] == 0 and p["status"] == "COMPLETED"]
                elif self.prediction_filter_var.get() == translate("WAITING"):
                    data = [p for p in data if p["status"] == "WAITING"]
                elif self.prediction_filter_var.get() == translate("COMPLETED"):
                    data = [p for p in data if p["status"] == "COMPLETED"]
            elif table == "fixtures":
                data = self.db_manager.get_fixtures()
            elif table == "teams":
                data = self.db_manager.get_teams()
            elif table == "leagues":
                data = self.db_manager.get_leagues()
            elif table == "form_changes":
                data = self.db_manager.get_form_changes()
                
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Export to CSV
            df.to_csv(file_path, index=False)
            
            # Update status
            self.status_label.configure(text=f"{translate('Exported to')} {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            self.status_label.configure(text=f"{translate('Error')}: {str(e)}")
            
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update UI elements with new theme
        self.refresh_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )
        self.export_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )

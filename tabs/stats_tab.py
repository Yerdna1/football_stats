import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager

logger = logging.getLogger(__name__)

class StatsTab:
    def __init__(self, parent, db_manager: DatabaseManager, settings_manager: SettingsManager = None):
        self.parent = parent
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        
        # Create UI elements
        self._create_ui()
        
        # Load initial data
        self._load_data()
        
    def _create_ui(self):
        """Create the stats tab UI elements"""
        # Main container with padding
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header section
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.pack(fill="x", padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Prediction Statistics", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=10)
        
        # Configure notebook style for larger font
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=('Helvetica', 36))  # Increased font size from 28 to 36
        style.configure("TNotebook", font=('Helvetica', 36))  # Add font configuration for the notebook itself
        
        # Create notebook for stats categories
        self.notebook = ttk.Notebook(self.main_frame, style="TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Summary Tab
        self.summary_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        
        # Predictions Tab
        self.predictions_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.predictions_frame, text="Predictions")
        
        # Charts Tab
        self.charts_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.charts_frame, text="Charts")
        
        # Create summary widgets
        self._create_summary_widgets()
        
        # Create predictions table
        self._create_predictions_table()
        
        # Create charts
        self._create_charts()
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.main_frame,
            text="Refresh Statistics",
            command=self._load_data,
            width=150,
            height=32,
            corner_radius=8,
            border_width=0
        )
        self.refresh_button.pack(pady=10)
        
    def _create_summary_widgets(self):
        """Create summary widgets"""
        # Create a frame for summary cards
        self.summary_cards_frame = ctk.CTkFrame(self.summary_frame)
        self.summary_cards_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create grid layout for cards
        self.summary_cards_frame.columnconfigure(0, weight=1)
        self.summary_cards_frame.columnconfigure(1, weight=1)
        self.summary_cards_frame.rowconfigure(0, weight=1)
        self.summary_cards_frame.rowconfigure(1, weight=1)
        
        # Total Predictions Card
        self.total_card = self._create_stat_card(
            self.summary_cards_frame,
            "Total Predictions",
            "0",
            0, 0
        )
        
        # Completed Predictions Card
        self.completed_card = self._create_stat_card(
            self.summary_cards_frame,
            "Completed Predictions",
            "0",
            0, 1
        )
        
        # Correct Predictions Card
        self.correct_card = self._create_stat_card(
            self.summary_cards_frame,
            "Correct Predictions",
            "0",
            1, 0
        )
        
        # Accuracy Card
        self.accuracy_card = self._create_stat_card(
            self.summary_cards_frame,
            "Accuracy",
            "0%",
            1, 1
        )
        
    def _create_stat_card(self, parent, title, value, row, col):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24)
        )
        value_label.pack(pady=(10, 20))
        
        return {
            "frame": card,
            "title": title_label,
            "value": value_label
        }
        
    def _create_predictions_table(self):
        """Create predictions table"""
        # Create frame for table
        self.predictions_table_frame = ctk.CTkFrame(self.predictions_frame)
        self.predictions_table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create filter controls
        self.filter_frame = ctk.CTkFrame(self.predictions_table_frame)
        self.filter_frame.pack(fill="x", padx=10, pady=10)
        
        # Status filter
        self.status_label = ctk.CTkLabel(
            self.filter_frame,
            text="Status:",
            font=ctk.CTkFont(size=18)
        )
        self.status_label.pack(side="left", padx=(10, 5))
        
        self.status_var = tk.StringVar(value="All")
        
        self.status_option = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["All", "WAITING", "COMPLETED"],
            variable=self.status_var,
            command=self._filter_predictions,
            font=ctk.CTkFont(size=18)
        )
        self.status_option.pack(side="left", padx=5)
        
        # Result filter
        self.result_label = ctk.CTkLabel(
            self.filter_frame,
            text="Result:",
            font=ctk.CTkFont(size=18)
        )
        self.result_label.pack(side="left", padx=(20, 5))
        
        self.result_var = tk.StringVar(value="All")
        
        self.result_option = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["All", "Correct", "Incorrect"],
            variable=self.result_var,
            command=self._filter_predictions,
            font=ctk.CTkFont(size=18)
        )
        self.result_option.pack(side="left", padx=5)
        
        # Configure style for larger font
        style = ttk.Style()
        # Get font size from settings or use default if settings_manager is not available
        font_size = 50  # Default font size
        if self.settings_manager:
            font_size = self.settings_manager.get_font_size()
            
        style.configure("Treeview", font=('Helvetica', font_size))  # Use font size from settings
        style.configure("Treeview.Heading", font=('Helvetica', 28, 'bold'))  # Increase header font size
        style.configure("Treeview", rowheight=max(60, int(font_size * 1.2)))  # Adjust row height based on font size
        
        # Create treeview
        self.predictions_table = ttk.Treeview(
            self.predictions_table_frame,
            columns=(
                "team", "league", "opponent", "date", "prediction",
                "performance_diff", "status", "result", "correct"
            ),
            show="headings"
        )
        
        # Configure columns
        self.predictions_table.heading("team", text="Team")
        self.predictions_table.heading("league", text="League")
        self.predictions_table.heading("opponent", text="Opponent")
        self.predictions_table.heading("date", text="Date")
        self.predictions_table.heading("prediction", text="Prediction")
        self.predictions_table.heading("performance_diff", text="Perf. Diff")
        self.predictions_table.heading("status", text="Status")
        self.predictions_table.heading("result", text="Result")
        self.predictions_table.heading("correct", text="Correct")
        
        self.predictions_table.column("team", width=150)
        self.predictions_table.column("league", width=150)
        self.predictions_table.column("opponent", width=150)
        self.predictions_table.column("date", width=100)
        self.predictions_table.column("prediction", width=100)
        self.predictions_table.column("performance_diff", width=80)
        self.predictions_table.column("status", width=80)
        self.predictions_table.column("result", width=80)
        self.predictions_table.column("correct", width=80)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(
            self.predictions_table_frame,
            orient="vertical",
            command=self.predictions_table.yview
        )
        hsb = ttk.Scrollbar(
            self.predictions_table_frame,
            orient="horizontal",
            command=self.predictions_table.xview
        )
        self.predictions_table.configure(
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        # Grid layout
        self.predictions_table.pack(fill="both", expand=True, padx=10, pady=10)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        
        # Configure tags
        self.predictions_table.tag_configure("correct", foreground="green")
        self.predictions_table.tag_configure("incorrect", foreground="red")
        self.predictions_table.tag_configure("waiting", foreground="blue")
        
    def _create_charts(self):
        """Create charts"""
        # Create frame for charts
        self.charts_container = ctk.CTkFrame(self.charts_frame)
        self.charts_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create grid layout for charts
        self.charts_container.columnconfigure(0, weight=1)
        self.charts_container.columnconfigure(1, weight=1)
        self.charts_container.rowconfigure(0, weight=1)
        self.charts_container.rowconfigure(1, weight=1)
        
        # Accuracy Pie Chart
        self.accuracy_chart_frame = ctk.CTkFrame(self.charts_container)
        self.accuracy_chart_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.accuracy_chart_label = ctk.CTkLabel(
            self.accuracy_chart_frame,
            text="Prediction Accuracy",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.accuracy_chart_label.pack(pady=10)
        
        # Create matplotlib figure for accuracy chart
        self.accuracy_fig = plt.Figure(figsize=(4, 3), dpi=100)
        self.accuracy_canvas = FigureCanvasTkAgg(self.accuracy_fig, master=self.accuracy_chart_frame)
        self.accuracy_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Predictions by Level Chart
        self.level_chart_frame = ctk.CTkFrame(self.charts_container)
        self.level_chart_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.level_chart_label = ctk.CTkLabel(
            self.level_chart_frame,
            text="Predictions by Level",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.level_chart_label.pack(pady=10)
        
        # Create matplotlib figure for level chart
        self.level_fig = plt.Figure(figsize=(4, 3), dpi=100)
        self.level_canvas = FigureCanvasTkAgg(self.level_fig, master=self.level_chart_frame)
        self.level_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Accuracy Over Time Chart
        self.time_chart_frame = ctk.CTkFrame(self.charts_container)
        self.time_chart_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.time_chart_label = ctk.CTkLabel(
            self.time_chart_frame,
            text="Accuracy Over Time",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.time_chart_label.pack(pady=10)
        
        # Create matplotlib figure for time chart
        self.time_fig = plt.Figure(figsize=(8, 3), dpi=100)
        self.time_canvas = FigureCanvasTkAgg(self.time_fig, master=self.time_chart_frame)
        self.time_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
    def _load_data(self):
        """Load data from database"""
        try:
            # Get prediction stats
            stats = self.db_manager.get_prediction_stats()
            
            # Update summary cards
            self.total_card["value"].configure(text=str(stats["total"]))
            self.completed_card["value"].configure(text=str(stats["completed"]))
            self.correct_card["value"].configure(text=str(stats["correct"]))
            self.accuracy_card["value"].configure(text=f"{stats['accuracy']:.1f}%")
            
            # Get predictions
            self.predictions = self.db_manager.get_predictions()
            
            # Update predictions table
            self._update_predictions_table()
            
            # Update charts
            self._update_charts(stats)
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            
    def _update_predictions_table(self):
        """Update predictions table with filtered data"""
        # Clear table
        for item in self.predictions_table.get_children():
            self.predictions_table.delete(item)
            
        # Apply filters
        status_filter = self.status_var.get()
        result_filter = self.result_var.get()
        
        filtered_predictions = self.predictions
        
        if status_filter != "All":
            filtered_predictions = [p for p in filtered_predictions if p["status"] == status_filter]
            
        if result_filter != "All":
            if result_filter == "Correct":
                filtered_predictions = [p for p in filtered_predictions if p["correct"] == 1]
            elif result_filter == "Incorrect":
                filtered_predictions = [p for p in filtered_predictions if p["correct"] == 0 and p["status"] == "COMPLETED"]
        
        # Add data to table
        for prediction in filtered_predictions:
            # Determine tag
            if prediction["status"] == "WAITING":
                tag = "waiting"
            elif prediction["correct"] == 1:
                tag = "correct"
            else:
                tag = "incorrect"
                
            # Add row
            self.predictions_table.insert(
                "", "end",
                values=(
                    prediction["team_name"],
                    prediction["league_name"],
                    prediction["opponent_name"],
                    prediction["match_date"],
                    prediction["prediction"],
                    prediction["performance_diff"],
                    prediction["status"],
                    prediction["result"] or "",
                    "Yes" if prediction["correct"] == 1 else "No" if prediction["status"] == "COMPLETED" else ""
                ),
                tags=(tag,)
            )
            
    def _filter_predictions(self, _=None):
        """Filter predictions based on selected filters"""
        self._update_predictions_table()
        
    def _update_charts(self, stats):
        """Update charts with stats data"""
        # Accuracy Pie Chart
        self.accuracy_fig.clear()
        ax = self.accuracy_fig.add_subplot(111)
        
        if stats["completed"] > 0:
            correct = stats["correct"]
            incorrect = stats["completed"] - correct
            
            ax.pie(
                [correct, incorrect],
                labels=["Correct", "Incorrect"],
                autopct='%1.1f%%',
                startangle=90,
                colors=['#4CAF50', '#F44336']
            )
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, "No completed predictions", ha='center', va='center')
            ax.axis('off')
            
        self.accuracy_canvas.draw()
        
        # Predictions by Level Chart
        self.level_fig.clear()
        ax = self.level_fig.add_subplot(111)
        
        if stats["total"] > 0:
            levels = stats["by_level"]["counts"]
            level_labels = [f"Level {level}" for level in sorted(levels.keys())]
            level_counts = [levels[level] for level in sorted(levels.keys())]
            
            ax.bar(level_labels, level_counts, color='#3498DB')
            ax.set_ylabel('Count')
            ax.set_title('Predictions by Level')
            
            # Add accuracy as text on bars
            for i, level in enumerate(sorted(levels.keys())):
                accuracy = stats["by_level"]["accuracy"].get(level, 0)
                if accuracy > 0:
                    ax.text(
                        i, level_counts[i] + 0.1,
                        f"{accuracy:.1f}%",
                        ha='center', va='bottom'
                    )
        else:
            ax.text(0.5, 0.5, "No predictions", ha='center', va='center')
            ax.axis('off')
            
        self.level_canvas.draw()
        
        # Accuracy Over Time Chart (placeholder)
        self.time_fig.clear()
        ax = self.time_fig.add_subplot(111)
        
        # This would require more complex data processing
        # For now, just show a placeholder
        ax.text(0.5, 0.5, "Accuracy Over Time (Coming Soon)", ha='center', va='center')
        ax.axis('off')
            
        self.time_canvas.draw()
        
    def update_settings(self):
        """Update settings when they are changed"""
        # Update font size for predictions table
        if self.settings_manager:
            font_size = self.settings_manager.get_font_size()
            style = ttk.Style()
            style.configure("Treeview", font=('Helvetica', font_size))
            style.configure("Treeview", rowheight=max(60, int(font_size * 1.2)))
        
        # Refresh data
        self._load_data()

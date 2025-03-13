import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable
import queue
import threading
import time

from tabs.base_tab import BaseTab
from modules.api_client import FootballAPI
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.translations import translate

# Create a custom logger for this tab
logger = logging.getLogger(__name__)

# Create a queue for log messages
log_queue = queue.Queue()

# Create a custom handler that puts logs into the queue
class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        
    def emit(self, record):
        self.log_queue.put(record)

# Add the queue handler to the root logger
root_logger = logging.getLogger()
queue_handler = QueueHandler(log_queue)
queue_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
queue_handler.setFormatter(formatter)
root_logger.addHandler(queue_handler)

class LogsTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Create UI elements
        self._create_ui()
        
        # Start log consumer thread
        self.running = True
        self.log_thread = threading.Thread(target=self._consume_logs)
        self.log_thread.daemon = True
        self.log_thread.start()
        
    def _create_ui(self):
        """Create the logs tab UI elements"""
        # Title
        self._create_title("Aplikačné logy")
        
        # Create control frame
        self.control_frame = ctk.CTkFrame(self.content_frame)
        self.control_frame.pack(fill="x", padx=10, pady=10)
        
        # Log level filter
        self.level_label = ctk.CTkLabel(
            self.control_frame,
            text=translate("Log Level:"),
            font=ctk.CTkFont(size=18)
        )
        self.level_label.pack(side="left", padx=(10, 5))
        
        self.level_var = tk.StringVar(value="INFO")
        
        self.level_option = ctk.CTkOptionMenu(
            self.control_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            variable=self.level_var,
            command=self._set_log_level,
            font=ctk.CTkFont(size=18)
        )
        self.level_option.pack(side="left", padx=5)
        
        # Clear logs button
        self.clear_button = self._create_button(
            self.control_frame,
            "Clear Logs",
            self._clear_logs,
            width=150,
            height=32,
            tooltip_text="Clear all log messages from the display"
        )
        self.clear_button.pack(side="right", padx=10)
        
        # Create log text area
        self.log_frame = ctk.CTkFrame(self.content_frame)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure style for larger font
        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 18))
        style.configure("Treeview.Heading", font=('Helvetica', 18, 'bold'))
        style.configure("Treeview", rowheight=30)
        
        # Create treeview for logs
        self.log_tree = ttk.Treeview(
            self.log_frame,
            columns=("time", "level", "source", "message"),
            show="headings",
            height=20
        )
        
        # Configure columns
        self.log_tree.heading("time", text=translate("Time"))
        self.log_tree.heading("level", text=translate("Level"))
        self.log_tree.heading("source", text=translate("Source"))
        self.log_tree.heading("message", text=translate("Message"))
        
        self.log_tree.column("time", width=150)
        self.log_tree.column("level", width=80)
        self.log_tree.column("source", width=150)
        self.log_tree.column("message", width=500)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_tree.yview)
        hsb = ttk.Scrollbar(self.log_frame, orient="horizontal", command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.log_tree.grid(column=0, row=0, sticky="nsew")
        vsb.grid(column=1, row=0, sticky="ns")
        hsb.grid(column=0, row=1, sticky="ew")
        
        # Configure grid weights
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)
        
        # Configure tags for different log levels
        self.log_tree.tag_configure("DEBUG", foreground="gray")
        self.log_tree.tag_configure("INFO", foreground="black")
        self.log_tree.tag_configure("WARNING", foreground="orange")
        self.log_tree.tag_configure("ERROR", foreground="red")
        self.log_tree.tag_configure("CRITICAL", foreground="red", background="yellow")
        
        # Add a status label in the footer
        self.status_label = ctk.CTkLabel(
            self.footer_frame,
            text=translate("Logging started"),
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(side="left", padx=10)
        
        # Log a test message
        logger.info("Logs tab initialized")
        
    def _set_log_level(self, level):
        """Set the log level filter"""
        # Update the queue handler level
        queue_handler.setLevel(getattr(logging, level))
        
        # Update status
        self.status_label.configure(text=f"{translate('Log level set to')} {level}")
        
        # Log the change
        logger.info(f"Log level changed to {level}")
        
    def _clear_logs(self):
        """Clear all logs from the display"""
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
            
        # Update status
        self.status_label.configure(text=translate("Logs cleared"))
        
        # Log the action
        logger.info("Logs cleared")
        
    def _consume_logs(self):
        """Consume logs from the queue and add them to the treeview"""
        while self.running:
            try:
                # Check if there are any logs in the queue
                if not log_queue.empty():
                    # Get the log record
                    record = log_queue.get(block=False)
                    
                    # Format the time
                    time_str = time.strftime("%H:%M:%S", time.localtime(record.created))
                    
                    try:
                        # Add to treeview - use try/except to handle case where main thread is not ready
                        self.parent.after(0, self._add_log_to_tree, time_str, record)
                    except RuntimeError:
                        # If main thread is not in main loop yet, just discard the log
                        pass
                    
                # Sleep a bit to avoid high CPU usage
                time.sleep(0.1)
            except queue.Empty:
                # Queue is empty, just continue
                time.sleep(0.1)
            except Exception as e:
                # Catch and print other exceptions but don't crash the thread
                print(f"Error in log consumer: {str(e)}")
                time.sleep(1.0)  # Sleep longer on error to avoid spamming
                
    def _add_log_to_tree(self, time_str, record):
        """Add a log record to the treeview (called from main thread)"""
        try:
            # Insert at the beginning
            self.log_tree.insert(
                "", 0,
                values=(
                    time_str,
                    record.levelname,
                    record.name,
                    record.getMessage()
                ),
                tags=(record.levelname,)
            )
            
            # Update status
            self.status_label.configure(text=f"{translate('Last log')}: {time_str}")
        except Exception as e:
            print(f"Error adding log to tree: {e}")
            
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update UI elements with new theme
        self.clear_button.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )
        
    def on_close(self):
        """Called when the tab is closed or the application is exiting"""
        self.running = False
        if self.log_thread.is_alive():
            self.log_thread.join(1.0)  # Wait for thread to finish with timeout

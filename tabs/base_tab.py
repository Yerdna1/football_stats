import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable

from modules.api_client import FootballAPI
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.translations import translate

logger = logging.getLogger(__name__)

class BaseTab:
    """Base class for all tabs with common functionality"""
    
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        self.parent = parent
        self.api = api
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        
        # Get theme colors
        self.theme = self.settings_manager.get_theme()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create header frame
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.pack(fill="x", padx=10, pady=10)
        
        # Create content frame
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create footer frame
        self.footer_frame = ctk.CTkFrame(self.main_frame)
        self.footer_frame.pack(fill="x", padx=10, pady=10)
        
        # Create loading indicator (hidden by default)
        self.loading_indicator_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color=self.theme["primary"],
            width=300,
            height=80
        )
        self.loading_indicator_label = ctk.CTkLabel(
            self.loading_indicator_frame,
            text=translate("Loading..."),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        self.loading_indicator_label.pack(pady=10, padx=20)
        # Don't pack the frame initially - it will be shown when needed
        
    def _create_table(self, parent, columns, height=400):
        """Create a table with the given columns and increased font size"""
        # Create frame for table
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure style for larger font
        style = ttk.Style()
        font_size = self.settings_manager.get_font_size()  # Get font size from settings
        style.configure("Treeview", font=('Helvetica', font_size))  # Use font size from settings
        style.configure("Treeview.Heading", font=('Helvetica', 28, 'bold'))  # Increase header font size
        style.configure("Treeview", rowheight=max(60, int(font_size * 1.2)))  # Adjust row height based on font size
        
        # Create treeview
        table = ttk.Treeview(frame, columns=[f"col{i}" for i in range(len(columns))], show="headings", height=height)
        
        # Configure columns
        for i, col in enumerate(columns):
            table.heading(f"col{i}", text=col["text"])
            table.column(f"col{i}", width=col["width"], anchor="center")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=table.xview)
        table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        table.grid(column=0, row=0, sticky="nsew")
        vsb.grid(column=1, row=0, sticky="ns")
        hsb.grid(column=0, row=1, sticky="ew")
        
        # Configure grid weights
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        return table
        
    def _create_title(self, text, font_size=24):
        """Create a title label"""
        title_label = ctk.CTkLabel(
            self.header_frame, 
            text=translate(text), 
            font=ctk.CTkFont(size=font_size, weight="bold")
        )
        title_label.pack(pady=10)
        return title_label
        
    def _create_button(self, parent, text, command, width=150, height=32, tooltip_text=None):
        """Create a styled button with optional tooltip"""
        button = ctk.CTkButton(
            parent,
            text=translate(text),
            command=command,
            width=width,
            height=height,
            corner_radius=8,
            border_width=0,
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"],
            text_color="white",
            font=ctk.CTkFont(size=24)
        )
        
        # Add tooltip if provided
        if tooltip_text:
            self._add_tooltip(button, translate(tooltip_text))
        else:
            # Add default tooltip based on button text
            default_tooltip = self._get_default_tooltip(text)
            if default_tooltip:
                self._add_tooltip(button, translate(default_tooltip))
                
        return button
        
    def _add_tooltip(self, widget, text):
        """Add tooltip to widget"""
        tooltip = ToolTip(widget, text)
        return tooltip
        
    def _get_default_tooltip(self, button_text):
        """Get default tooltip text based on button text"""
        tooltips = {
            "Refresh Data": "Obnoviť dáta z databázy a API",
            "Export Data": "Exportovať dáta do súboru CSV",
            "Save to Database": "Uložiť aktuálne dáta do databázy",
            "Check Results": "Skontrolovať výsledky predchádzajúcich predpovedí",
            "Refresh Statistics": "Obnoviť štatistiky a grafy",
            "Export to CSV": "Exportovať dáta do súboru CSV",
            "Save Settings": "Uložiť aktuálne nastavenia",
            "Reset to Defaults": "Obnoviť predvolené nastavenia",
            "Select All": "Vybrať všetky položky v zozname",
            "Select None": "Zrušiť výber všetkých položiek v zozname",
            "Fetch Data": "Načítať dáta z API",
            "Apply Filter": "Použiť vybraný filter na dáta",
            "Clear Filter": "Vyčistiť všetky filtre",
            "Add": "Pridať novú položku",
            "Edit": "Upraviť vybranú položku",
            "Delete": "Odstrániť vybranú položku",
            "Search": "Vyhľadať podľa zadaných kritérií"
        }
        
        return tooltips.get(button_text)
        
    def show_loading_indicator(self):
        """Show the loading indicator overlay"""
        # Pack the loading indicator in the center of the content frame
        self.loading_indicator_frame.pack(in_=self.content_frame, expand=True, padx=20, pady=20)
        self.loading_indicator_frame.lift()  # Bring to front
        self._animate_loading_indicator(0)
        
    def hide_loading_indicator(self):
        """Hide the loading indicator overlay"""
        self.loading_indicator_frame.pack_forget()
        
    def _animate_loading_indicator(self, count):
        """Animate the loading indicator text"""
        if self.loading_indicator_frame.winfo_ismapped():
            dots = "." * (count % 4)
            self.loading_indicator_label.configure(text=f"{translate('Loading')}{dots}")
            self.parent.after(300, lambda: self._animate_loading_indicator(count + 1))
    
    def _show_loading_animation(self, button, original_text="Refresh Data"):
        """Show loading animation on a button"""
        button.configure(text=translate("Loading..."), state="disabled")
        self._animate_loading(button, 0, original_text)
        
    def _animate_loading(self, button, count, original_text):
        """Animate the loading text"""
        if button.cget("text").startswith(translate("Loading")):
            dots = "." * (count % 4)
            button.configure(text=f"{translate('Loading')}{dots}")
            self.parent.after(300, lambda: self._animate_loading(button, count + 1, original_text))
        else:
            button.configure(text=translate(original_text), state="normal")
            
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme
        self.theme = self.settings_manager.get_theme()
        
        # Update font size for tables
        font_size = self.settings_manager.get_font_size()
        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', font_size))
        style.configure("Treeview", rowheight=max(60, int(font_size * 1.2)))
        
        # This method should be overridden by subclasses to update specific UI elements
        pass

class ToolTip:
    """Custom tooltip implementation"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
        
    def on_enter(self, event=None):
        """Show tooltip when mouse enters widget"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip label
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Helvetica", 12)
        )
        label.pack(padx=2, pady=2)
        
    def on_leave(self, event=None):
        """Hide tooltip when mouse leaves widget"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

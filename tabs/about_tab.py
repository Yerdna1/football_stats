import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Any, Optional, Callable
import webbrowser

from tabs.base_tab import BaseTab
from modules.api_client import FootballAPI
from modules.db_manager import DatabaseManager
from modules.settings_manager import SettingsManager
from modules.translations import translate

logger = logging.getLogger(__name__)

class AboutTab(BaseTab):
    def __init__(self, parent, api: FootballAPI, db_manager: DatabaseManager, settings_manager: SettingsManager):
        super().__init__(parent, api, db_manager, settings_manager)
        
        # Create UI elements
        self._create_ui()
        
    def _create_ui(self):
        """Create the about tab UI elements"""
        # Title
        self._create_title("O aplikácii")
        
        # Create scrollable frame for content
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Application name and version
        self.app_name_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Analyzátor futbalových štatistík",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.app_name_label.pack(pady=(0, 10))
        
        self.version_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Verzia 2.0",
            font=ctk.CTkFont(size=16)
        )
        self.version_label.pack(pady=(0, 20))
        
        # Description
        self.description_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Komplexný nástroj na analýzu futbalových štatistík a predpovedanie výsledkov zápasov.",
            font=ctk.CTkFont(size=16),
            wraplength=800
        )
        self.description_label.pack(pady=(0, 20))
        
        # Features section
        self._create_section_title("Hlavné funkcie")
        
        # Modern UI
        self._create_feature_section(
            "Moderné používateľské rozhranie",
            [
                "Čisté, responzívne rozhranie s 11 funkčnými záložkami",
                "Podpora tém s viacerými farebnými schémami (modrá, zelená, fialová, červená, tmavá)",
                "Veľmi veľké písmo (18pt) vo všetkých tabuľkách pre lepšiu čitateľnosť",
                "Extra veľké písmo (28pt) v záložkách pre lepšiu čitateľnosť",
                "Zvýšená výška riadkov (40px) pre lepšiu interakciu",
                "Animované tlačidlá a interaktívne prvky",
                "Kompletný preklad do slovenčiny"
            ]
        )
        
        # Improved layout
        self._create_feature_section(
            "Vylepšené rozloženie",
            [
                "Ligy v nastaveniach rozdelené do 6 stĺpcov pre lepší prehľad",
                "Záložky s väčším písmom pre lepšiu čitateľnosť",
                "Optimalizované rozloženie pre lepšiu použiteľnosť",
                "Zobrazenie počtu vybraných líg (napr. \"Vybrané: 45/60\")",
                "Tlačidlá pre rýchly výber všetkých alebo žiadnej ligy"
            ]
        )
        
        # Tabs structure
        self._create_feature_section(
            "Kompletná štruktúra záložiek",
            [
                "Série bez výhry: Sledovanie tímov na sériách bez výhry/prehry",
                "Analýza tímu: Podrobné štatistiky a výkonnosť tímu",
                "Ďalšie kolo: Nadchádzajúce zápasy s predpoveďami",
                "Štatistiky ligy: Tabuľky a štatistiky ligy",
                "Analýza formy: Analýza formy tímu s rozdielmi výkonnosti",
                "Zber dát: Funkcionalita zberu a exportu dát",
                "Firebase analýza: Analýza zmien formy s ukladaním do databázy",
                "Štatistiky: Štatistiky predpovedí a vizualizácia",
                "Zobrazenie databázy: Prehliadanie a filtrovanie záznamov v databáze",
                "O aplikácii: Informácie o aplikácii a jej funkciách",
                "Nastavenia: Komplexné nastavenia aplikácie"
            ]
        )
        
        # Database integration
        self._create_feature_section(
            "Integrácia databázy",
            [
                "SQLite databáza na ukladanie predpovedí, zápasov, tímov a ďalších údajov",
                "Validácia minulých predpovedí oproti výsledkom",
                "Výpočet štatistík presnosti predpovedí",
                "Funkcionalita exportu predpovedí do CSV",
                "Záložka Zobrazenie databázy pre prehliadanie a filtrovanie záznamov v databáze",
                "Zobrazenie všetkých tabuliek (predpovede, zápasy, tímy, ligy, zmeny formy)",
                "Filtrovanie predpovedí podľa stavu (čakajúce, dokončené) a výsledku (správne, nesprávne)",
                "Export vybraných dát do CSV súboru",
                "Štatistiky pre každú tabuľku"
            ]
        )
        
        # Customizable settings
        self._create_feature_section(
            "Prispôsobiteľné nastavenia",
            [
                "Nastavenia vzhľadu (svetlý/tmavý režim, farebné témy)",
                "Nastavenia dát (dĺžka formy, hodnoty prahov)",
                "Výber ligy so zoskupením podľa krajiny",
                "Konfigurácia prahov predpovedí"
            ]
        )
        
        # Performance prediction system
        self._create_feature_section(
            "Systém predpovedí výkonnosti",
            [
                "Dvojúrovňový systém predpovedí (VÝHRA/PREHRA a VEĽKÁ VÝHRA/VEĽKÁ PREHRA)",
                "Konfigurovateľné prahy pre predpovede",
                "Sledovanie presnosti predpovedí",
                "Validácia predpovedí oproti skutočným výsledkom",
                "Štatistiky úspešnosti predpovedí"
            ]
        )
        
        # Extended league support
        self._create_feature_section(
            "Rozšírená podpora líg",
            [
                "Pridaných viac ako 50 líg z celého sveta",
                "Ligy rozdelené podľa krajín a kontinentov",
                "Podpora pre najvyššie súťaže, druhé ligy a pohárové súťaže",
                "Medzinárodné súťaže (Liga majstrov, Európska liga, atď.)"
            ]
        )
        
        # Demo data
        self._create_feature_section(
            "Demo dáta",
            [
                "Pridaná podpora pre demo dáta",
                "Automatické generovanie zápasov, tímov a predpovedí",
                "Možnosť testovať funkcionalitu bez potreby API kľúča",
                "Realistické dáta pre testovanie a demonštráciu"
            ]
        )
        
        # Database storage section
        self._create_section_title("Ukladanie dát do databázy")
        
        self._create_feature_section(
            "Typy ukladaných dát",
            [
                "Predpovede - Ukladá predpovede výsledkov zápasov na základe rozdielov vo výkonnosti tímov",
                "Zápasy - Informácie o nadchádzajúcich a minulých zápasoch",
                "Tímy - Informácie o tímoch",
                "Ligy - Informácie o ligách",
                "Zmeny formy - Sledovanie zmien vo forme tímov"
            ]
        )
        
        # API data section
        self._create_section_title("O dátach API")
        
        self.api_description = ctk.CTkLabel(
            self.scroll_frame,
            text="Upozornenia ako \"No standings for league X\" sú očakávané, pretože používame zástupný API kľúč. Pre použitie aplikácie s reálnymi dátami je potrebné nahradiť zástupný API kľúč v súbore config.py:",
            font=ctk.CTkFont(size=14),
            wraplength=800,
            justify="left"
        )
        self.api_description.pack(anchor="w", pady=(0, 10))
        
        self._create_feature_section(
            "Získanie API kľúča",
            [
                "Prejdite na https://www.api-football.com/ a zaregistrujte sa",
                "Prihláste sa na ich bezplatný alebo platený plán",
                "Získajte svoj API kľúč z vášho ovládacieho panela"
            ]
        )
        
        self._create_feature_section(
            "Aktualizácia API kľúča",
            [
                "Otvorte súbor modules/config.py",
                "Nájdite riadok: API_KEY = \"placeholder_key\"",
                "Nahraďte ho: API_KEY = \"váš_skutočný_api_kľúč\"",
                "Reštartujte aplikáciu"
            ]
        )
        
        # Contact information
        self._create_section_title("Kontakt")
        
        self.contact_info = ctk.CTkLabel(
            self.scroll_frame,
            text="Andrej Galad\nEmail: marekzm@azet.sk",
            font=ctk.CTkFont(size=16),
            justify="left"
        )
        self.contact_info.pack(anchor="w", pady=(0, 20))
        
        # Footer
        self.footer_label = ctk.CTkLabel(
            self.scroll_frame,
            text="© 2025 Analyzátor futbalových štatistík. Všetky práva vyhradené.",
            font=ctk.CTkFont(size=12)
        )
        self.footer_label.pack(pady=(30, 0))
        
        # API link
        self.api_link = ctk.CTkButton(
            self.scroll_frame,
            text="Navštíviť API-Football",
            command=lambda: webbrowser.open("https://www.api-football.com/"),
            width=200,
            height=32,
            corner_radius=8,
            border_width=0,
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"],
            text_color="white"
        )
        self.api_link.pack(pady=(20, 0))
        
        # Add tooltip to API link button
        self._add_tooltip(self.api_link, "Kliknite pre návštevu stránky API-Football, kde môžete získať API kľúč")
        
    def _create_section_title(self, title):
        """Create a section title"""
        section_title = ctk.CTkLabel(
            self.scroll_frame,
            text=title,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        section_title.pack(anchor="w", pady=(20, 10))
        
        # Add separator
        separator = ttk.Separator(self.scroll_frame, orient="horizontal")
        separator.pack(fill="x", pady=(0, 10))
        
    def _create_feature_section(self, title, features):
        """Create a feature section with title and bullet points"""
        # Title
        feature_title = ctk.CTkLabel(
            self.scroll_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        feature_title.pack(anchor="w", pady=(10, 5))
        
        # Features
        for feature in features:
            feature_item = ctk.CTkLabel(
                self.scroll_frame,
                text=f"• {feature}",
                font=ctk.CTkFont(size=14),
                wraplength=800,
                justify="left"
            )
            feature_item.pack(anchor="w", padx=(20, 0), pady=2)
            
    def _add_tooltip(self, widget, text):
        """Add tooltip to widget"""
        # Use the BaseTab's _add_tooltip method
        return super()._add_tooltip(widget, text)
        
    def update_settings(self):
        """Update settings from settings manager"""
        # Update theme from parent class
        super().update_settings()
        
        # Update UI elements with new theme
        self.api_link.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme["primary"]
        )

"""
Translation module for the Football Statistics Analyzer application.
Contains translations from English to Slovak.
"""

# Dictionary mapping English terms to Slovak translations
EN_TO_SK = {
    # Tab names
    "Winless Streaks": "Série bez výhry",
    "Team Analysis": "Analýza tímu",
    "Next Round": "Ďalšie kolo",
    "League Stats": "Štatistiky ligy",
    "Form Analysis": "Analýza formy",
    "Data Collection": "Zber dát",
    "Firebase Analysis": "Firebase analýza",
    "Statistics": "Štatistiky",
    "Database View": "Zobrazenie databázy",
    "About": "O aplikácii",
    "Settings": "Nastavenia",
    
    # Settings tab
    "Appearance": "Vzhľad",
    "Data Settings": "Nastavenia dát",
    "Leagues": "Ligy",
    "Predictions": "Predpovede",
    
    # Appearance settings
    "Appearance Mode:": "Režim vzhľadu:",
    "System": "Systémový",
    "Light": "Svetlý",
    "Dark": "Tmavý",
    "Color Theme:": "Farebná téma:",
    "blue": "modrá",
    "green": "zelená",
    "purple": "fialová",
    "red": "červená",
    "dark": "tmavá",
    
    # Data settings
    "Form Analysis Length:": "Dĺžka analýzy formy:",
    "Current value:": "Aktuálna hodnota:",
    "matches": "zápasov",
    "Performance Difference Threshold:": "Prah rozdielu výkonnosti:",
    "Auto Refresh Data:": "Automatické obnovenie dát:",
    "Enable Auto Refresh": "Povoliť automatické obnovenie",
    "Refresh Interval (minutes):": "Interval obnovenia (minúty):",
    "minutes": "minút",
    
    # Leagues settings
    "Select Leagues to Analyze:": "Vyberte ligy na analýzu:",
    "Selected": "Vybrané",
    "Select All": "Vybrať všetky",
    "Select None": "Zrušiť výber",
    
    # Predictions settings
    "Prediction Thresholds:": "Prahy predpovedí:",
    "Level 1 (Win/Loss):": "Úroveň 1 (Výhra/Prehra):",
    "Level 2 (Big Win/Big Loss):": "Úroveň 2 (Veľká výhra/Veľká prehra):",
    "Export Predictions:": "Export predpovedí:",
    "Export to CSV": "Export do CSV",
    
    # Buttons
    "Save Settings": "Uložiť nastavenia",
    "Reset to Defaults": "Obnoviť predvolené",
    "Refresh Data": "Obnoviť dáta",
    "Export Data": "Exportovať dáta",
    "Save to Database": "Uložiť do databázy",
    "Check Results": "Skontrolovať výsledky",
    "Refresh Statistics": "Obnoviť štatistiky",
    
    # Form tab
    "Form Changes Analysis": "Analýza zmien formy",
    "Select League:": "Vyberte ligu:",
    "Threshold:": "Prah:",
    
    # Tables
    "Team": "Tím",
    "League": "Liga",
    "Perf. Diff": "Rozdiel výk.",
    "Prediction": "Predpoveď",
    "Opponent": "Súper",
    "Date": "Dátum",
    "Time": "Čas",
    "Venue": "Miesto",
    "Status": "Stav",
    "Result": "Výsledok",
    "Correct": "Správne",
    "Home": "Domáci",
    "Away": "Hostia",
    "Score": "Skóre",
    "Pos": "Poz",
    "P": "Z",
    "W": "V",
    "D": "R",
    "L": "P",
    "GF": "GS",
    "GA": "GI",
    "GD": "GR",
    "Pts": "Body",
    "Form": "Forma",
    
    # Status values
    "WAITING": "ČAKAJÚCE",
    "COMPLETED": "DOKONČENÉ",
    "All": "Všetky",
    
    # Result values
    "Yes": "Áno",
    "No": "Nie",
    
    # Prediction values
    "WIN": "VÝHRA",
    "LOSS": "PREHRA",
    "BIG WIN": "VEĽKÁ VÝHRA",
    "BIG LOSS": "VEĽKÁ PREHRA",
    
    # Stats tab
    "Prediction Statistics": "Štatistiky predpovedí",
    "Summary": "Súhrn",
    "Charts": "Grafy",
    "Total Predictions": "Celkové predpovede",
    "Completed Predictions": "Dokončené predpovede",
    "Correct Predictions": "Správne predpovede",
    "Accuracy": "Presnosť",
    "Prediction Accuracy": "Presnosť predpovedí",
    "Predictions by Level": "Predpovede podľa úrovne",
    "Accuracy Over Time": "Presnosť v čase",
    "Correct": "Správne",
    "Incorrect": "Nesprávne",
    "Level": "Úroveň",
    "Count": "Počet",
    
    # Next Round tab
    "Next Round Fixtures": "Zápasy ďalšieho kola",
    "Round:": "Kolo:",
    "Match Details:": "Detaily zápasu:",
    "Select a match to view details": "Vyberte zápas pre zobrazenie detailov",
    
    # League Stats tab
    "League Statistics": "Štatistiky ligy",
    "Standings": "Tabuľka",
    "Total Goals": "Celkové góly",
    "Avg. Goals/Match": "Priem. gólov/zápas",
    "Home Wins %": "Domáce výhry %",
    "Away Wins %": "Vonkajšie výhry %",
    "Clean Sheets": "Čisté konto",
    "Total Cards": "Celkové karty",
    
    # Data Collection tab
    "Data Collection": "Zber dát",
    "Data Type:": "Typ dát:",
    "Fixtures": "Zápasy",
    "Teams": "Tímy",
    "Players": "Hráči",
    "Season:": "Sezóna:",
    "Fetch Data": "Načítať dáta",
    "CSV": "CSV",
    "JSON": "JSON",
    
    # Firebase tab
    "Form Changes": "Zmeny formy",
    "Upcoming Fixtures": "Nadchádzajúce zápasy",
    "Results": "Výsledky",
    
    # Database View tab
    "Database View": "Zobrazenie databázy",
    "Select Table:": "Vybrať tabuľku:",
    "Filter:": "Filter:",
    "Table View": "Tabuľkový pohľad",
    "Total Records": "Celkový počet záznamov",
    "Completed": "Dokončené",
    "Correct": "Správne",
    "Accuracy": "Presnosť",
    "Export to CSV": "Export do CSV",
    "Data loaded at": "Dáta načítané o",
    "Refresh Failed": "Obnovenie zlyhalo",
    "Export": "Export",
    "Exported to": "Exportované do",
    "Error": "Chyba",
    "Country": "Krajina",
    "Logo URL": "URL loga",
    "Season": "Sezóna",
    "Fixture ID": "ID zápasu",
    "predictions": "predpovede",
    "fixtures": "zápasy",
    "teams": "tímy",
    "leagues": "ligy",
    "form_changes": "zmeny formy",
    
    # Misc
    "Loading...": "Načítava sa...",
    "No data available": "Žiadne dostupné dáta",
    "Coming Soon": "Čoskoro",
    "Ready": "Pripravené",
    "Settings updated at": "Nastavenia aktualizované o",
    "Football Statistics Analyzer": "Analyzátor futbalových štatistík"
}

def translate(text):
    """
    Translate text from English to Slovak.
    If the text is not found in the dictionary, return the original text.
    
    Args:
        text (str): Text to translate
        
    Returns:
        str: Translated text
    """
    return EN_TO_SK.get(text, text)

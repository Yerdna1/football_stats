# translations.py
# Slovak translations for the football dashboard

TRANSLATIONS = {
    # Tab names
    "Team Analysis": "Analýza tímov",
    
    # Section titles
    "Time Analysis Dashboard": "Dashboard časovej analýzy",
    "Recent Results": "Nedávne výsledky",
    "Teams Without Goals": "Tímy bez gólov",
    "Additional Statistics": "Dodatočné štatistiky",
    "Streaks & Results": "Série a výsledky",
    "Clean Sheets & Scoring": "Čisté kontá a skórovanie",
    "Formations Used": "Použité formácie",
    
    # UI elements
    "Select League": "Vybrať ligu",
    "Select Team": "Vybrať tím",
    
    # Table headers
    "Date": "Dátum",
    "Opponent": "Súper",
    "Score": "Skóre",
    "Result": "Výsledok",
    "Team": "Tím",
    "Games Without Scoring": "Zápasy bez skórovania"
}

def get_translation(text):
    """
    Return the Slovak translation for a given English text
    If translation doesn't exist, return the original text
    """
    return TRANSLATIONS.get(text, text)

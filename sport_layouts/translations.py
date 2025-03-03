# translations.py
# Slovak translations for the football dashboard

TRANSLATIONS = {
    # Tab names
    "Team Analysis": "Analýza tímov",
    "League Statistics": "Štatistiky ligy",
    
    # Section titles
    "Time Analysis Dashboard": "Dashboard časovej analýzy",
    "Recent Results": "Nedávne výsledky",
    "Teams Without Goals": "Tímy bez gólov",
    "Additional Statistics": "Dodatočné štatistiky",
    "Streaks & Results": "Série a výsledky",
    "Clean Sheets & Scoring": "Čisté kontá a skórovanie",
    "Formations Used": "Použité formácie",
    "League Statistics Analysis": "Analýza štatistík ligy",
    "Goals Comparison Across Leagues": "Porovnanie gólov medzi ligami",
    "Goal Statistics": "Gólové štatistiky",
    "Yellow Card Statistics": "Štatistiky žltých kariet",
    "Red Card Statistics": "Štatistiky červených kariet",
    "Most Common Results": "Najčastejšie výsledky",
    
    # UI elements
    "Select League": "Vybrať ligu",
    "Select Team": "Vybrať tím",
    "Average Goals per Match:": "Priemer gólov na zápas:",
    "Average Yellow Cards per Match:": "Priemer žltých kariet na zápas:",
    "Average Red Cards per Match:": "Priemer červených kariet na zápas:",
    
    # Table headers
    "Date": "Dátum",
    "Opponent": "Súper",
    "Score": "Skóre",
    "Result": "Výsledok",
    "Team": "Tím",
    "Games Without Scoring": "Zápasy bez skórovania",
    "Count": "Počet",
    "Percentage": "Percentuálny podiel"
}

def get_translation(text):
    """
    Return the Slovak translation for a given English text
    If translation doesn't exist, return the original text
    """
    return TRANSLATIONS.get(text, text)

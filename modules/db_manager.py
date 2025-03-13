import sqlite3
import logging
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id INTEGER NOT NULL,
                    team_name TEXT NOT NULL,
                    league_id INTEGER NOT NULL,
                    league_name TEXT NOT NULL,
                    fixture_id INTEGER NOT NULL,
                    opponent_id INTEGER NOT NULL,
                    opponent_name TEXT NOT NULL,
                    match_date TEXT NOT NULL,
                    venue TEXT,
                    performance_diff REAL NOT NULL,
                    prediction TEXT NOT NULL,
                    prediction_level INTEGER NOT NULL,
                    result TEXT,
                    correct INTEGER,
                    created_at TEXT NOT NULL,
                    UNIQUE(fixture_id, team_id)
                )
            ''')
            
            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            # Create fixtures table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fixtures (
                    id INTEGER PRIMARY KEY,
                    league_id INTEGER NOT NULL,
                    home_team_id INTEGER NOT NULL,
                    home_team_name TEXT NOT NULL,
                    away_team_id INTEGER NOT NULL,
                    away_team_name TEXT NOT NULL,
                    match_date TEXT NOT NULL,
                    match_time TEXT,
                    venue TEXT,
                    status TEXT,
                    home_score INTEGER,
                    away_score INTEGER,
                    created_at TEXT NOT NULL,
                    UNIQUE(id)
                )
            ''')
            
            # Create teams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    league_id INTEGER NOT NULL,
                    country TEXT,
                    founded INTEGER,
                    stadium TEXT,
                    capacity INTEGER,
                    created_at TEXT NOT NULL,
                    UNIQUE(id)
                )
            ''')
            
            # Create players table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    team_id INTEGER NOT NULL,
                    position TEXT,
                    age INTEGER,
                    nationality TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(id)
                )
            ''')
            
            # Create standings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS standings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    league_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    team_name TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    played INTEGER NOT NULL,
                    won INTEGER NOT NULL,
                    drawn INTEGER NOT NULL,
                    lost INTEGER NOT NULL,
                    goals_for INTEGER NOT NULL,
                    goals_against INTEGER NOT NULL,
                    goal_diff INTEGER NOT NULL,
                    points INTEGER NOT NULL,
                    form TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(league_id, team_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
            
    def save_prediction(self, prediction_data: Dict[str, Any]) -> int:
        """Save a prediction to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if prediction already exists
            cursor.execute(
                "SELECT id FROM predictions WHERE fixture_id = ? AND team_id = ?",
                (prediction_data['fixture_id'], prediction_data['team_id'])
            )
            existing = cursor.fetchone()
            
            if existing:
                # Prediction already exists, return existing ID
                conn.close()
                return 0
                
            # Insert new prediction
            cursor.execute('''
                INSERT INTO predictions (
                    team_id, team_name, league_id, league_name, fixture_id,
                    opponent_id, opponent_name, match_date, venue,
                    performance_diff, prediction, prediction_level, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction_data['team_id'],
                prediction_data['team_name'],
                prediction_data['league_id'],
                prediction_data['league_name'],
                prediction_data['fixture_id'],
                prediction_data['opponent_id'],
                prediction_data['opponent_name'],
                prediction_data['match_date'],
                prediction_data.get('venue', ''),
                prediction_data['performance_diff'],
                prediction_data['prediction'],
                prediction_data['prediction_level'],
                datetime.now().isoformat()
            ))
            
            prediction_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return prediction_id
            
        except Exception as e:
            logger.error(f"Error saving prediction: {str(e)}")
            return 0
            
    def update_prediction_result(self, prediction_id: int, result: str, correct: int) -> bool:
        """Update a prediction with its result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE predictions SET result = ?, correct = ? WHERE id = ?",
                (result, correct, prediction_id)
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating prediction result: {str(e)}")
            return False
            
    def get_predictions(self) -> List[Dict[str, Any]]:
        """Get all predictions from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions
                ORDER BY match_date DESC
            ''')
            
            predictions = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting predictions: {str(e)}")
            return []
            
    def get_upcoming_fixtures(self) -> List[Dict[str, Any]]:
        """Get upcoming fixtures from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions
                WHERE result IS NULL
                ORDER BY match_date ASC
            ''')
            
            fixtures = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return fixtures
            
        except Exception as e:
            logger.error(f"Error getting upcoming fixtures: {str(e)}")
            return []
            
    def get_completed_predictions(self) -> List[Dict[str, Any]]:
        """Get completed predictions from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions
                WHERE result IS NOT NULL
                ORDER BY match_date DESC
            ''')
            
            predictions = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting completed predictions: {str(e)}")
            return []
            
    def get_predictions_to_check(self) -> List[Dict[str, Any]]:
        """Get predictions that need to be checked for results"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions
                WHERE result IS NULL
                AND date(match_date) < date('now')
                ORDER BY match_date ASC
            ''')
            
            predictions = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting predictions to check: {str(e)}")
            return []
            
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total predictions
            cursor.execute("SELECT COUNT(*) FROM predictions")
            total = cursor.fetchone()[0]
            
            # Get completed predictions
            cursor.execute("SELECT COUNT(*) FROM predictions WHERE result IS NOT NULL")
            completed = cursor.fetchone()[0]
            
            # Get correct predictions
            cursor.execute("SELECT COUNT(*) FROM predictions WHERE correct = 1")
            correct = cursor.fetchone()[0]
            
            # Calculate accuracy
            accuracy = (correct / completed * 100) if completed > 0 else 0
            
            # Get stats by prediction level
            cursor.execute('''
                SELECT prediction_level, COUNT(*) as count
                FROM predictions
                GROUP BY prediction_level
            ''')
            level_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get accuracy by prediction level
            cursor.execute('''
                SELECT prediction_level, 
                       SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct_count,
                       COUNT(*) as total_count
                FROM predictions
                WHERE result IS NOT NULL
                GROUP BY prediction_level
            ''')
            
            level_accuracy = {}
            for row in cursor.fetchall():
                level = row[0]
                correct_count = row[1]
                total_count = row[2]
                level_accuracy[level] = (correct_count / total_count * 100) if total_count > 0 else 0
            
            conn.close()
            
            return {
                "total": total,
                "completed": completed,
                "correct": correct,
                "accuracy": accuracy,
                "by_level": {
                    "counts": level_counts,
                    "accuracy": level_accuracy
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction stats: {str(e)}")
            return {
                "total": 0,
                "completed": 0,
                "correct": 0,
                "accuracy": 0,
                "by_level": {
                    "counts": {},
                    "accuracy": {}
                }
            }
            
    def save_fixtures(self, fixtures: List[Dict[str, Any]]) -> int:
        """Save fixtures to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for fixture in fixtures:
                try:
                    # Extract data
                    fixture_id = fixture['fixture']['id']
                    league_id = fixture['league']['id']
                    home_team_id = fixture['teams']['home']['id']
                    home_team_name = fixture['teams']['home']['name']
                    away_team_id = fixture['teams']['away']['id']
                    away_team_name = fixture['teams']['away']['name']
                    match_date = fixture['fixture']['date'].split('T')[0]
                    match_time = fixture['fixture']['date'].split('T')[1].split('+')[0][:-3]
                    venue = fixture['fixture']['venue']['name'] if fixture['fixture']['venue']['name'] else ""
                    status = fixture['fixture']['status']['long']
                    
                    # Get scores if available
                    home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else None
                    away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else None
                    
                    # Insert or update fixture
                    cursor.execute('''
                        INSERT OR REPLACE INTO fixtures (
                            id, league_id, home_team_id, home_team_name,
                            away_team_id, away_team_name, match_date, match_time,
                            venue, status, home_score, away_score, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        fixture_id, league_id, home_team_id, home_team_name,
                        away_team_id, away_team_name, match_date, match_time,
                        venue, status, home_score, away_score, datetime.now().isoformat()
                    ))
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving fixture {fixture.get('fixture', {}).get('id', 'unknown')}: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving fixtures: {str(e)}")
            return 0
            
    def save_teams(self, teams: List[Dict[str, Any]]) -> int:
        """Save teams to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for team in teams:
                try:
                    # Extract data
                    team_id = team['team']['id']
                    name = team['team']['name']
                    league_id = team.get('league', {}).get('id', 0)
                    
                    # Insert or update team
                    cursor.execute('''
                        INSERT OR REPLACE INTO teams (
                            id, name, league_id, created_at
                        ) VALUES (?, ?, ?, ?)
                    ''', (
                        team_id, name, league_id, datetime.now().isoformat()
                    ))
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving team {team.get('team', {}).get('id', 'unknown')}: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving teams: {str(e)}")
            return 0
            
    def save_players(self, players: List[Dict[str, Any]]) -> int:
        """Save players to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for player in players:
                try:
                    # Extract data
                    player_id = player['player']['id']
                    name = player['player']['name']
                    team_id = player.get('statistics', [{}])[0].get('team', {}).get('id', 0)
                    
                    # Insert or update player
                    cursor.execute('''
                        INSERT OR REPLACE INTO players (
                            id, name, team_id, created_at
                        ) VALUES (?, ?, ?, ?)
                    ''', (
                        player_id, name, team_id, datetime.now().isoformat()
                    ))
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving player {player.get('player', {}).get('id', 'unknown')}: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving players: {str(e)}")
            return 0
            
    def save_standings(self, standings: List[Dict[str, Any]]) -> int:
        """Save standings to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for team in standings:
                try:
                    # Extract data
                    league_id = team.get('league', {}).get('id', 0)
                    team_id = team['team']['id']
                    team_name = team['team']['name']
                    position = team['rank']
                    played = team['all']['played']
                    won = team['all']['win']
                    drawn = team['all']['draw']
                    lost = team['all']['lose']
                    goals_for = team['all']['goals']['for']
                    goals_against = team['all']['goals']['against']
                    goal_diff = team['goalsDiff']
                    points = team['points']
                    form = team.get('form', '')
                    
                    # Insert or update standing
                    cursor.execute('''
                        INSERT OR REPLACE INTO standings (
                            league_id, team_id, team_name, position, played,
                            won, drawn, lost, goals_for, goals_against,
                            goal_diff, points, form, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        league_id, team_id, team_name, position, played,
                        won, drawn, lost, goals_for, goals_against,
                        goal_diff, points, form, datetime.now().isoformat()
                    ))
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving standing for team {team.get('team', {}).get('id', 'unknown')}: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving standings: {str(e)}")
            return 0
            
    def export_predictions_to_csv(self, filepath: str) -> bool:
        """Export predictions to CSV file"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions
                ORDER BY match_date DESC
            ''')
            
            predictions = cursor.fetchall()
            
            if not predictions:
                conn.close()
                return False
                
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                writer.writerow([column[0] for column in cursor.description])
                
                # Write data
                for prediction in predictions:
                    writer.writerow(prediction)
                    
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting predictions to CSV: {str(e)}")
            return False
            
    def get_fixtures(self) -> List[Dict[str, Any]]:
        """Get all fixtures from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT f.*, l.name as league_name
                FROM fixtures f
                LEFT JOIN (
                    SELECT id, name FROM teams
                ) l ON f.league_id = l.id
                ORDER BY match_date DESC
            ''')
            
            fixtures = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return fixtures
            
        except Exception as e:
            logger.error(f"Error getting fixtures: {str(e)}")
            return []
            
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.*, l.name as league_name
                FROM teams t
                LEFT JOIN (
                    SELECT id, name FROM teams
                ) l ON t.league_id = l.id
                ORDER BY t.name
            ''')
            
            teams = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return teams
            
        except Exception as e:
            logger.error(f"Error getting teams: {str(e)}")
            return []
            
    def get_leagues(self) -> List[Dict[str, Any]]:
        """Get all leagues from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT league_id as id, league_name as name, '' as country, '' as logo, '' as season
                FROM predictions
                ORDER BY league_name
            ''')
            
            leagues = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return leagues
            
        except Exception as e:
            logger.error(f"Error getting leagues: {str(e)}")
            return []
            
    def get_form_changes(self) -> List[Dict[str, Any]]:
        """Get all form changes from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    id,
                    team_id,
                    team_name,
                    league_id,
                    league_name,
                    match_date as date,
                    performance_diff,
                    fixture_id
                FROM predictions
                WHERE performance_diff > 0
                ORDER BY performance_diff DESC
            ''')
            
            form_changes = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return form_changes
            
        except Exception as e:
            logger.error(f"Error getting form changes: {str(e)}")
            return []

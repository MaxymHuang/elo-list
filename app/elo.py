import math
import numpy as np
from datetime import datetime

class AdvancedELOSystem:
    def __init__(self, initial_rating=1500, initial_rd=350, initial_volatility=0.06):
        """
        Advanced ELO system with Glicko-2 inspired features
        
        Args:
            initial_rating: Starting ELO rating
            initial_rd: Rating deviation (uncertainty)
            initial_volatility: Rating volatility
        """
        self.initial_rating = initial_rating
        self.initial_rd = initial_rd
        self.initial_volatility = initial_volatility
        
    def calculate_dynamic_k_factor(self, rating, rd, games_played, is_provisional=False):
        """
        Calculate dynamic K-factor based on multiple factors
        
        Args:
            rating: Current ELO rating
            rd: Rating deviation
            games_played: Number of games played
            is_provisional: Whether player is in provisional period
        """
        base_k = 32
        
        # Higher K for provisional players
        if is_provisional or games_played < 10:
            base_k = 50
        elif games_played < 30:
            base_k = 40
        
        # Adjust based on rating deviation (uncertainty)
        uncertainty_multiplier = min(2.0, rd / 100)
        
        # Adjust based on rating level
        if rating < 1200:
            rating_multiplier = 1.2
        elif rating > 2000:
            rating_multiplier = 0.8
        else:
            rating_multiplier = 1.0
            
        return base_k * uncertainty_multiplier * rating_multiplier
    
    def expected_score(self, rating_a, rating_b, rd_a=None, rd_b=None):
        """
        Calculate expected score with optional rating deviation consideration
        """
        if rd_a and rd_b:
            # Adjust for uncertainty
            effective_diff = (rating_a - rating_b) / math.sqrt(1 + (3 * (rd_a**2 + rd_b**2)) / (math.pi**2))
            return 1 / (1 + 10 ** (-effective_diff / 400))
        else:
            return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_rating_deviation(self, rd, time_elapsed_days=1):
        """
        Update rating deviation based on time elapsed
        """
        c = 15  # Rating deviation increase per day
        return min(350, math.sqrt(rd**2 + (c * time_elapsed_days)**2))
    
    def update_volatility(self, volatility, expected, actual, rd, tau=0.5):
        """
        Update volatility using simplified Glicko-2 approach
        """
        delta = (actual - expected) * rd
        v = 1 / (expected * (1 - expected))
        
        # Simplified volatility update
        a = math.log(volatility**2)
        f = lambda x: (math.exp(x) * (delta**2 - rd**2 - v - math.exp(x))) / (2 * (rd**2 + v + math.exp(x))**2) - (x - a) / tau**2
        
        # Newton-Raphson iteration (simplified)
        x = a
        for _ in range(5):
            d = (math.exp(x) * (delta**2 - rd**2 - v - math.exp(x))) / (2 * (rd**2 + v + math.exp(x))**2) - 1 / tau**2
            if abs(d) < 1e-6:
                break
            x = x - f(x) / d
            
        return math.exp(x / 2)

def update_elo_ratings(anime_list, winner_id, loser_id, elo_system=None):
    """
    Enhanced ELO rating update with advanced features
    """
    if elo_system is None:
        elo_system = AdvancedELOSystem()
    
    winner = next(anime for anime in anime_list if anime['id'] == winner_id)
    loser = next(anime for anime in anime_list if anime['id'] == loser_id)
    
    # Initialize advanced stats if not present
    for anime in [winner, loser]:
        if 'rd' not in anime:
            anime['rd'] = elo_system.initial_rd
        if 'volatility' not in anime:
            anime['volatility'] = elo_system.initial_volatility
        if 'games_played' not in anime:
            anime['games_played'] = 0
        if 'last_played' not in anime or anime['last_played'] is None:
            anime['last_played'] = datetime.now()
        if 'win_streak' not in anime:
            anime['win_streak'] = 0
        if 'performance_history' not in anime:
            anime['performance_history'] = []
    
    # Update time-based rating deviation
    time_elapsed_winner = (datetime.now() - winner['last_played']).days
    time_elapsed_loser = (datetime.now() - loser['last_played']).days
    winner['rd'] = elo_system.update_rating_deviation(winner['rd'], time_elapsed_winner)
    loser['rd'] = elo_system.update_rating_deviation(loser['rd'], time_elapsed_loser)
    
    # Calculate expected scores
    expected_winner = elo_system.expected_score(winner['elo'], loser['elo'], winner['rd'], loser['rd'])
    expected_loser = 1 - expected_winner
    
    # Calculate dynamic K-factors
    k_winner = elo_system.calculate_dynamic_k_factor(
        winner['elo'], winner['rd'], winner['games_played']
    )
    k_loser = elo_system.calculate_dynamic_k_factor(
        loser['elo'], loser['rd'], loser['games_played']
    )
    
    # Update ratings
    winner_rating_change = k_winner * (1 - expected_winner)
    loser_rating_change = k_loser * (0 - expected_loser)
    
    winner['elo'] += winner_rating_change
    loser['elo'] += loser_rating_change
    
    # Update rating deviations (decrease after game)
    winner['rd'] = max(30, winner['rd'] * 0.95)
    loser['rd'] = max(30, loser['rd'] * 0.95)
    
    # Update volatility
    winner['volatility'] = elo_system.update_volatility(
        winner['volatility'], expected_winner, 1, winner['rd']
    )
    loser['volatility'] = elo_system.update_volatility(
        loser['volatility'], expected_loser, 0, loser['rd']
    )
    
    # Update game statistics
    winner['games_played'] += 1
    loser['games_played'] += 1
    winner['win_streak'] += 1
    loser['win_streak'] = 0
    winner['last_played'] = datetime.now()
    loser['last_played'] = datetime.now()
    
    # Track performance history
    winner['performance_history'].append({
        'rating': winner['elo'],
        'rd': winner['rd'],
        'opponent_rating': loser['elo'],
        'result': 1,
        'timestamp': datetime.now()
    })
    loser['performance_history'].append({
        'rating': loser['elo'],
        'rd': loser['rd'],
        'opponent_rating': winner['elo'],
        'result': 0,
        'timestamp': datetime.now()
    })
    
    # Keep only last 50 games in history
    for anime in [winner, loser]:
        if len(anime['performance_history']) > 50:
            anime['performance_history'] = anime['performance_history'][-50:]
    
    return anime_list

def normalize_ratings(anime_list, scale_min=1, scale_max=10):
    """
    Enhanced normalization with confidence intervals
    """
    if not anime_list:
        return anime_list
    
    ratings = [anime['elo'] for anime in anime_list]
    min_elo = min(ratings)
    max_elo = max(ratings)
    
    if max_elo == min_elo:
        for anime in anime_list:
            anime['rating'] = (scale_min + scale_max) / 2
            anime['confidence_interval'] = (anime['rating'] - 0.5, anime['rating'] + 0.5)
        return anime_list
    
    for anime in anime_list:
        # Normalize rating
        normalized = scale_min + ((anime['elo'] - min_elo) * (scale_max - scale_min) / (max_elo - min_elo))
        anime['rating'] = round(normalized, 2)
        
        # Calculate confidence interval based on rating deviation
        rd = anime.get('rd', 100)
        margin = (rd / 100) * (scale_max - scale_min) / 4  # Scale margin appropriately
        anime['confidence_interval'] = (
            max(scale_min, anime['rating'] - margin),
            min(scale_max, anime['rating'] + margin)
        )
        
        # Calculate percentile rank
        better_count = sum(1 for other in anime_list if other['elo'] > anime['elo'])
        anime['percentile'] = round((1 - better_count / len(anime_list)) * 100, 1)
    
    return anime_list

def calculate_rating_reliability(anime):
    """
    Calculate how reliable an anime's rating is based on various factors
    """
    games_played = anime.get('games_played', 0)
    rd = anime.get('rd', 350)
    volatility = anime.get('volatility', 0.06)
    
    # Base reliability on games played
    games_factor = min(1.0, games_played / 30)
    
    # Factor in rating deviation (lower RD = higher reliability)
    rd_factor = max(0.1, 1 - (rd - 30) / 320)
    
    # Factor in volatility (lower volatility = higher reliability)
    volatility_factor = max(0.1, 1 - (volatility - 0.03) / 0.1)
    
    reliability = (games_factor * 0.5 + rd_factor * 0.3 + volatility_factor * 0.2) * 100
    return round(reliability, 1)

def get_strength_of_schedule(anime, anime_list):
    """
    Calculate strength of schedule based on opponents faced
    """
    history = anime.get('performance_history', [])
    if not history:
        return 50.0  # Neutral if no games
    
    opponent_ratings = [game['opponent_rating'] for game in history]
    avg_opponent_rating = sum(opponent_ratings) / len(opponent_ratings)
    
    # Convert to percentile relative to all anime
    all_ratings = [a['elo'] for a in anime_list]
    percentile = (sum(1 for r in all_ratings if r < avg_opponent_rating) / len(all_ratings)) * 100
    
    return round(percentile, 1)

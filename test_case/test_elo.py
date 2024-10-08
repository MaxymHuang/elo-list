import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from elo import update_elo_ratings, normalize_ratings

class TestElo(unittest.TestCase):

    def setUp(self):
        # Initial setup with some anime data
        self.anime_list = [
            {'id': 1, 'title': 'Anime A', 'elo': 1000},
            {'id': 2, 'title': 'Anime B', 'elo': 1000},
            {'id': 3, 'title': 'Anime C', 'elo': 1200},
            {'id': 4, 'title': 'Anime D', 'elo': 900}
        ]
    
    def test_update_elo_ratings(self):
        # Test 1: Check if ELO ratings are correctly updated for a match

        # Simulate Anime A (id=1) winning against Anime B (id=2)
        updated_anime_list = update_elo_ratings(self.anime_list, winner_id=1, loser_id=2)

        anime_a = next(anime for anime in updated_anime_list if anime['id'] == 1)
        anime_b = next(anime for anime in updated_anime_list if anime['id'] == 2)

        # Anime A should have gained ELO points
        self.assertGreater(anime_a['elo'], 1000)

        # Anime B should have lost ELO points
        self.assertLess(anime_b['elo'], 1000)

    def test_normalize_ratings(self):
        # Test 2: Check if ELO ratings are correctly normalized to a 1-10 scale

        # Normalize the anime list
        normalized_anime_list = normalize_ratings(self.anime_list)

        # Get the normalized ratings
        ratings = [anime['rating'] for anime in normalized_anime_list]

        # All ratings should be between 1 and 10
        for rating in ratings:
            self.assertGreaterEqual(rating, 1)
            self.assertLessEqual(rating, 10)

        # The anime with the highest ELO should have a rating of 10
        anime_with_max_elo = max(self.anime_list, key=lambda x: x['elo'])
        self.assertEqual(anime_with_max_elo['rating'], 10)

        # The anime with the lowest ELO should have a rating of 1
        anime_with_min_elo = min(self.anime_list, key=lambda x: x['elo'])
        self.assertEqual(anime_with_min_elo['rating'], 1)

if __name__ == '__main__':
    unittest.main()

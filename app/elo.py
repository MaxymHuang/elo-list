def update_elo_ratings(anime_list, winner_id, loser_id, k=32):
    winner = next(anime for anime in anime_list if anime['id'] == winner_id)
    loser = next(anime for anime in anime_list if anime['id'] == loser_id)

    # Calculate expected scores
    expected_winner = 1 / (1 + 10 ** ((loser['elo'] - winner['elo']) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner['elo'] - loser['elo']) / 400))

    # Update ELO ratings
    winner['elo'] += round(k * (1 - expected_winner), 3)
    loser['elo'] += round(k * (0 - expected_loser), 3)

    return anime_list

def normalize_ratings(anime_list):
    # Normalize ELO ratings to 1-10 scale
    min_elo = min(anime['elo'] for anime in anime_list)
    max_elo = max(anime['elo'] for anime in anime_list)
    for anime in anime_list:
        anime['rating'] = round(((anime['elo'] - min_elo) / (max_elo - min_elo)) * 9 + 1, 2)
    return anime_list

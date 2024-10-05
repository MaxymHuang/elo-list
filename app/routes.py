from app import app
from flask import render_template, request, redirect, url_for, session
from app.parser import parse_xml_to_json
from app.elo import update_elo_ratings, normalize_ratings
import json
import os
import random

# Secret key for session management
app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        xml_file = request.files['file']
        if xml_file:
            # Parse XML to JSON and save to session
            anime_list = parse_xml_to_json(xml_file)
            session['anime_list'] = anime_list
            session['comparisons'] = []
            # Calculate total comparisons (n * (n - 1) / 2)
            session['total_comparisons'] = len(anime_list) * (len(anime_list) - 1) // 2
            session['remaining_comparisons'] = session['total_comparisons']  # Start with remaining comparisons equal to total
            return redirect(url_for('compare'))
    return render_template('index.html')

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    anime_list = session.get('anime_list', [])
    comparisons = session.get('comparisons', [])
    elo_history = session.get('elo_history', [])  # Store ELO history
    remaining_comparisons = session.get('remaining_comparisons', 0)
    
    if request.method == 'POST':
        # Update ELO ratings based on user choice
        winner_id = int(request.form['winner'])
        loser_id = int(request.form['loser'])
        anime_list = update_elo_ratings(anime_list, winner_id, loser_id)
        session['anime_list'] = anime_list
        comparisons.append((winner_id, loser_id))
        session['comparisons'] = comparisons
        session['remaining_comparisons'] -= 1  # Decrease remaining comparisons

    if len(comparisons) >= len(anime_list) - 1:
        # All comparisons done
        return redirect(url_for('results'))

    if request.method == 'POST':
        # Update ELO ratings based on user choice
        winner_id = int(request.form['winner'])
        loser_id = int(request.form['loser'])
        anime_list = update_elo_ratings(anime_list, winner_id, loser_id)

        # Save the current ELO state to history
        elo_history.append({anime['title']: anime['elo'] for anime in anime_list})
        session['elo_history'] = elo_history  # Update history in session
        session['anime_list'] = anime_list
        comparisons.append((winner_id, loser_id))
        session['comparisons'] = comparisons

    # Select two animes to compare
    remaining_anime = [anime for anime in anime_list if anime['id'] not in [item for sublist in comparisons for item in sublist]]
    if len(remaining_anime) < 2:
        return redirect(url_for('results'))

    anime1, anime2 = random.sample(remaining_anime, 2)

    return render_template('compare.html', anime1=anime1, anime2=anime2, 
                           remaining_comparisons=remaining_comparisons,
                           total_comparisons=session['total_comparisons'],
                           anime_list=anime_list)

@app.route('/results')
def results():
    anime_list = session.get('anime_list', [])
    normalized_list = normalize_ratings(anime_list)
    return render_template('results.html', anime_list=normalized_list)

@app.route('/restart')
def restart():
    # Clear session and start over
    session.clear()
    return redirect(url_for('index'))

from app import app
from flask import render_template, request, redirect, url_for, session, jsonify
from app.parser import parse_xml_to_json
from app.elo import update_elo_ratings, normalize_ratings, AdvancedELOSystem, calculate_rating_reliability, get_strength_of_schedule
from app.reports import generate_reports, export_detailed_report
import json
import os
import random
from datetime import datetime

# Secret key for session management
app.secret_key = 'your_secret_key_here'

# Initialize advanced ELO system
elo_system = AdvancedELOSystem()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        xml_file = request.files['file']
        if xml_file:
            # Parse XML to JSON and save to session
            anime_list = parse_xml_to_json(xml_file)
            
            # Initialize advanced ELO features for each anime
            for anime in anime_list:
                anime['rd'] = elo_system.initial_rd
                anime['volatility'] = elo_system.initial_volatility
                anime['games_played'] = 0
                anime['win_streak'] = 0
                anime['performance_history'] = []
                anime['last_played'] = datetime.now()
            
            session['anime_list'] = anime_list
            session['comparisons'] = []
            session['elo_history'] = []
            # Calculate total comparisons needed for reasonable accuracy
            total_needed = min(len(anime_list) * 3, len(anime_list) * (len(anime_list) - 1) // 4)
            session['total_comparisons'] = total_needed
            session['remaining_comparisons'] = total_needed
            return redirect(url_for('compare'))
    return render_template('index.html')

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    anime_list = session.get('anime_list', [])
    comparisons = session.get('comparisons', [])
    elo_history = session.get('elo_history', [])
    remaining_comparisons = session.get('remaining_comparisons', 0)
    
    if request.method == 'POST':
        # Update ELO ratings based on user choice
        winner_id = int(request.form['winner'])
        loser_id = int(request.form['loser'])
        
        # Use advanced ELO system
        anime_list = update_elo_ratings(anime_list, winner_id, loser_id, elo_system)
        
        # Save the current ELO state to history
        elo_state = {anime['title']: anime['elo'] for anime in anime_list}
        elo_history.append(elo_state)
        
        session['anime_list'] = anime_list
        session['elo_history'] = elo_history
        comparisons.append((winner_id, loser_id))
        session['comparisons'] = comparisons
        session['remaining_comparisons'] -= 1

    # Check if we have enough comparisons for meaningful results
    if remaining_comparisons <= 0 or len(comparisons) >= session.get('total_comparisons', 100):
        return redirect(url_for('results'))

    # Smart pairing algorithm - prioritize uncertain matchups
    def get_comparison_value(anime1, anime2):
        """Calculate the value of comparing two anime"""
        elo_diff = abs(anime1['elo'] - anime2['elo'])
        uncertainty = (anime1.get('rd', 100) + anime2.get('rd', 100)) / 2
        games_factor = 1 / (1 + min(anime1.get('games_played', 0), anime2.get('games_played', 0)))
        
        # Prefer close matches with high uncertainty
        return uncertainty * games_factor * (1 / (1 + elo_diff / 200))

    # Find the best pair to compare
    best_pair = None
    best_value = 0
    
    for i, anime1 in enumerate(anime_list):
        for j, anime2 in enumerate(anime_list[i+1:], i+1):
            # Skip if already compared recently
            if (anime1['id'], anime2['id']) in comparisons[-10:] or (anime2['id'], anime1['id']) in comparisons[-10:]:
                continue
            
            value = get_comparison_value(anime1, anime2)
            if value > best_value:
                best_value = value
                best_pair = (anime1, anime2)
    
    # Fallback to random if no good pair found
    if best_pair is None:
        available_anime = [anime for anime in anime_list]
        if len(available_anime) >= 2:
            best_pair = random.sample(available_anime, 2)
        else:
            return redirect(url_for('results'))

    anime1, anime2 = best_pair

    return render_template('compare.html', 
                         anime1=anime1, 
                         anime2=anime2, 
                         remaining_comparisons=remaining_comparisons,
                         total_comparisons=session['total_comparisons'],
                         anime_list=anime_list)

@app.route('/results')
def results():
    anime_list = session.get('anime_list', [])
    
    # Apply advanced normalization
    normalized_list = normalize_ratings(anime_list)
    
    # Calculate additional metrics for each anime
    for anime in normalized_list:
        anime['reliability'] = calculate_rating_reliability(anime)
        anime['strength_of_schedule'] = get_strength_of_schedule(anime, normalized_list)
    
    # Sort by ELO rating
    normalized_list.sort(key=lambda x: x['elo'], reverse=True)
    
    return render_template('results.html', anime_list=normalized_list)

@app.route('/reports')
def reports():
    anime_list = session.get('anime_list', [])
    elo_history = session.get('elo_history', [])

    if not elo_history:
        return redirect(url_for('index'))

    # Generate comprehensive reports
    confidence_intervals, plots_created, stats_dict = generate_reports(anime_list, elo_history)
    
    # Export detailed text report
    report_path = export_detailed_report(anime_list, stats_dict)

    return render_template('reports.html', 
                         confidence_intervals=confidence_intervals,
                         plots_created=plots_created,
                         stats_dict=stats_dict,
                         report_available=True)

@app.route('/api/anime/<int:anime_id>/details')
def anime_details(anime_id):
    """API endpoint for detailed anime information"""
    anime_list = session.get('anime_list', [])
    anime = next((a for a in anime_list if a['id'] == anime_id), None)
    
    if not anime:
        return jsonify({'error': 'Anime not found'}), 404
    
    # Calculate additional details
    details = {
        'title': anime['title'],
        'elo': anime['elo'],
        'rating': anime.get('rating', 0),
        'reliability': calculate_rating_reliability(anime),
        'strength_of_schedule': get_strength_of_schedule(anime, anime_list),
        'games_played': anime.get('games_played', 0),
        'win_streak': anime.get('win_streak', 0),
        'volatility': anime.get('volatility', 0.06),
        'rd': anime.get('rd', 100),
        'percentile': anime.get('percentile', 50),
        'confidence_interval': anime.get('confidence_interval', (0, 0)),
        'performance_history': anime.get('performance_history', [])[-10:]  # Last 10 games
    }
    
    return jsonify(details)

@app.route('/restart')
def restart():
    # Clear session and start over
    session.clear()
    return redirect(url_for('index'))

@app.route('/export/csv')
def export_csv():
    """Export results as CSV"""
    import csv
    import io
    from flask import Response
    
    anime_list = session.get('anime_list', [])
    if not anime_list:
        return redirect(url_for('index'))
    
    # Normalize ratings
    normalized_list = normalize_ratings(anime_list)
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Rank', 'Title', 'ELO Rating', 'Normalized Rating', 'Reliability %', 
        'Strength of Schedule', 'Games Played', 'Win Streak', 'Volatility', 
        'Rating Deviation', 'Percentile', 'Confidence Lower', 'Confidence Upper'
    ])
    
    # Sort by ELO and write data
    sorted_anime = sorted(normalized_list, key=lambda x: x['elo'], reverse=True)
    for rank, anime in enumerate(sorted_anime, 1):
        ci = anime.get('confidence_interval', (0, 0))
        writer.writerow([
            rank,
            anime['title'],
            round(anime['elo'], 2),
            anime.get('rating', 0),
            calculate_rating_reliability(anime),
            get_strength_of_schedule(anime, normalized_list),
            anime.get('games_played', 0),
            anime.get('win_streak', 0),
            round(anime.get('volatility', 0.06), 4),
            round(anime.get('rd', 100), 2),
            anime.get('percentile', 50),
            round(ci[0], 2),
            round(ci[1], 2)
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=anime_elo_rankings.csv'}
    )
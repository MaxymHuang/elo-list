import matplotlib.pyplot as plt
import numpy as np
import os

# Calculate confidence intervals and track elo convergence
def generate_reports(anime_list, elo_history):
    # Confidence intervals (basic approach)
    confidence_intervals = {}
    for anime in anime_list:
        title = anime['title'].strip().strip('"')
        # Get the ELO scores for each comparison
        elo_scores = [round(state.get(title, 1000), 2) for state in elo_history]
        comparisons = len(elo_scores)
        mean_elo = np.mean(elo_scores)
        stand_dev = np.std(elo_scores)
        # Simplified confidence interval (margin decreases with more comparisons)
        margin_of_error = stand_dev / np.sqrt(comparisons) if comparisons > 0 else 0
        confidence_intervals[anime['title']] = (mean_elo - margin_of_error, mean_elo + margin_of_error)

    # Generate plot showing elo convergence
    plt.figure(figsize=(10, 6))
    
    for anime in anime_list:
        title = anime['title'].strip().strip('"')
        # Get the ELO scores for each comparison
        elo_scores = [round(state.get(title, 1000), 2) for state in elo_history]
        x_values = list(range(1, len(elo_scores) + 1))

        # Plot the ELO score evolution
        plt.plot(x_values, elo_scores, label=anime['title'])

        # Plot the confidence interval as shaded region
        lower_bound, upper_bound = confidence_intervals[anime['title']]
        plt.fill_between(x_values, lower_bound, upper_bound, alpha=0.05)

    plt.title("ELO Convergence Over Time")
    plt.xlabel("Number of Comparisons")
    plt.ylabel("ELO Score")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize='small')
    plt.tight_layout()

    # Save the plot as a PNG file
    plot_path = os.path.join('app', 'static', 'elo_convergence_plot.png')
    plt.savefig(plot_path)

    return confidence_intervals, plot_path

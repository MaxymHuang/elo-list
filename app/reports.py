import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AdvancedAnalytics:
    def __init__(self, anime_list, elo_history):
        self.anime_list = anime_list
        self.elo_history = elo_history
        self.df = self._create_dataframe()
        
    def _create_dataframe(self):
        """Create a comprehensive DataFrame for analysis"""
        data = []
        for anime in self.anime_list:
            row = {
                'title': anime['title'],
                'elo': anime['elo'],
                'rating': anime.get('rating', 0),
                'rd': anime.get('rd', 100),
                'volatility': anime.get('volatility', 0.06),
                'games_played': anime.get('games_played', 0),
                'win_streak': anime.get('win_streak', 0),
                'percentile': anime.get('percentile', 50),
                'confidence_lower': anime.get('confidence_interval', (0, 0))[0],
                'confidence_upper': anime.get('confidence_interval', (0, 0))[1]
            }
            data.append(row)
        return pd.DataFrame(data)
    
    def calculate_advanced_statistics(self):
        """Calculate comprehensive statistics"""
        stats_dict = {}
        
        # Basic statistics
        stats_dict['basic'] = {
            'total_anime': len(self.anime_list),
            'mean_elo': self.df['elo'].mean(),
            'median_elo': self.df['elo'].median(),
            'std_elo': self.df['elo'].std(),
            'elo_range': self.df['elo'].max() - self.df['elo'].min(),
            'skewness': stats.skew(self.df['elo']),
            'kurtosis': stats.kurtosis(self.df['elo'])
        }
        
        # Rating distribution analysis
        stats_dict['distribution'] = {
            'top_10_percent': self.df[self.df['percentile'] >= 90]['title'].tolist(),
            'bottom_10_percent': self.df[self.df['percentile'] <= 10]['title'].tolist(),
            'most_volatile': self.df.nlargest(3, 'volatility')['title'].tolist(),
            'most_stable': self.df.nsmallest(3, 'volatility')['title'].tolist(),
            'highest_uncertainty': self.df.nlargest(3, 'rd')['title'].tolist(),
            'most_certain': self.df.nsmallest(3, 'rd')['title'].tolist()
        }
        
        # Convergence analysis
        if len(self.elo_history) > 5:
            stats_dict['convergence'] = self._analyze_convergence()
        
        # Clustering analysis
        stats_dict['clusters'] = self._perform_clustering()
        
        # Reliability analysis
        stats_dict['reliability'] = self._analyze_reliability()
        
        return stats_dict
    
    def _analyze_convergence(self):
        """Analyze how ratings have converged over time"""
        convergence_data = {}
        
        # Calculate rating stability over last 10 comparisons
        if len(self.elo_history) >= 10:
            recent_history = self.elo_history[-10:]
            stability_scores = {}
            
            for anime in self.anime_list:
                title = anime['title']
                recent_ratings = [state.get(title, anime['elo']) for state in recent_history]
                if len(recent_ratings) > 1:
                    stability = 1 / (1 + np.std(recent_ratings))
                    stability_scores[title] = stability
            
            convergence_data['stability_scores'] = stability_scores
            convergence_data['most_stable'] = max(stability_scores.items(), key=lambda x: x[1])[0] if stability_scores else None
            convergence_data['least_stable'] = min(stability_scores.items(), key=lambda x: x[1])[0] if stability_scores else None
        
        # Calculate overall system convergence
        if len(self.elo_history) >= 5:
            recent_variance = []
            for i in range(-5, 0):
                ratings = list(self.elo_history[i].values())
                recent_variance.append(np.var(ratings))
            
            convergence_data['system_convergence'] = {
                'variance_trend': 'decreasing' if recent_variance[-1] < recent_variance[0] else 'increasing',
                'variance_values': recent_variance
            }
        
        return convergence_data
    
    def _perform_clustering(self):
        """Perform clustering analysis to identify anime groups"""
        if len(self.df) < 3:
            return {'error': 'Not enough data for clustering'}
        
        # Prepare features for clustering
        features = ['elo', 'rd', 'volatility', 'games_played']
        available_features = [f for f in features if f in self.df.columns and self.df[f].notna().all()]
        
        if len(available_features) < 2:
            return {'error': 'Insufficient features for clustering'}
        
        X = self.df[available_features].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Determine optimal number of clusters
        n_clusters = min(4, len(self.df) // 2)
        if n_clusters < 2:
            n_clusters = 2
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Analyze clusters
        cluster_analysis = {}
        for i in range(n_clusters):
            cluster_mask = clusters == i
            cluster_anime = self.df[cluster_mask]
            
            cluster_analysis[f'cluster_{i}'] = {
                'anime': cluster_anime['title'].tolist(),
                'characteristics': {
                    'avg_elo': cluster_anime['elo'].mean(),
                    'avg_rd': cluster_anime['rd'].mean() if 'rd' in cluster_anime else None,
                    'avg_volatility': cluster_anime['volatility'].mean() if 'volatility' in cluster_anime else None,
                    'size': len(cluster_anime)
                }
            }
        
        return cluster_analysis
    
    def _analyze_reliability(self):
        """Analyze rating reliability across the dataset"""
        reliability_data = {}
        
        # Calculate reliability scores
        from app.elo import calculate_rating_reliability
        reliability_scores = {}
        for anime in self.anime_list:
            reliability_scores[anime['title']] = calculate_rating_reliability(anime)
        
        reliability_data['scores'] = reliability_scores
        reliability_data['average_reliability'] = np.mean(list(reliability_scores.values()))
        reliability_data['most_reliable'] = max(reliability_scores.items(), key=lambda x: x[1])
        reliability_data['least_reliable'] = min(reliability_scores.items(), key=lambda x: x[1])
        
        # Categorize by reliability
        high_reliability = [title for title, score in reliability_scores.items() if score >= 80]
        medium_reliability = [title for title, score in reliability_scores.items() if 50 <= score < 80]
        low_reliability = [title for title, score in reliability_scores.items() if score < 50]
        
        reliability_data['categories'] = {
            'high': high_reliability,
            'medium': medium_reliability,
            'low': low_reliability
        }
        
        return reliability_data

def generate_comprehensive_visualizations(anime_list, elo_history, stats_dict):
    """Generate comprehensive visualizations"""
    plots_created = []
    
    # Create output directory
    plot_dir = os.path.join('app', 'static', 'plots')
    os.makedirs(plot_dir, exist_ok=True)
    
    # 1. ELO Distribution with Confidence Intervals
    plt.figure(figsize=(12, 8))
    
    # Main distribution
    plt.subplot(2, 2, 1)
    elos = [anime['elo'] for anime in anime_list]
    plt.hist(elos, bins=min(15, len(elos)//2), alpha=0.7, color='skyblue', edgecolor='black')
    plt.axvline(np.mean(elos), color='red', linestyle='--', label=f'Mean: {np.mean(elos):.1f}')
    plt.axvline(np.median(elos), color='green', linestyle='--', label=f'Median: {np.median(elos):.1f}')
    plt.xlabel('ELO Rating')
    plt.ylabel('Frequency')
    plt.title('ELO Rating Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. Rating vs Uncertainty
    plt.subplot(2, 2, 2)
    elos = [anime['elo'] for anime in anime_list]
    rds = [anime.get('rd', 100) for anime in anime_list]
    plt.scatter(elos, rds, alpha=0.6, s=50)
    plt.xlabel('ELO Rating')
    plt.ylabel('Rating Deviation (Uncertainty)')
    plt.title('Rating vs Uncertainty')
    plt.grid(True, alpha=0.3)
    
    # 3. Convergence over time
    plt.subplot(2, 2, 3)
    if len(elo_history) > 1:
        # Plot top 5 anime convergence
        top_anime = sorted(anime_list, key=lambda x: x['elo'], reverse=True)[:5]
        for anime in top_anime:
            title = anime['title']
            ratings = [state.get(title, anime['elo']) for state in elo_history]
            plt.plot(range(len(ratings)), ratings, label=title[:15] + '...' if len(title) > 15 else title, marker='o', markersize=3)
        
        plt.xlabel('Comparison Number')
        plt.ylabel('ELO Rating')
        plt.title('Top 5 Anime Rating Convergence')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        plt.grid(True, alpha=0.3)
    
    # 4. Reliability vs Rating
    plt.subplot(2, 2, 4)
    from app.elo import calculate_rating_reliability
    elos = [anime['elo'] for anime in anime_list]
    reliabilities = [calculate_rating_reliability(anime) for anime in anime_list]
    colors = ['red' if r < 50 else 'orange' if r < 80 else 'green' for r in reliabilities]
    plt.scatter(elos, reliabilities, c=colors, alpha=0.6, s=50)
    plt.xlabel('ELO Rating')
    plt.ylabel('Reliability Score')
    plt.title('Rating Reliability Analysis')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = os.path.join(plot_dir, 'comprehensive_analysis.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    plots_created.append('comprehensive_analysis.png')
    
    # 5. Detailed Convergence Plot
    if len(elo_history) > 5:
        plt.figure(figsize=(14, 8))
        
        # System variance over time
        plt.subplot(2, 1, 1)
        variances = []
        for state in elo_history:
            ratings = list(state.values())
            variances.append(np.var(ratings))
        
        plt.plot(range(len(variances)), variances, 'b-', linewidth=2, marker='o', markersize=4)
        plt.xlabel('Comparison Number')
        plt.ylabel('Rating Variance')
        plt.title('System Convergence: Rating Variance Over Time')
        plt.grid(True, alpha=0.3)
        
        # Individual anime trajectories
        plt.subplot(2, 1, 2)
        for anime in anime_list:
            title = anime['title']
            ratings = [state.get(title, anime['elo']) for state in elo_history]
            plt.plot(range(len(ratings)), ratings, alpha=0.7, linewidth=1)
        
        plt.xlabel('Comparison Number')
        plt.ylabel('ELO Rating')
        plt.title('All Anime Rating Trajectories')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = os.path.join(plot_dir, 'convergence_analysis.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        plots_created.append('convergence_analysis.png')
    
    # 6. Advanced Statistics Visualization
    plt.figure(figsize=(15, 10))
    
    # Box plot of ratings by quartiles
    plt.subplot(2, 3, 1)
    quartiles = pd.qcut([anime['elo'] for anime in anime_list], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
    elos_by_quartile = [[anime['elo'] for i, anime in enumerate(anime_list) if quartiles[i] == q] for q in ['Q1', 'Q2', 'Q3', 'Q4']]
    plt.boxplot(elos_by_quartile, labels=['Q1', 'Q2', 'Q3', 'Q4'])
    plt.ylabel('ELO Rating')
    plt.title('Rating Distribution by Quartiles')
    plt.grid(True, alpha=0.3)
    
    # Volatility distribution
    plt.subplot(2, 3, 2)
    volatilities = [anime.get('volatility', 0.06) for anime in anime_list]
    plt.hist(volatilities, bins=min(10, len(volatilities)//2), alpha=0.7, color='orange', edgecolor='black')
    plt.xlabel('Volatility')
    plt.ylabel('Frequency')
    plt.title('Rating Volatility Distribution')
    plt.grid(True, alpha=0.3)
    
    # Games played vs ELO
    plt.subplot(2, 3, 3)
    games = [anime.get('games_played', 0) for anime in anime_list]
    elos = [anime['elo'] for anime in anime_list]
    plt.scatter(games, elos, alpha=0.6, s=50, color='purple')
    plt.xlabel('Games Played')
    plt.ylabel('ELO Rating')
    plt.title('Experience vs Rating')
    plt.grid(True, alpha=0.3)
    
    # Confidence interval widths
    plt.subplot(2, 3, 4)
    ci_widths = []
    for anime in anime_list:
        ci = anime.get('confidence_interval', (0, 0))
        ci_widths.append(ci[1] - ci[0])
    plt.hist(ci_widths, bins=min(10, len(ci_widths)//2), alpha=0.7, color='green', edgecolor='black')
    plt.xlabel('Confidence Interval Width')
    plt.ylabel('Frequency')
    plt.title('Rating Certainty Distribution')
    plt.grid(True, alpha=0.3)
    
    # Rating vs Percentile
    plt.subplot(2, 3, 5)
    percentiles = [anime.get('percentile', 50) for anime in anime_list]
    ratings = [anime.get('rating', 5) for anime in anime_list]
    plt.scatter(percentiles, ratings, alpha=0.6, s=50, color='red')
    plt.xlabel('Percentile Rank')
    plt.ylabel('Normalized Rating (1-10)')
    plt.title('Percentile vs Normalized Rating')
    plt.grid(True, alpha=0.3)
    
    # Win streak distribution
    plt.subplot(2, 3, 6)
    win_streaks = [anime.get('win_streak', 0) for anime in anime_list]
    plt.hist(win_streaks, bins=min(10, max(win_streaks) + 1), alpha=0.7, color='gold', edgecolor='black')
    plt.xlabel('Current Win Streak')
    plt.ylabel('Frequency')
    plt.title('Win Streak Distribution')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = os.path.join(plot_dir, 'advanced_statistics.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    plots_created.append('advanced_statistics.png')
    
    return plots_created

def generate_reports(anime_list, elo_history):
    """Generate comprehensive reports with advanced analytics"""
    
    # Create analytics instance
    analytics = AdvancedAnalytics(anime_list, elo_history)
    
    # Calculate advanced statistics
    stats_dict = analytics.calculate_advanced_statistics()
    
    # Generate visualizations
    plots_created = generate_comprehensive_visualizations(anime_list, elo_history, stats_dict)
    
    # Calculate confidence intervals (legacy compatibility)
    confidence_intervals = {}
    for anime in anime_list:
        title = anime['title'].strip().strip('"')
        ci = anime.get('confidence_interval', (anime.get('rating', 5) - 0.5, anime.get('rating', 5) + 0.5))
        confidence_intervals[title] = ci
    
    return confidence_intervals, plots_created, stats_dict

def export_detailed_report(anime_list, stats_dict, filename='detailed_anime_report.txt'):
    """Export a detailed text report"""
    report_path = os.path.join('app', 'static', filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPREHENSIVE ANIME ELO RATING ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Basic Statistics
        f.write("BASIC STATISTICS\n")
        f.write("-" * 40 + "\n")
        basic = stats_dict.get('basic', {})
        f.write(f"Total Anime Analyzed: {basic.get('total_anime', 0)}\n")
        f.write(f"Mean ELO Rating: {basic.get('mean_elo', 0):.2f}\n")
        f.write(f"Median ELO Rating: {basic.get('median_elo', 0):.2f}\n")
        f.write(f"Standard Deviation: {basic.get('std_elo', 0):.2f}\n")
        f.write(f"Rating Range: {basic.get('elo_range', 0):.2f}\n")
        f.write(f"Distribution Skewness: {basic.get('skewness', 0):.3f}\n")
        f.write(f"Distribution Kurtosis: {basic.get('kurtosis', 0):.3f}\n\n")
        
        # Top Rankings
        f.write("TOP RANKINGS\n")
        f.write("-" * 40 + "\n")
        sorted_anime = sorted(anime_list, key=lambda x: x['elo'], reverse=True)
        for i, anime in enumerate(sorted_anime[:10], 1):
            reliability = anime.get('reliability', 'N/A')
            f.write(f"{i:2d}. {anime['title']:<30} ELO: {anime['elo']:7.2f} "
                   f"Rating: {anime.get('rating', 0):4.1f} Reliability: {reliability}\n")
        
        f.write("\n")
        
        # Distribution Analysis
        if 'distribution' in stats_dict:
            dist = stats_dict['distribution']
            f.write("DISTRIBUTION ANALYSIS\n")
            f.write("-" * 40 + "\n")
            f.write("Top 10% Anime:\n")
            for anime in dist.get('top_10_percent', []):
                f.write(f"  • {anime}\n")
            f.write("\nBottom 10% Anime:\n")
            for anime in dist.get('bottom_10_percent', []):
                f.write(f"  • {anime}\n")
            f.write(f"\nMost Volatile: {', '.join(dist.get('most_volatile', []))}\n")
            f.write(f"Most Stable: {', '.join(dist.get('most_stable', []))}\n\n")
        
        # Reliability Analysis
        if 'reliability' in stats_dict:
            rel = stats_dict['reliability']
            f.write("RELIABILITY ANALYSIS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Average Reliability Score: {rel.get('average_reliability', 0):.1f}%\n")
            most_rel = rel.get('most_reliable', ('N/A', 0))
            least_rel = rel.get('least_reliable', ('N/A', 0))
            f.write(f"Most Reliable: {most_rel[0]} ({most_rel[1]:.1f}%)\n")
            f.write(f"Least Reliable: {least_rel[0]} ({least_rel[1]:.1f}%)\n\n")
            
            categories = rel.get('categories', {})
            f.write(f"High Reliability (≥80%): {len(categories.get('high', []))} anime\n")
            f.write(f"Medium Reliability (50-79%): {len(categories.get('medium', []))} anime\n")
            f.write(f"Low Reliability (<50%): {len(categories.get('low', []))} anime\n\n")
        
        # Clustering Analysis
        if 'clusters' in stats_dict and 'error' not in stats_dict['clusters']:
            f.write("CLUSTERING ANALYSIS\n")
            f.write("-" * 40 + "\n")
            clusters = stats_dict['clusters']
            for cluster_name, cluster_data in clusters.items():
                f.write(f"\n{cluster_name.upper()}:\n")
                chars = cluster_data.get('characteristics', {})
                f.write(f"  Size: {chars.get('size', 0)} anime\n")
                f.write(f"  Average ELO: {chars.get('avg_elo', 0):.2f}\n")
                if chars.get('avg_rd'):
                    f.write(f"  Average Uncertainty: {chars.get('avg_rd', 0):.2f}\n")
                f.write("  Anime in this cluster:\n")
                for anime in cluster_data.get('anime', []):
                    f.write(f"    • {anime}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("End of Report\n")
    
    return report_path

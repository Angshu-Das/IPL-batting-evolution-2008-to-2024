import pandas as pd
import numpy as np
from scipy import stats
import os

class IPLAnalyzer:
    def __init__(self):
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load the cleaned data with proper error handling"""
        try:
            # Load with low_memory=False to handle mixed types
            self.data = pd.read_csv('data/processed/cleaned_data.csv', low_memory=False)
            print("✅ Cleaned data loaded successfully!")
            print(f"📊 Data shape: {self.data.shape}")
            
            # Ensure year column is integer
            self.data['year'] = pd.to_numeric(self.data['year'], errors='coerce')
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def calculate_batting_stats(self):
        """Calculate comprehensive batting statistics"""
        print("📈 Calculating batting statistics...")
        
        # Filter out rows where batter is missing
        valid_data = self.data[self.data['batter'].notna()]
        
        # Player-level stats by season
        batting_stats = valid_data.groupby(['year', 'batter']).agg({
            'batsman_runs': ['sum', 'count'],
            'is_boundary': 'sum',
            'is_dot_ball': 'sum',
            'is_wicket': 'sum',
            'is_six': 'sum',
            'is_four': 'sum'
        }).reset_index()
        
        batting_stats.columns = [
            'year', 'batter', 'runs_scored', 'balls_faced', 
            'boundaries', 'dot_balls', 'wickets', 'sixes', 'fours'
        ]
        
        # Calculate metrics
        batting_stats['strike_rate'] = (batting_stats['runs_scored'] / batting_stats['balls_faced']) * 100
        batting_stats['boundary_percentage'] = (batting_stats['boundaries'] / batting_stats['balls_faced']) * 100
        batting_stats['dot_ball_percentage'] = (batting_stats['dot_balls'] / batting_stats['balls_faced']) * 100
        batting_stats['six_percentage'] = (batting_stats['sixes'] / batting_stats['balls_faced']) * 100
        batting_stats['four_percentage'] = (batting_stats['fours'] / batting_stats['balls_faced']) * 100
        
        # Handle average (avoid division by zero)
        batting_stats['average'] = batting_stats.apply(
            lambda x: x['runs_scored'] / x['wickets'] if x['wickets'] > 0 else np.nan, 
            axis=1
        )
        
        print(f"✅ Batting stats calculated for {len(batting_stats)} player-seasons")
        return batting_stats
    
    def get_seasonal_trends(self, batting_stats):
        """Calculate seasonal trends"""
        print("📊 Calculating seasonal trends...")
        
        seasonal_trends = batting_stats.groupby('year').agg({
            'strike_rate': 'mean',
            'boundary_percentage': 'mean',
            'dot_ball_percentage': 'mean',
            'six_percentage': 'mean',
            'four_percentage': 'mean',
            'runs_scored': 'mean',
            'balls_faced': 'mean'
        }).reset_index()
        
        # Calculate overall run rate (runs per over)
        seasonal_runs = self.data.groupby('year').agg({
            'total_runs': 'sum',
            'over': 'count'
        }).reset_index()
        seasonal_runs['run_rate'] = (seasonal_runs['total_runs'] / seasonal_runs['over']) * 6
        
        # Merge run rate with other trends
        seasonal_trends = pd.merge(seasonal_trends, seasonal_runs[['year', 'run_rate']], on='year')
        
        print("✅ Seasonal trends calculated")
        return seasonal_trends
    
    def era_comparison(self, era1=(2008, 2013), era2=(2014, 2024)):
        """Compare two eras using statistical tests - FIXED VERSION"""
        print(f"🔬 Comparing eras: {era1} vs {era2}")
        
        era1_data = self.data[(self.data['year'] >= era1[0]) & (self.data['year'] <= era1[1])]
        era2_data = self.data[(self.data['year'] >= era2[0]) & (self.data['year'] <= era2[1])]
        
        # FIXED: Calculate strike rates properly without deprecated method
        def calculate_player_sr(player_data):
            if len(player_data) == 0:
                return np.nan
            runs = player_data['batsman_runs'].sum()
            balls = len(player_data)
            return (runs / balls) * 100 if balls > 0 else np.nan
        
        # Calculate strike rates for each batter in each era
        era1_player_stats = era1_data.groupby('batter').apply(
            lambda x: pd.Series({
                'strike_rate': calculate_player_sr(x),
                'balls_faced': len(x)
            })
        ).reset_index()
        
        era2_player_stats = era2_data.groupby('batter').apply(
            lambda x: pd.Series({
                'strike_rate': calculate_player_sr(x),
                'balls_faced': len(x)
            })
        ).reset_index()
        
        # Filter players with minimum balls faced (e.g., at least 30 balls)
        min_balls = 30
        era1_sr = era1_player_stats[era1_player_stats['balls_faced'] >= min_balls]['strike_rate'].dropna()
        era2_sr = era2_player_stats[era2_player_stats['balls_faced'] >= min_balls]['strike_rate'].dropna()
        
        # Perform t-test only if we have enough data
        if len(era1_sr) > 1 and len(era2_sr) > 1:
            t_stat, p_value = stats.ttest_ind(era1_sr, era2_sr)
        else:
            t_stat, p_value = np.nan, np.nan
        
        # Calculate boundary percentages
        era1_boundary_pct = (era1_data['is_boundary'].sum() / len(era1_data)) * 100
        era2_boundary_pct = (era2_data['is_boundary'].sum() / len(era2_data)) * 100
        
        result = {
            'era1_name': f"{era1[0]}-{era1[1]}",
            'era2_name': f"{era2[0]}-{era2[1]}",
            'era1_avg_sr': era1_sr.mean(),
            'era2_avg_sr': era2_sr.mean(),
            'strike_rate_increase': era2_sr.mean() - era1_sr.mean(),
            'era1_boundary_pct': era1_boundary_pct,
            'era2_boundary_pct': era2_boundary_pct,
            'boundary_increase': era2_boundary_pct - era1_boundary_pct,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05 if not np.isnan(p_value) else False,
            'players_era1': len(era1_sr),
            'players_era2': len(era2_sr)
        }
        
        print("✅ Era comparison completed")
        return result
    
    def top_performers_analysis(self, batting_stats):
        """Analyze top performers across eras"""
        print("🏆 Analyzing top performers...")
        
        # Filter players with significant balls faced (at least 100 balls per season)
        significant_players = batting_stats[batting_stats['balls_faced'] >= 100]
        
        # Top 10 batsmen by strike rate (min 100 balls)
        top_strike_rate = significant_players.nlargest(10, 'strike_rate')[['year', 'batter', 'strike_rate', 'balls_faced']]
        
        # Top 10 boundary hitters
        top_boundary = significant_players.nlargest(10, 'boundary_percentage')[['year', 'batter', 'boundary_percentage', 'balls_faced']]
        
        return {
            'top_strike_rate': top_strike_rate,
            'top_boundary': top_boundary
        }

def run_complete_analysis():
    """Run the complete analysis pipeline"""
    print("=" * 50)
    print("🏏 IPL BATTING EVOLUTION ANALYSIS")
    print("=" * 50)
    
    analyzer = IPLAnalyzer()
    
    if analyzer.data is None:
        print("❌ Cannot proceed - no data loaded")
        return
    
    # 1. Calculate batting stats
    batting_stats = analyzer.calculate_batting_stats()
    
    # 2. Get seasonal trends
    seasonal_trends = analyzer.get_seasonal_trends(batting_stats)
    
    # 3. Era comparison
    era_compare = analyzer.era_comparison()
    
    # 4. Top performers
    top_performers = analyzer.top_performers_analysis(batting_stats)
    
    print("\n" + "=" * 50)
    print("📊 ANALYSIS RESULTS SUMMARY")
    print("=" * 50)
    
    # FIXED: Safe way to get first and last year data
    if len(seasonal_trends) > 0:
        first_year = seasonal_trends['year'].min()
        last_year = seasonal_trends['year'].max()
        
        first_year_sr = seasonal_trends[seasonal_trends['year'] == first_year]['strike_rate']
        last_year_sr = seasonal_trends[seasonal_trends['year'] == last_year]['strike_rate']
        
        print(f"\n📈 STRIKE RATE EVOLUTION:")
        if len(first_year_sr) > 0 and len(last_year_sr) > 0:
            sr_change = last_year_sr.iloc[0] - first_year_sr.iloc[0]
            print(f"   {first_year}: {first_year_sr.iloc[0]:.1f}")
            print(f"   {last_year}: {last_year_sr.iloc[0]:.1f}")
            print(f"   Change: +{sr_change:.1f}")
        else:
            print("   Could not calculate strike rate evolution")
    else:
        print("   No seasonal trends data available")
    
    print(f"\n🎯 ERA COMPARISON ({era_compare['era1_name']} vs {era_compare['era2_name']}):")
    print(f"   Strike Rate: {era_compare['era1_avg_sr']:.1f} → {era_compare['era2_avg_sr']:.1f} (+{era_compare['strike_rate_increase']:.1f})")
    print(f"   Boundary %: {era_compare['era1_boundary_pct']:.1f}% → {era_compare['era2_boundary_pct']:.1f}% (+{era_compare['boundary_increase']:.1f}%)")
    print(f"   Players analyzed: {era_compare['players_era1']} in era1, {era_compare['players_era2']} in era2")
    print(f"   Statistical Significance: {'YES' if era_compare['significant'] else 'NO'} (p-value: {era_compare['p_value']:.4f})")
    
    print(f"\n🏆 TOP 5 STRIKE RATE PLAYERS (min 100 balls):")
    if len(top_performers['top_strike_rate']) > 0:
        print(top_performers['top_strike_rate'].head(5).to_string(index=False))
    else:
        print("   No top performers data")
    
    # Save results
    os.makedirs('data/processed', exist_ok=True)
    seasonal_trends.to_csv('data/processed/seasonal_trends.csv', index=False)
    batting_stats.to_csv('data/processed/batting_stats.csv', index=False)
    
    print(f"\n💾 Results saved to:")
    print(f"   - data/processed/seasonal_trends.csv")
    print(f"   - data/processed/batting_stats.csv")
    
    print(f"\n🎉 ANALYSIS COMPLETED SUCCESSFULLY!")
    
    return batting_stats, seasonal_trends, era_compare

if __name__ == "__main__":
    run_complete_analysis()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for better looking plots
plt.style.use('default')
sns.set_palette("husl")

class IPLVisualizer:
    def __init__(self):
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        self.load_data()
    
    def load_data(self):
        """Load the analysis results"""
        try:
            self.seasonal_trends = pd.read_csv('data/processed/seasonal_trends.csv')
            self.batting_stats = pd.read_csv('data/processed/batting_stats.csv')
            print("✅ Visualization data loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def plot_strike_rate_evolution(self):
        """Plot the evolution of strike rate over years with trend line"""
        plt.figure(figsize=(12, 6))
        
        # Main strike rate line
        plt.plot(self.seasonal_trends['year'], self.seasonal_trends['strike_rate'], 
                marker='o', linewidth=3, markersize=8, color=self.colors[0], label='Strike Rate')
        
        # Add trend line
        x = self.seasonal_trends['year']
        y = self.seasonal_trends['strike_rate']

        # Calculate trend line
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        trend_line = p(x)

        # Plot trend line
        plt.plot(x, trend_line, "r--", alpha=0.8, linewidth=2, label=f'Trend Line (Slope: {z[0]:.2f})')

        # Add some statistics to the chart
        sr_increase = y.iloc[-1] - y.iloc[0]
        avg_growth = sr_increase / (len(x) - 1)

        plt.title('Evolution of Batting Strike Rate in IPL (2007-2024)\n' + 
             f'Total Increase: +{sr_increase:.1f} points | Annual Growth: +{avg_growth:.1f} points/year', 
             fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Average Strike Rate', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('strike_rate_evolution.png', dpi=300, bbox_inches='tight')
        plt.show()

        print("✅ Strike rate evolution chart with trend line saved!")
    
    def plot_boundary_evolution(self):
        """Plot boundary and dot ball evolution"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Boundary percentage
        ax1.plot(self.seasonal_trends['year'], self.seasonal_trends['boundary_percentage'], 
                marker='s', linewidth=2, markersize=6, color=self.colors[1])
        ax1.set_title('Boundary Percentage Evolution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Boundary Percentage (%)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Dot ball percentage
        ax2.plot(self.seasonal_trends['year'], self.seasonal_trends['dot_ball_percentage'], 
                marker='^', linewidth=2, markersize=6, color=self.colors[2])
        ax2.set_title('Dot Ball Percentage Evolution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Dot Ball Percentage (%)')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('boundary_evolution.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Boundary evolution charts saved!")
    
    def plot_six_vs_four_evolution(self):
        """Plot sixes vs fours evolution"""
        plt.figure(figsize=(12, 6))
        
        plt.plot(self.seasonal_trends['year'], self.seasonal_trends['six_percentage'], 
                marker='o', linewidth=2, markersize=6, color='#ff7f0e', label='Six Percentage')
        plt.plot(self.seasonal_trends['year'], self.seasonal_trends['four_percentage'], 
                marker='s', linewidth=2, markersize=6, color='#1f77b4', label='Four Percentage')
        
        plt.title('Evolution of Sixes vs Fours in IPL (2007-2024)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Percentage (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('six_vs_four_evolution.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Six vs Four evolution chart saved!")
    
    def plot_run_rate_evolution(self):
        """Plot run rate evolution"""
        plt.figure(figsize=(12, 6))
        
        plt.plot(self.seasonal_trends['year'], self.seasonal_trends['run_rate'], 
                marker='D', linewidth=2, markersize=6, color=self.colors[3])
        
        plt.title('Evolution of Run Rate in IPL (2007-2024)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Run Rate (Runs per Over)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('run_rate_evolution.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Run rate evolution chart saved!")
    
    def plot_top_performers(self):
        """Plot top performers"""
        # Get top 10 players by strike rate (min 100 balls)
        top_players = self.batting_stats[self.batting_stats['balls_faced'] >= 100]\
            .nlargest(10, 'strike_rate')
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(top_players['batter'], top_players['strike_rate'], 
                       color=self.colors[4], alpha=0.7)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}', ha='left', va='center', fontweight='bold')
        
        plt.title('Top 10 Batsmen by Strike Rate (Min 100 Balls)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Strike Rate')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        plt.savefig('top_performers.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Top performers chart saved!")
    
    def create_comprehensive_dashboard(self):
        """Create a comprehensive dashboard with all charts"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Strike Rate Evolution
        axes[0,0].plot(self.seasonal_trends['year'], self.seasonal_trends['strike_rate'], 
                      marker='o', linewidth=2, color=self.colors[0])
        axes[0,0].set_title('Strike Rate Evolution', fontweight='bold')
        axes[0,0].set_ylabel('Strike Rate')
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Boundary Percentage
        axes[0,1].plot(self.seasonal_trends['year'], self.seasonal_trends['boundary_percentage'], 
                      marker='s', linewidth=2, color=self.colors[1])
        axes[0,1].set_title('Boundary Percentage', fontweight='bold')
        axes[0,1].set_ylabel('Boundary %')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Run Rate
        axes[1,0].plot(self.seasonal_trends['year'], self.seasonal_trends['run_rate'], 
                      marker='D', linewidth=2, color=self.colors[2])
        axes[1,0].set_title('Run Rate Evolution', fontweight='bold')
        axes[1,0].set_xlabel('Year')
        axes[1,0].set_ylabel('Run Rate')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Six vs Four
        axes[1,1].plot(self.seasonal_trends['year'], self.seasonal_trends['six_percentage'], 
                      marker='o', linewidth=2, label='Six %', color='#ff7f0e')
        axes[1,1].plot(self.seasonal_trends['year'], self.seasonal_trends['four_percentage'], 
                      marker='s', linewidth=2, label='Four %', color='#1f77b4')
        axes[1,1].set_title('Sixes vs Fours', fontweight='bold')
        axes[1,1].set_xlabel('Year')
        axes[1,1].set_ylabel('Percentage (%)')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.suptitle('IPL Batting Evolution Analysis Dashboard (2007-2024)', 
                    fontsize=18, fontweight='bold', y=0.95)
        plt.tight_layout()
        plt.savefig('comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Comprehensive dashboard saved!")

def create_all_visualizations():
    """Create all visualizations"""
    print("=" * 50)
    print("🎨 CREATING IPL VISUALIZATIONS")
    print("=" * 50)
    
    visualizer = IPLVisualizer()
    
    # Create individual charts
    visualizer.plot_strike_rate_evolution()
    visualizer.plot_boundary_evolution()
    visualizer.plot_six_vs_four_evolution()
    visualizer.plot_run_rate_evolution()
    visualizer.plot_top_performers()
    
    # Create comprehensive dashboard
    visualizer.create_comprehensive_dashboard()
    
    print("\n" + "=" * 50)
    print("✅ ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
    print("📊 Charts saved in your project folder:")
    print("   - strike_rate_evolution.png")
    print("   - boundary_evolution.png") 
    print("   - six_vs_four_evolution.png")
    print("   - run_rate_evolution.png")
    print("   - top_performers.png")
    print("   - comprehensive_dashboard.png")
    print("=" * 50)

if __name__ == "__main__":
    create_all_visualizations()
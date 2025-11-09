from flask import Flask, render_template, jsonify
import pandas as pd
import json
import os

app = Flask(__name__)

class IPLData:
    def __init__(self):
        self.seasonal_trends = None
        self.batting_stats = None
        self.load_data()
    
    def load_data(self):
        """Load the analysis results"""
        try:
            self.seasonal_trends = pd.read_csv('data/processed/seasonal_trends.csv')
            self.batting_stats = pd.read_csv('data/processed/batting_stats.csv')
            print("✅ Data loaded successfully for web app!")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False

# Initialize data
ipl_data = IPLData()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/trends')
def get_trends():
    """API endpoint for seasonal trends - FIXED VERSION"""
    if ipl_data.seasonal_trends is not None:
        # Convert to list of dictionaries and handle NaN values
        trends_data = ipl_data.seasonal_trends.where(pd.notnull(ipl_data.seasonal_trends), None)
        trends_json = trends_data.to_dict('records')
        
        # Debug: Print first record to see what data is available
        if trends_json:
            print("📊 First trend record:", {k: v for k, v in trends_json[0].items() if v is not None})
        
        return jsonify(trends_json)
    return jsonify([])

@app.route('/api/top_players')
def get_top_players():
    """API endpoint for top players"""
    if ipl_data.batting_stats is not None:
        # Get top 10 players by strike rate (min 100 balls)
        top_players = ipl_data.batting_stats[ipl_data.batting_stats['balls_faced'] >= 100]\
            .nlargest(10, 'strike_rate')[['batter', 'strike_rate', 'year', 'balls_faced']]\
            .to_dict('records')
        return jsonify(top_players)
    return jsonify([])

@app.route('/api/era_comparison')
def get_era_comparison():
    """API endpoint for era comparison"""
    if ipl_data.seasonal_trends is not None:
        # Calculate era comparison
        era1 = ipl_data.seasonal_trends[ipl_data.seasonal_trends['year'].between(2008, 2013)]
        era2 = ipl_data.seasonal_trends[ipl_data.seasonal_trends['year'].between(2014, 2024)]
        
        era_comparison = {
            'era1': {
                'name': '2008-2013',
                'avg_strike_rate': float(era1['strike_rate'].mean()) if not era1.empty else 0,
                'avg_boundary_pct': float(era1['boundary_percentage'].mean()) if not era1.empty else 0
            },
            'era2': {
                'name': '2014-2024', 
                'avg_strike_rate': float(era2['strike_rate'].mean()) if not era2.empty else 0,
                'avg_boundary_pct': float(era2['boundary_percentage'].mean()) if not era2.empty else 0
            }
        }
        return jsonify(era_comparison)
    return jsonify({})

@app.route('/dashboard')
def dashboard():
    """Interactive dashboard page"""
    return render_template('dashboard.html')

@app.route('/players')
def players():
    """Players analysis page"""
    return render_template('players.html')

@app.route('/api/debug')
def debug_data():
    """Debug endpoint to check available data"""
    if ipl_data.seasonal_trends is not None:
        debug_info = {
            'columns': ipl_data.seasonal_trends.columns.tolist(),
            'years': ipl_data.seasonal_trends['year'].tolist(),
            'sample_data': ipl_data.seasonal_trends.head(3).to_dict('records')
        }
        return jsonify(debug_info)
    return jsonify({'error': 'No data loaded'})

if __name__ == '__main__':
    print("🚀 Starting IPL Analysis Web App...")
    print("📊 Available routes:")
    print("   - http://localhost:5000/ (Home)")
    print("   - http://localhost:5000/dashboard (Interactive Charts)")
    print("   - http://localhost:5000/players (Top Players)")
    print("   - http://localhost:5000/api/trends (Data API)")
    print("   - http://localhost:5000/api/debug (Debug Info)")
    app.run(debug=True, port=5000)
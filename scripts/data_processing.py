import pandas as pd
import numpy as np
import os

class DataProcessor:
    def __init__(self):
        self.ball_df = None
        self.match_df = None
        self.merged_df = None
    
    def load_data(self):
        """Load the CSV files from the correct location"""
        try:
            # ✅ CORRECT file paths based on your actual structure
            ball_file = 'data/raw/iiipl.csv'
            match_file = 'data/raw/iiipl2.csv'
            
            print(f"📁 Loading files:")
            print(f"   - {ball_file}")
            print(f"   - {match_file}")
            
            # Load CSV files (not Excel)
            self.ball_df = pd.read_csv(ball_file)
            self.match_df = pd.read_csv(match_file)
            
            print("✅ Data loaded successfully!")
            print(f"📊 Ball data shape: {self.ball_df.shape}")
            print(f"📊 Match data shape: {self.match_df.shape}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print("💡 Make sure your CSV files are in 'data/raw/' folder")
            return False
    
    def clean_data(self):
        """Clean and preprocess the data"""
        print("🧹 Cleaning data...")
        
        # Handle missing values in ball data
        self.ball_df.fillna({
            'extras_type': 'none',
            'player_dismissed': 'not_out',
            'dismissal_kind': 'not_out',
            'fielder': 'none'
        }, inplace=True)
        
        # Convert data types
        self.ball_df['is_wicket'] = self.ball_df['is_wicket'].astype(int)
        
        # Clean match data - handle date conversion
        self.match_df['date'] = pd.to_datetime(self.match_df['date'])
        
        # Extract year from season - handle different season formats
        # Some might be '2008', others '2007/08'
        def extract_year(season):
            if isinstance(season, str):
                # Extract first 4 digits if it's like '2007/08'
                numbers = ''.join(filter(str.isdigit, season))
                if len(numbers) >= 4:
                    return int(numbers[:4])
            return None
        
        self.match_df['year'] = self.match_df['season'].apply(extract_year)
        
        print("✅ Data cleaning completed!")
    
    def merge_datasets(self):
        """Merge ball and match data"""
        print("🔗 Merging datasets...")
        
        self.merged_df = pd.merge(
            self.ball_df, 
            self.match_df, 
            left_on='match_id', 
            right_on='id', 
            how='left'
        )
        
        # Create additional useful columns
        self.merged_df['is_boundary'] = self.merged_df['batsman_runs'].isin([4, 6])
        self.merged_df['is_dot_ball'] = (self.merged_df['total_runs'] == 0) & (self.merged_df['extras_type'] == 'none')
        self.merged_df['is_six'] = self.merged_df['batsman_runs'] == 6
        self.merged_df['is_four'] = self.merged_df['batsman_runs'] == 4
        
        print("✅ Datasets merged successfully!")
        print(f"📊 Merged data shape: {self.merged_df.shape}")
        
        return self.merged_df
    
    def save_cleaned_data(self, output_path='data/processed/cleaned_data.csv'):
        """Save cleaned data to CSV"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.merged_df.to_csv(output_path, index=False)
        print(f"✅ Cleaned data saved to: {output_path}")
        
        # Also save some basic stats
        basic_stats = {
            'total_matches': self.merged_df['match_id'].nunique(),
            'total_balls': len(self.merged_df),
            'total_seasons': self.merged_df['year'].nunique(),
            'seasons_range': f"{self.merged_df['year'].min()}-{self.merged_df['year'].max()}",
            'unique_players': self.merged_df['batter'].nunique(),
            'unique_teams': pd.concat([self.merged_df['team1'], self.merged_df['team2']]).nunique()
        }
        
        print("\n📈 Dataset Summary:")
        for key, value in basic_stats.items():
            print(f"   {key}: {value}")

def process_data():
    """Main function to process the data"""
    processor = DataProcessor()
    
    # Load data
    if processor.load_data():
        # Clean data
        processor.clean_data()
        
        # Merge datasets
        merged_data = processor.merge_datasets()
        
        # Save cleaned data
        processor.save_cleaned_data()
        
        print("\n🎉 SUCCESS! Data processing completed!")
        print("🚀 You can now run analysis scripts!")
        
        return merged_data
    else:
        print("\n❌ Data processing failed!")
        return None

if __name__ == "__main__":
    process_data()
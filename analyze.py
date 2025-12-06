import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

from ingest_data import ingest_streaming_data
from utility_methods import (ensure_results_directory,
                             filter_by_date_range,
                             filter_by_bools,
                             save_data)
from visualize import (
    create_listening_histogram,
    create_hourly_listening_pattern,
    create_monthly_listening_trend,
    create_top_artists_chart,
    create_top_tracks_chart,
    create_skip_analysis_charts,
    create_generic_pie
)


def load_date_range():
    """
    Load start and end dates from environment variables.
    Can use either START_DATE/END_DATE or YEAR.
    
    Returns:
        tuple: (start_date, end_date, timezone) as datetime objects and timezone string
    """
    load_dotenv()
    
    # Get timezone from environment (default to America/New_York)
    timezone = os.getenv('TIMEZONE', 'America/New_York')
    
    # Check if YEAR is specified
    year_str = os.getenv('YEAR')
    if year_str:
        try:
            year = int(year_str)
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            print(f"Analyzing year: {year}")
            print(f"Timezone: {timezone}")
            return start_date, end_date, timezone
        except ValueError:
            print(f"Warning: Invalid YEAR format in .env. Use YYYY format.")
    
    # Otherwise use START_DATE and END_DATE
    start_date_str = os.getenv('START_DATE')
    end_date_str = os.getenv('END_DATE')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            print(f"Start date: {start_date.date()}")
        except ValueError:
            print(f"Warning: Invalid START_DATE format in .env. Use YYYY-MM-DD format.")
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            print(f"End date: {end_date.date()}")
        except ValueError:
            print(f"Warning: Invalid END_DATE format in .env. Use YYYY-MM-DD format.")
    
    if start_date or end_date:
        print(f"Timezone: {timezone}")
    
    return start_date, end_date, timezone





def main():
    """
    Main analysis entry point.
    """
    print("Starting Spotify data analysis...\n")
    
    # Ensure Results directory exists
    results_dir = ensure_results_directory()
    print(f"Results directory ready: {results_dir}\n")
    
    # Load date range from .env
    start_date, end_date, timezone = load_date_range()
    if start_date and end_date:
        date_range = f"{start_date.date()} to {end_date.date()}"
    if not date_range:
        date_range = "All available data"
    
    # Ingest streaming data
    print("Ingesting streaming data...")
    df = ingest_streaming_data()
    save_data(df, title='combined_streaming_data', output_dir=results_dir)
    
    if df.empty:
        print("No data to analyze.")
        return
    
    print()
    
    # Filter by date range if dates are provided
    if start_date or end_date:
        df = filter_by_date_range(df, start_date, end_date)
    
    # Filter by boolean flags from .env
    SPOTIFY_DEFINED_PLAY = os.getenv('SPOTIFY_DEFINED_PLAY', 'False').lower() in ('true', '1', 't')
    MUSIC_ONLY_MODE = os.getenv('MUSIC_ONLY_MODE', 'False').lower() in ('true', '1', 't')
    df = filter_by_bools(df, spotify_defined_play=SPOTIFY_DEFINED_PLAY, music_only_mode=MUSIC_ONLY_MODE)
    save_data(df, title='filtered_streaming_data', output_dir=results_dir)
    
    # Create visualizations
    print("Generating visualizations...")
    create_listening_histogram(df, output_dir=results_dir)
    create_hourly_listening_pattern(df, timezone=timezone, output_dir=results_dir)
    create_monthly_listening_trend(df, output_dir=results_dir)
    create_top_artists_chart(df, output_dir=results_dir)
    create_top_tracks_chart(df, output_dir=results_dir)
    create_skip_analysis_charts(df, output_dir=results_dir)
    create_generic_pie(df, column='platform', title=f'Listening by Platform from {date_range}', output_dir=results_dir)
    create_generic_pie(df, column='conn_country', title=f'Listening by Country from {date_range}', output_dir=results_dir)
    create_generic_pie(df, column='reason_end', title=f'Listening by Reason End from {date_range}', output_dir=results_dir)
    print()
    
    # TODO: Add analysis logic here
    print("Analysis complete!")
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Date range in data: {df['ts'].min()} to {df['ts'].max()}")


if __name__ == '__main__':
    main()

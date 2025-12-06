from pathlib import Path
import pandas as pd


def ensure_results_directory(results_dir='Results'):
    """
    Check if the Results directory exists, and create it if it doesn't.
    
    Args:
        results_dir (str): Path to the results directory (default: 'Results')
        
    Returns:
        Path: Path object for the results directory
    """
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)
    return results_path

def filter_by_date_range(df, start_date=None, end_date=None, date_column='ts'):
    """
    Filter the DataFrame by date range.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        start_date (datetime): Start date for filtering (inclusive)
        end_date (datetime): End date for filtering (inclusive)
        date_column (str): Name of the date column to filter on
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if date_column not in df.columns:
        print(f"Warning: Date column '{date_column}' not found in data.")
        return df
    
    # Convert date column to datetime if it's not already
    df[date_column] = pd.to_datetime(df[date_column])
    
    filtered_df = df.copy()
    
    if start_date:
        # Make start_date timezone-aware if the column has timezone info
        if filtered_df[date_column].dt.tz is not None:
            start_date = pd.to_datetime(start_date).tz_localize('UTC')
        filtered_df = filtered_df[filtered_df[date_column] >= start_date]
        print(f"Filtered to records from {start_date.date()} onwards")
    
    if end_date:
        # Make end_date timezone-aware if the column has timezone info
        if filtered_df[date_column].dt.tz is not None:
            end_date = pd.to_datetime(end_date).tz_localize('UTC')
        filtered_df = filtered_df[filtered_df[date_column] <= end_date]
        print(f"Filtered to records up to {end_date.date()}")
    
    print(f"Records after date filtering: {len(filtered_df)}")



    return filtered_df

def filter_by_bools(df, spotify_defined_play=False, music_only_mode=False):
    """
    Filter the DataFrame by date range.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        start_date (datetime): Start date for filtering (inclusive)
        end_date (datetime): End date for filtering (inclusive)
        date_column (str): Name of the date column to filter on
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """

    # Final filtering for 30 second plays if bool is set
    if spotify_defined_play:
        df = df[df['ms_played'] >= 30000]
        print(f"Records with at least 30 seconds played: {len(df)}")
    
    if music_only_mode:
        df = df[df['episode_name'].isnull()]
        print(f"Records filtered to music only (no podcasts): {len(df)}")
        df = df[df['master_metadata_album_artist_name'] != "Spotify"]
        print(f"Records filtered to exclude Spotify as artist: {len(df)}")
   


    return df

def save_data(df,title, output_dir='Results'):
    """
    Save the combined data to a CSV file.
    
    Args:
        df (pd.DataFrame): The combined data to save
        output_dir (str): Directory to save the output file
    """
    output_path = Path(output_dir) / f'{title}.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Combined data saved to: {output_path}")
    print(f"Shape: {df.shape}")

import pandas as pd
from pathlib import Path

def ingest_streaming_data(data_folder='Data/Spotify Extended Streaming History'):
    """
    Ingest all JSON files from the extended streaming data folder and combine them into a single DataFrame.
    
    Args:
        data_folder (str): Path to the folder containing JSON files
        
    Returns:
        pd.DataFrame: Combined data from all JSON files
    """
    data_path = Path(data_folder)
    
    # Check if the folder exists
    if not data_path.exists():
        raise FileNotFoundError(f"Folder not found: {data_folder}")
    
    # Get all JSON files in the folder
    json_files = sorted(data_path.glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in {data_folder}")
        return pd.DataFrame()
    
    # Read and combine all JSON files
    dataframes = []
    for json_file in json_files:
        try:
            df = pd.read_json(json_file)
            dataframes.append(df)
            print(f"Loaded: {json_file.name} - {len(df)} records")
        except Exception as e:
            print(f"Error reading {json_file.name}: {e}")
    
    # Combine all dataframes
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        print(f"\nTotal records ingested: {len(combined_df)}")
        print(f"Columns: {list(combined_df.columns)}")
        return combined_df
    else:
        return pd.DataFrame()


def save_combined_data(df, output_file='Results/combined_streaming_data.csv'):
    """
    Save the combined data to a CSV file.
    
    Args:
        df (pd.DataFrame): The combined data to save
        output_file (str): Path to the output file
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Combined data saved to: {output_file}")
    print(f"Shape: {df.shape}")


if __name__ == '__main__':
    # Ingest the data
    streaming_data = ingest_streaming_data()
    
    # Save to a CSV file
    if not streaming_data.empty:
        save_combined_data(streaming_data)
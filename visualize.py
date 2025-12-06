import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


def create_listening_histogram(df, date_column='ts', output_dir='Results'):
    """
    Create a histogram showing the number of tracks listened to over time.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        date_column (str): Name of the date column
        output_dir (str): Directory to save the visualization
        
    Returns:
        str: Path to the saved HTML file
    """
    # Ensure the date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Extract date (without time) for grouping
    df['date'] = df[date_column].dt.date
    
    # Count tracks per day
    daily_counts = df.groupby('date').size().reset_index(name='track_count')
    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
    
    # Create the histogram
    fig = px.bar(
        daily_counts,
        x='date',
        y='track_count',
        title='Tracks Listened Per Day',
        labels={'date': 'Date', 'track_count': 'Number of Tracks'},
        color='track_count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Tracks',
        hovermode='x unified',
        showlegend=False
    )
    
    # Save to HTML
    output_path = Path(output_dir) / 'listening_histogram.html'
    fig.write_html(output_path)
    print(f"Histogram saved to: {output_path}")
    
    return str(output_path)


def create_hourly_listening_pattern(df, date_column='ts', timezone='America/New_York', output_dir='Results'):
    """
    Create a visualization showing listening patterns by hour of day in a specific timezone.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        date_column (str): Name of the date column
        timezone (str): Timezone to convert to (e.g., 'America/New_York', 'Europe/London', 'America/Los_Angeles')
        output_dir (str): Directory to save the visualization
        
    Returns:
        str: Path to the saved HTML file
    """
    # Ensure the date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Convert to specified timezone
    if df[date_column].dt.tz is not None:
        df['local_time'] = df[date_column].dt.tz_convert(timezone)
    else:
        # If no timezone, assume UTC and convert
        df['local_time'] = df[date_column].dt.tz_localize('UTC').dt.tz_convert(timezone)
    
    # Extract hour in local timezone
    df['hour'] = df['local_time'].dt.hour
    
    # Count tracks per hour
    hourly_counts = df.groupby('hour').size().reset_index(name='track_count')
    
    # Create bar chart
    fig = px.bar(
        hourly_counts,
        x='hour',
        y='track_count',
        title=f'Listening Patterns by Hour of Day ({timezone})',
        labels={'hour': 'Hour of Day', 'track_count': 'Number of Tracks'},
        color='track_count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_title='Hour of Day (0-23)',
        yaxis_title='Number of Tracks',
        showlegend=False
    )
    
    # Save to HTML
    output_path = Path(output_dir) / 'hourly_listening_pattern.html'
    fig.write_html(output_path)
    print(f"Hourly pattern saved to: {output_path}")
    
    return str(output_path)


def create_monthly_listening_trend(df, date_column='ts', output_dir='Results'):
    """
    Create a line chart showing listening trends by month.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        date_column (str): Name of the date column
        output_dir (str): Directory to save the visualization
        
    Returns:
        str: Path to the saved HTML file
    """
    # Ensure the date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Extract year-month
    df['year_month'] = df[date_column].dt.to_period('M').astype(str)
    
    # Count tracks per month
    monthly_counts = df.groupby('year_month').size().reset_index(name='track_count')
    
    # Create line chart
    fig = px.line(
        monthly_counts,
        x='year_month',
        y='track_count',
        title='Monthly Listening Trend',
        labels={'year_month': 'Month', 'track_count': 'Number of Tracks'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Number of Tracks',
        hovermode='x unified'
    )
    
    # Save to HTML
    output_path = Path(output_dir) / 'monthly_listening_trend.html'
    fig.write_html(output_path)
    print(f"Monthly trend saved to: {output_path}")
    
    return str(output_path)


def create_top_artists_chart(df, artist_column='master_metadata_album_artist_name', 
                             top_n=20, output_dir='Results'):
    """
    Create a bar chart of top artists by play count.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        artist_column (str): Name of the artist column
        top_n (int): Number of top artists to display
        output_dir (str): Directory to save the visualization
        
    Returns:
        str: Path to the saved HTML file
    """
    # Count plays per artist
    artist_counts = df[artist_column].value_counts().head(top_n).reset_index()
    artist_counts.columns = ['artist', 'play_count']
    
    # Create horizontal bar chart
    fig = px.bar(
        artist_counts,
        y='artist',
        x='play_count',
        orientation='h',
        title=f'Top {top_n} Artists by Play Count',
        labels={'artist': 'Artist', 'play_count': 'Number of Plays'},
        color='play_count',
        color_continuous_scale='Plasma'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    # Save to HTML
    output_path = Path(output_dir) / 'top_artists.html'
    fig.write_html(output_path)
    print(f"Top artists chart saved to: {output_path}")
    
    return str(output_path)


def create_top_tracks_chart(df, track_column='master_metadata_track_name',
                            artist_column='master_metadata_album_artist_name',
                            top_n=20, output_dir='Results'):
    """
    Create a bar chart of top tracks by play count.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        track_column (str): Name of the track column
        artist_column (str): Name of the artist column
        top_n (int): Number of top tracks to display
        output_dir (str): Directory to save the visualization
        
    Returns:
        str: Path to the saved HTML file
    """
    # Create combined track-artist identifier
    df['track_artist'] = df[track_column] + ' - ' + df[artist_column]
    
    # Count plays per track
    track_counts = df['track_artist'].value_counts().head(top_n).reset_index()
    track_counts.columns = ['track', 'play_count']
    
    # Create horizontal bar chart
    fig = px.bar(
        track_counts,
        y='track',
        x='play_count',
        orientation='h',
        title=f'Top {top_n} Tracks by Play Count',
        labels={'track': 'Track - Artist', 'play_count': 'Number of Plays'},
        color='play_count',
        color_continuous_scale='Turbo'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    # Save to HTML
    output_path = Path(output_dir) / 'top_tracks.html'
    fig.write_html(output_path)
    print(f"Top tracks chart saved to: {output_path}")
    
    return str(output_path)


def create_skip_analysis_charts(df, track_column='master_metadata_track_name',
                                artist_column='master_metadata_album_artist_name',
                                skipped_column='skipped',
                                reason_column='reason_end',
                                top_n=50, output_dir='Results'):
    """
    Create visualizations analyzing track skipping behavior.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        track_column (str): Name of the track column
        artist_column (str): Name of the artist column
        skipped_column (str): Name of the skipped boolean column
        reason_column (str): Name of the reason_end column
        top_n (int): Number of top tracks to display
        output_dir (str): Directory to save the visualization
        
    Returns:
        list: Paths to the saved HTML files
    """
    output_paths = []
    
    # Check if we have skip data
    if skipped_column not in df.columns and reason_column not in df.columns:
        print(f"Warning: No skip data found in dataset.")
        return output_paths
    
    # Create combined track-artist identifier
    df['track_artist'] = df[track_column] + ' - ' + df[artist_column]
    
    # Analysis using 'skipped' column if available
    if skipped_column in df.columns:
        # Most skipped tracks
        skipped_df = df[df[skipped_column] == True].copy()
        if not skipped_df.empty:
            most_skipped = skipped_df['track_artist'].value_counts().head(top_n).reset_index()
            most_skipped.columns = ['track', 'skip_count']
            
            fig = px.bar(
                most_skipped,
                y='track',
                x='skip_count',
                orientation='h',
                title=f'Top {top_n} Most Skipped Tracks',
                labels={'track': 'Track - Artist', 'skip_count': 'Times Skipped'},
                color='skip_count',
                color_continuous_scale='Reds'
            )
            
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            
            output_path = Path(output_dir) / 'most_skipped_tracks.html'
            fig.write_html(output_path)
            print(f"Most skipped tracks chart saved to: {output_path}")
            output_paths.append(str(output_path))
        
        # Least skipped tracks (among tracks played multiple times)
        track_stats = df.groupby('track_artist').agg({
            skipped_column: ['sum', 'count']
        }).reset_index()
        track_stats.columns = ['track', 'skip_count', 'total_plays']
        
        # Filter to tracks with at least 10 plays to make it meaningful
        track_stats = track_stats[track_stats['total_plays'] >= 10]
        track_stats['skip_rate'] = track_stats['skip_count'] / track_stats['total_plays']
        least_skipped = track_stats.nsmallest(top_n, 'skip_rate')
        
        if not least_skipped.empty:
            fig = px.bar(
                least_skipped,
                y='track',
                x='skip_rate',
                orientation='h',
                title=f'Top {top_n} Least Likely to be Skipped Tracks (min 10 plays)',
                labels={'track': 'Track - Artist', 'skip_rate': 'Skip Rate'},
                color='skip_rate',
                color_continuous_scale='Greens_r'
            )
            
            fig.update_layout(
                yaxis={'categoryorder': 'total descending'},
                showlegend=False
            )
            
            output_path = Path(output_dir) / 'least_skipped_tracks.html'
            fig.write_html(output_path)
            print(f"Least skipped tracks chart saved to: {output_path}")
            output_paths.append(str(output_path))

        most_skipped = track_stats.nlargest(top_n, 'skip_rate')
        if not most_skipped.empty:
            fig = px.bar(
                most_skipped,
                y='track',
                x='skip_rate',
                orientation='h',
                title=f'Top {top_n} Most Likely to be Skipped Tracks (min 10 plays)',
                labels={'track': 'Track - Artist', 'skip_rate': 'Skip Rate'},
                color='skip_rate',
                color_continuous_scale='Reds'
            )
            
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            
            output_path = Path(output_dir) / 'most_likely_skipped_tracks.html'
            fig.write_html(output_path)
            print(f"Most likely skipped tracks chart saved to: {output_path}")
            output_paths.append(str(output_path))
    
    # Analysis using 'reason_end' column
    if reason_column in df.columns:
        # Tracks most often skipped (based on reason_end)
        skip_reasons = ['fwdbtn']  # Common skip indicators
        skipped_by_reason = df[df[reason_column].isin(['fwdbtn'])].copy()
        
        if not skipped_by_reason.empty:
            reason_skipped = skipped_by_reason['track_artist'].value_counts().head(top_n).reset_index()
            reason_skipped.columns = ['track', 'skip_count']
            
            fig = px.bar(
                reason_skipped,
                y='track',
                x='skip_count',
                orientation='h',
                title=f'Top {top_n} Most Skipped Tracks (by skip button)',
                labels={'track': 'Track - Artist', 'skip_count': 'Times Skipped'},
                color='skip_count',
                color_continuous_scale='OrRd'
            )
            
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            
            output_path = Path(output_dir) / 'most_skipped_by_button.html'
            fig.write_html(output_path)
            print(f"Most skipped tracks (by button) chart saved to: {output_path}")
            output_paths.append(str(output_path))
    
    return output_paths

def create_generic_pie(df, column, title, output_dir='Results'):
    """
    Create a generic pie chart for any categorical column.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        column (str): Name of the categorical column
        title (str): Title of the pie chart
        output_dir (str): Directory to save the output HTML file
        filename (str): Name of the output HTML file
    """
    # Count occurrences of each category
    category_counts = df[column].value_counts().reset_index()
    category_counts.columns = [column, 'count']
    
    # Create pie chart
    fig = px.pie(
        category_counts,
        names=column,
        values='count',
        title=title,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    
    filename=f'{title}_pie_chart.html'
    # Save to HTML
    output_path = Path(output_dir) / filename
    fig.write_html(output_path)
    print(f"Pie chart saved to: {output_path}")
    
    return str(output_path)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


def _get_datetime_series(df, date_column='ts'):
    """Return a normalized datetime series for the requested date column."""
    if date_column not in df.columns:
        return None

    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    return df[date_column]


def _format_timestamp(timestamp):
    """Format a pandas timestamp for display in chart titles."""
    if pd.isna(timestamp):
        return None

    if timestamp.tzinfo is not None:
        return timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')

    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def _build_title_with_time_range(title, df, date_column='ts', timezone=None):
    """Append the dataframe-derived time range to a chart title."""
    timestamps = _get_datetime_series(df, date_column)
    if timestamps is None:
        return title

    timestamps = timestamps.dropna()
    if timestamps.empty:
        return title

    if timezone:
        if timestamps.dt.tz is not None:
            timestamps = timestamps.dt.tz_convert(timezone)
        else:
            timestamps = timestamps.dt.tz_localize('UTC').dt.tz_convert(timezone)

    start_time = _format_timestamp(timestamps.min())
    end_time = _format_timestamp(timestamps.max())
    return f'{title}<br><sup>{start_time} to {end_time}</sup>'


def _get_expanded_year_palette():
    """Return a large de-duplicated qualitative palette for many year categories."""
    palette = []
    for color_set in (
        px.colors.qualitative.Alphabet,
        px.colors.qualitative.Dark24,
        px.colors.qualitative.Light24,
        px.colors.qualitative.Safe,
        px.colors.qualitative.Vivid,
        px.colors.qualitative.Bold,
        px.colors.qualitative.Set3,
        px.colors.qualitative.Plotly,
    ):
        for color in color_set:
            if color not in palette:
                palette.append(color)
    return palette


def _prepare_yearly_top_tracks_with_first_heard(
    df,
    track_column='master_metadata_track_name',
    artist_column='master_metadata_album_artist_name',
    top_n=20,
    date_column='ts',
    first_heard_df=None,
):
    """Prepare yearly ranked top tracks merged with first-heard timestamps."""
    required_columns = {track_column, artist_column, date_column}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        print(f"Warning: Missing columns for first-heard track ranking chart: {sorted(missing_columns)}")
        return None, None

    working_df = df.copy()
    working_df[date_column] = _get_datetime_series(working_df, date_column)
    working_df = working_df.dropna(subset=[date_column, track_column, artist_column])

    if working_df.empty:
        print("Warning: No valid data available for first-heard track ranking chart.")
        return None, None

    first_heard_source_df = working_df if first_heard_df is None else first_heard_df.copy()
    first_heard_source_df[date_column] = _get_datetime_series(first_heard_source_df, date_column)
    first_heard_source_df = first_heard_source_df.dropna(subset=[date_column, track_column, artist_column])

    if first_heard_source_df.empty:
        print("Warning: No valid data available for first-heard source timestamps.")
        return None, None

    working_df['track_artist'] = working_df[track_column] + ' - ' + working_df[artist_column]
    first_heard_source_df['track_artist'] = (
        first_heard_source_df[track_column] + ' - ' + first_heard_source_df[artist_column]
    )
    working_df['year'] = working_df[date_column].dt.year

    first_heard = (
        first_heard_source_df.groupby('track_artist', as_index=False)[date_column]
        .min()
        .rename(columns={date_column: 'first_heard'})
    )

    yearly_track_counts = (
        working_df.groupby(['year', 'track_artist'], as_index=False)
        .size()
        .rename(columns={'size': 'play_count'})
    )
    yearly_track_counts['rank'] = (
        yearly_track_counts.groupby('year')['play_count']
        .rank(method='dense', ascending=False)
        .astype(int)
    )

    ranked_tracks = yearly_track_counts[yearly_track_counts['rank'] <= top_n].copy()
    if ranked_tracks.empty:
        print("Warning: No ranked tracks available for first-heard track ranking chart.")
        return None, None

    ranked_tracks = ranked_tracks.merge(first_heard, on='track_artist', how='left')
    ranked_tracks['year_label'] = ranked_tracks['year'].astype(str)
    ranked_tracks['first_heard_label'] = ranked_tracks['first_heard'].apply(_format_timestamp)
    ranked_tracks['first_heard_year'] = ranked_tracks['first_heard'].dt.year

    return ranked_tracks, working_df


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
    df[date_column] = _get_datetime_series(df, date_column)
    
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
        title=_build_title_with_time_range('Tracks Listened Per Day', df, date_column=date_column),
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
    df[date_column] = _get_datetime_series(df, date_column)
    
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
        title=_build_title_with_time_range(
            f'Listening Patterns by Hour of Day ({timezone})',
            df,
            date_column=date_column,
            timezone=timezone,
        ),
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
    df[date_column] = _get_datetime_series(df, date_column)
    
    # Extract year-month
    df['year_month'] = df[date_column].dt.to_period('M').astype(str)
    
    # Count tracks per month
    monthly_counts = df.groupby('year_month').size().reset_index(name='track_count')
    
    # Create line chart
    fig = px.line(
        monthly_counts,
        x='year_month',
        y='track_count',
        title=_build_title_with_time_range('Monthly Listening Trend', df, date_column=date_column),
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
                             top_n=20, date_column='ts', output_dir='Results'):
    """
    Create a bar chart of top artists by play count.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        artist_column (str): Name of the artist column
        top_n (int): Number of top artists to display
        date_column (str): Name of the date column
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
        title=_build_title_with_time_range(
            f'Top {top_n} Artists by Play Count',
            df,
            date_column=date_column,
        ),
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
                            top_n=20, date_column='ts', output_dir='Results'):
    """
    Create a bar chart of top tracks by play count.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        track_column (str): Name of the track column
        artist_column (str): Name of the artist column
        top_n (int): Number of top tracks to display
        date_column (str): Name of the date column
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
        title=_build_title_with_time_range(
            f'Top {top_n} Tracks by Play Count',
            df,
            date_column=date_column,
        ),
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


def create_top_tracks_first_heard_by_year_chart(
    df,
    track_column='master_metadata_track_name',
    artist_column='master_metadata_album_artist_name',
    top_n=20,
    date_column='ts',
    first_heard_df=None,
    output_dir='Results',
):
    """
    Create a scatter plot comparing a track's first listen date to its yearly ranking.

    Args:
        df (pd.DataFrame): The streaming data DataFrame
        track_column (str): Name of the track column
        artist_column (str): Name of the artist column
        top_n (int): Maximum yearly rank to include per year
        date_column (str): Name of the date column
        first_heard_df (pd.DataFrame | None): Source dataframe for first-heard timestamps
        output_dir (str): Directory to save the visualization

    Returns:
        str | None: Path to the saved HTML file when data is available
    """
    ranked_tracks, working_df = _prepare_yearly_top_tracks_with_first_heard(
        df,
        track_column=track_column,
        artist_column=artist_column,
        top_n=top_n,
        date_column=date_column,
        first_heard_df=first_heard_df,
    )
    if ranked_tracks is None:
        return None

    fig = px.scatter(
        ranked_tracks,
        x='first_heard',
        y='rank',
        color='year_label',
        size='play_count',
        hover_name='track_artist',
        hover_data={
            'year_label': True,
            'rank': True,
            'play_count': True,
            'first_heard_label': True,
            'first_heard': False,
        },
        title=_build_title_with_time_range(
            f'First Heard Date vs Yearly Top {top_n} Track Rank',
            working_df,
            date_column=date_column,
        ),
        labels={
            'first_heard': 'First Time Heard',
            'rank': 'Yearly Rank',
            'play_count': 'Play Count',
            'year_label': 'Year',
            'first_heard_label': 'First Heard',
        },
        color_discrete_sequence=_get_expanded_year_palette(),
    )

    fig.update_layout(
        xaxis_title='First Time Heard',
        yaxis_title='Yearly Rank (1 = highest play count)',
        legend_title='Year',
    )
    fig.update_yaxes(autorange='reversed', dtick=1)

    output_path = Path(output_dir) / 'top_tracks_first_heard_by_year.html'
    fig.write_html(output_path)
    print(f"Top tracks first-heard-by-year chart saved to: {output_path}")

    return str(output_path)


def create_top_tracks_first_heard_same_year_percentage_chart(
    df,
    track_column='master_metadata_track_name',
    artist_column='master_metadata_album_artist_name',
    top_n=20,
    date_column='ts',
    first_heard_df=None,
    output_dir='Results',
):
    """
    Create a chart showing the share of yearly top tracks first heard in the same year.

    Args:
        df (pd.DataFrame): The streaming data DataFrame
        track_column (str): Name of the track column
        artist_column (str): Name of the artist column
        top_n (int): Maximum yearly rank to include per year
        date_column (str): Name of the date column
        first_heard_df (pd.DataFrame | None): Source dataframe for first-heard timestamps
        output_dir (str): Directory to save the visualization

    Returns:
        str | None: Path to the saved HTML file when data is available
    """
    ranked_tracks, working_df = _prepare_yearly_top_tracks_with_first_heard(
        df,
        track_column=track_column,
        artist_column=artist_column,
        top_n=top_n,
        date_column=date_column,
        first_heard_df=first_heard_df,
    )
    if ranked_tracks is None:
        return None

    ranked_tracks['first_heard_same_year'] = ranked_tracks['first_heard_year'] == ranked_tracks['year']
    yearly_summary = (
        ranked_tracks.groupby('year', as_index=False)
        .agg(
            top_track_count=('track_artist', 'nunique'),
            first_heard_same_year_count=('first_heard_same_year', 'sum'),
        )
        .sort_values('year')
    )

    if yearly_summary.empty:
        print("Warning: No data available for first-heard same-year percentage chart.")
        return None

    yearly_summary['same_year_percentage'] = (
        yearly_summary['first_heard_same_year_count'] / yearly_summary['top_track_count']
    ) * 100
    yearly_summary['year_label'] = yearly_summary['year'].astype(str)

    fig = px.bar(
        yearly_summary,
        x='year_label',
        y='same_year_percentage',
        color='year_label',
        text=yearly_summary['same_year_percentage'].round(1).astype(str) + '%',
        hover_data={
            'year_label': True,
            'same_year_percentage': ':.2f',
            'first_heard_same_year_count': True,
            'top_track_count': True,
        },
        title=_build_title_with_time_range(
            f'Percent of Yearly Top {top_n} Tracks First Heard in the Same Year',
            working_df,
            date_column=date_column,
        ),
        labels={
            'year_label': 'Year',
            'same_year_percentage': 'Percent of Top Tracks',
            'first_heard_same_year_count': 'Tracks First Heard That Year',
            'top_track_count': 'Total Top Tracks',
        },
        color_discrete_sequence=_get_expanded_year_palette(),
    )

    fig.update_layout(showlegend=False)
    fig.update_yaxes(range=[0, 100], ticksuffix='%')

    output_path = Path(output_dir) / 'top_tracks_first_heard_same_year_percentage.html'
    fig.write_html(output_path)
    print(f"Top tracks first-heard same-year percentage chart saved to: {output_path}")

    return str(output_path)


def create_skip_analysis_charts(df, track_column='master_metadata_track_name',
                                artist_column='master_metadata_album_artist_name',
                                skipped_column='skipped',
                                reason_column='reason_end',
                                top_n=50, date_column='ts', output_dir='Results'):
    """
    Create visualizations analyzing track skipping behavior.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        track_column (str): Name of the track column
        artist_column (str): Name of the artist column
        skipped_column (str): Name of the skipped boolean column
        reason_column (str): Name of the reason_end column
        top_n (int): Number of top tracks to display
        date_column (str): Name of the date column
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
                title=_build_title_with_time_range(
                    f'Top {top_n} Most Skipped Tracks',
                    df,
                    date_column=date_column,
                ),
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
                title=_build_title_with_time_range(
                    f'Top {top_n} Least Likely to be Skipped Tracks (min 10 plays)',
                    df,
                    date_column=date_column,
                ),
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
                title=_build_title_with_time_range(
                    f'Top {top_n} Most Likely to be Skipped Tracks (min 10 plays)',
                    df,
                    date_column=date_column,
                ),
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
                title=_build_title_with_time_range(
                    f'Top {top_n} Most Skipped Tracks (by skip button)',
                    df,
                    date_column=date_column,
                ),
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

def create_generic_pie(df, column, title, date_column='ts', output_dir='Results'):
    """
    Create a generic pie chart for any categorical column.
    
    Args:
        df (pd.DataFrame): The streaming data DataFrame
        column (str): Name of the categorical column
        title (str): Title of the pie chart
        date_column (str): Name of the date column
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
        title=_build_title_with_time_range(title, df, date_column=date_column),
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    
    filename=f'{title}_pie_chart.html'
    # Save to HTML
    output_path = Path(output_dir) / filename
    fig.write_html(output_path)
    print(f"Pie chart saved to: {output_path}")
    
    return str(output_path)
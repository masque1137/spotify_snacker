# Spotify Snacker 🎵

> Because Spotify's Yearly Wrapped has gotten lame

A Python-based tool to analyze your Spotify Extended Streaming History and generate comprehensive visualizations of your listening habits.

## Features

### Data Analysis
- **Extended Streaming History Support**: Processes Spotify's extended streaming history JSON files
- **Date Range Filtering**: Analyze specific time periods or entire listening history
- **Smart Filtering Options**:
  - Filter by minimum play duration (30+ seconds for "real" plays)
  - Music-only mode (exclude podcasts)
  - Timezone-aware analysis

### Visualizations

The tool generates interactive HTML visualizations using Plotly:

#### Temporal Analysis
- **Daily Listening Histogram**: Track count per day over time
- **Hourly Listening Patterns**: See when you listen most throughout the day (timezone-aware)
- **Monthly Trends**: Long-term listening behavior across months

#### Content Analysis
- **Top Artists**: Your most-played artists
- **Top Tracks**: Your most-played songs (with artist attribution)
- **Platform Distribution**: Where you listen (desktop, mobile, web, etc.)
- **Country Distribution**: Geographic breakdown of listening sessions
- **Reason End Analysis**: How your listening sessions end (completed, skipped, etc.)

#### Skip Behavior Analysis
- **Most Skipped Tracks**: Tracks you frequently skip
- **Most Likely to Skip**: Tracks with highest skip rates (min. 10 plays)
- **Least Likely to Skip**: Your never-skip favorites (min. 10 plays)
- **Skip Button Analysis**: Tracks manually skipped via forward button

## Setup

### Prerequisites
- Python 3.7+
- Spotify Extended Streaming History data

### Installation

1. Clone the repository:
```bash
git clone https://github.com/masque1137/spotify_snacker.git
cd spotify_snacker
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Request your Spotify data:
   - Go to [Spotify Privacy Settings](https://www.spotify.com/account/privacy/)
   - Request "Extended Streaming History"
   - Wait for Spotify to prepare your data (can take several days)
   - Download and extract to the `Data/Spotify Extended Streaming History/` folder

## Configuration

Create a `.env` file in the project root to customize analysis parameters:

```env
# Date Range Options (Option 1: Specify a year)
YEAR=2024

# Date Range Options (Option 2: Specify start and end dates)
START_DATE=2024-01-01
END_DATE=2024-12-31

# Timezone for hourly analysis (default: America/New_York)
TIMEZONE=America/New_York

# Filtering Options
SPOTIFY_DEFINED_PLAY=True    # Only count plays 30+ seconds
MUSIC_ONLY_MODE=True          # Exclude podcasts and Spotify-created content
```

NOTE: if YEAR is filled in, START_DATE and END_DATE will be ignored

### Configuration Options

- **YEAR**: Analyze a specific year (takes precedence over START_DATE/END_DATE)
- **START_DATE** / **END_DATE**: Custom date range (format: YYYY-MM-DD)
- **TIMEZONE**: Your timezone for hourly patterns (e.g., 'America/Los_Angeles', 'Europe/London', defaults to America/New York)
- **SPOTIFY_DEFINED_PLAY**: Filter to plays over 30 seconds (Spotify's metric for "real" plays)
- **MUSIC_ONLY_MODE**: Exclude podcasts and Spotify-generated content

## Usage

Run the analysis:

```bash
python analyze.py
```

Results will be saved to the `Results/` directory as interactive HTML files.

## Project Structure

```
spotify_snacker/
├── analyze.py              # Main analysis script
├── ingest_data.py          # Data ingestion functions
├── visualize.py            # Visualization generation
├── utility_methods.py      # Helper functions (filtering, saving)
├── Data/
│   └── Spotify Extended Streaming History/
│       └── Streaming_History_Audio_*.json
└── Results/                # Generated visualizations (HTML files)
```

## Output Files

All visualizations are saved as interactive HTML files in the `Results/` directory:

- `combined_streaming_data.csv` - Raw combined data
- `filtered_streaming_data.csv` - Data after applying filters
- `listening_histogram.html` - Daily listening activity
- `hourly_listening_pattern.html` - Hourly patterns
- `monthly_listening_trend.html` - Monthly trends
- `top_artists.html` - Top 20 artists
- `top_tracks.html` - Top 20 tracks
- `most_skipped_tracks.html` - Most skipped content
- `least_skipped_tracks.html` - Least skipped content
- `most_likely_skipped_tracks.html` - Highest skip rate tracks
- `Listening by Platform_pie_chart.html` - Platform distribution
- `Listening by Country_pie_chart.html` - Country distribution
- `Listening by Reason End_pie_chart.html` - Session end reasons

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Plotly](https://plotly.com/python/) - Interactive visualizations
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Configuration management

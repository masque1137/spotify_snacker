from pathlib import Path


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

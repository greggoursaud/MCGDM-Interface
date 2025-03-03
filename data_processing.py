import pandas as pd

def load_data(agents_file, weights_file):
    """
    Load the agent scores and criteria weights from CSV files.
    
    Args:
        agents_file: Path to the CSV file containing agent scores
        weights_file: Path to the CSV file containing criteria weights
    
    Returns:
        tuple: (agents_df, weights_df) - DataFrames
    """
    # Read the agents scores CSV file into a pandas DataFrame
    try:
        agents_df = pd.read_csv(agents_file, index_col=0)
    except Exception as e:
        raise ValueError(f"Error reading agents scores file: {e}")

    # Read the criteria weights CSV file into a pandas DataFrame
    try:
        weights_df = pd.read_csv(weights_file, index_col=0)
    except Exception as e:
        raise ValueError(f"Error reading criteria weights file: {e}")

    # Validate the data
    validate_data(agents_df, weights_df)
    
    return agents_df, weights_df

def validate_data(agents_df, weights_df):
    """
    Validate agent scores and weights DataFrames for missing values and headers.
    
    Args:
        agents_df: DataFrame containing agent scores
        weights_df: DataFrame containing criteria weights
    
    Raises:
        ValueError: If validation fails
    """
    # Check for missing values
    if agents_df.isnull().values.any():
        raise ValueError("Agents scores file contains missing values.")
    if weights_df.isnull().values.any():
        raise ValueError("Criteria weights file contains missing values.")

    # Check for missing headers
    if agents_df.columns.isnull().any() or agents_df.index.isnull().any():
        raise ValueError("Agents scores file is missing headers.")
    if weights_df.columns.isnull().any() or weights_df.index.isnull().any():
        raise ValueError("Criteria weights file is missing headers.")
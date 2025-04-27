import pandas as pd
import numpy as np

def calculate_statistics(weights_df):
    """
    Calculate statistical measures for criteria weights.
    
    Args:
        weights_df: DataFrame containing criteria weights
        
    Returns:
        DataFrame: Criteria assessment characteristics
    """
    if weights_df.empty:
        raise ValueError("weights_df cannot be empty")
        
    # Calculate the first quartile (Q1), third quartile (Q3), Min, and Max for each criterion
    Q1 = weights_df.quantile(0.25)
    Q3 = weights_df.quantile(0.75)
    Min = weights_df.min()
    Max = weights_df.max()

    # Filter the data to include only the values between Q1 and Q3
    mask = (weights_df >= Q1) & (weights_df <= Q3)
    masked_values = weights_df.where(mask)
    SICP = masked_values.mean()

    # Combine the statistics into a single DataFrame
    criteria_assessment_characteristics = pd.DataFrame({
        'Min': Min,
        'Q1': Q1,
        'SICP': SICP,
        'Q3': Q3,
        'Max': Max
    }).transpose()
    
    return criteria_assessment_characteristics

def apply_score_bell(value, min_val, q1_val, sicp_val, q3_val, max_val):
    """
    Apply the Score Bell equations based on the value's position.
    
    Args:
        value: The value to calculate score for
        min_val, q1_val, sicp_val, q3_val, max_val: Statistical reference points
        
    Returns:
        float: Calculated score between 0 and 100
    """
    try:
        if value < q1_val:
            # Zone 1 (Dispersion Zone)
            xrel = value - min_val
            denominator = q1_val - min_val
            return np.exp(np.log(50) * ((xrel / denominator) ** 2))
        elif value < sicp_val:
            # Zone 2 (Influence Zone)
            xrel = value - q1_val
            denominator = sicp_val - q1_val
            return 101 - np.exp(np.log(51) * ((1 - (xrel / denominator)) ** 2))
        elif value <= q3_val:
            # Zone 3 (Influence Zone)
            xrel = value - sicp_val
            denominator = q3_val - sicp_val
            return 101 - np.exp(np.log(51) * ((xrel / denominator) ** 2))
        else:
            # Zone 4 (Dispersion Zone)
            xrel = value - q3_val
            denominator = max_val - q3_val
            return np.exp(np.log(50) * ((1 - (xrel / denominator)) ** 2))
    except Exception as e:
        print(f"Error calculating score bell for value {value}: {str(e)}")
        raise

def calculate_percentage_score_matrix(hsm):
    """
    Calculate the percentage score matrix (λ_ij) from the decision matrix (HSM).
    
    Args:
        hsm: Decision matrix as a numpy array
        
    Returns:
        numpy.ndarray: Percentage score matrix
    """
    # Calculate the column sums
    column_sums = hsm.sum(axis=0)
    
    # Compute the percentage score matrix
    percentage_score_matrix = (hsm / column_sums) * 100
    
    return percentage_score_matrix

def calculate_criteria_weights(final_dm_weights_df, weights_df):
    """
    Calculate the aggregated criteria weights with correction factor.
    
    Args:
        final_dm_weights_df: DataFrame with percentage scores
        weights_df: DataFrame with original criteria weights
        
    Returns:
        list: Corrected criteria weights
    """
    # Convert DataFrames to numpy arrays 
    final_dm_weights_array = final_dm_weights_df.to_numpy()
    weights_array = weights_df.to_numpy() / 100
    
    # Element-wise multiplication of the arrays
    weighted_scores = final_dm_weights_array * weights_array
    
    # Sum the results along the appropriate axis (axis=0 for summing columns)
    aggregated_weights = np.sum(weighted_scores, axis=0)
    
    # Calculate the correction factor (β)
    weights_sum = np.sum(aggregated_weights)
    correction_factor = 100 / weights_sum
    
    # Apply the correction factor to normalize the weights
    corrected_weights = aggregated_weights * correction_factor
    
    return corrected_weights.tolist()

def calculate_final_scores(corrected_weights, agents_df):
    """
    Calculate the final scores and rankings for candidates.
    
    Args:
        corrected_weights: List of corrected weights for each criterion
        agents_df: DataFrame with agent scores
        
    Returns:
        DataFrame: Final scores and rankings
    """
    # Convert the agents DataFrame to a numpy array
    agents_array = agents_df.to_numpy()
    
    # Convert corrected weights to a numpy array
    corrected_weights_array = np.array(corrected_weights)
    
    # Calculate the weighted scores for each criterion
    weighted_scores = agents_array * corrected_weights_array
    
    # Calculate the total score for each candidate
    total_scores = np.sum(weighted_scores, axis=1)
    
    # Create a DataFrame with the individual weighted scores
    weighted_scores_df = pd.DataFrame(weighted_scores, index=agents_df.index, columns=agents_df.columns)
    
    # Add the total scores as a new column
    weighted_scores_df['Total Score'] = total_scores
    
    # Calculate rankings based on total scores (descending order)
    # Handle ties with the same rank using pandas rank method
    rankings = (-weighted_scores_df['Total Score']).rank(method='min').astype(int)
    weighted_scores_df['Ranking'] = rankings
    
    return weighted_scores_df
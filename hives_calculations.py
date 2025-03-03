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
    # Calculate the first quartile (Q1), third quartile (Q3), Min, and Max for each criterion
    Q1 = weights_df.quantile(0.25)
    Q3 = weights_df.quantile(0.75)
    Min = weights_df.min()
    Max = weights_df.max()

    # Filter the data to include only the values between Q1 and Q3
    characteristics_df = weights_df.apply(lambda x: x[(x >= Q1[x.name]) & (x <= Q3[x.name])])

    # Calculate the average of the filtered values for each criterion (SICP)
    SICP = characteristics_df.mean()

    # Combine the statistics into a single DataFrame
    criteria_assessment_characteristics = pd.DataFrame({
        'Min': Min,
        'Q1': Q1,
        'SICP': SICP,
        'Q3': Q3,
        'Max': Max
    }).transpose()
    
    return criteria_assessment_characteristics

def calculate_relative_distance(value, min_val, q1_val, sicp_val, q3_val, max_val):
    """
    Calculate the relative distance of a value within its statistical zone.
    
    Args:
        value: The value to calculate relative distance for
        min_val, q1_val, sicp_val, q3_val, max_val: Statistical reference points
        
    Returns:
        float: Calculated relative distance
    """
    if value < q1_val:
        return value - min_val
    elif value < sicp_val:
        return value - q1_val
    elif value <= q3_val:
        return value - sicp_val
    else:
        return value - q3_val

def apply_score_bell(value, min_val, q1_val, sicp_val, q3_val, max_val):
    """
    Apply the Score Bell equations based on the value's position.
    
    Args:
        value: The value to calculate score for
        min_val, q1_val, sicp_val, q3_val, max_val: Statistical reference points
        
    Returns:
        float: Calculated score
    """
    if value < q1_val:
        #zone = 1 (Dispersion Zone)
        xrel = value - min_val
        return np.exp(np.log(50) * ((xrel / (q1_val - min_val)) ** 2))
    elif value < sicp_val:
        #zone = 2 (Influence Zone)
        xrel = value - q1_val
        return 101 - np.exp(np.log(51) * ((1 - (xrel / (sicp_val - q1_val))) ** 2))
    elif value <= q3_val:
        #zone = 3 (Influence Zone)
        xrel = value - sicp_val
        return 101 - np.exp(np.log(51) * ((xrel / (q3_val - sicp_val)) ** 2))
    else:
        #zone = 4 (Dispersion Zone)
        xrel = value - q3_val
        return np.exp(np.log(50) * ((1 - (xrel / (max_val - q3_val))) ** 2))

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
    correction_factor = 100 / np.sum(aggregated_weights)
    
    # Apply the correction factor to normalize the weights
    corrected_weights = aggregated_weights * correction_factor
    
    # Return the result as a list
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
    
    # Calculate the total score for each candidate by summing the weighted scores across the criteria
    total_scores = np.sum(weighted_scores, axis=1)
    
    # Create a DataFrame with the individual weighted scores
    weighted_scores_df = pd.DataFrame(weighted_scores, index=agents_df.index, columns=agents_df.columns)
    
    # Add the total scores as a new column to the DataFrame
    weighted_scores_df['Total Score'] = total_scores
    
    # Add the ranking based on the total scores
    weighted_scores_df['Ranking'] = weighted_scores_df['Total Score'].rank(ascending=False, method='min').astype(int)
    
    return weighted_scores_df
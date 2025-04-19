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
    # Input validation
    if not isinstance(weights_df, pd.DataFrame):
        raise TypeError("weights_df must be a pandas DataFrame")
    
    if weights_df.empty:
        raise ValueError("weights_df cannot be empty")
    
    # Check for non-numeric values
    if not weights_df.applymap(lambda x: isinstance(x, (int, float))).all().all():
        raise ValueError("All values in weights_df must be numeric")
        
    # Calculate the first quartile (Q1), third quartile (Q3), Min, and Max for each criterion
    Q1 = weights_df.quantile(0.25)
    Q3 = weights_df.quantile(0.75)
    Min = weights_df.min()
    Max = weights_df.max()
    
    # Check for cases where Min == Max, which would cause issues in calculations
    for col in weights_df.columns:
        if abs(Max[col] - Min[col]) < 1e-10:
            # If all values are the same, set Q1 and Q3 equal to Min/Max to avoid division by zero later
            Q1[col] = Min[col]
            Q3[col] = Max[col]
            weights_df[col] = weights_df[col] + np.random.normal(0, 1e-5, size=len(weights_df))
            
    # Re-calculate if we made adjustments
    if any(abs(Max - Min) < 1e-10):
        Q1 = weights_df.quantile(0.25)
        Q3 = weights_df.quantile(0.75)
        Min = weights_df.min()
        Max = weights_df.max()

    # Filter the data to include only the values between Q1 and Q3
    # Add a small buffer to avoid empty dataframes if all values are very close
    characteristics_df = weights_df.apply(lambda x: x[(x >= Q1[x.name] - 1e-10) & (x <= Q3[x.name] + 1e-10)])

    # Check if we have empty rows after filtering and handle them
    if characteristics_df.isna().all().any():
        # For any column with all NaN, use the original values
        for col in characteristics_df.columns:
            if characteristics_df[col].isna().all():
                characteristics_df[col] = weights_df[col]

    # Calculate the average of the filtered values for each criterion (SICP)
    SICP = characteristics_df.mean()
    
    # If any SICP is NaN (should not happen with the above checks), set it to the average of Q1 and Q3
    if SICP.isna().any():
        for col in SICP.index:
            if np.isnan(SICP[col]):
                SICP[col] = (Q1[col] + Q3[col]) / 2

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
    # Input validation
    if not all(isinstance(x, (int, float)) for x in [value, min_val, q1_val, sicp_val, q3_val, max_val]):
        raise TypeError("All inputs to apply_score_bell must be numeric")
    
    # Handle NaN inputs
    if np.isnan(value) or np.isnan(min_val) or np.isnan(q1_val) or np.isnan(sicp_val) or np.isnan(q3_val) or np.isnan(max_val):
        return 50.0  # Return a neutral score if any inputs are NaN
    
    if value < q1_val:
        # Zone 1 (Dispersion Zone)
        xrel = value - min_val
        # Prevent division by zero
        denominator = q1_val - min_val
        if abs(denominator) < 1e-10:
            return 50.0  # Return a neutral score to avoid numerical issues
        return np.exp(np.log(50) * ((xrel / denominator) ** 2))
    elif value < sicp_val:
        # Zone 2 (Influence Zone)
        xrel = value - q1_val
        # Prevent division by zero
        denominator = sicp_val - q1_val
        if abs(denominator) < 1e-10:
            return 100.0  # Return highest score for this zone
        return 101 - np.exp(np.log(51) * ((1 - (xrel / denominator)) ** 2))
    elif value <= q3_val:
        # Zone 3 (Influence Zone)
        xrel = value - sicp_val
        # Prevent division by zero
        denominator = q3_val - sicp_val
        if abs(denominator) < 1e-10:
            return 100.0  # Return highest score for this zone
        return 101 - np.exp(np.log(51) * ((xrel / denominator) ** 2))
    else:
        # Zone 4 (Dispersion Zone)
        xrel = value - q3_val
        # Prevent division by zero
        denominator = max_val - q3_val
        if abs(denominator) < 1e-10:
            return 50.0  # Return a neutral score to avoid numerical issues
        return np.exp(np.log(50) * ((1 - (xrel / denominator)) ** 2))

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
    # Avoid division by zero by adding a small epsilon
    column_sums = np.where(column_sums == 0, 1e-10, column_sums)
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
    # Input validation
    if not isinstance(final_dm_weights_df, pd.DataFrame) or not isinstance(weights_df, pd.DataFrame):
        raise TypeError("Inputs must be pandas DataFrames")
    
    if final_dm_weights_df.shape != weights_df.shape:
        raise ValueError("DataFrames must have the same shape")
    
    # Convert DataFrames to numpy arrays 
    final_dm_weights_array = final_dm_weights_df.to_numpy()
    weights_array = weights_df.to_numpy() / 100
    
    # Check for NaN values and replace them
    final_dm_weights_array = np.nan_to_num(final_dm_weights_array, nan=100/final_dm_weights_array.shape[1])
    weights_array = np.nan_to_num(weights_array, nan=1/weights_array.shape[1])
    
    # Element-wise multiplication of the arrays
    weighted_scores = final_dm_weights_array * weights_array
    
    # Sum the results along the appropriate axis (axis=0 for summing columns)
    aggregated_weights = np.sum(weighted_scores, axis=0)
    
    # Calculate the correction factor (β)
    # Protect against division by zero
    sum_weights = np.sum(aggregated_weights)
    if abs(sum_weights) < 1e-10:
        # If sum is close to zero, assign equal weights
        corrected_weights = np.ones(len(aggregated_weights)) * (100.0 / len(aggregated_weights))
    else:
        correction_factor = 100 / sum_weights
        # Apply the correction factor to normalize the weights
        corrected_weights = aggregated_weights * correction_factor
    
    # Ensure weights sum to 100 (with small floating point tolerance)
    if not (99.9 <= np.sum(corrected_weights) <= 100.1):
        # Normalize to exactly 100
        corrected_weights = (corrected_weights / np.sum(corrected_weights)) * 100
    
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
    # Input validation
    if not isinstance(corrected_weights, (list, np.ndarray)) or not isinstance(agents_df, pd.DataFrame):
        raise TypeError("Invalid input types")
    
    if len(corrected_weights) != agents_df.shape[1]:
        raise ValueError("Number of weights must match number of criteria")
    
    # Print debug info
    print(f"Debug: Corrected weights shape: {len(corrected_weights)}")
    print(f"Debug: Agents DataFrame shape: {agents_df.shape}")
    
    # Check weights for NaN values
    if any(np.isnan(w) for w in corrected_weights):
        print("Warning: NaN values detected in weights, replacing with equal weights")
        corrected_weights = [100.0 / len(corrected_weights)] * len(corrected_weights)
    
    # Convert the agents DataFrame to a numpy array
    agents_array = agents_df.to_numpy()
    
    # Convert corrected weights to a numpy array
    corrected_weights_array = np.array(corrected_weights)
    
    # Check for NaN values in the agents array
    if np.isnan(agents_array).any():
        print("Warning: NaN values detected in alternatives data, replacing with zeros")
        
    # Replace NaN and infinite values with appropriate defaults
    agents_array = np.nan_to_num(agents_array, nan=50.0, posinf=100.0, neginf=0.0)
    
    # Calculate the weighted scores for each criterion
    weighted_scores = agents_array * corrected_weights_array
    
    # Calculate the total score for each candidate
    total_scores = np.sum(weighted_scores, axis=1)
    
    # Create a DataFrame with the individual weighted scores
    weighted_scores_df = pd.DataFrame(weighted_scores, index=agents_df.index, columns=agents_df.columns)
    
    # Add the total scores as a new column
    weighted_scores_df['Total Score'] = total_scores
    
    # Handle ranking with NaN values
    # Sort by total score (descending) and assign ranks
    rankings = pd.Series(index=agents_df.index, dtype=float)
    sorted_indices = np.argsort(-total_scores)  # Negative for descending order
    for rank, idx in enumerate(sorted_indices, 1):
        rankings.iloc[idx] = rank
    
    weighted_scores_df['Ranking'] = rankings
    
    # One final check for any remaining NaN values
    if weighted_scores_df.isna().any().any():
        print("Warning: NaN values still present in the final results, applying final fix")
        weighted_scores_df = weighted_scores_df.fillna(0.0)
    
    return weighted_scores_df
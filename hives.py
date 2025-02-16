import pandas as pd
import numpy as np
import time

def hives_algorithm(agents_df, weights_df):

    start_time = time.time()

      # Read the agents scores CSV file into a pandas DataFrame
    try:
        agents_df = pd.read_csv(agents_df, index_col=0)
    except Exception as e:
        raise ValueError(f"Error reading agents scores file: {e}")

    # Read the criteria weights CSV file into a pandas DataFrame
    try:
        weights_df = pd.read_csv(weights_df, index_col=0)
    except Exception as e:
        raise ValueError(f"Error reading criteria weights file: {e}")

    # Check for missing values in the DataFrames
    if agents_df.isnull().values.any():
        raise ValueError("Agents scores file contains missing values.")
    if weights_df.isnull().values.any():
        raise ValueError("Criteria weights file contains missing values.")

    # Check for missing headers
    if agents_df.columns.isnull().any() or agents_df.index.isnull().any():
        raise ValueError("Agents scores file is missing headers.")
    if weights_df.columns.isnull().any() or weights_df.index.isnull().any():
        raise ValueError("Criteria weights file is missing headers.")

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

    # Define a function to calculate the relative distance (xrel) for each value
    def calculate_xrel(value, min_val, q1_val, sicp_val, q3_val, max_val):
        if value < q1_val:
            return value - min_val
        elif value < sicp_val:
            return value - q1_val
        elif value <= q3_val:
            return value - sicp_val
        else:
            return value - q3_val

    # Apply the function to calculate the relative distance for each value in the weights_df
    xrel_df = weights_df.apply(lambda x: x.apply(calculate_xrel, args=(Min[x.name], Q1[x.name], SICP[x.name], Q3[x.name], Max[x.name])))


    # Define the function to apply the Score Bell equations based on the value
    def apply_score_bell(value, min_val, q1_val, sicp_val, q3_val, max_val):
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

    # Apply the Score Bell function to each value in the weights_df
    score_bell_df = weights_df.apply(lambda x: x.apply(apply_score_bell, args=(Min[x.name], Q1[x.name], SICP[x.name], Q3[x.name], Max[x.name])))


    # Define a function to calculate the percentage score matrix (λ_ij) from the decision matrix (HSM)
    def calculate_percentage_score_matrix(HSM):
        # Calculate the column sums
        column_sums = HSM.sum(axis=0)
        # Compute the percentage score matrix
        percentage_score_matrix = (HSM / column_sums) * 100
        return percentage_score_matrix

    # Convert score_bell_df to a numpy array and calculate the percentage score matrix
    HSM = score_bell_df.to_numpy()
    lambda_matrix = calculate_percentage_score_matrix(HSM)

    # Convert lambda_matrix back to a DataFrame
    final_dm_weights_df = pd.DataFrame(lambda_matrix, index=score_bell_df.index, columns=score_bell_df.columns)

    def calculate_criteria_weights(final_dm_weights_df, weights_df):
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

    def final_candidates_scores(corrected_weights, agents_df):
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

    # Calculate the criteria weights
    criteria_weights = calculate_criteria_weights(final_dm_weights_df, weights_df)

    # Calculate the final scores for each candidate
    final_scores_df = final_candidates_scores(criteria_weights, agents_df)

    final_scores_df = final_scores_df.reset_index().rename(columns={"index": "Candidates"})


    #print(final_scores_df)

    #print("--- %s seconds ---" % (time.time() - start_time))
    #print("done")

    return final_scores_df


hives_algorithm('candidates_scores.csv', 'criteria_weights.csv')
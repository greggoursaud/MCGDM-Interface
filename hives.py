import pandas as pd
import numpy as np
import time

from data_processing import load_data
from hives_calculations import (
    calculate_statistics,
    apply_score_bell,
    calculate_percentage_score_matrix,
    calculate_criteria_weights,
    calculate_final_scores
)

def hives_algorithm(agents_file, weights_file):
    """
    Implement the HIVES algorithm for multi-criteria group decision making.
    
    Args:
        agents_file: Path to CSV file with agent/alternative scores
        weights_file: Path to CSV file with criteria weights
        
    Returns:
        DataFrame: Final scores and rankings for candidates
    """
    start_time = time.time()

    # Load and validate input data
    agents_df, weights_df = load_data(agents_file, weights_file)
    
    # Calculate statistical measures
    criteria_assessment_characteristics = calculate_statistics(weights_df)
    
    # Extract statistical values for easier reference
    Min = criteria_assessment_characteristics.loc['Min']
    Q1 = criteria_assessment_characteristics.loc['Q1']
    SICP = criteria_assessment_characteristics.loc['SICP']
    Q3 = criteria_assessment_characteristics.loc['Q3']
    Max = criteria_assessment_characteristics.loc['Max']
    
    # Apply the Score Bell function to each value in the weights_df
    score_bell_df = weights_df.apply(lambda x: x.apply(apply_score_bell, args=(Min[x.name], Q1[x.name], SICP[x.name], Q3[x.name], Max[x.name])))

    # Convert score_bell_df to a numpy array and calculate the percentage score matrix
    HSM = score_bell_df.to_numpy()
    lambda_matrix = calculate_percentage_score_matrix(HSM)

    # Convert lambda_matrix back to a DataFrame
    final_dm_weights_df = pd.DataFrame(lambda_matrix, index=score_bell_df.index, columns=score_bell_df.columns)

    # Calculate the criteria weights
    criteria_weights = calculate_criteria_weights(final_dm_weights_df, weights_df)

    # Calculate the final scores for each candidate
    final_scores_df = calculate_final_scores(criteria_weights, agents_df)

    # Reset index to make 'Candidates' a column
    final_scores_df = final_scores_df.reset_index().rename(columns={"index": "Candidates"})

    # Uncomment to print execution time
    # print("--- %s seconds ---" % (time.time() - start_time))

    return final_scores_df

# For testing the module directly
if __name__ == "__main__":
    result = hives_algorithm('candidates_scores.csv', 'criteria_weights.csv')
    print(result)
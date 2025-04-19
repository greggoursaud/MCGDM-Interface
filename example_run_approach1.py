import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

# Import the implementation of Approach 1
from optimisation_hives_approach1 import (
    generate_alternatives, 
    normalize_objectives,
    visualize_alternatives, 
    approach1_optimize_first_then_hives
)

def run_example():
    """
    Run a detailed example of the optimization-HIVES approach, following the 3-step process:
    1. Generate Alternatives
    2. Visualize Alternatives
    3. Apply HIVES
    """
    print("==================================================")
    print("     OPTIMIZATION WITH HIVES - EXAMPLE RUN        ")
    print("     (Generate Alternatives First, Then HIVES)    ")
    print("==================================================")
    
    # Define weights for each decision-maker (DM)
    print("\nSTEP 0: Defining decision-maker weights for criteria...\n")
    weights_data = {
        'DM1': {'Cost': 40, 'Durability': 30, 'Performance': 30},
        'DM2': {'Cost': 50, 'Durability': 20, 'Performance': 30},
        'DM3': {'Cost': 30, 'Durability': 40, 'Performance': 30}
    }
    
    # Display weights in a table
    weights_df = pd.DataFrame(weights_data).T
    print(weights_df)
    
    # Define objective names
    objective_names = ['Cost', 'Durability', 'Performance']
    
    # Define problem parameters
    problem_name = 'dtlz2'
    n_var = 5           # Using fewer variables for faster computation
    n_obj = 3
    pop_size = 50       # Smaller population for a quicker demo
    n_gen = 20          # Fewer generations for a quicker demo
    
    print("\nSTEP 1: Generating Pareto-optimal alternatives...")
    print("(Using realistic alternatives with non-zero values for all objectives)")
    start_time = time.time()
    
    # Define problem parameters
    problem_name = 'dtlz2'
    n_var = 5           # Using fewer variables for faster computation
    n_obj = 3
    pop_size = 50       # Smaller population for a quicker demo
    n_gen = 20          # Fewer generations for a quicker demo
    
    # Generate alternatives with minimum thresholds to ensure realistic values
    print("\nRunning full approach with realistic alternatives...")
    final_scores, X_opt, F_opt, top_indices = approach1_optimize_first_then_hives(
        weights_data, 
        objective_names=objective_names,
        problem_name=problem_name,
        n_var=n_var,
        n_obj=n_obj,
        pop_size=pop_size,
        n_gen=n_gen,
        minimize_objectives=True,
        balance_factor=0.3,      # Favor balanced solutions
        min_acceptable=15.0,     # Minimum acceptable score for any criterion
        use_realistic_alternatives=True,  # Use realistic alternatives
        min_obj_threshold=0.1    # Minimum threshold for objective values
    )
    
    print(f"\nGenerated {len(F_opt)} realistic alternatives in {time.time() - start_time:.2f} seconds")
    
    # Display a sample of the original objective values
    print("\nSample of original objective values (first 5 alternatives):")
    sample_df = pd.DataFrame(F_opt[:5], columns=objective_names)
    print(sample_df)
    
    # Calculate and print statistics for objectives
    obj_stats = pd.DataFrame(F_opt, columns=objective_names).describe()
    print("\nStatistics for original objective values:")
    print(obj_stats)
    
    print("\nSTEP 2: Visualizing the alternatives before ranking...")
    # Visualize alternatives before ranking
    visualize_alternatives(F_opt, objective_names, top_indices=None)
    
    print("\nNormalizing objectives for HIVES...")
    # Normalize objectives
    F_normalized = normalize_objectives(F_opt, minimize=True)
    
    # Display a sample of the normalized objective values
    print("\nSample of normalized objective values (first 5 alternatives):")
    norm_sample_df = pd.DataFrame(F_normalized[:5], columns=objective_names)
    print(norm_sample_df)
    
    print("\nSTEP 3: Applying HIVES to rank alternatives...")
    print("\nRunning full HIVES analysis with balance factor to avoid extreme solutions...")
    # Now run the full approach with the same alternatives we generated
    final_scores, X_opt, F_opt, top_indices = approach1_optimize_first_then_hives(
        weights_data, 
        objective_names=objective_names,
        problem_name=problem_name,
        n_var=n_var,
        n_obj=n_obj,
        pop_size=pop_size,
        n_gen=n_gen,
        minimize_objectives=True,
        balance_factor=0.3,      # Favor balanced solutions
        min_acceptable=15.0      # Minimum acceptable score for any criterion
    )
    
    # Compare realistic vs. standard alternatives
    print("\nComparing realistic vs. standard alternatives:")
    # Run the approach with standard NSGA-II alternatives
    standard_scores, X_std, F_std, _ = approach1_optimize_first_then_hives(
        weights_data, 
        objective_names=objective_names,
        problem_name=problem_name,
        n_var=n_var,
        n_obj=n_obj,
        pop_size=pop_size,
        n_gen=n_gen,
        minimize_objectives=True,
        balance_factor=0.3,      # Favor balanced solutions
        min_acceptable=15.0,     # Minimum acceptable score for any criterion
        use_realistic_alternatives=False,  # Use standard alternatives
        min_obj_threshold=0.0    # No minimum threshold
    )
    
    # Display distribution of objective values for both approaches
    print("\nDistribution of objective values (Realistic Alternatives):")
    real_min = np.min(F_opt, axis=0)
    real_max = np.max(F_opt, axis=0)
    real_mean = np.mean(F_opt, axis=0)
    for i, name in enumerate(objective_names):
        print(f"{name}: Min={real_min[i]:.4f}, Mean={real_mean[i]:.4f}, Max={real_max[i]:.4f}")
    
    print("\nDistribution of objective values (Standard Alternatives):")
    std_min = np.min(F_std, axis=0)
    std_max = np.max(F_std, axis=0)
    std_mean = np.mean(F_std, axis=0)
    for i, name in enumerate(objective_names):
        print(f"{name}: Min={std_min[i]:.4f}, Mean={std_mean[i]:.4f}, Max={std_max[i]:.4f}")
    
    # Display more details about the best alternative
    best_alt = final_scores.iloc[0]['Alternatives']
    best_index = int(best_alt.split('_')[1])
    
    print("\n==================================================")
    print(f"BEST ALTERNATIVE (REALISTIC): {best_alt}")
    print("==================================================")
    print("\nDecision Variables:")
    for i, val in enumerate(X_opt[best_index]):
        print(f"x{i+1}: {val:.4f}")
    
    print("\nObjective Values:")
    for i, name in enumerate(objective_names):
        print(f"{name}: {F_opt[best_index, i]:.4f}")
    
    print(f"\nTotal Score: {final_scores.iloc[0]['Total Score']:.2f}")
    print(f"Balance Factor: {final_scores.iloc[0]['Balance Factor']:.2f}")
    
    # Run a simplified sensitivity analysis with fewer weight configurations
    print("\n==================================================")
    print("SENSITIVITY ANALYSIS")
    print("==================================================")
    
    # Define alternative weight configurations - using just one for brevity
    alternative_weights = [
        {
            'name': 'Cost-Focused',
            'weights': {
                'DM1': {'Cost': 70, 'Durability': 15, 'Performance': 15},
                'DM2': {'Cost': 60, 'Durability': 20, 'Performance': 20},
                'DM3': {'Cost': 50, 'Durability': 25, 'Performance': 25}
            }
        }
    ]
    
    # Run quick analysis with each weight configuration
    for config in alternative_weights:
        print(f"\n{config['name']} Configuration:")
        weights_df = pd.DataFrame(config['weights']).T
        print(weights_df)
        
        # Only apply the calculations without generating new alternatives
        # Create alternatives DataFrame from previously generated solutions
        alternatives_df = pd.DataFrame(F_normalized, columns=objective_names)
        alternatives_df.index = [f'Alternative_{i}' for i in range(len(alternatives_df))]
        
        print(f"Calculating aggregated weights for {config['name']} configuration...")
        
        # Calculate HIVES weights from the provided weights data
        weights_df_alt = pd.DataFrame(config['weights']).T
        
        # Calculate statistical measures
        criteria_assessment_characteristics = calculate_statistics(weights_df_alt)
        
        # Extract statistical values for easier reference
        Min = criteria_assessment_characteristics.loc['Min']
        Q1 = criteria_assessment_characteristics.loc['Q1']
        SICP = criteria_assessment_characteristics.loc['SICP']
        Q3 = criteria_assessment_characteristics.loc['Q3']
        Max = criteria_assessment_characteristics.loc['Max']
        
        # Apply the Score Bell function
        score_bell_df = weights_df_alt.apply(lambda x: x.apply(apply_score_bell, 
                                                args=(Min[x.name], Q1[x.name], SICP[x.name], Q3[x.name], Max[x.name])))

        # Calculate percentage score matrix
        HSM = score_bell_df.to_numpy()
        lambda_matrix = calculate_percentage_score_matrix(HSM)
        final_dm_weights_df = pd.DataFrame(lambda_matrix, index=score_bell_df.index, columns=score_bell_df.columns)
        
        # Calculate criteria weights
        criteria_weights = calculate_criteria_weights(final_dm_weights_df, weights_df_alt)
        
        print("\nAggregated criteria weights:")
        for i, weight in enumerate(criteria_weights):
            print(f"{objective_names[i]}: {weight:.2f}%")
        
        # Calculate final scores
        alt_scores_df = calculate_final_scores(criteria_weights, alternatives_df)
        
        # Reset index to make 'Alternatives' a column
        alt_scores_df = alt_scores_df.reset_index().rename(columns={"index": "Alternatives"})
        
        # Sort by ranking
        alt_scores_df_sorted = alt_scores_df.sort_values('Ranking')
        
        # Display top 3 alternatives
        print(f"\nTop 3 alternatives with {config['name']} weights:")
        print(alt_scores_df_sorted.head(3)[['Alternatives', 'Total Score', 'Ranking']])
        
        # Compare with the original ranking
        print("\nComparison with original ranking:")
        alt_top_3 = alt_scores_df_sorted.head(3)['Alternatives'].tolist()
        orig_top_3 = final_scores.head(3)['Alternatives'].tolist()
        
        # Find positions of alternative's top 3 in original ranking
        comparison = []
        for alt in alt_top_3:
            orig_rank = final_scores[final_scores['Alternatives'] == alt]['Ranking'].values[0]
            comparison.append({
                'Alternative': alt,
                f'{config["name"]} Rank': alt_scores_df_sorted[alt_scores_df_sorted['Alternatives'] == alt]['Ranking'].values[0],
                'Original Rank': orig_rank,
                'Change': f"{'+' if orig_rank > 3 else ''}{3 - orig_rank if orig_rank <= 3 else '+' + str(int(orig_rank - 3))}"
            })
        
        # Display comparison table
        comparison_df = pd.DataFrame(comparison)
        print(comparison_df)
    
    print("\n==================================================")
    print("CONCLUSION")
    print("==================================================")
    print("The Optimization-HIVES approach successfully:")
    print("1. Generated diverse Pareto-optimal alternatives using NSGA-II")
    print("2. Normalized the objective values to a consistent scale")
    print("3. Applied HIVES to rank alternatives based on decision-maker preferences")
    print("4. Identified the best alternative considering trade-offs between objectives")
    print("5. Demonstrated how different weight configurations affect the rankings")
    
    return final_scores, X_opt, F_opt, top_indices

# Import necessary functions for sensitivity analysis
from hives_calculations import (
    calculate_statistics,
    apply_score_bell,
    calculate_percentage_score_matrix,
    calculate_criteria_weights,
    calculate_final_scores
)

if __name__ == "__main__":
    final_scores, X_opt, F_opt, top_indices = run_example()
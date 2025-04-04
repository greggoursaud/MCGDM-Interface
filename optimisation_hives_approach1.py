import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pymoo.problems import get_problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from hives_calculations import (
    calculate_statistics,
    apply_score_bell,
    calculate_percentage_score_matrix,
    calculate_criteria_weights,
    calculate_final_scores
)

def generate_alternatives(problem_name='dtlz2', n_var=10, n_obj=3, pop_size=100, n_gen=100, seed=1):
    """
    Generate alternatives using a multi-objective optimization algorithm.
    
    Args:
        problem_name: Name of the test problem (default: 'dtlz2')
        n_var: Number of decision variables (default: 10)
        n_obj: Number of objectives (default: 3)
        pop_size: Population size for the algorithm (default: 100)
        n_gen: Number of generations (default: 100)
        seed: Random seed for reproducibility (default: 1)
        
    Returns:
        tuple: Decision variables (X) and objective values (F) of the Pareto-optimal solutions
    """
    # Configure the problem
    problem = get_problem(problem_name, n_var=n_var, n_obj=n_obj)
    
    # Configure and run NSGA-II to generate Pareto-optimal solutions
    algorithm = NSGA2(pop_size=pop_size)
    
    res = minimize(problem,
                   algorithm,
                   ('n_gen', n_gen),
                   seed=seed,
                   verbose=True)
    
    # Extract the decision variables and objective values
    X_opt = res.X  # Decision variables
    F_opt = res.F  # Objective values
    
    return X_opt, F_opt, problem

def visualize_alternatives(F_opt, objective_names=None, top_indices=None, highlight_best=False):
    """
    Visualize alternatives in the objective space.
    
    Args:
        F_opt: Objective values of the Pareto-optimal solutions
        objective_names: List of objective names (default: None)
        top_indices: Indices of top solutions to highlight (default: None)
        highlight_best: Whether to highlight the best solution (default: False)
        
    Returns:
        None: Displays the plot
    """
    if objective_names is None:
        objective_names = [f'Objective {i+1}' for i in range(F_opt.shape[1])]
    
    if F_opt.shape[1] == 3:  # If we have 3 objectives
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot all solutions
        ax.scatter(F_opt[:, 0], F_opt[:, 1], F_opt[:, 2], c='blue', marker='o', alpha=0.5)
        
        # Highlight top solutions if provided
        if top_indices is not None:
            ax.scatter(F_opt[top_indices, 0], F_opt[top_indices, 1], F_opt[top_indices, 2], 
                      c='red', marker='*', s=200, label='Top solutions')
        
        # Highlight best solution if requested
        if highlight_best and top_indices is not None:
            ax.scatter(F_opt[top_indices[0], 0], F_opt[top_indices[0], 1], F_opt[top_indices[0], 2], 
                      c='green', marker='X', s=300, label='Best solution')
        
        ax.set_xlabel(objective_names[0])
        ax.set_ylabel(objective_names[1])
        ax.set_zlabel(objective_names[2])
        
        if top_indices is not None:
            plt.legend()
            
        plt.title('Pareto Front Visualization')
        plt.show()
        
    elif F_opt.shape[1] == 2:  # If we have 2 objectives
        plt.figure(figsize=(10, 6))
        plt.scatter(F_opt[:, 0], F_opt[:, 1], c='blue', alpha=0.5)
        
        # Highlight top solutions if provided
        if top_indices is not None:
            plt.scatter(F_opt[top_indices, 0], F_opt[top_indices, 1], c='red', marker='*', s=200, label='Top solutions')
        
        # Highlight best solution if requested
        if highlight_best and top_indices is not None:
            plt.scatter(F_opt[top_indices[0], 0], F_opt[top_indices[0], 1], c='green', marker='X', s=300, label='Best solution')
        
        plt.xlabel(objective_names[0])
        plt.ylabel(objective_names[1])
        
        if top_indices is not None:
            plt.legend()
            
        plt.title('Pareto Front Visualization')
        plt.grid(True)
        plt.show()
        
    else:  # For more than 3 objectives, use parallel coordinates plot
        from pandas.plotting import parallel_coordinates
        
        # Create a DataFrame for the parallel coordinates plot
        df = pd.DataFrame(F_opt, columns=objective_names)
        df['Alternative'] = df.index
        
        if top_indices is not None:
            # Create a column to identify top solutions
            df['Group'] = 'Other'
            df.loc[top_indices, 'Group'] = 'Top'
            if highlight_best:
                df.loc[top_indices[0], 'Group'] = 'Best'
            
            plt.figure(figsize=(12, 6))
            parallel_coordinates(df, 'Group', colormap='viridis')
        else:
            plt.figure(figsize=(12, 6))
            parallel_coordinates(df, 'Alternative', colormap='viridis')
            
        plt.title('Parallel Coordinates Plot of Pareto-Optimal Solutions')
        plt.grid(True)
        plt.show()

def normalize_objectives(F_opt, minimize=True):
    """
    Normalize objective values to [0, 100] scale.
    
    Args:
        F_opt: Objective values
        minimize: Whether the objectives should be minimized (default: True)
        
    Returns:
        numpy.ndarray: Normalized objective values
    """
    # Find min and max for each objective
    min_values = np.min(F_opt, axis=0)
    max_values = np.max(F_opt, axis=0)
    range_values = max_values - min_values
    
    if minimize:
        # Normalize to [0, 100] scale and invert (since we're minimizing)
        # 100 is the best (lowest original value), 0 is the worst (highest original value)
        F_normalized = 100 * (1 - (F_opt - min_values) / range_values)
    else:
        # Normalize to [0, 100] scale without inverting (for maximization)
        # 100 is the best (highest original value), 0 is the worst (lowest original value)
        F_normalized = 100 * ((F_opt - min_values) / range_values)
    
    return F_normalized

def approach1_optimize_first_then_hives(weights_data, objective_names=None, problem_name='dtlz2', 
                                        n_var=10, n_obj=3, pop_size=100, n_gen=100, 
                                        minimize_objectives=True):
    """
    Implement Approach 1: Generate alternatives first, then apply HIVES.
    
    Args:
        weights_data: Dictionary with DM weights for each criterion
        objective_names: List of objective names (default: None)
        problem_name: Name of the test problem (default: 'dtlz2')
        n_var: Number of decision variables (default: 10)
        n_obj: Number of objectives (default: 3)
        pop_size: Population size for the algorithm (default: 100)
        n_gen: Number of generations (default: 100)
        minimize_objectives: Whether objectives should be minimized (default: True)
        
    Returns:
        tuple: Final scores DataFrame, decision variables, objective values, top indices
    """
    start_time = time.time()
    
    # Step 1: Generate alternatives
    X_opt, F_opt, problem = generate_alternatives(problem_name, n_var, n_obj, pop_size, n_gen)
    
    if objective_names is None:
        objective_names = [f'Objective {i+1}' for i in range(n_obj)]
    
    print(f"Generated {len(F_opt)} Pareto-optimal alternatives")
    
    # Step 2: Normalize objectives for HIVES
    F_normalized = normalize_objectives(F_opt, minimize=minimize_objectives)
    
    # Create DataFrame for alternatives
    alternatives_df = pd.DataFrame(F_normalized, columns=objective_names)
    alternatives_df.index = [f'Alternative_{i}' for i in range(len(alternatives_df))]
    
    # Convert weights_data to DataFrame
    weights_df = pd.DataFrame(weights_data).T
    
    # Step 3: Apply HIVES to rank alternatives
    
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
    
    # Print the aggregated weights
    print("\nAggregated criteria weights:")
    for i, weight in enumerate(criteria_weights):
        print(f"{objective_names[i]}: {weight:.2f}%")

    # Calculate the final scores for each alternative
    final_scores_df = calculate_final_scores(criteria_weights, alternatives_df)

    # Reset index to make 'Alternatives' a column
    final_scores_df = final_scores_df.reset_index().rename(columns={"index": "Alternatives"})

    # Sort by ranking
    final_scores_df_sorted = final_scores_df.sort_values('Ranking')
    
    # Get top indices
    top_5 = final_scores_df_sorted.head(5)['Alternatives'].tolist()
    top_indices = [int(alt.split('_')[1]) for alt in top_5]
    
    # Get best alternative
    best_alt = final_scores_df_sorted.iloc[0]['Alternatives']
    best_index = int(best_alt.split('_')[1])
    
    print(f"\nBest Alternative: {best_alt}")
    print(f"Final Score: {final_scores_df_sorted.iloc[0]['Total Score']:.2f}")
    
    # Print the actual objective values for the best alternative
    print("\nBest Alternative Objective Values (original):")
    for i, name in enumerate(objective_names):
        print(f"{name}: {F_opt[best_index, i]:.4f}")
    
    print(f"\nExecution time: {time.time() - start_time:.2f} seconds")
    
    return final_scores_df_sorted, X_opt, F_opt, top_indices

# For testing the module directly
if __name__ == "__main__":
    # Define weights for each decision-maker (DM)
    weights_data = {
        'DM1': {'Cost': 40, 'Durability': 30, 'Performance': 30},
        'DM2': {'Cost': 50, 'Durability': 20, 'Performance': 30},
        'DM3': {'Cost': 30, 'Durability': 40, 'Performance': 30}
    }
    
    # Define objective names
    objective_names = ['Cost', 'Durability', 'Performance']
    
    # Run Approach 1
    final_scores, X_opt, F_opt, top_indices = approach1_optimize_first_then_hives(
        weights_data, 
        objective_names=objective_names,
        problem_name='dtlz2',
        n_var=10,
        n_obj=3,
        pop_size=100,
        n_gen=100,
        minimize_objectives=True
    )
    
    # Display top 10 alternatives
    print("\nTop 10 alternatives:")
    print(final_scores.head(10))
    
    # Visualize the alternatives
    visualize_alternatives(F_opt, objective_names, top_indices, highlight_best=True)
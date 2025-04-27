"""
This file provides optimisation extensions to the HIVES algorithm.
It includes implementations of both optimisation approaches:
1. Generate Alternatives First, Then Apply HIVES
2. Apply HIVES First, Then Optimize

These extensions allow the HIVES algorithm to be integrated with
optimization techniques for more advanced multi-criteria decision making.
"""

import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution, minimize as scipy_minimize

# For Approach 1 (Generate Alternatives First, Then HIVES)
try:
    from pymoo.problems import get_problem
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.optimize import minimize
    from mpl_toolkits.mplot3d import Axes3D
    PYMOO_AVAILABLE = True
except ImportError:
    PYMOO_AVAILABLE = False
    print("Warning: pymoo package not available. Approach 1 functionality will be limited.")

# Import core HIVES functionality
from hives_calculations import (
    calculate_statistics,
    apply_score_bell,
    calculate_percentage_score_matrix,
    calculate_criteria_weights,
    calculate_final_scores
)

# =============================================================================
# Approach 1: Generate Alternatives First, Then Apply HIVES
# =============================================================================

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
    if not PYMOO_AVAILABLE:
        raise ImportError("This function requires the pymoo package. Please install it to use this functionality.")
        
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

def normalize_objectives(F_opt, minimize=True):
    """
    Normalize objective values to the [0, 100] scale for use with HIVES.
    
    Args:
        F_opt: Array of objective values
        minimize: Whether objectives should be minimized (default: True)
        
    Returns:
        numpy.ndarray: Normalized objective values
    """
    # Compute the min, max for each objective
    min_values = np.min(F_opt, axis=0)
    max_values = np.max(F_opt, axis=0)
    
    # Compute range, avoiding division by zero
    range_values = max_values - min_values
    range_values = np.where(range_values < 1e-10, 1.0, range_values)  # Avoid division by zero
    
    if minimize:
        # Normalize to [0, 100] scale with inversion (for minimization)
        # 100 is the best (lowest original value), 0 is the worst (highest original value)
        F_normalized = 100 * (1 - ((F_opt - min_values) / range_values))
    else:
        # Normalize to [0, 100] scale without inverting (for maximization)
        # 100 is the best (highest original value), 0 is the worst (lowest original value)
        F_normalized = 100 * ((F_opt - min_values) / range_values)
    
    # Replace any NaN values with 50 (neutral score)
    F_normalized = np.nan_to_num(F_normalized, nan=50.0)
    
    return F_normalized

def visualize_alternatives(F_opt, objective_names=None, top_indices=None, highlight_best=False):
    """
    Visualize alternatives using appropriate plots based on the number of objectives.
    
    Args:
        F_opt: Array of objective values
        objective_names: List of objective names (default: None)
        top_indices: Indices of top-ranked alternatives to highlight (default: None)
        highlight_best: Whether to highlight the best alternative (default: False)
    """
    if objective_names is None:
        objective_names = [f'Objective {i+1}' for i in range(F_opt.shape[1])]
    
    if F_opt.shape[1] > 3:  # More than 3 objectives
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
        
    else:  # For 3 objectives, create 3D and 2D projections
        fig = plt.figure(figsize=(15, 10))
        
        # 3D plot
        ax1 = fig.add_subplot(221, projection='3d')
        scatter = ax1.scatter(F_opt[:, 0], F_opt[:, 1], F_opt[:, 2], 
                      c=np.sum(F_opt, axis=1), cmap='viridis', 
                      marker='o', alpha=0.7, s=50)
        plt.colorbar(scatter, ax=ax1, label='Sum of objectives')
        
        # Highlight top solutions if provided
        if top_indices is not None:
            ax1.scatter(F_opt[top_indices, 0], F_opt[top_indices, 1], F_opt[top_indices, 2], 
                      c='red', marker='*', s=200, label='Top solutions')
        
        # Highlight best solution if requested
        if highlight_best and top_indices is not None:
            ax1.scatter(F_opt[top_indices[0], 0], F_opt[top_indices[0], 1], F_opt[top_indices[0], 2], 
                      c='green', marker='X', s=300, label='Best solution')
        
        ax1.set_xlabel(objective_names[0])
        ax1.set_ylabel(objective_names[1])
        ax1.set_zlabel(objective_names[2])
        ax1.set_title('3D Objective Space')
        
        if top_indices is not None:
            ax1.legend()
        
        # Create 2D projections for better understanding
        # X-Y projection
        ax2 = fig.add_subplot(222)
        ax2.scatter(F_opt[:, 0], F_opt[:, 1], c='blue', alpha=0.5)
        if top_indices is not None:
            ax2.scatter(F_opt[top_indices, 0], F_opt[top_indices, 1], c='red', marker='*', s=100)
        ax2.set_xlabel(objective_names[0])
        ax2.set_ylabel(objective_names[1])
        ax2.set_title(f'{objective_names[0]} vs {objective_names[1]}')
        ax2.grid(True)
        
        # X-Z projection
        ax3 = fig.add_subplot(223)
        ax3.scatter(F_opt[:, 0], F_opt[:, 2], c='blue', alpha=0.5)
        if top_indices is not None:
            ax3.scatter(F_opt[top_indices, 0], F_opt[top_indices, 2], c='red', marker='*', s=100)
        ax3.set_xlabel(objective_names[0])
        ax3.set_ylabel(objective_names[2])
        ax3.set_title(f'{objective_names[0]} vs {objective_names[2]}')
        ax3.grid(True)
        
        # Y-Z projection
        ax4 = fig.add_subplot(224)
        ax4.scatter(F_opt[:, 1], F_opt[:, 2], c='blue', alpha=0.5)
        if top_indices is not None:
            ax4.scatter(F_opt[top_indices, 1], F_opt[top_indices, 2], c='red', marker='*', s=100)
        ax4.set_xlabel(objective_names[1])
        ax4.set_ylabel(objective_names[2])
        ax4.set_title(f'{objective_names[1]} vs {objective_names[2]}')
        ax4.grid(True)
        
        plt.tight_layout()
        plt.show()
        
        # Also show parallel coordinates plot for better visualization of trade-offs
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

def approach1_optimize_first_then_hives(weights_data, objective_names=None, problem_name='dtlz2', 
                                        n_var=10, n_obj=3, pop_size=100, n_gen=100, 
                                        minimize_objectives=True, balance_factor=0.0,
                                        min_acceptable=0.0, use_realistic_alternatives=False,
                                        min_obj_threshold=0.0):
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
        balance_factor: Factor for favoring balanced solutions (default: 0.0)
        min_acceptable: Minimum acceptable score for any criterion (default: 0.0)
        use_realistic_alternatives: Whether to use realistic alternatives (default: False)
        min_obj_threshold: Minimum threshold for objective values (default: 0.0)
        
    Returns:
        tuple: Final scores DataFrame, decision variables, objective values, top indices
    """
    if not PYMOO_AVAILABLE:
        raise ImportError("This function requires the pymoo package. Please install it to use this functionality.")
        
    start_time = time.time()
    
    # Step 1: Generate alternatives
    X_opt, F_opt, problem = generate_alternatives(problem_name, n_var, n_obj, pop_size, n_gen)
    
    if objective_names is None:
        objective_names = [f'Objective {i+1}' for i in range(n_obj)]
    
    print(f"Generated {len(F_opt)} Pareto-optimal alternatives")
    
    # Step 2: Normalize objectives for HIVES
    F_normalized = normalize_objectives(F_opt, minimize=minimize_objectives)
    
    # Verify no NaN values in normalized data
    if np.isnan(F_normalized).any():
        print("Warning: NaN values found after normalization, replacing with neutral scores")
        F_normalized = np.nan_to_num(F_normalized, nan=50.0)
    
    # Create DataFrame for alternatives
    alternatives_df = pd.DataFrame(F_normalized, columns=objective_names)
    alternatives_df.index = [f'Alternative_{i}' for i in range(len(alternatives_df))]
    
    # Print first few rows to verify data
    print("\nSample of normalized alternatives:")
    print(alternatives_df.head())
    
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

    # Check for NaN values in score_bell_df
    if score_bell_df.isna().any().any():
        print("Warning: NaN values in score bell calculations, replacing with default scores")
        score_bell_df = score_bell_df.fillna(50.0)

    # Convert score_bell_df to a numpy array and calculate the percentage score matrix
    HSM = score_bell_df.to_numpy()
    lambda_matrix = calculate_percentage_score_matrix(HSM)

    # Convert lambda_matrix back to a DataFrame
    final_dm_weights_df = pd.DataFrame(lambda_matrix, index=score_bell_df.index, columns=score_bell_df.columns)

    # Calculate the criteria weights
    criteria_weights = calculate_criteria_weights(final_dm_weights_df, weights_df)
    
    # Check for NaN values in criteria_weights and replace them
    for i, weight in enumerate(criteria_weights):
        if np.isnan(weight):
            print(f"Warning: NaN weight for {objective_names[i]}, using equal weight")
            criteria_weights[i] = 100.0 / len(criteria_weights)
    
    # Print the aggregated weights
    print("\nAggregated criteria weights:")
    for i, weight in enumerate(criteria_weights):
        print(f"{objective_names[i]}: {weight:.2f}%")

    # Calculate the final scores for each alternative
    final_scores_df = calculate_final_scores(criteria_weights, alternatives_df)

    # Check for NaN values in final scores
    if final_scores_df.isna().any().any():
        print("Warning: NaN values in final scores, replacing with zeros")
        final_scores_df = final_scores_df.fillna(0.0)

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


# =============================================================================
# Approach 2: Apply HIVES First, Then Optimize
# =============================================================================

def get_hives_weights(weights_data, objective_names=None):
    """
    Apply the HIVES method to calculate consensus weights.
    
    Args:
        weights_data: Dictionary with DM weights for each criterion
        objective_names: List of objective names (default: None)
        
    Returns:
        tuple: List of consensus weights, and dataframe with weight information
    """
    # Convert weights_data to DataFrame
    weights_df = pd.DataFrame(weights_data).T
    
    if objective_names is not None and len(objective_names) != weights_df.shape[1]:
        raise ValueError(f"Number of objective names ({len(objective_names)}) doesn't match "
                         f"number of criteria ({weights_df.shape[1]})")
        
    # Use column names from weights_df if objective_names not provided
    if objective_names is None:
        objective_names = weights_df.columns.tolist()
    
    # Calculate statistical measures
    criteria_assessment_characteristics = calculate_statistics(weights_df)
    
    # Extract statistical values for easier reference
    Min = criteria_assessment_characteristics.loc['Min']
    Q1 = criteria_assessment_characteristics.loc['Q1']
    SICP = criteria_assessment_characteristics.loc['SICP']
    Q3 = criteria_assessment_characteristics.loc['Q3']
    Max = criteria_assessment_characteristics.loc['Max']
    
    # Apply the Score Bell function to each value in the weights_df
    score_bell_df = weights_df.apply(lambda x: x.apply(apply_score_bell, 
                                                       args=(Min[x.name], Q1[x.name], 
                                                             SICP[x.name], Q3[x.name], 
                                                             Max[x.name])))
    
    # Check for NaN values in score_bell_df
    if score_bell_df.isna().any().any():
        print("Warning: NaN values in score bell calculations, replacing with default scores")
        score_bell_df = score_bell_df.fillna(50.0)

    # Convert score_bell_df to a numpy array and calculate the percentage score matrix
    HSM = score_bell_df.to_numpy()
    lambda_matrix = calculate_percentage_score_matrix(HSM)

    # Convert lambda_matrix back to a DataFrame
    final_dm_weights_df = pd.DataFrame(lambda_matrix, index=score_bell_df.index, 
                                       columns=score_bell_df.columns)

    # Calculate the criteria weights
    criteria_weights = calculate_criteria_weights(final_dm_weights_df, weights_df)
    
    # Check for NaN values in criteria_weights and replace them
    for i, weight in enumerate(criteria_weights):
        if np.isnan(weight):
            print(f"Warning: NaN weight for {objective_names[i]}, using equal weight")
            criteria_weights[i] = 100.0 / len(criteria_weights)
    
    # Create a DataFrame with weight information
    weights_info_df = pd.DataFrame({
        'Criterion': objective_names,
        'Weight': criteria_weights
    })
    
    return criteria_weights, weights_info_df

def setup_problem(problem_name='dtlz2', n_var=10, n_obj=3):
    """
    Set up the optimization problem.
    
    Args:
        problem_name: Name of the test problem (default: 'dtlz2')
        n_var: Number of decision variables (default: 10)
        n_obj: Number of objectives (default: 3)
        
    Returns:
        tuple: Problem instance, variable bounds, ideal point, nadir point
    """
    if not PYMOO_AVAILABLE:
        raise ImportError("This function requires the pymoo package. Please install it to use this functionality.")
        
    # Configure the problem
    problem = get_problem(problem_name, n_var=n_var, n_obj=n_obj)
    
    # Get the bounds for decision variables
    if hasattr(problem, 'xl') and hasattr(problem, 'xu'):
        bounds = [(problem.xl[i], problem.xu[i]) for i in range(n_var)]
    else:
        bounds = [(0, 1) for _ in range(n_var)]  # Default bounds
    
    # Estimate the ideal and nadir points
    # For many test problems, the ideal point is the origin
    ideal_point = np.zeros(n_obj)
    
    # For many test problems, the nadir point can be approximated
    # This is a simplification; in practice, computing the true nadir point can be complex
    if problem_name.startswith('dtlz'):
        nadir_point = np.ones(n_obj)
    else:
        # For other problems, use a conservative estimate
        nadir_point = np.ones(n_obj) * 2.0
    
    return problem, bounds, ideal_point, nadir_point

def weighted_tchebycheff(x, problem, weights, ideal_point, nadir_point, minimize_objectives=True):
    """
    Compute the weighted Tchebycheff scalarization.
    
    Args:
        x: Decision variables
        problem: Problem instance
        weights: List of weights for each objective
        ideal_point: Ideal point (best possible value for each objective)
        nadir_point: Nadir point (worst possible value for each objective)
        minimize_objectives: Whether objectives should be minimized (default: True)
        
    Returns:
        float: Scalarized objective value
    """
    # Evaluate the objective functions
    f_value = problem.evaluate(x)
    
    # Ensure weights are normalized to sum to 1
    weights_normalized = np.array(weights) / np.sum(weights)
    
    # Calculate the range of each objective for normalization
    range_values = nadir_point - ideal_point
    # Avoid division by zero
    range_values = np.where(range_values < 1e-10, 1.0, range_values)
    
    if minimize_objectives:
        # For minimization, the normalized value approaches 0 as it gets better
        f_normalized = (f_value - ideal_point) / range_values
    else:
        # For maximization, invert the normalization
        f_normalized = 1.0 - (f_value - ideal_point) / range_values
    
    # Apply weights and compute Tchebycheff metric
    # We add a small augmentation term to ensure Pareto optimality
    weighted_diffs = weights_normalized * f_normalized
    max_weighted_diff = np.max(weighted_diffs)
    
    # Augmentation term to ensure Pareto optimality
    augmentation = 0.001 * np.sum(weighted_diffs)
    
    return max_weighted_diff + augmentation

def weighted_sum(x, problem, weights, ideal_point, nadir_point, minimize_objectives=True):
    """
    Compute the weighted sum scalarization.
    
    Args:
        x: Decision variables
        problem: Problem instance
        weights: List of weights for each objective
        ideal_point: Ideal point (best possible value for each objective)
        nadir_point: Nadir point (worst possible value for each objective)
        minimize_objectives: Whether objectives should be minimized (default: True)
        
    Returns:
        float: Scalarized objective value
    """
    # Evaluate the objective functions
    f_value = problem.evaluate(x)
    
    # Ensure weights are normalized to sum to 1
    weights_normalized = np.array(weights) / np.sum(weights)
    
    # Calculate the range of each objective for normalization
    range_values = nadir_point - ideal_point
    # Avoid division by zero
    range_values = np.where(range_values < 1e-10, 1.0, range_values)
    
    if minimize_objectives:
        # For minimization, the normalized value approaches 0 as it gets better
        f_normalized = (f_value - ideal_point) / range_values
    else:
        # For maximization, invert the normalization
        f_normalized = 1.0 - (f_value - ideal_point) / range_values
    
    # Apply weighted sum
    return np.sum(weights_normalized * f_normalized)

def approach2_hives_first_then_optimize(weights_data, objective_names=None, 
                                        problem_name='dtlz2', n_var=10, n_obj=3,
                                        minimize_objectives=True, scalarization='tchebycheff',
                                        optimizer='differential_evolution'):
    """
    Implement Approach 2: Apply HIVES first, then optimize.
    
    Args:
        weights_data: Dictionary with DM weights for each criterion
        objective_names: List of objective names (default: None)
        problem_name: Name of the test problem (default: 'dtlz2')
        n_var: Number of decision variables (default: 10)
        n_obj: Number of objectives (default: 3)
        minimize_objectives: Whether objectives should be minimized (default: True)
        scalarization: Scalarization method ('tchebycheff' or 'weighted_sum')
        optimizer: Optimization algorithm ('differential_evolution' or 'nelder_mead')
        
    Returns:
        dict: Results including optimal decision variables, objective values, and execution time
    """
    if not PYMOO_AVAILABLE:
        raise ImportError("This function requires the pymoo package. Please install it to use this functionality.")
        
    start_time = time.time()
    
    # Step 1: Apply HIVES to get consensus weights
    print("Step 1: Applying HIVES to determine consensus weights")
    consensus_weights, weights_info_df = get_hives_weights(weights_data, objective_names)
    
    # Display HIVES weights
    print("\nConsensus weights from HIVES:")
    for i, weight in enumerate(consensus_weights):
        criterion_name = objective_names[i] if objective_names else f"Criterion {i+1}"
        print(f"{criterion_name}: {weight:.2f}%")
    
    # Step 2: Set up the optimization problem
    print("\nStep 2: Setting up the optimization problem")
    problem, bounds, ideal_point, nadir_point = setup_problem(problem_name, n_var, n_obj)
    
    # Step 3: Define the scalarized objective function
    print(f"\nStep 3: Scalarizing using the {scalarization} method")
    if scalarization == 'tchebycheff':
        scalarized_objective = lambda x: weighted_tchebycheff(
            x, problem, consensus_weights, ideal_point, nadir_point, minimize_objectives
        )
    elif scalarization == 'weighted_sum':
        scalarized_objective = lambda x: weighted_sum(
            x, problem, consensus_weights, ideal_point, nadir_point, minimize_objectives
        )
    else:
        raise ValueError(f"Unsupported scalarization method: {scalarization}")
    
    # Step 4: Optimize the scalarized function
    print(f"\nStep 4: Optimizing using {optimizer}")
    if optimizer == 'differential_evolution':
        options = {'maxiter': 1000, 'popsize': 15, 'tol': 1e-8}
        print(f"Running differential evolution with options: {options}")
        results = differential_evolution(
            scalarized_objective, 
            bounds=bounds,
            strategy='best1bin',
            maxiter=options['maxiter'],
            popsize=options['popsize'],
            tol=options['tol'],
            mutation=(0.5, 1.0),
            recombination=0.7,
            disp=True
        )
        x_opt = results.x
        success = results.success
        message = results.message
    elif optimizer == 'nelder_mead':
        options = {'maxiter': 10000, 'xatol': 1e-8, 'fatol': 1e-8}
        print(f"Running Nelder-Mead with options: {options}")
        # Start from the middle of the bounds
        x0 = np.array([(b[0] + b[1]) / 2.0 for b in bounds])
        results = scipy_minimize(
            scalarized_objective,
            x0,
            method='Nelder-Mead',
            options=options
        )
        x_opt = results.x
        success = results.success
        message = results.message
    else:
        raise ValueError(f"Unsupported optimizer: {optimizer}")
    
    # Check optimization result
    if not success:
        print(f"Warning: Optimization may not have converged. Message: {message}")
    
    # Step 5: Evaluate the optimal solution
    print("\nStep 5: Evaluating the optimal solution")
    f_opt = problem.evaluate(x_opt)
    
    # Return results
    execution_time = time.time() - start_time
    print(f"\nExecution time: {execution_time:.2f} seconds")
    
    # Format the results for return
    result_dict = {
        'x_optimal': x_opt,
        'f_optimal': f_opt,
        'consensus_weights': consensus_weights,
        'weights_info': weights_info_df,
        'execution_time': execution_time
    }
    
    return result_dict

def visualize_solution(f_opt, objective_names=None, consensus_weights=None, minimize_objectives=True):
    """
    Visualize the optimal solution.
    
    Args:
        f_opt: Optimal objective values
        objective_names: List of objective names
        consensus_weights: Weights from HIVES method
        minimize_objectives: Whether objectives should be minimized
    """
    if objective_names is None:
        objective_names = [f'Objective {i+1}' for i in range(len(f_opt))]
    
    # Create a figure with subplots
    n_obj = len(f_opt)
    figsize = (10, 8) if n_obj <= 5 else (12, 10)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    # Normalize objective values for visualization
    if minimize_objectives:
        # For minimization, lower is better, so invert for display
        normalized_values = 1.0 - (f_opt / np.max(f_opt))
    else:
        # For maximization, higher is better
        normalized_values = f_opt / np.max(f_opt)
    
    # Bar plot of objective values
    bars = ax1.bar(objective_names, f_opt, alpha=0.7, color='blue')
    
    # Add value labels on top of bars
    for bar, value in zip(bars, f_opt):
        ax1.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02 * max(f_opt),
            f'{value:.4f}',
            ha='center', va='bottom', rotation=0
        )
    
    ax1.set_title('Optimal Objective Values')
    ax1.set_xlabel('Objectives')
    ax1.set_ylabel('Value')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Radar chart (polar plot) of normalized values and weights
    if n_obj >= 3:
        # Set up radar chart
        angles = np.linspace(0, 2*np.pi, n_obj, endpoint=False).tolist()
        
        # Close the loop
        normalized_values = np.append(normalized_values, normalized_values[0])
        angles.append(angles[0])
        
        # Convert weights to [0,1] scale and close the loop
        if consensus_weights is not None:
            normalized_weights = np.array(consensus_weights) / 100.0
            normalized_weights = np.append(normalized_weights, normalized_weights[0])
            
            # Plot weights
            ax2.plot(angles, normalized_weights, 'r-', linewidth=2, label='Normalized weights')
            ax2.fill(angles, normalized_weights, 'r', alpha=0.1)
        
        # Plot normalized values
        ax2.plot(angles, normalized_values, 'b-', linewidth=2, label='Normalized performance')
        ax2.fill(angles, normalized_values, 'b', alpha=0.1)
        
        # Set radar chart labels
        objective_names_loop = objective_names.copy()
        objective_names_loop.append(objective_names[0])
        ax2.set_xticks(angles)
        ax2.set_xticklabels(objective_names_loop)
        
        ax2.set_ylim(0, 1)
        ax2.set_title('Normalized Performance vs. Weights')
        ax2.grid(True)
        ax2.legend(loc='upper right')
    else:
        # For 1-2 objectives, use a different visualization
        if consensus_weights is not None:
            x = np.arange(n_obj)
            ax2.bar(x - 0.2, normalized_values, width=0.4, label='Normalized performance', color='blue')
            ax2.bar(x + 0.2, np.array(consensus_weights) / 100.0, width=0.4, label='Normalized weights', color='red')
            ax2.set_xticks(x)
            ax2.set_xticklabels(objective_names)
            ax2.set_ylim(0, 1)
            ax2.set_title('Normalized Performance vs. Weights')
            ax2.legend()
            ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.show()


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
    
    print("Testing HIVES Optimization Module")
    print("=================================")
    
    try:
        # Test approach 1 if pymoo is available
        if PYMOO_AVAILABLE:
            print("\nApproach 1: Generate Alternatives First, Then Apply HIVES")
            print("-------------------------------------------------------")
            
            final_scores, X_opt, F_opt, top_indices = approach1_optimize_first_then_hives(
                weights_data, 
                objective_names=objective_names,
                problem_name='dtlz2',
                n_var=10,
                n_obj=3,
                pop_size=20,  # Small size for testing
                n_gen=20,     # Small size for testing
                minimize_objectives=True
            )
            
            # Display top 5 alternatives
            print("\nTop 5 alternatives:")
            print(final_scores.head(5))
            
            # Test approach 2
            print("\nApproach 2: Apply HIVES First, Then Optimize")
            print("-------------------------------------------------------")
            
            results = approach2_hives_first_then_optimize(
                weights_data, 
                objective_names=objective_names,
                problem_name='dtlz2',
                n_var=10,
                n_obj=3,
                minimize_objectives=True,
                scalarization='tchebycheff',
                optimizer='differential_evolution'
            )
            
            # Display results
            print("\nOptimal Decision Variables:")
            for i, val in enumerate(results['x_optimal']):
                print(f"x_{i+1} = {val:.6f}")
            
            print("\nOptimal Objective Values:")
            for i, name in enumerate(objective_names):
                print(f"{name}: {results['f_optimal'][i]:.6f}")
        else:
            print("Pymoo package not available, skipping tests requiring it.")
            
            # We can still test the get_hives_weights function
            print("\nTesting get_hives_weights function:")
            consensus_weights, weights_info_df = get_hives_weights(weights_data, objective_names)
            
            print("\nConsensus weights from HIVES:")
            for i, weight in enumerate(consensus_weights):
                print(f"{objective_names[i]}: {weight:.2f}%")
    
    except Exception as e:
        print(f"An error occurred during testing: {str(e)}")

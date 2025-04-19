import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymoo.problems import get_problem
from scipy.optimize import differential_evolution
from hives_calculations import (
    calculate_statistics,
    apply_score_bell,
    calculate_percentage_score_matrix,
    calculate_criteria_weights
)

# Example: Setting up optimization problem with HIVES

# Step 1: Define decision-maker weights for criteria
weights_data = {
    'DM1': {'Cost': 40, 'Efficiency': 30, 'Sustainability': 30},
    'DM2': {'Cost': 50, 'Efficiency': 25, 'Sustainability': 25},
    'DM3': {'Cost': 30, 'Efficiency': 40, 'Sustainability': 30},
    'DM4': {'Cost': 45, 'Efficiency': 30, 'Sustainability': 25}
}

# Step 2: Apply HIVES to determine consensus weights
def get_hives_weights(weights_data):
    """Calculate consensus weights using HIVES method"""
    weights_df = pd.DataFrame(weights_data).T
    
    # Calculate statistical measures
    criteria_assessment_characteristics = calculate_statistics(weights_df)
    
    # Extract statistical values
    Min = criteria_assessment_characteristics.loc['Min']
    Q1 = criteria_assessment_characteristics.loc['Q1']
    SICP = criteria_assessment_characteristics.loc['SICP']
    Q3 = criteria_assessment_characteristics.loc['Q3']
    Max = criteria_assessment_characteristics.loc['Max']
    
    # Apply the Score Bell function
    score_bell_df = weights_df.apply(lambda x: x.apply(apply_score_bell, 
                                                     args=(Min[x.name], Q1[x.name], 
                                                           SICP[x.name], Q3[x.name], 
                                                           Max[x.name])))
    
    # Calculate percentage score matrix
    HSM = score_bell_df.to_numpy()
    lambda_matrix = calculate_percentage_score_matrix(HSM)
    final_dm_weights_df = pd.DataFrame(lambda_matrix, index=score_bell_df.index, 
                                     columns=score_bell_df.columns)
    
    # Calculate final criteria weights
    criteria_weights = calculate_criteria_weights(final_dm_weights_df, weights_df)
    
    return criteria_weights

# Calculate consensus weights
consensus_weights = get_hives_weights(weights_data)
print("Consensus weights from HIVES:")
objective_names = list(next(iter(weights_data.values())).keys())
for i, name in enumerate(objective_names):
    print(f"{name}: {consensus_weights[i]:.2f}%")

# Step 3: Define a real-world optimization problem
# Replace the test problem with your actual problem definition
print("\n--- Applying to a Real-World Problem ---")

# Example: Investment portfolio optimization
# Decision variables: Percentage allocation to different investment options
n_investments = 5  # Number of investment options
var_names = [f"Investment_{i+1}" for i in range(n_investments)]
bounds = [(0, 1) for _ in range(n_investments)]  # Each investment can be 0-100%

# Define your actual objective functions
def evaluate_real_problem(x):
    """
    Evaluate the real-world objective functions for a given solution.
    x: array of decision variables (e.g., investment allocations)
    returns: array of objective values [cost, efficiency, sustainability]
    """
    # Ensure allocation sums to 100%
    x_normalized = x / np.sum(x)
    
    # Example objective functions (replace with your actual calculations):
    
    # Cost objective (minimize) - e.g., total investment cost or risk
    # Lower values are better
    expected_costs = np.array([0.05, 0.04, 0.07, 0.06, 0.03])  # Per investment
    cost = np.sum(x_normalized * expected_costs)
    
    # Efficiency objective (maximize) - e.g., expected return
    # Higher values are better
    expected_returns = np.array([0.07, 0.10, 0.12, 0.09, 0.06])  # Per investment
    efficiency = np.sum(x_normalized * expected_returns)
    
    # Sustainability objective (maximize) - e.g., ESG score
    # Higher values are better
    sustainability_scores = np.array([0.8, 0.6, 0.4, 0.7, 0.9])  # Per investment
    sustainability = np.sum(x_normalized * sustainability_scores)
    
    return np.array([cost, efficiency, sustainability])

# Define which objectives should be minimized (True) or maximized (False)
minimize_objectives = [True, False, False]  # Minimize cost, maximize efficiency & sustainability

# Add explanation about weights vs objective values
print("\nNote: The HIVES weights sum to 100% because they represent relative importance.")
print("However, objective values are actual performance metrics that don't need to sum to 1.")
print("Each objective has its own scale and interpretation based on the problem definition.")

# Find ideal and nadir points by sampling
population_size = 1000
sample_solutions = np.random.random((population_size, n_investments))
# Normalize each solution to sum to 1
sample_solutions = np.array([x/np.sum(x) for x in sample_solutions])
sample_evaluations = np.array([evaluate_real_problem(x) for x in sample_solutions])

# Apply minimization/maximization direction to evaluations for normalization
sample_evaluations_adjusted = sample_evaluations.copy()
for i, minimize in enumerate(minimize_objectives):
    if not minimize:  # If maximizing, negate the values
        sample_evaluations_adjusted[:, i] = -sample_evaluations[:, i]

# Proper ideal (best) and nadir (worst) points considering minimization/maximization
z_ideal = np.min(sample_evaluations_adjusted, axis=0)
z_nadir = np.max(sample_evaluations_adjusted, axis=0)

# Step 4: Define improved scalarizing function with HIVES weights
def tchebycheff_scalarization(x, weights):
    """Improved Tchebycheff scalarization function using HIVES weights"""
    # Normalize input to ensure sum equals 1 (for allocation problems)
    x_normalized = x / np.sum(x)
    
    # Evaluate the objective functions
    f_values = evaluate_real_problem(x_normalized)
    
    # Normalize weights to sum to 1
    weights_normalized = np.array(weights) / 100.0
    
    # Adjust objectives based on whether we're minimizing or maximizing
    f_adjusted = f_values.copy()
    for i, minimize in enumerate(minimize_objectives):
        if not minimize:  # If maximizing, negate the value
            f_adjusted[i] = -f_values[i]
    
    # Normalize objectives to [0,1] range where 0 is best
    f_normalized = (f_adjusted - z_ideal) / (z_nadir - z_ideal)
    
    # Weighted Tchebycheff with proper normalization
    weighted_diffs = weights_normalized * f_normalized
    max_term = np.max(weighted_diffs)
    
    # Augmentation term to ensure Pareto optimality
    augmentation = 0.001 * np.sum(weighted_diffs)
    
    return max_term + augmentation

# Step 5: Optimize using the improved scalarizing function
result = differential_evolution(
    lambda x: tchebycheff_scalarization(x, consensus_weights),
    bounds=bounds,
    strategy='best1bin',
    maxiter=1000,
    popsize=15,
    tol=1e-8,
    mutation=(0.5, 1.0),
    recombination=0.7
)

# Step 6: Extract and display results
x_optimal = result.x
# Normalize to ensure sum equals 1
x_optimal = x_optimal / np.sum(x_optimal)
f_optimal = evaluate_real_problem(x_optimal)

print("\nOptimal solution found:")
print("Decision variables (Investment allocations):")
for i, (name, value) in enumerate(zip(var_names, x_optimal)):
    print(f"  {name}: {value*100:.2f}%")

print("\nObjective values:")
for i, name in enumerate(objective_names):
    print(f"{name}: {f_optimal[i]:.6f}")
    print(f"  Direction: {'Minimizing' if minimize_objectives[i] else 'Maximizing'}")

# Step 7: Visualization - update to show portfolio allocation and objective values
plt.figure(figsize=(10, 6))

# Bar chart of objective values - add direction information
plt.subplot(1, 2, 1)
colors = ['lightcoral' if min_obj else 'skyblue' for min_obj in minimize_objectives]
plt.bar(objective_names, f_optimal, color=colors)
plt.title('Optimal Objective Values')
plt.ylabel('Value')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add text to indicate direction
for i, (name, val, min_obj) in enumerate(zip(objective_names, f_optimal, minimize_objectives)):
    direction = 'Min' if min_obj else 'Max'
    plt.text(i, val/2, direction, ha='center', fontweight='bold')

# Update bar chart comparing HIVES weights to normalized performance
plt.subplot(1, 2, 2)
normalized_performance = f_optimal / np.max(f_optimal)
normalized_weights = np.array(consensus_weights) / 100.0

x = np.arange(len(objective_names))
width = 0.35
plt.bar(x - width/2, normalized_weights, width, label='HIVES Weights', color='lightcoral')
plt.bar(x + width/2, normalized_performance, width, label='Normalized Performance', color='skyblue')

plt.xlabel('Objectives')
plt.ylabel('Normalized Value')
plt.title('Weights vs. Performance')
plt.xticks(x, objective_names)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# Example of how this integrates with your existing code structure
print("\nTo integrate this approach into your MCGDM Interface:")
print("1. Use the hives.py module to process decision-maker inputs")
print("2. Pass the resulting weights to the optimization algorithm")
print("3. Return the single optimal solution instead of multiple alternatives")

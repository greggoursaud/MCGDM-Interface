import pandas as pd
import numpy as np
from optimisation_hives_approach1 import approach1_optimize_first_then_hives, visualize_alternatives

# Example data based on the markdown example
weights_data = {
    'DM1': {'Cost': 40, 'Durability': 30, 'Performance': 30},
    'DM2': {'Cost': 50, 'Durability': 20, 'Performance': 30},
    'DM3': {'Cost': 30, 'Durability': 40, 'Performance': 30}
}

def run_demo():
    """Run a demonstration of Optimization with HIVES - Approach 1"""
    print("=" * 50)
    print("OPTIMIZATION WITH HIVES - APPROACH 1 DEMO")
    print("Generate Alternatives First, Then Apply HIVES")
    print("=" * 50)
    
    print("\nInput Data:")
    print("-----------")
    print("Decision Maker Weights:")
    weights_df = pd.DataFrame(weights_data).T
    print(weights_df)
    
    # Define objectives
    objective_names = ['Cost', 'Durability', 'Performance']
    
    print("\nRunning optimization and HIVES...")
    print("---------------------------------")
    
    # Run the algorithm with smaller parameters for quick demonstration
    final_scores, X_opt, F_opt, top_indices = approach1_optimize_first_then_hives(
        weights_data=weights_data,
        objective_names=objective_names,
        problem_name='dtlz2',
        n_var=5,           # Using fewer variables for faster computation
        n_obj=3,
        pop_size=50,       # Smaller population for demo
        n_gen=20,          # Fewer generations for demo
        minimize_objectives=True
    )
    
    print("\nResults:")
    print("--------")
    print("\nTop 5 Alternatives:")
    print(final_scores.head())
    
    # Get details of the best alternative
    best_alt = final_scores.iloc[0]['Alternatives']
    best_index = int(best_alt.split('_')[1])
    
    print("\nBest Alternative Details:")
    print("------------------------")
    print(f"Alternative ID: {best_alt}")
    print("\nDecision Variables:")
    for i, val in enumerate(X_opt[best_index]):
        print(f"x{i+1}: {val:.4f}")
    
    print("\nObjective Values:")
    for i, name in enumerate(objective_names):
        print(f"{name}: {F_opt[best_index, i]:.4f}")
    
    print(f"\nFinal Score: {final_scores.iloc[0]['Total Score']:.2f}")
    
    # Visualize results
    print("\nGenerating visualization...")
    visualize_alternatives(F_opt, objective_names, top_indices, highlight_best=True)
    
    return final_scores, X_opt, F_opt, top_indices

if __name__ == "__main__":
    final_scores, X_opt, F_opt, top_indices = run_demo()
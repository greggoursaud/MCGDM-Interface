import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Import the implementation of Approach 1
from optimisation_hives_approach1 import approach1_optimize_first_then_hives, visualize_alternatives

def run_example():
    """
    Run a simple example of the optimization-HIVES approach.
    """
    print("==================================================")
    print("     OPTIMIZATION WITH HIVES - EXAMPLE RUN        ")
    print("     (Generate Alternatives First, Then HIVES)    ")
    print("==================================================")
    
    # Define weights for each decision-maker (DM)
    print("\nDefining decision-maker weights for criteria...\n")
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
    
    print("\nStep 1: Generating Pareto-optimal alternatives using NSGA-II...")
    print("(This may take a few moments...)")
    
    # Run Approach 1 with a smaller population and fewer generations for a quicker demo
    final_scores, X_opt, F_opt, top_indices = approach1_optimize_first_then_hives(
        weights_data, 
        objective_names=objective_names,
        problem_name='dtlz2',
        n_var=5,           # Using fewer variables for faster computation
        n_obj=3,
        pop_size=50,       # Smaller population for a quicker demo
        n_gen=20,          # Fewer generations for a quicker demo
        minimize_objectives=True
    )
    
    print("\nStep 2: Top 5 alternatives after HIVES ranking:")
    print(final_scores.head(5))
    
    print("\nStep 3: Visualizing the alternatives...")
    visualize_alternatives(F_opt, objective_names, top_indices, highlight_best=True)
    
    # Display more details about the best alternative
    best_alt = final_scores.iloc[0]['Alternatives']
    best_index = int(best_alt.split('_')[1])
    
    print("\n==================================================")
    print(f"BEST ALTERNATIVE: {best_alt}")
    print("==================================================")
    print("\nDecision Variables:")
    for i, val in enumerate(X_opt[best_index]):
        print(f"x{i+1}: {val:.4f}")
    
    print("\nObjective Values:")
    for i, name in enumerate(objective_names):
        print(f"{name}: {F_opt[best_index, i]:.4f}")
    
    print(f"\nTotal Score: {final_scores.iloc[0]['Total Score']:.2f}")
    print("==================================================")
    
    return final_scores, X_opt, F_opt, top_indices

if __name__ == "__main__":
    final_scores, X_opt, F_opt, top_indices = run_example()
import flet as ft
import pandas as pd
import numpy as np
from hives import hives_algorithm
import random
import traceback  # Import traceback at the top level of the file
import tempfile
import os
import json
import time  # Add time module for timing operations
from scipy.optimize import differential_evolution  # Add this import for optimization
from dashboard_page import build_dashboard_page
# Add import for optimization approach
from optimisation_hives_approach2 import approach2_hives_first_then_optimize, get_hives_weights
from user_utils import get_navigation_controls

def build_input_page(page: ft.Page):
    # Get user data and navigation controls
    user_data = page.client_storage.get("user_data")
    nav_controls = get_navigation_controls(page, user_data)
    
    # State variables
    criteria_count = ft.Ref[ft.TextField]()
    alternatives_count = ft.Ref[ft.TextField]()
    decision_makers_count = ft.Ref[ft.TextField]()
    
    # Create empty containers that will be populated with input fields
    alternatives_container = ft.Ref[ft.Column]()
    weights_container = ft.Ref[ft.Column]()
    
    # Step tracking
    current_step = ft.Ref[ft.Container]()
    step_1 = ft.Ref[ft.Container]()
    step_2 = ft.Ref[ft.Container]()
    step_3 = ft.Ref[ft.Container]()
    
    # Add reference for optimization option
    optimization_checkbox = ft.Ref[ft.Checkbox]()
    
    # Progress indicator references
    step1_circle = ft.Ref[ft.Container]()
    step2_circle = ft.Ref[ft.Container]()
    step3_circle = ft.Ref[ft.Container]()

    # Data containers for generated tables
    alternatives_data = []
    weights_data = []
    
    # References to weight sum indicators
    weight_sums = []
    
    # Maximum weight sum
    MAX_WEIGHT_SUM = 100
    
    def update_progress_indicators():
        """Update the progress indicators based on the current step"""
        if current_step.current == step_1.current:
            step1_circle.current.bgcolor = "white"
            step2_circle.current.bgcolor = "#AAAAAA"
            step3_circle.current.bgcolor = "#AAAAAA"
        elif current_step.current == step_2.current:
            step1_circle.current.bgcolor = "#AAAAAA"
            step2_circle.current.bgcolor = "white"
            step3_circle.current.bgcolor = "#AAAAAA"
        elif current_step.current == step_3.current:
            step1_circle.current.bgcolor = "#AAAAAA"
            step2_circle.current.bgcolor = "#AAAAAA"
            step3_circle.current.bgcolor = "white"
        
        page.update()
    
    def go_to_step(step_container):
        if current_step.current:
            current_step.current.visible = False
        
        step_container.current.visible = True
        current_step.current = step_container.current
        update_progress_indicators()
    
    def generate_forms(e):
        try:
            c_count = int(criteria_count.current.value)
            a_count = int(alternatives_count.current.value)
            dm_count = int(decision_makers_count.current.value)
            
            if c_count <= 0 or a_count <= 0 or dm_count <= 0:
                page.snack_bar = ft.SnackBar(ft.Text("Please enter positive numbers for all fields"))
                page.snack_bar.open = True
                page.update()
                return
                
            # Generate alternatives table
            alternatives_container.current.controls.clear()
            generate_alternatives_table(c_count, a_count)
            
            # Generate weights table
            weights_container.current.controls.clear()
            generate_weights_table(c_count, dm_count)
            
            # Move to step 2 (alternatives data entry)
            go_to_step(step_2)
            
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter valid numbers"))
            page.snack_bar.open = True
            page.update()
    
    def generate_alternatives_table(c_count, a_count):
        # Create headers for alternatives table
        headers = ["Alternative"]
        headers.extend([f"C{i+1}" for i in range(c_count)])
        
        # Create alternatives table
        alternatives_table = ft.Column(spacing=10)
        alternatives_data.clear()
        
        # Add header row with specific widths and center alignment
        header_controls = [ft.Text(headers[0], width=100, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER)]
        for i in range(1, len(headers)):
            header_controls.append(ft.Text(headers[i], width=80, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER))
        header_row = ft.Row(header_controls, spacing=10)
        alternatives_table.controls.append(header_row)
        
        # Add editable rows for each alternative
        for i in range(a_count):
            row_data = [f"A{i+1}"]
            row_data.extend(["" for _ in range(c_count)])
            alternatives_data.append(row_data)
            
            # Center the alternative label (A1, A2, etc.)
            row_controls = [ft.Text(row_data[0], width=100, color="white", text_align=ft.TextAlign.CENTER)]
            for j in range(1, len(row_data)):
                field = ft.TextField(
                    value=row_data[j],
                    width=80,
                    color="white",
                    border_color="white",
                    focused_border_color="white",
                    cursor_color="white",
                    text_align=ft.TextAlign.CENTER,  # Center the input text too
                    on_change=lambda e, r=i, c=j: update_alternatives_data(r, c, e.control.value)
                )
                row_controls.append(field)
            
            alternatives_table.controls.append(ft.Row(row_controls, spacing=10))
        
        # Add randomize button for alternatives
        randomize_btn = ft.ElevatedButton(
            "Randomise Alternatives",
            on_click=lambda _: randomize_alternatives(c_count, a_count),
            style=ft.ButtonStyle(
                bgcolor="#4CAF50",
                color="white",
                padding=ft.padding.symmetric(vertical=10, horizontal=20),
                text_style=ft.TextStyle(size=14)
            )
        )
        
        # Add table and button to container
        alternatives_container.current.controls.extend([
            ft.Container(
                content=alternatives_table,
                padding=10,
                border=ft.border.all(1, "white"),
                border_radius=5,
                width=min(page.width, 800)
            ),
            randomize_btn
        ])
    
    def generate_weights_table(c_count, dm_count):
        # Create weights table
        weights_table = ft.Column(spacing=10)
        weights_data.clear()
        weight_sums.clear()
        
        # Add header row for weights with sum column - with specific widths
        weight_headers = ["DM"]
        weight_headers.extend([f"C{i+1}" for i in range(c_count)])
        weight_headers.append("Sum")
        
        # Create header row with proper widths and center alignment
        header_controls = [ft.Text(weight_headers[0], width=100, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER)]
        # Middle columns (criteria) with width=80
        for i in range(1, len(weight_headers)-1):
            header_controls.append(ft.Text(weight_headers[i], width=80, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER))
        # Last column (Sum) with width=100
        header_controls.append(ft.Text(weight_headers[-1], width=100, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER))
        
        weights_table.controls.append(ft.Row(header_controls, spacing=10))
        
        # Add editable rows for each decision maker
        for i in range(dm_count):
            row_data = [f"DM{i+1}"]
            row_data.extend(["" for _ in range(c_count)])
            weights_data.append(row_data)
            
            # Center the DM label (DM1, DM2, etc.)
            row_controls = [ft.Text(row_data[0], width=100, color="white", text_align=ft.TextAlign.CENTER)]
            for j in range(1, len(row_data)):
                field = ft.TextField(
                    value=row_data[j],
                    width=80,
                    color="white",
                    border_color="white",
                    focused_border_color="white",
                    cursor_color="white",
                    text_align=ft.TextAlign.CENTER,  # Center the input text too
                    on_change=lambda e, r=i, c=j: update_weights_data(r, c, e.control.value)
                )
                row_controls.append(field)
            
            # Add sum indicator with center alignment
            sum_indicator = ft.Text("0", width=100, color="white", text_align=ft.TextAlign.CENTER)
            row_controls.append(sum_indicator)
            weight_sums.append(sum_indicator)
            
            weights_table.controls.append(ft.Row(row_controls, spacing=10))
        
        # Add randomize button for weights
        randomize_btn = ft.ElevatedButton(
            "Randomise Weights",
            on_click=lambda _: randomize_weights(c_count, dm_count),
            style=ft.ButtonStyle(
                bgcolor="#4CAF50",
                color="white",
                padding=ft.padding.symmetric(vertical=10, horizontal=20),
                text_style=ft.TextStyle(size=14)
            )
        )
        
        note_text = ft.Text(
            f"Note: The sum of weights for each decision maker must equal exactly {MAX_WEIGHT_SUM}.",
            style=ft.TextStyle(size=14, color="white", italic=True)
        )
        
        # Add table and button to container
        weights_container.current.controls.extend([
            ft.Container(
                content=weights_table,
                padding=10,
                border=ft.border.all(1, "white"),
                border_radius=5,
                width=min(page.width, 800)
            ),
            note_text,
            randomize_btn
        ])
    
    def update_alternatives_data(row, col, value):
        alternatives_data[row][col] = value
    
    def update_weights_data(row, col, value):
        weights_data[row][col] = value
        update_weight_sum(row)
    
    def update_weight_sum(row):
        try:
            # Calculate sum of weights for this row
            row_sum = 0
            for col in range(1, len(weights_data[row])):
                if weights_data[row][col] and weights_data[row][col].strip():
                    row_sum += float(weights_data[row][col])
            
            # Update sum indicator
            sum_text = f"{row_sum}"
            weight_sums[row].value = sum_text
            
            # Set color based on sum value
            if row_sum != MAX_WEIGHT_SUM:
                weight_sums[row].color = "red"
            else:
                weight_sums[row].color = "white"
                
            page.update()
        except (ValueError, TypeError):
            # Handle invalid input
            weight_sums[row].value = "Error"
            weight_sums[row].color = "red"
            page.update()
    
    def randomize_alternatives(c_count, a_count):
        """Randomise the alternative values with reasonable numbers for testing"""
        for i in range(a_count):
            for j in range(1, c_count + 1):
                # Generate a random value between 1 and 100
                random_value = str(random.randint(1, 100))
                alternatives_data[i][j] = random_value
                
                # Update the text field at position j in row i
                row = alternatives_container.current.controls[0].content.controls[i + 1]  # +1 to skip header
                field = row.controls[j]
                field.value = random_value
        
        page.update()
    
    def randomize_weights(c_count, dm_count):
        """Randomise the weights ensuring they sum to 100 for each decision maker"""
        for i in range(dm_count):
            # Generate random weights that sum to MAX_WEIGHT_SUM
            random_weights = []
            remaining = MAX_WEIGHT_SUM
            
            # Generate c_count-1 random proportions
            for j in range(c_count - 1):
                if remaining <= 0:
                    random_weights.append(0)
                else:
                    weight = random.randint(1, min(remaining - 1, 50))  # Ensure we have something left
                    random_weights.append(weight)
                    remaining -= weight
            
            # Add the last weight to make the sum exactly MAX_WEIGHT_SUM
            random_weights.append(remaining)
            
            # Shuffle the weights
            random.shuffle(random_weights)
            
            # Update the data and UI
            for j in range(1, c_count + 1):
                weight_value = str(random_weights[j-1])
                weights_data[i][j] = weight_value
                
                # Update the text field
                row = weights_container.current.controls[0].content.controls[i + 1]  # +1 to skip header
                field = row.controls[j]
                field.value = weight_value
            
            # Update sum indicator
            update_weight_sum(i)
        
        page.update()
    
    def process_data(e):
        try:
            # Check if any weight sum doesn't equal MAX_WEIGHT_SUM
            has_invalid_weights = False
            for i in range(len(weight_sums)):
                try:
                    if float(weight_sums[i].value) != MAX_WEIGHT_SUM:
                        has_invalid_weights = True
                        break
                except (ValueError, TypeError):
                    has_invalid_weights = True
                    break
            
            if has_invalid_weights:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Weight sum for one or more decision makers does not equal exactly {MAX_WEIGHT_SUM}. Please adjust the weights.")
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # Convert alternatives data to pandas DataFrame
            alt_headers = ["Alternative"] + [f"C{i+1}" for i in range(len(alternatives_data[0])-1)]
            alt_df = pd.DataFrame(alternatives_data, columns=alt_headers)
            
            # Convert weights data to pandas DataFrame
            weight_headers = ["DM"] + [f"C{i+1}" for i in range(len(weights_data[0])-1)]
            weight_df = pd.DataFrame(weights_data, columns=weight_headers)
            
            # Create copies with numeric data for processing
            alt_df_process = alt_df.copy()
            alt_df_process.set_index("Alternative", inplace=True)
            weight_df_process = weight_df.copy()
            weight_df_process.set_index("DM", inplace=True)
            
            # Convert to numeric
            for col in alt_df_process.columns:
                alt_df_process[col] = pd.to_numeric(alt_df_process[col])
            
            for col in weight_df_process.columns:
                weight_df_process[col] = pd.to_numeric(weight_df_process[col])
            
            # Use temporary files for processing
            alt_csv_path = "temp_alt.csv"
            weight_csv_path = "temp_weight.csv"
            
            alt_df_process.to_csv(alt_csv_path)
            weight_df_process.to_csv(weight_csv_path)
            
            # Check if optimization approach is selected
            use_optimization = False
            if optimization_checkbox.current:
                use_optimization = optimization_checkbox.current.value
                
            # Debug print to check if optimization is being used
            print(f"Using optimization approach: {use_optimization}")
            
            if use_optimization:
                # Get criteria names and convert weights data to required format
                criteria_names = list(alt_df_process.columns)
                
                # Convert weights dataframe to dictionary format required by optimization
                weights_dict = {}
                for dm_idx, dm_name in enumerate(weight_df_process.index):
                    weights_dict[f'DM{dm_idx+1}'] = {}
                    for criterion in weight_df_process.columns:
                        weights_dict[f'DM{dm_idx+1}'][criterion] = weight_df_process.loc[dm_name, criterion]
                
                # First calculate HIVES weights directly using the imported function
                consensus_weights, _ = get_hives_weights(weights_dict, criteria_names)
                
                # Define the real problem (user's data) instead of test problem
                def evaluate_real_problem(x):
                    """
                    Evaluate using the user's actual alternatives data
                    x: array of decision variables (represents weights for alternatives)
                    returns: array of objective values (criteria)
                    """
                    # Normalize weights to sum to 1
                    x_normalized = x / np.sum(x)
                    
                    # Calculate weighted score for each criterion
                    f_values = np.zeros(len(criteria_names))
                    
                    # For each criterion, calculate weighted sum across alternatives
                    for i, criterion in enumerate(criteria_names):
                        criterion_values = np.array(alt_df_process[criterion])
                        f_values[i] = np.sum(x_normalized * criterion_values)
                    
                    return f_values
                
                # Define which objectives should be minimized (default: all maximizing)
                # In future versions this could be configured by the user
                minimize_objectives = [False] * len(criteria_names)
                
                # Find ideal and nadir points by sampling
                n_alternatives = alt_df_process.shape[0]
                population_size = 1000
                sample_solutions = np.random.random((population_size, n_alternatives))
                sample_solutions = np.array([x/np.sum(x) for x in sample_solutions])
                sample_evaluations = np.array([evaluate_real_problem(x) for x in sample_solutions])
                
                # Adjust based on minimization/maximization
                sample_evaluations_adjusted = sample_evaluations.copy()
                for i, minimize in enumerate(minimize_objectives):
                    if not minimize:  # If maximizing, negate the values
                        sample_evaluations_adjusted[:, i] = -sample_evaluations[:, i]
                
                # Find ideal and nadir points
                z_ideal = np.min(sample_evaluations_adjusted, axis=0)
                z_nadir = np.max(sample_evaluations_adjusted, axis=0)
                
                # Define the scalarization function with fewer iterations for faster results
                def tchebycheff_scalarization(x, weights):
                    x_normalized = x / np.sum(x)
                    f_values = evaluate_real_problem(x_normalized)
                    
                    weights_normalized = np.array(weights) / 100.0
                    
                    f_adjusted = f_values.copy()
                    for i, minimize in enumerate(minimize_objectives):
                        if not minimize:
                            f_adjusted[i] = -f_values[i]
                    
                    f_normalized = (f_adjusted - z_ideal) / (z_nadir - z_ideal)
                    weighted_diffs = weights_normalized * f_normalized
                    
                    return np.max(weighted_diffs) + 0.001 * np.sum(weighted_diffs)
                
                # Set up bounds for the weights (one per alternative)
                bounds = [(0, 1) for _ in range(n_alternatives)]
                
                # Run optimization with reduced iterations for responsiveness
                start_time = time.time()
                result = differential_evolution(
                    lambda x: tchebycheff_scalarization(x, consensus_weights),
                    bounds=bounds,
                    strategy='best1bin',
                    maxiter=100,  # Reduced from 1000
                    popsize=10,   # Reduced from 15
                    tol=1e-6,     # Less strict tolerance
                    mutation=(0.5, 1.0),
                    recombination=0.7
                )
                execution_time = time.time() - start_time
                
                # Extract results
                x_optimal = result.x / np.sum(result.x)  # Normalize
                f_optimal = evaluate_real_problem(x_optimal)
                
                # Create results for dashboard
                results = pd.DataFrame({
                    'Criterion': criteria_names,
                    'Weight': consensus_weights,
                    'Value': f_optimal
                })
                
                # Create alternative selection data
                alt_selection = pd.DataFrame({
                    'Alternative': alt_df_process.index.tolist(),
                    'Weight': x_optimal * 100  # Convert to percentage
                })
                
                # Add metadata about optimization
                optimization_metadata = {
                    'is_optimization': True,
                    'x_optimal': x_optimal.tolist(),
                    'execution_time': execution_time,
                    'alternative_weights': alt_selection.to_dict('records')
                }
                
                dashboard_data = {
                    "results": results.to_dict('records'),
                    "alternatives": alt_df.to_dict('records'),
                    "weights": weight_df.to_dict('records'),
                    "has_plot": True,
                    "optimization_data": optimization_metadata
                }
                    
            else:
                # Run HIVES algorithm (original approach)
                results = hives_algorithm(alt_csv_path, weight_csv_path)

                
                # Save data to client storage
                dashboard_data = {
                    "results": results.to_dict('records'),
                    "alternatives": alt_df.to_dict('records'),
                    "weights": weight_df.to_dict('records'),
                    "has_plot": True  # Flag to indicate parallel plot should be generated
                }
            
            # Store in client storage for main.py to use
            page.client_storage.set("dashboard_data", dashboard_data)
            
            # Navigate to dashboard page
            page.go("/dashboard")
            
        except Exception as e:
            error_message = f"Error processing data: {str(e)}\n{traceback.format_exc()}"
            print(error_message)
            page.snack_bar = ft.SnackBar(ft.Text(f"Error processing data: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    # Step 1 - Define problem parameters
    step1_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Step 1: Define Problem Parameters",
                    style=ft.TextStyle(
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="white"
                    )
                ),
                ft.Text(
                    "First, specify the dimensions of your decision-making problem.",
                    style=ft.TextStyle(size=16, color="white")
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.TextField(
                                label="Number of Criteria",
                                hint_text="Enter number of criteria",
                                keyboard_type=ft.KeyboardType.NUMBER,
                                ref=criteria_count,
                                width=300,
                                border_color="white",
                                focused_border_color="white",
                                color="white",
                                cursor_color="white",
                                label_style=ft.TextStyle(color="white")
                            ),
                            ft.TextField(
                                label="Number of Alternatives",
                                hint_text="Enter number of alternatives/candidates",
                                keyboard_type=ft.KeyboardType.NUMBER,
                                ref=alternatives_count,
                                width=300,
                                border_color="white",
                                focused_border_color="white",
                                color="white",
                                cursor_color="white",
                                label_style=ft.TextStyle(color="white")
                            ),
                            ft.TextField(
                                label="Number of Decision Makers",
                                hint_text="Enter number of decision makers",
                                keyboard_type=ft.KeyboardType.NUMBER,
                                ref=decision_makers_count,
                                width=300,
                                border_color="white",
                                focused_border_color="white",
                                color="white",
                                cursor_color="white",
                                label_style=ft.TextStyle(color="white")
                            ),
                            ft.Divider(color="white", height=1),
                            # Centered Advanced Options Section
                            ft.Column(
                                [
                                    ft.Text(
                                        "Advanced Options (Beta)", # Added (Beta)
                                        style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD, color="white")
                                    ),
                                    ft.Checkbox(
                                        ref=optimization_checkbox,
                                        label="Use Optimization Approach (HIVES + Optimization)",
                                        value=False,
                                        fill_color="#4CAF50",
                                        check_color="white",
                                        label_style=ft.TextStyle(color="white", weight=ft.FontWeight.BOLD),
                                    ),
                                    ft.Text(
                                        "The optimization approach uses HIVES to determine consensus weights, then finds a single optimal solution that best satisfies all criteria.",
                                        style=ft.TextStyle(color="white", italic=True, size=12), # Reduced size
                                        text_align=ft.TextAlign.CENTER, # Center align text
                                        width=300 # Constrain width for better centering
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Center items in this column
                                spacing=10 # Add some spacing
                            ),
                            ft.ElevatedButton(
                                text="Continue to Alternatives Entry",
                                on_click=generate_forms,
                                style=ft.ButtonStyle(
                                    bgcolor="white",
                                    color="black",
                                    padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                    text_style=ft.TextStyle(size=16)
                                )
                            ),
                        ],
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER # This centers the entire inner column content
                    ),
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, # This centers the main step container's content
            spacing=20
        ),
        ref=step_1
    )
    
    # Step 2 - Alternatives Data Entry
    step2_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Step 2: Enter Alternatives Data",
                    style=ft.TextStyle(
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="white"
                    )
                ),
                ft.Text(
                    "Enter the evaluation values for each alternative across all criteria.",
                    style=ft.TextStyle(size=16, color="white")
                ),
                ft.Container(
                    content=ft.Column(
                        ref=alternatives_container,
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Back to Parameters",
                            on_click=lambda _: go_to_step(step_1),
                            style=ft.ButtonStyle(
                                bgcolor="#EAEAEA",
                                color="black",
                                padding=ft.padding.symmetric(vertical=15, horizontal=20),
                                text_style=ft.TextStyle(size=14)
                            )
                        ),
                        ft.ElevatedButton(
                            text="Continue to Weights Entry",
                            on_click=lambda _: go_to_step(step_3),
                            style=ft.ButtonStyle(
                                bgcolor="white",
                                color="black",
                                padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                text_style=ft.TextStyle(size=16)
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        visible=False,
        ref=step_2
    )
    
    # Step 3 - Weights Data Entry - remove the optimization option that we moved to Step 1
    step3_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Step 3: Enter Criteria Weights",
                    style=ft.TextStyle(
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="white"
                    )
                ),
                ft.Text(
                    "Enter the weights assigned by each decision maker to the criteria.",
                    style=ft.TextStyle(size=16, color="white")
                ),
                ft.Container(
                    content=ft.Column(
                        ref=weights_container,
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Back to Alternatives",
                            on_click=lambda _: go_to_step(step_2),
                            style=ft.ButtonStyle(
                                bgcolor="#EAEAEA",
                                color="black",
                                padding=ft.padding.symmetric(vertical=15, horizontal=20),
                                text_style=ft.TextStyle(size=14)
                            )
                        ),
                        ft.ElevatedButton(
                            text="Process Data",
                            on_click=process_data,
                            style=ft.ButtonStyle(
                                bgcolor="white",
                                color="black",
                                padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                text_style=ft.TextStyle(size=16)
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        visible=False,
        ref=step_3
    )

    # Set current step
    current_step.current = step1_container
    
    # Create progress indicator with fixed colors (not using lambda)
    step1_indicator = ft.Container(
        content=ft.Text("1", 
            color="#2C2C2C",
            text_align=ft.TextAlign.CENTER,
            size=16,
            weight=ft.FontWeight.BOLD
        ),
        width=40,
        height=40,
        bgcolor="white",  # Initial state: step 1 is active
        border_radius=20,
        alignment=ft.alignment.center,
        ref=step1_circle
    )
    
    step2_indicator = ft.Container(
        content=ft.Text("2", 
            color="#2C2C2C",
            text_align=ft.TextAlign.CENTER,
            size=16,
            weight=ft.FontWeight.BOLD
        ),
        width=40,
        height=40,
        bgcolor="#AAAAAA",  # Initial state: step 2 is inactive
        border_radius=20,
        alignment=ft.alignment.center,
        ref=step2_circle
    )
    
    step3_indicator = ft.Container(
        content=ft.Text("3", 
            color="#2C2C2C",
            text_align=ft.TextAlign.CENTER,
            size=16,
            weight=ft.FontWeight.BOLD
        ),
        width=40,
        height=40,
        bgcolor="#AAAAAA",  # Initial state: step 3 is inactive
        border_radius=20,
        alignment=ft.alignment.center,
        ref=step3_circle
    )
    
    return ft.View(
        "/input",
        [
        # Updated Navigation Bar with back arrow like in register_page
            ft.Container(
                bgcolor="#EAEAEA",
                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: page.go("/start"),
                            tooltip="Back to Start"
                        ),
                        ft.IconButton(
                            icon=ft.icons.HOME,
                            on_click=lambda _: page.go("/"),
                            tooltip="Go to Home"
                        ),
                        ft.Container(expand=True),
                        # Use the nav_controls variable instead of hard-coded buttons
                        nav_controls,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=15
                )
            ),
            
            # Main content area with dark background matching the hero section
            ft.Container(
                content=ft.Column(
                    [
                        # Header with app title
                        ft.Row(
                            [
                                ft.Text(
                                    "Weigh",
                                    style=ft.TextStyle(
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                        color="white",
                                    ),
                                ),
                                ft.Text(
                                    "IN",
                                    style=ft.TextStyle(
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                        italic=True,
                                        color="white",
                                    ),
                                ),
                                ft.Text(
                                    " - Input Data",  # Page title addition
                                    style=ft.TextStyle(
                                        size=32,
                                        weight=ft.FontWeight.NORMAL,
                                        color="white",
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        
                        # Progress indicator - using containers with refs instead of lambda
                        ft.Row(
                            [
                                step1_indicator,
                                ft.Container(
                                    content=ft.Divider(
                                        height=2,
                                        color="white"
                                    ),
                                    width=60
                                ),
                                step2_indicator,
                                ft.Container(
                                    content=ft.Divider(
                                        height=2,
                                        color="white"
                                    ),
                                    width=60
                                ),
                                step3_indicator
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=0
                        ),
                        
                        # Step containers
                        step1_container,
                        step2_container,
                        step3_container
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                ),
                alignment=ft.alignment.top_center,
                padding=20,
                expand=True,
                bgcolor="#2C2C2C"  # Dark background matching home page hero section
            )
        ]
    )

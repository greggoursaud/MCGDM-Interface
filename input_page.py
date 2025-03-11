import flet as ft
import pandas as pd
import numpy as np
from hives import hives_algorithm
from parallel_coordinate import parallel_coordinates_plot
import random
import traceback  # Import traceback at the top level of the file
import tempfile
import os
import json
from dashboard_page import build_dashboard_page

def build_input_page(page: ft.Page):
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
            
            # Run HIVES algorithm
            results = hives_algorithm(alt_csv_path, weight_csv_path)
            
            # Generate parallel coordinates plot
            parallel_plot = parallel_coordinates_plot(results)
            
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
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
    
    # Step 3 - Weights Data Entry
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
                        # Using Container with expand=True instead of Spacer
                        ft.Container(expand=True),
                        ft.ElevatedButton("Sign in", bgcolor="#2C2C2C", color="white", on_click=lambda _: page.go("/login")),
                        ft.ElevatedButton("Register", bgcolor="white", color="black", on_click=lambda _: page.go("/register")),
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

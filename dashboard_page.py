import flet as ft
from flet.plotly_chart import PlotlyChart
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from user_utils import get_navigation_controls  # Add this import at the top

# Add nav_controls, optimization_data, parallel_plot to signature
def build_dashboard_page(page: ft.Page, results_df=None, loaded_session=None, alternatives_df=None, weights_df=None, nav_controls=None, optimization_data=None, parallel_plot=None):
    """Build the dashboard page to display results and allow saving."""

    # Determine if this is a loaded session BEFORE potentially overwriting dfs
    is_loaded_session = loaded_session is not None

    # Set flag in client storage for save button logic
    if is_loaded_session:
        page.client_storage.set("is_loaded_session", True)
    else:
        # Ensure flag is removed if it's not a loaded session
        page.client_storage.remove("is_loaded_session")

    # Check if a session was loaded from the profile page
    if is_loaded_session and (results_df is None or results_df.empty):  # Use loaded session if no results were provided directly
        results_df = pd.DataFrame(loaded_session.get("results", []))
        alternatives_df = pd.DataFrame(loaded_session.get("alternatives", []))
        weights_df = pd.DataFrame(loaded_session.get("weights", []))
        # Clear the loaded session from storage after use
        page.client_storage.remove("loaded_session") # Keep the is_loaded_session flag

    # If no nav_controls were provided, create them using get_navigationControls
    if nav_controls is None:
        user_data = page.client_storage.get("user_data")
        nav_controls = get_navigation_controls(page, user_data)

    # Check if results_df is valid
    if results_df is None or results_df.empty:
        return ft.View(
            "/dashboard",
            [
                # Updated navigation bar to match other pages
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
                            nav_controls,  # Use nav_controls here
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=15
                    )
                ),
                # Main content container with error message
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
                                        " - Dashboard",
                                        style=ft.TextStyle(
                                            size=32,
                                            weight=ft.FontWeight.NORMAL,
                                            color="white",
                                        ),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "No data available. Please go back and try again.",
                                style=ft.TextStyle(size=20, color="white")
                            ),
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                "Go back",
                                on_click=lambda _: page.go("/start"),
                                style=ft.ButtonStyle(
                                    bgcolor="white",
                                    color="black",
                                    padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                    text_style=ft.TextStyle(size=16)
                                )
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                    bgcolor="#2C2C2C"
                )
            ]
        )

    # Define default nav_controls if None is passed (for the main view)
    if nav_controls is None:
        nav_controls = ft.Row() # Provide a default empty Row

    # Create individual views that will be switched using tabs
    # Pass alt_df and weight_df to create_results_view
    # Pass optimization_data if available
    results_view = create_results_view(page, results_df, optimization_data, alternatives_df, weights_df)
    charts_view = create_chart_view(results_df)
    radar_view = create_radar_view(results_df)

    # Create views list
    views = [results_view, charts_view, radar_view]

    # Add optimization view if data is available
    optimization_view = None
    if optimization_data: # Check the argument
        optimization_view = create_optimization_view(results_df, optimization_data)
        views.insert(1, optimization_view)  # Insert after results view

    # Add parallel plot view if available
    parallel_view = None
    if parallel_plot is not None: # Check the argument
        # Assuming parallel_plot is the figure itself
        parallel_view = create_parallel_view(parallel_plot)
        views.insert(2, parallel_view)

    # Add data views
    alternatives_view = None
    weights_view = None

    # Always try to add alternatives and weights views
    if alternatives_df is not None and not alternatives_df.empty: # Check if DataFrame is not None and not empty
        alternatives_view = create_data_view(alternatives_df, "Alternatives Data")
        views.append(alternatives_view)

    if weights_df is not None and not weights_df.empty: # Check if DataFrame is not None and not empty
        weights_view = create_data_view(weights_df, "Weights Data")
        views.append(weights_view)

    # Create a reference to store the current view
    content_ref = ft.Ref[ft.Container]()

    # Create tab button labels with icons
    tab_labels = [
        {"text": "Results", "icon": ft.icons.ANALYTICS_OUTLINED},
        # {"text": "Score Chart", "icon": ft.icons.BAR_CHART}, # This seems redundant if charts_view is the bar chart
        # {"text": "Radar Chart", "icon": ft.icons.RADAR}, # This seems redundant
    ]
    # Add tabs based on the views actually created
    if optimization_view is not None:
        tab_labels.append({"text": "Optimization", "icon": ft.icons.INSIGHTS})
    if charts_view is not None: # Assuming charts_view is the bar chart
         tab_labels.append({"text": "Score Chart", "icon": ft.icons.BAR_CHART})
    if parallel_view is not None:
        tab_labels.append({"text": "Parallel Plot", "icon": ft.icons.STACKED_LINE_CHART})
    if radar_view is not None:
         tab_labels.append({"text": "Radar Chart", "icon": ft.icons.RADAR})
    if alternatives_view is not None:
        tab_labels.append({"text": "Alternatives", "icon": ft.icons.FORMAT_LIST_BULLETED})
    if weights_view is not None:
        tab_labels.append({"text": "Weights", "icon": ft.icons.SCALE})


    # Create tab buttons
    tab_buttons = []

    # Function to switch views
    def create_tab_click_handler(index):
        def handle_click(e):
            # Update all buttons styling
            for i, btn_data in enumerate(zip(tab_buttons, tab_labels)):
                btn, tab_info = btn_data
                icon_widget = btn.content.controls[0] # Get the Icon widget

                if i == index:
                    btn.bgcolor = "white"
                    btn.color = "#2C2C2C" # Text color
                    icon_widget.color = "#2C2C2C" # Icon color
                else:
                    btn.bgcolor = "#1C1C1C" # Use the card background color for unselected
                    btn.color = "white" # Text color
                    icon_widget.color = "white" # Icon color

            # Set the content - check if the view is a callable function
            if callable(views[index]):
                # If it's a function, call it with the page parameter
                content_ref.current.content = views[index](page)
            else:
                # Otherwise use it directly
                content_ref.current.content = views[index]

            page.update()
        return handle_click

    # Create tab buttons (ensure this loop uses the final tab_labels list)
    for i, tab in enumerate(tab_labels):
        is_selected = (i == 0)
        text_color = "#2C2C2C" if is_selected else "white"
        icon_color = "#2C2C2C" if is_selected else "white"
        bg_color = "white" if is_selected else "#1C1C1C" # Use card background for unselected

        btn = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(name=tab["icon"], size=18, color=icon_color), # Set initial icon color
                    ft.Text(tab["text"], size=14)
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            style=ft.ButtonStyle(
                bgcolor=bg_color, # Set initial background color
                color=text_color, # Set initial text color
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(12),
                elevation=0, # Keep elevation low for a flatter tab look
                overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE if not is_selected else ft.colors.BLACK), # Subtle overlay
            ),
            on_click=create_tab_click_handler(i)
        )
        tab_buttons.append(btn)

    # Build the page
    return ft.View(
        "/dashboard",
        [
            # Updated navigation bar to match other pages
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
                        nav_controls,  # Use nav_controls here
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=15
                )
            ),

            # Main content container
            ft.Container(
                content=ft.Column(
                    [
                        # Header with app title and optional "Saved Session" indicator
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
                                    " - Results Dashboard",
                                    style=ft.TextStyle(
                                        size=32,
                                        weight=ft.FontWeight.NORMAL,
                                        color="white",
                                    ),
                                ),
                                # Show a badge if this is a loaded session
                                ft.Container(
                                    content=ft.Chip(
                                        label=ft.Text("Saved Session", color="white"),
                                        bgcolor="#34A853",
                                        leading=ft.Icon(ft.icons.CHECK_CIRCLE, color="white", size=14),
                                        padding=8,
                                    ),
                                    visible=is_loaded_session, # Use defined variable
                                    margin=ft.margin.only(left=15)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),

                        # Custom tab bar
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Row(
                                        tab_buttons, # Use generated tab buttons
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=10,
                                        scroll=ft.ScrollMode.ADAPTIVE # Allow horizontal scroll if needed
                                    ),
                                    padding=ft.padding.all(10),
                                    bgcolor="#1C1C1C"
                                ),
                                elevation=4
                            ),
                            padding=ft.padding.only(top=20, bottom=5),
                        ),

                        # Content area that will be updated with the selected view
                        ft.Container(
                            ref=content_ref,
                            # Initialize with the first view's content
                            content=views[0](page) if callable(views[0]) else views[0],
                            expand=True
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                    expand=True
                ),
                alignment=ft.alignment.top_center,
                padding=20,
                expand=True,
                bgcolor="#2C2C2C"
            )
        ]
    )

def create_results_view(page, results_df, optimization_data=None, alt_df=None, weight_df=None):
    """Create a view to display results data table and summary."""

    # Create a copy of the DataFrame for sorting
    sorted_df = results_df.copy()

    # Create summary card with the highest-scoring alternative
    max_idx = sorted_df["Total Score"].idxmax() if "Total Score" in sorted_df.columns else 0
    top_alt = sorted_df.iloc[max_idx, 0] if not sorted_df.empty else "N/A"

    summary_card = ft.Card(
        content=ft.Container(
            content=ft.Column([ 
                ft.Text(f"Top Alternative: {top_alt}", size=22, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER, no_wrap=False)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=350,  # Wider horizontally (increased from 250)
            height=200,  # Reduced height (from 350) to make it a proper bar shape
            padding=ft.padding.symmetric(vertical=20, horizontal=15),
            bgcolor="#1C1C1C"
        )
    )
    
    # Reference to the DataTable for updating after sort
    table_ref = ft.Ref[ft.DataTable]()
    
    # Flag to track if table is ready for operations
    table_initialized = False

    # Track sort state - column index and direction
    sort_state = {
        "column": None,
        "ascending": True
    }

    def sort_data(column):
        """Sort the data by the specified column"""
        nonlocal sorted_df, sort_state
        
        # Safety check - make sure table is initialized
        if not table_initialized or table_ref.current is None:
            page.snack_bar = ft.SnackBar(ft.Text("Table is not ready for sorting yet. Please try again."))
            page.snack_bar.open = True
            page.update()
            return

        # Determine the column to sort by
        col_name = sorted_df.columns[column]

        # Check if we're sorting by the same column as before
        if sort_state["column"] == column:
            # Toggle sort direction
            sort_state["ascending"] = not sort_state["ascending"]
        else:
            # New column, set default sort direction
            # For first column (alternatives), sort ascending
            # For score columns, sort descending
            sort_state["ascending"] = (column == 0)
            sort_state["column"] = column

        # Sort the dataframe
        sorted_df = sorted_df.sort_values(
            by=col_name, 
            ascending=sort_state["ascending"]
        )

        # Update the table with new rows - passing page here
        update_table_rows(page)
        # Update column icons to show sort direction
        update_column_icons()

    def update_table_rows(page):
        """Update the table rows based on the sorted dataframe"""
        # Safety check - make sure table exists
        if table_ref.current is None:
            return
            
        # Clear existing rows
        table_ref.current.rows.clear()

        # Create new sorted rows
        for _, row in sorted_df.iterrows():
            cells = []
            for cell in row:
                # Format floats to 2 decimal places
                if isinstance(cell, float):
                    cell_text = f"{cell:.2f}"
                else:
                    cell_text = str(cell)
                cells.append(ft.DataCell(ft.Text(cell_text, color="white")))
            table_ref.current.rows.append(ft.DataRow(cells))

        # Update the page
        page.update()

    def update_column_icons():
        """Update column icons to reflect current sort state"""
        # Safety check - make sure table exists
        if table_ref.current is None:
            return
            
        for i, col in enumerate(table_ref.current.columns):
            # Skip columns without sort functionality
            if i != 0 and sorted_df.columns[i] != "Total Score" and sorted_df.columns[i] != "Ranking":
                continue

            # Get the row that contains the text and icon
            row_controls = col.content.controls
            
            # Find the icon button (should be the second control in the row)
            icon_button = row_controls[1]
            
            # Update the icon based on sort state
            if i == sort_state["column"]:
                # This column is being sorted - show the direction
                icon_button.icon = ft.icons.ARROW_UPWARD if sort_state["ascending"] else ft.icons.ARROW_DOWNWARD
            else:
                # Not the current sort column - show default sort icon
                icon_button.icon = ft.icons.ARROW_DOWNWARD

    # Create columns with sort functionality
    table_columns = []
    for i, col in enumerate(sorted_df.columns):
        # Add sort icon to columns that can be sorted
        if i == 0 or col == "Total Score" or col == "Ranking":  # First column or score/rank columns
            table_columns.append(
                ft.DataColumn(
                    ft.Row(
                        [
                            ft.Text(col, color="white"),
                            ft.IconButton(
                                icon=ft.icons.ARROW_DOWNWARD,  # Default icon
                                icon_color="white",
                                icon_size=16,
                                tooltip=f"Sort by {col}",
                                on_click=lambda e, col=i: sort_data(col)
                            )
                        ],
                        spacing=5
                    )
                )
            )
        else:
            # Regular column without sort functionality
            table_columns.append(ft.DataColumn(ft.Text(col, color="white")))

    # Create initial rows
    table_rows = []
    for _, row in sorted_df.iterrows():
        cells = []
        for cell in row:
            # Format floats to 2 decimal places
            if isinstance(cell, float):
                cell_text = f"{cell:.2f}"
            else:
                cell_text = str(cell)
            cells.append(ft.DataCell(ft.Text(cell_text, color="white")))
        table_rows.append(ft.DataRow(cells))

    # Create the DataTable with reference
    data_table = ft.DataTable(
        ref=table_ref,  # Assign the reference
        columns=table_columns,
        rows=table_rows,
        border=ft.border.all(1, "white"),
        vertical_lines=ft.border.BorderSide(1, "white"),
        horizontal_lines=ft.border.BorderSide(1, "white"),
        bgcolor="#1C1C1C",
        heading_row_height=70
    )
    
    # Mark table as initialized after creation
    table_initialized = True

    # Add optimization info if available
    optimization_info = ft.Container()
    if optimization_data:
        optimization_info = ft.Container(
            content=ft.Column([
                ft.Text("Optimization Approach", size=18, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(
                    f"The HIVES weights were used to find an optimal solution that balances all criteria.",
                    color="white", size=14
                ),
                ft.Text(
                    f"Execution time: {optimization_data['execution_time']:.2f} seconds",
                    color="white", size=14
                )
            ],

            padding=15,
            bgcolor="#1C1C1C",
            border=ft.border.all(1, "white"),
            border_radius=10,
            margin=ft.margin.only(bottom=20)
        )
        )

    # Create a dedicated save button for saving the complete dashboard data
    save_dashboard_button = create_save_button(page, "Save Session", 
                                              results_df, alt_df, weight_df, save_type="complete")

    # Important: Use the same data_table instance here
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Results", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(
                    content=ft.Row(
                        [summary_card],  # Only include the card in the row
                        alignment=ft.MainAxisAlignment.CENTER  # Center it
                    ),
                    height=80,  # Reduced height
                ),
                # Add save button in its own row if it exists
                ft.Container(
                    content=ft.Row(
                        [save_dashboard_button],
                        alignment=ft.MainAxisAlignment.END
                    ),
                    visible=save_dashboard_button is not None,
                    padding=ft.padding.only(bottom=10)
                ) if save_dashboard_button else ft.Container(height=0),
                ft.Container(height=10),
                optimization_info if optimization_data else ft.Container(),
                ft.Container(
                    content=data_table,  # Use the data_table with the reference
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10,
                    bgcolor="#1C1C1C"
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        expand=True
    )

def create_optimization_view(results_df, optimization_data):
    """Create a view to display optimization results."""

    # Extract optimal decision variables
    x_optimal = optimization_data.get('x_optimal', [])

    # Create a table for decision variables
    decision_vars_rows = []
    for i, val in enumerate(x_optimal):
        decision_vars_rows.append(
            ft.DataRow([
                ft.DataCell(ft.Text(f"x_{i+1}", color="white")),
                ft.DataCell(ft.Text(f"{val:.6f}", color="white"))
            ])
        )

    decision_vars_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Variable", color="white")),
            ft.DataColumn(ft.Text("Value", color="white"))
        ],
        rows=decision_vars_rows,
        border=ft.border.all(1, "white"),
        vertical_lines=ft.border.BorderSide(1, "white"),
        horizontal_lines=ft.border.BorderSide(1, "white"),
        bgcolor="#1C1C1C"
    )

    # Extract criteria and values from results_df
    if 'Criterion' in results_df.columns and 'Value' in results_df.columns:
        criteria = results_df['Criterion'].tolist()
        values = results_df['Value'].tolist()
        weights = results_df['Weight'].tolist() if 'Weight' in results_df.columns else None

        # Create visualization of the results
        # Bar chart for objective values
        value_chart_data = []
        for i, (criterion, value) in enumerate(zip(criteria, values)):
            value_chart_data.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[ft.BarChartRod(
                        from_y=0,
                        to_y=value,
                        width=40,
                        color="#4285F4",
                        border_radius=ft.border_radius.all(5),
                        tooltip=f"{criterion}: {value:.4f}",
                    )]
                )
            )

        max_value = max(values) * 1.1 if values else 1 # Handle empty values list

        value_chart = ft.BarChart(
            bar_groups=value_chart_data,
            animate=300,
            border=ft.border.all(1, "white"),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=max_value/5,
                color="white54",
                width=1,
            ),
            max_y=max_value,
            tooltip_bgcolor="#2C2C2C",
            height=250,
            left_axis=ft.ChartAxis(
                # Corrected list comprehension for labels
                labels=[
                    ft.ChartAxisLabel(
                        value=i * max_value/5,
                        label=ft.Text(f"{i * max_value/5:.1f}", size=10, color="white")
                    )
                    for i in range(6) # Generate 6 labels (0 to 5 intervals)
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Container(
                            content=ft.Text(
                                criteria[i] if len(criteria[i]) < 12 else criteria[i][:10] + "...",
                                size=10,
                                color="white",
                            ),
                            alignment=ft.alignment.center,
                            width=40,
                            height=40
                        )
                    )
                    for i in range(len(criteria))
                ],
                labels_size=60
            )
        )
    else: # Handle case where required columns are missing
        value_chart = ft.Text("Objective data columns ('Criterion', 'Value') not found.", color="orange")


    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Optimization Results", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("What is this?", size=18, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text(
                            "The optimization approach uses HIVES to determine consensus weights among decision makers, "
                            "then finds a single optimal solution that best balances all criteria according to those weights.",
                            color="white", size=14
                        ),
                        ft.Text(
                            f"Execution time: {optimization_data['execution_time']:.2f} seconds",
                            color="white", size=14, italic=True
                        )
                    ]),
                    padding=15,
                    bgcolor="#1C1C1C",
                    border=ft.border.all(1, "white"),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                ft.Container(
                    content=decision_vars_table,
                    padding=10,
                    bgcolor="#1C1C1C"
                ),
                ft.Container(
                    content=value_chart, # Use the defined value_chart
                    padding=10,
                    bgcolor="#1C1C1C"
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        expand=True
    )

def create_chart_view(results_df):
    """Create a modern bar chart of the results using Flet's native chart components."""
    # Find the best column names to use
    if "Alternative" in results_df.columns:
        x_col = "Alternative"
    elif results_df.columns[0] in ["Candidates", "Alternatives", "DMs"]:
        x_col = results_df.columns[0]
    else:
        x_col = results_df.columns[0]  # Use first column

    y_col = "Total Score" if "Total Score" in results_df.columns else results_df.columns[-2]

    # Extract data for the bar chart
    alternatives = results_df[x_col].tolist()
    scores = results_df[y_col].tolist()

    # Calculate max score for scale
    max_score = max(scores) * 1.1  # Add 10% for better visualization

    # Generate bar chart data
    chart_data = []
    for i, (alt, score) in enumerate(zip(alternatives, scores)):
        chart_data.append(
            ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=score,
                        width=40,
                        color="#4285F4",
                        border_radius=ft.border_radius.all(5),
                        tooltip=f"{alt}: {score:.2f}",
                    )
                ]
            )
        )

    # Create label texts - truncate long labels
    label_texts = []
    for alt in alternatives:
        if len(alt) > 15:
            label_texts.append(alt[:15] + "...")
        else:
            label_texts.append(alt)

    # Create the bar chart
    bar_chart = ft.BarChart(
        bar_groups=chart_data,
        animate=300,
        border=ft.border.all(1, "white"),
        horizontal_grid_lines=ft.ChartGridLines(
            interval=max_score/5,
            color="white54",
            width=1,
        ),
        max_y=max_score,
        tooltip_bgcolor="#2C2C2C",
        expand=True,
        left_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=i * max_score/5,
                    label=ft.Text(f"{i * max_score/5:.1f}", size=10, color="white")
                )
                for i in range(6)
            ],
            labels_size=40
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=i,
                    label=ft.Container(
                        content=ft.Text(
                            label_texts[i],
                            size=10,
                            color="white",
                        ),
                        alignment=ft.alignment.center,
                        # Remove the transform property and adjust sizing for many labels
                        width=50 if len(alternatives) > 5 else None,
                        height=40 if len(alternatives) > 5 else None,
                    )
                )
                for i in range(len(alternatives))
            ],
            labels_size=80 if len(alternatives) > 5 else 40
        )
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Score Visualisation", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(
                    content=bar_chart,
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10,
                    bgcolor="#1C1C1C",
                    expand=True,
                    height=500
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        expand=True
    )

def create_radar_view(results_df):
    """Create a radar chart that allows users to select multiple alternatives for comparison."""

    # Find the first column (alternatives column)
    alt_col = results_df.columns[0]

    # Get all alternatives
    alternatives = results_df[alt_col].tolist()

    # Get criteria columns - exclude first column, Total Score, and Rank columns
    criteria_cols = [col for col in results_df.columns if col != alt_col and col != "Total Score" and col != "Rank" and col != "Ranking"]

    # Check for minimum number of criteria
    if len(criteria_cols) < 3:
        return ft.Container(
            content=ft.Text("Not enough criteria for radar chart (minimum 3 required)", color="white"),
            padding=20
        )

    # Reference to the chart to update when selections change
    chart_ref = ft.Ref[ft.Container]()
    
    # Reference to debug info text for updating
    debug_info_ref = ft.Ref[ft.Text]()
    
    # Enable debug mode - set to False to hide debug panel
    debug_mode = False

    # List to store selected alternatives
    selected_alternatives = [alternatives[0]]  # Default: first alternative selected

    # Generate a fixed set of colors for consistency
    colors = [
        "#4285F4", "#EA4335", "#FBBC05", "#34A853", "#8AB4F8", "#F6AEA9", 
        "#FDE293", "#A8DAB5", "#D2E3FC", "#FCCCC5", "#FEF7C0", "#CEEAD6"
    ]

    # Calculate the global min and max for each criterion for normalization
    # This helps ensure that the radar chart displays consistently
    min_vals = {}
    max_vals = {}
    avg_vals = {}  # For reference lines

    for col in criteria_cols:
        min_vals[col] = results_df[col].min()
        max_vals[col] = results_df[col].max()
        avg_vals[col] = results_df[col].mean()

        # Avoid division by zero for normalization
        if min_vals[col] == max_vals[col]:  # If all values are the same
            max_vals[col] = min_vals[col] + 1  # Avoid division by zero

    def normalize_value(value, col):
        """Normalize a value between 0 and 1"""
        if max_vals[col] == min_vals[col]:
            return 0.5  # Default to middle if all values are the same
        return (value - min_vals[col]) / (max_vals[col] - min_vals[col])

    def update_debug_info(message="", error=None):
        """Update the debug information panel"""
        if not debug_mode or debug_info_ref.current is None:
            return
            
        debug_text = f"Selected alternatives: {selected_alternatives}\n"
        debug_text += f"Total alternatives in data: {len(alternatives)}\n"
        debug_text += f"Criteria columns: {len(criteria_cols)}\n"
        
        if message:
            debug_text += f"\nMessage: {message}\n"
            
        if error:
            debug_text += f"\nError: {str(error)}\n"
            debug_text += f"Error type: {type(error).__name__}\n"
            
            # Add traceback for more detailed error info
            import traceback
            debug_text += f"\nTraceback:\n{traceback.format_exc()}"
            
        debug_info_ref.current.value = debug_text
        
    def update_radar_chart():
        """Update the radar chart with currently selected alternatives"""
        try:
            # Show loading state
            chart_ref.current.content = ft.Column([
                ft.ProgressRing(color="white"),
                ft.Text("Updating chart...", color="white")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            # Update debug info with current selection
            update_debug_info(f"Updating chart with {len(selected_alternatives)} alternatives")
            
            # Filter the dataframe for selected alternatives
            selected_df = results_df[results_df[alt_col].isin(selected_alternatives)]
            
            # Check if filtering worked correctly
            if selected_df.empty and selected_alternatives:
                error_msg = f"No data found after filtering for alternatives: {selected_alternatives}"
                update_debug_info(error_msg)
                chart_ref.current.content = ft.Text(
                    error_msg, 
                    color="orange"
                )
                return
                
            # Create a new radar plot
            fig = go.Figure()

            # Special case: If no data or only one criterion, show message
            if selected_df.empty:
                chart_ref.current.content = ft.Text("No data selected", color="white")
                return

            # Add reference line for average values if the checkbox is checked
            if show_avg_ref.value:
                # Calculate normalized average values for each criterion
                avg_values = []
                hover_texts = []

                for col in criteria_cols:
                    avg_value = avg_vals[col]
                    normalized_avg = normalize_value(avg_value, col)
                    avg_values.append(normalized_avg)
                    hover_texts.append(f"{col} Avg: {avg_value:.2f}")

                # Close the polygon by repeating the first value
                avg_values.append(avg_values[0])
                hover_texts.append(hover_texts[0])

                fig.add_trace(go.Scatterpolar(
                    r=avg_values,
                    theta=criteria_cols + [criteria_cols[0]],
                    name="Average",
                    line=dict(color="white", width=2, dash="dash"),
                    marker=dict(size=4, color="white"),
                    fill=None,
                    hoverinfo="text",
                    hovertext=hover_texts
                ))
                
                # Debug: log average values
                update_debug_info(f"Added average reference line with values: {avg_values[:3]}...")

            # Process the data for each selected alternative
            traces_added = 0
            for i, (_, row) in enumerate(selected_df.iterrows()):
                alt_name = row[alt_col]
                
                # Debug which alternative we're processing
                update_debug_info(f"Processing alternative: {alt_name}")

                # Get normalized values for each criterion
                values = []
                hover_texts = []

                for col in criteria_cols:
                    value = row[col]
                    normalized_value = normalize_value(value, col)
                    values.append(normalized_value)
                    hover_texts.append(
                        f"{col}: {value:.2f}<br>"
                        f"Normalized: {normalized_value:.2f}<br>"
                        f"Average: {avg_vals[col]:.2f}"
                    )

                # Close the polygon by repeating the first value and hover text
                values.append(values[0])
                hover_texts.append(hover_texts[0])

                # Get the color for this alternative
                color = colors[i % len(colors)]

                # Extract the RGB components from hex
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)

                # Add a trace for this alternative
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=criteria_cols + [criteria_cols[0]],
                    fill='toself',
                    name=alt_name,
                    line=dict(color=color, width=2),
                    fillcolor=f'rgba({r}, {g}, {b}, 0.25)',
                    hoverinfo="text",
                    hovertext=hover_texts
                ))
                traces_added += 1

            # Update debug info with trace count
            update_debug_info(f"Added {traces_added} traces to the chart")

            # Update layout with improved settings
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1.0],
                        showticklabels=True,
                        tickvals=[0, 0.25, 0.5, 0.75, 1.0],
                        ticktext=["0", "0.25", "0.5", "0.75", "1.0"],
                        gridcolor="white",
                        color="white"
                    ),
                    angularaxis=dict(
                        color="white",
                        gridcolor="white",
                        linecolor="white"
                    ),
                    bgcolor="#1C1C1C"
                ),
                paper_bgcolor="#1C1C1C",
                plot_bgcolor="#1C1C1C",
                font=dict(color="white"),
                margin=dict(l=10, r=10, t=30, b=10),  # Reduced margins
                height=450,  # Increased from 380 to 450 for more space
                showlegend=True,
                legend=dict(
                    font=dict(color="white"),
                    bgcolor="rgba(44, 44, 44, 0.7)",
                    bordercolor="white",
                    borderwidth=1
                ),
                dragmode=False,  # Disable drag to prevent accidental chart manipulation
                uirevision='true',  # Preserve zoom level when updating
                hovermode="closest"
            )

            # Update the chart container
            plotly_chart = PlotlyChart(fig, expand=True)
            chart_ref.current.content = plotly_chart
            update_debug_info("Chart updated successfully")
            
        except Exception as e:
            # Display error message if something goes wrong
            chart_ref.current.content = ft.Text(f"Error creating chart: {str(e)}", color="red")
            # Update debug info with error details
            update_debug_info("Error updating chart", e)

    # Create checkboxes for each alternative
    checkboxes = []

    # Function to handle checkbox changes
    def on_checkbox_change(e):
        alt = e.control.data
        if e.control.value:
            if alt not in selected_alternatives:
                selected_alternatives.append(alt)
                update_debug_info(f"Added {alt} to selections")
        else:
            if alt in selected_alternatives:
                selected_alternatives.remove(alt)
                update_debug_info(f"Removed {alt} from selections")

        # Ensure at least one alternative is selected
        if not selected_alternatives:
            e.control.value = True
            selected_alternatives.append(alt)
            update_debug_info(f"Re-added {alt} (keeping minimum selection)")
            e.page.update()
            return

        # Update the chart
        update_radar_chart()
        e.page.update()

    # Function to handle average reference toggle
    def on_avg_ref_change(e):
        # Update the chart immediately when the checkbox is toggled
        update_radar_chart()
        # Make sure to update the page to show the changes
        e.page.update()

    # Function to select/deselect all alternatives
    def on_select_all(e):
        # Set all checkboxes to checked (True)
        for cb in checkboxes:
            cb.value = True

        # Update selected alternatives list to include all alternatives
        selected_alternatives.clear()
        selected_alternatives.extend(alternatives)

        # Update the chart
        update_radar_chart()
        e.page.update()

    # Function to deselect all except the first alternative
    def on_deselect_all(e):
        # Keep track of if we've kept one selected
        kept_one = False

        # Clear the selected alternatives list
        selected_alternatives.clear()

        # Update all checkboxes
        for i, cb in enumerate(checkboxes):
            if i == 0 and not kept_one:
                # Keep the first one selected to ensure at least one is always selected
                cb.value = True
                selected_alternatives.append(cb.data)
                kept_one = True
            else:
                cb.value = False

        # Update the chart
        update_radar_chart()
        e.page.update()

    # Create a checkbox for each alternative
    for i, alt in enumerate(alternatives):
        cb = ft.Checkbox(
            label=alt,
            label_style=ft.TextStyle(color="white"),
            value=True if i == 0 else False,  # Default: only first alternative selected
            data=alt,
            fill_color="white",
            check_color="#1C1C1C",
            on_change=on_checkbox_change
        )
        checkboxes.append(cb)

    # Create select all and deselect all buttons
    select_all_btn = ft.ElevatedButton(
        "Select All",
        icon=ft.icons.SELECT_ALL,
        on_click=on_select_all,
        style=ft.ButtonStyle(
            bgcolor="#2A5B9F",
            color="white"
        )
    )

    deselect_all_btn = ft.ElevatedButton(
        "Deselect All",
        icon=ft.icons.DESELECT,
        on_click=on_deselect_all,
        style=ft.ButtonStyle(
            bgcolor="#953735",
            color="white"
        )
    )

    # Create reference line toggles - only average reference
    show_avg_ref = ft.Checkbox(
        label="Show Average Reference",
        value=False,
        fill_color="white",
        check_color="#1C1C1C",
        label_style=ft.TextStyle(color="white"),
        on_change=on_avg_ref_change  # Use the dedicated handler function
    )

    # Use a single column with all checkboxes - better for scrolling with many alternatives
    checkbox_column = ft.Column(
        [cb for cb in checkboxes],
        spacing=5,
        scroll=ft.ScrollMode.AUTO,
    )

    # Initial container for the chart (will be populated by update function)
    chart_container = ft.Container(
        ref=chart_ref,
        expand=True,
        height=500,  # Increased from 450 to 500 for more space at bottom
        bgcolor="#1C1C1C",
        border=ft.border.all(1, "white"),
        border_radius=10,
        padding=10
    )

    # Create control panel with increased width for better alternative selection
    control_panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("Select Alternatives to Compare", 
                       size=16, 
                       color="white", 
                       weight=ft.FontWeight.BOLD),
                ft.Divider(color="white54", height=1),

                # Add Select All / Deselect All buttons in a row
                ft.Row(
                    [select_all_btn, deselect_all_btn],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),

                ft.Container(
                    content=checkbox_column,
                    height=255,  # Adjusted height to accommodate the new buttons
                    expand=True,
                    border=ft.border.all(1, "#3C3C3C"),
                    border_radius=5,
                    bgcolor="#262626",
                    padding=10
                ),
                ft.Container(height=5),
                show_avg_ref  # Only showing the average reference option
            ],
            spacing=10
        ),
        width=300,  # Increased from 250 to 300 for better readability
        padding=15,
        border=ft.border.all(1, "white"),
        border_radius=10,
        bgcolor="#2C2C2C",
        height=500  # Increased from 450 to 500 to match chart height
    )

    # Create a debug panel
    debug_panel = ft.Container(
        content=ft.Column([
            ft.Text("Debug Information", color="yellow", weight=ft.FontWeight.BOLD),
            ft.Divider(color="yellow"),
            ft.Text(
                ref=debug_info_ref,
                value="Debug information will appear here...",
                color="yellow", 
                selectable=True,
                no_wrap=False,
                size=12
            )
        ],
        scroll=ft.ScrollMode.ALWAYS),  # Move scroll property here, to the Column
        padding=10,
        bgcolor="#2A2A2A",
        border=ft.border.all(1, "yellow"),
        border_radius=5,
        visible=debug_mode,
        margin=ft.margin.only(top=20),
        height=300
    )

    # Add debug panel to the layout if debug mode is enabled
    main_content = [
        ft.Container(height=15),
        ft.Container(
            content=ft.Row(
                [
                    control_panel,
                    ft.Container(width=15),  # Spacing
                    ft.Container(
                        content=chart_container,
                        expand=True
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START
            ),
            expand=True
        )
    ]
    
    if debug_mode:
        main_content.append(debug_panel)

    # Create the view with improved layout
    view = ft.Container(
        content=ft.Column(
            main_content,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,  # Added spacing between elements
        ),
        padding=ft.padding.only(left=20, top=20, right=20, bottom=30),  # Extra padding at bottom
        expand=True
    )

    # Initialize the chart
    update_radar_chart()

    return view

def create_parallel_view(parallel_plot):
    """Create a view for the parallel coordinates plot."""
    # Style the plot for dark theme
    parallel_plot.update_layout(
        paper_bgcolor="#1C1C1C",
        plot_bgcolor="#1C1C1C",
        font=dict(color="white")
    )

    chart = PlotlyChart(parallel_plot, expand=True)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Parallel Coordinates Plot", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(
                    content=chart,
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10,
                    bgcolor="#1C1C1C",
                    expand=True,
                    height=500
                ),
                ft.Container(
                    content=ft.Text(
                        "The parallel coordinates plot helps visualize multi-dimensional data. Each vertical line represents a criterion, and each colored line represents an alternative.",
                        color="white", size=14, italic=True
                    ),
                    padding=ft.padding.only(top=10)
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        expand=True
    )

def create_data_view(data_df, title_text):
    """Create a view to display data tables."""
    if data_df is None or (isinstance(data_df, pd.DataFrame) and data_df.empty):
        # Return a function that returns the container, consistent with the successful case
        return lambda page: ft.Container( 
            content=ft.Text(f"No {title_text.lower()} available", color="white"),
            padding=20
        )

    # Convert to DataFrame if it's a dictionary
    if isinstance(data_df, dict):
        data_df = pd.DataFrame(data_df)

    # Create columns for data table
    table_columns = [
        ft.DataColumn(ft.Text(col, color="white")) 
        for col in data_df.columns
    ]

    # Create rows for data table
    table_rows = []
    for _, row in data_df.iterrows():
        cells = []
        for cell in row:
            # Format floats to 2 decimal places
            if isinstance(cell, float):
                cell_text = f"{cell:.2f}"
            else:
                cell_text = str(cell)
            cells.append(ft.DataCell(ft.Text(cell_text, color="white")))
        table_rows.append(ft.DataRow(cells))

    data_table = ft.DataTable(
        columns=table_columns,
        rows=table_rows,
        border=ft.border.all(1, "white"),
        vertical_lines=ft.border.BorderSide(1, "white"),
        horizontal_lines=ft.border.BorderSide(1, "white"),
        bgcolor="#1C1C1C",
        heading_row_height=70
    )

    # Determine which data we're displaying
    is_alternatives = "alternatives" in title_text.lower() or "alt" in title_text.lower()
    is_weights = "weights" in title_text.lower() or "weight" in title_text.lower()

    # Return a lambda that builds the view when called
    return lambda page: ft.Container(
        content=ft.Column(
            [
                # Replace the row with a container containing a centered title and right-aligned button
                ft.Container(
                    content=ft.Stack(
                        [
                            # Center the title
                            ft.Container(
                                content=ft.Row(
                                    [ft.Text(title_text, size=24, weight=ft.FontWeight.BOLD, color="white")],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                expand=True
                            ),
                            # Position the save button on the right if it exists
                            ft.Container(
                                content=create_save_button(
                                    page, 
                                    "Save This Dataset", 
                                    None if not is_alternatives else data_df,
                                    data_df if is_alternatives else None,
                                    data_df if is_weights else None,
                                    save_type="dataset"
                                ),
                                alignment=ft.alignment.top_right,
                                visible=create_save_button(page, "", None, None, None) is not None
                            )
                        ],
                    ),
                    height=70,
                    padding=ft.padding.only(bottom=10)
                ),
                
                ft.Container(
                    content=data_table,
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10,
                    bgcolor="#1C1C1C"
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        expand=True
    )

def create_save_button(page, button_text, results_df=None, alt_df=None, weight_df=None, save_type="complete"):
    """Create a button to save data based on the specified type."""
    # Check if user is logged in
    user_data = page.client_storage.get("user_data")

    # Check if this is a loaded session using the flag from client storage
    is_loaded_session = page.client_storage.get("is_loaded_session") or False

    # Don't show save buttons if not logged in or if this is already a loaded session
    if not user_data or is_loaded_session:
        return None

    # Create a save button
    def save_data_to_profile(e):
        try:
            # Get current user ID directly from client storage
            user_id = page.client_storage.get("user_id") # Changed this line

            if not user_id:
                page.snack_bar = ft.SnackBar(ft.Text("Error: User ID not found in storage. Please log in again.")) # Updated error message
                page.snack_bar.open = True
                page.update()
                return

            # Create a dialog to get session name
            session_name_ref = ft.Ref[ft.TextField]()

            def save_session_with_name(e):
                # Get the session name from the text field
                default_name = f"Session {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
                if save_type == "dataset":
                    # For dataset saves, use a more specific default name
                    if alt_df is not None and not isinstance(alt_df, pd.DataFrame):
                        default_name = f"Alternatives {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"
                    elif weight_df is not None and not isinstance(weight_df, pd.DataFrame):
                        # Fixed: Add missing closing quote in the format string
                        default_name = f"Weights {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"

                session_name = session_name_ref.current.value or default_name

                # Close the dialog
                session_dialog.open = False
                # page.update() # Update is called later after potential snackbar

                # Prepare data to save - start with timestamp and name
                save_data_payload = { # Renamed to avoid conflict with firebase function
                    "session_name": session_name,
                    "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                # Create a comprehensive data package with all available dataframes
                data_package = {}

                # Add results if available and should be included in this save type
                if results_df is not None and save_type == "complete":
                    # Ensure it's a DataFrame before calling to_dict
                    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
                        data_package["results"] = results_df.to_dict('records')
                    # elif not isinstance(results_df, pd.DataFrame): # Avoid saving non-dataframe results directly unless intended
                    #     data_package["results"] = results_df

                # Add alternatives if available
                if alt_df is not None:
                     # Ensure it's a DataFrame before calling to_dict
                    if isinstance(alt_df, pd.DataFrame) and not alt_df.empty:
                        data_package["alternatives"] = alt_df.to_dict('records')
                    # elif not isinstance(alt_df, pd.DataFrame):
                    #     data_package["alternatives"] = alt_df

                # Add weights if available
                if weight_df is not None:
                     # Ensure it's a DataFrame before calling to_dict
                    if isinstance(weight_df, pd.DataFrame) and not weight_df.empty:
                        data_package["weights"] = weight_df.to_dict('records')
                    # elif not isinstance(weight_df, pd.DataFrame):
                    #     data_package["weights"] = weight_df

                # Check if there's actually any data to save
                if not data_package:
                    page.snack_bar = ft.SnackBar(ft.Text("No data selected or available to save for this type"))
                    page.snack_bar.open = True
                    page.update()
                    return

                # Add the data package to save_data
                save_data_payload["data"] = data_package

                # Get existing saved data or initialize empty dict
                try:
                    from firebase_functions import load_data
                    existing_data = load_data(page, user_id)

                    if not existing_data:
                        existing_data = {"saved_sessions": []}
                    elif "saved_sessions" not in existing_data or not isinstance(existing_data["saved_sessions"], list):
                         # Ensure saved_sessions exists and is a list
                        existing_data["saved_sessions"] = []

                    # Add new data to the list
                    existing_data["saved_sessions"].append(save_data_payload)

                    # Save updated data to Firebase
                    from firebase_functions import save_data as firebase_save
                    firebase_save(page, user_id, existing_data)

                    # Show success message
                    data_type = "complete session" if save_type == "complete" else "dataset"
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"{data_type.capitalize()} '{session_name}' saved to your profile")
                    )
                    page.snack_bar.open = True

                except Exception as db_error:
                     page.snack_bar = ft.SnackBar(ft.Text(f"Database error: {str(db_error)}"))
                     page.snack_bar.open = True

                page.update() # Update page after potential snackbar

            # Create dialog title and hint text based on save type
            dialog_title = "Save Session" if save_type == "complete" else "Save Dataset"
            hint_text = f"Session {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"

            if save_type == "dataset":
                if alt_df is not None:
                    hint_text = f"Alternatives {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"
                elif weight_df is not None:
                    hint_text = f"Weights {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"

            # Create and display a dialog to get session name
            session_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(dialog_title),
                content=ft.Column([ 
                    ft.Text("Enter a name for this save:"),
                    ft.TextField(
                        ref=session_name_ref,
                        hint_text=hint_text,
                        autofocus=True,
                        border_color="white",
                    ),
                ], tight=True, spacing=20, width=400),
                actions=[
                    ft.ElevatedButton(
                        "Cancel", 
                        on_click=lambda e: setattr(session_dialog, 'open', False) or page.update()
                    ),
                    ft.ElevatedButton(
                        "Save", 
                        on_click=save_session_with_name,
                        bgcolor="#34A853",
                        color="white"
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            # Show the dialog
            page.dialog = session_dialog
            session_dialog.open = True
            page.update()

        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error saving data: {str(e)}"))
            page.snack_bar.open = True
            page.update()

    # Choose button color based on save type
    button_color = "#34A853" if save_type == "complete" else "#4285F4"
    button_icon = ft.icons.SAVE if save_type == "complete" else ft.icons.DATASET

    save_button = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(name=button_icon, color="white"),
                ft.Text(button_text, color="white")
            ],
            spacing=5
        ),
        style=ft.ButtonStyle(
            bgcolor=button_color,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=save_data_to_profile,
        width=180, 
        height=50, 
    )

    return save_button

import flet as ft
from flet.plotly_chart import PlotlyChart
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random

def build_dashboard_page(page: ft.Page, results_df=None, parallel_plot=None, alt_df=None, weight_df=None):
    """Build a dashboard page to display MCGDM results."""
    
    # Check if results_df is a dictionary and convert to DataFrame if needed
    if isinstance(results_df, dict):
        if "results" in results_df:
            # Extract both results and the other dataframes
            results = pd.DataFrame(results_df["results"])
            
            if "alternatives" in results_df:
                alt_df = pd.DataFrame(results_df["alternatives"])
            
            if "weights" in results_df:
                weight_df = pd.DataFrame(results_df["weights"])
                
            results_df = results
        else:
            results_df = pd.DataFrame(results_df)
    
    # If no data provided or empty DataFrame, show error message
    if results_df is None or (isinstance(results_df, pd.DataFrame) and results_df.empty):
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
                            ft.Row(
                                [
                                    ft.ElevatedButton("Sign in", bgcolor="#2C2C2C", color="white", on_click=lambda _: page.go("/login")),
                                    ft.ElevatedButton("Register", bgcolor="white", color="black", on_click=lambda _: page.go("/register")),
                                ],
                                spacing=15
                            ),
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
    
    # Create individual views that will be switched using tabs
    results_view = create_results_view(page, results_df)
    charts_view = create_chart_view(results_df)
    radar_view = create_radar_view(results_df)
    
    # Create views list
    views = [results_view, charts_view, radar_view]
    
    # Add parallel plot view if available
    parallel_view = None
    if parallel_plot is not None:
        parallel_view = create_parallel_view(parallel_plot)
        views.insert(2, parallel_view)
    
    # Add data views
    alternatives_view = None
    weights_view = None
    
    # Always try to add alternatives and weights views
    if alt_df is not None:
        alternatives_view = create_data_view(alt_df, "Alternatives Data")
        views.append(alternatives_view)
    
    if weight_df is not None:
        weights_view = create_data_view(weight_df, "Weights Data")
        views.append(weights_view)
    
    # Create a reference to store the current view
    content_ref = ft.Ref[ft.Container]()
    
    # Create tab button labels with icons
    tab_labels = [
        {"text": "Results", "icon": ft.icons.ANALYTICS_OUTLINED},
        {"text": "Score Chart", "icon": ft.icons.BAR_CHART},
        {"text": "Radar Chart", "icon": ft.icons.RADAR},
    ]
    
    # Insert parallel plot tab if available
    if parallel_view is not None:
        tab_labels.insert(2, {"text": "Parallel Plot", "icon": ft.icons.STACKED_LINE_CHART})
    
    # Add alternatives and weights tabs if available
    if alternatives_view is not None:
        tab_labels.append({"text": "Alternatives", "icon": ft.icons.FORMAT_LIST_BULLETED})
    
    if weights_view is not None:
        tab_labels.append({"text": "Weights", "icon": ft.icons.SCALE})
    
    # Create tab buttons
    tab_buttons = []
    
    # Function to switch views
    def create_tab_click_handler(index):
        def handle_click(e):
            # Update all buttons
            for i, btn in enumerate(tab_buttons):
                if i == index:
                    btn.bgcolor = "white"
                    btn.color = "#2C2C2C"
                else:
                    btn.bgcolor = "#2C2C2C"
                    btn.color = "white"
            
            # Set the content
            content_ref.current.content = views[index]
            page.update()
        return handle_click
    
    # Create tab buttons
    for i, tab in enumerate(tab_labels):
        btn = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(name=tab["icon"], size=18),
                    ft.Text(tab["text"], size=14)
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            style=ft.ButtonStyle(
                bgcolor="white" if i == 0 else "#2C2C2C",
                color="#2C2C2C" if i == 0 else "white",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(12),
            ),
            elevation=0,
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
                        ft.Row(
                            [
                                ft.ElevatedButton("Sign in", bgcolor="#2C2C2C", color="white", on_click=lambda _: page.go("/login")),
                                ft.ElevatedButton("Register", bgcolor="white", color="black", on_click=lambda _: page.go("/register")),
                            ],
                            spacing=15
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=15
                )
            ),
            
            # Main content container
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
                                    " - Results Dashboard",
                                    style=ft.TextStyle(
                                        size=32,
                                        weight=ft.FontWeight.NORMAL,
                                        color="white",
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        
                        # Custom tab bar
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Row(
                                        tab_buttons,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=10
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
                            content=views[0],  # Start with results view
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

def create_results_view(page, results_df):
    """Create a view to display results data table and summary."""
    
    # Create a copy of the DataFrame for sorting
    sorted_df = results_df.copy()
    
    # Create summary card with the highest-scoring alternative
    max_idx = sorted_df["Total Score"].idxmax() if "Total Score" in sorted_df.columns else 0
    top_alt = sorted_df.iloc[max_idx, 0] if not sorted_df.empty else "N/A"
    
    summary_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Top Alternative", size=20, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(f"{top_alt}", size=30, color="white")
            ]),
            width=300,
            padding=20,
            bgcolor="#1C1C1C"
        )
    )

    # Reference to the DataTable for updating after sort
    table_ref = ft.Ref[ft.DataTable]()
    
    def sort_data(column):
        """Sort the data by the specified column"""
        nonlocal sorted_df
        
        # Determine the column to sort by
        col_name = sorted_df.columns[column]
        
        # Check if we're sorting by first column (Alternative) or by score
        if column == 0:  # First column (Alternative name)
            sorted_df = sorted_df.sort_values(by=col_name)
        else:  # Any other column (likely Total Score)
            sorted_df = sorted_df.sort_values(by=col_name, ascending=False)  # Higher scores on top
            
        # Update the table with new rows - passing page here
        update_table_rows(page)
    
    def update_table_rows(page):
        """Update the table rows based on the sorted dataframe"""
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
    
    # Create columns with sort functionality
    table_columns = []
    for i, col in enumerate(sorted_df.columns):
        # Add sort icon to columns that can be sorted
        if i == 0 or col == "Ranking":  # First column or score/rank columns
            table_columns.append(
                ft.DataColumn(
                    ft.Row(
                        [
                            ft.Text(col, color="white"),
                            ft.IconButton(
                                icon=ft.icons.ARROW_DOWNWARD,
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
    results_table = ft.DataTable(
        ref=table_ref,
        columns=table_columns,
        rows=table_rows,
        border=ft.border.all(1, "white"),
        vertical_lines=ft.border.BorderSide(1, "white"),
        horizontal_lines=ft.border.BorderSide(1, "white"),
        bgcolor="#1C1C1C",
        heading_row_height=70
    )
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Results", size=24, weight=ft.FontWeight.BOLD, color="white"),
                summary_card,
                ft.Container(height=20),
                ft.Container(
                    content=results_table,
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
    
    def update_radar_chart():
        """Update the radar chart with currently selected alternatives"""
        try:
            # Filter the dataframe for selected alternatives
            selected_df = results_df[results_df[alt_col].isin(selected_alternatives)]
            
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
            
            # Process the data for each selected alternative
            for i, (_, row) in enumerate(selected_df.iterrows()):
                alt_name = row[alt_col]
                
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
                height=380,  # Slightly smaller height
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
        except Exception as e:
            # Display error message if something goes wrong
            chart_ref.current.content = ft.Text(f"Error creating chart: {str(e)}", color="red")
    
    # Create checkboxes for each alternative
    checkboxes = []
    
    # Function to handle checkbox changes
    def on_checkbox_change(e):
        alt = e.control.data
        if e.control.value:
            if alt not in selected_alternatives:
                selected_alternatives.append(alt)
        else:
            if alt in selected_alternatives:
                selected_alternatives.remove(alt)
        
        # Ensure at least one alternative is selected
        if not selected_alternatives:
            e.control.value = True
            selected_alternatives.append(alt)
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
        height=380,  # Match the figure height
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
        height=380  # Match chart height
    )
    
    # Create the view with improved layout
    view = ft.Container(
        content=ft.Column(
            [
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
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
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
        return ft.Container(
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
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(title_text, size=24, weight=ft.FontWeight.BOLD, color="white"),
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

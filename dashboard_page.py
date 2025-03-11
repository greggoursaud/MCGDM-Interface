import flet as ft
from flet.plotly_chart import PlotlyChart
import pandas as pd
import numpy as np
import plotly.express as px

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
    
    # Create individual views that will be switched using buttons
    results_view = create_results_view(page, results_df)
    charts_view = create_chart_view(results_df)
    
    # Create views list
    views = [results_view, charts_view]
    
    # Add parallel plot view if available
    parallel_view = None
    if parallel_plot is not None:
        parallel_view = create_parallel_view(parallel_plot)
        views.insert(1, parallel_view)
    
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
    
    # Store the currently selected tab index
    current_tab_index = 0
    
    # Create references to all the tab buttons
    button_refs = []
    
    # Create navigation buttons with refs
    results_btn = ft.ElevatedButton(
        "Results",
        style=ft.ButtonStyle(
            bgcolor="white",
            color="black",
            padding=ft.padding.symmetric(vertical=10, horizontal=15)
        )
    )
    button_refs.append(results_btn)
    
    chart_btn = ft.ElevatedButton(
        "Score Chart",
        style=ft.ButtonStyle(
            bgcolor="#2C2C2C",
            color="white",
            padding=ft.padding.symmetric(vertical=10, horizontal=15)
        )
    )
    button_refs.append(chart_btn)
    
    parallel_btn = None
    if parallel_view is not None:
        parallel_btn = ft.ElevatedButton(
            "Parallel Plot",
            style=ft.ButtonStyle(
                bgcolor="#2C2C2C",
                color="white",
                padding=ft.padding.symmetric(vertical=10, horizontal=15)
            )
        )
        button_refs.insert(1, parallel_btn)
    
    alt_btn = None
    if alternatives_view is not None:
        alt_btn = ft.ElevatedButton(
            "Alternatives",
            style=ft.ButtonStyle(
                bgcolor="#2C2C2C",
                color="white",
                padding=ft.padding.symmetric(vertical=10, horizontal=15)
            )
        )
        button_refs.append(alt_btn)
    
    weights_btn = None
    if weights_view is not None:
        weights_btn = ft.ElevatedButton(
            "Weights",
            style=ft.ButtonStyle(
                bgcolor="#2C2C2C",
                color="white",
                padding=ft.padding.symmetric(vertical=10, horizontal=15)
            )
        )
        button_refs.append(weights_btn)
    
    # Create container to hold current view
    content_container = ft.Container(
        content=views[0],  # Start with results view
        expand=True
    )
    
    # Function to switch views and update button styles
    def switch_view(index):
        def handle_click(e):
            nonlocal current_tab_index
            
            # Update button styles - reset all to default
            for i, btn in enumerate(button_refs):
                btn.style = ft.ButtonStyle(
                    bgcolor="#2C2C2C",
                    color="white",
                    padding=ft.padding.symmetric(vertical=10, horizontal=15)
                )
            
            # Set the selected button to white
            button_refs[index].style = ft.ButtonStyle(
                bgcolor="white",
                color="black",
                padding=ft.padding.symmetric(vertical=10, horizontal=15)
            )
            
            # Update the current view
            content_container.content = views[index]
            current_tab_index = index
            
            # Update the page
            page.update()
            
        return handle_click
    
    # Add click handlers to all buttons
    results_btn.on_click = switch_view(0)
    
    if parallel_view is not None:
        parallel_btn.on_click = switch_view(1)
        chart_btn.on_click = switch_view(2)
    else:
        chart_btn.on_click = switch_view(1)
    
    offset = 2 if parallel_view is None else 3
    
    if alternatives_view is not None:
        alt_btn.on_click = switch_view(offset)
        offset += 1
        
    if weights_view is not None:
        weights_btn.on_click = switch_view(offset)
    
    # Assemble the navigation buttons into a row
    nav_buttons = ft.Row(
        [results_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )
    
    if parallel_view is not None:
        nav_buttons.controls.append(parallel_btn)
    
    nav_buttons.controls.append(chart_btn)
    
    if alternatives_view is not None:
        nav_buttons.controls.append(alt_btn)
    
    if weights_view is not None:
        nav_buttons.controls.append(weights_btn)
    
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
                        
                        # Navigation buttons
                        ft.Container(
                            content=nav_buttons,
                            padding=ft.padding.symmetric(vertical=10),
                            border_radius=10
                        ),
                        
                        # Main content
                        content_container
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
        if i == 0 or col == "Total Score" or col == "Rank":  # First column or score/rank columns
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

# The rest of the functions remain unchanged
def create_chart_view(results_df):
    """Create a bar chart of the results."""
    # Find the best column names to use
    if "Alternative" in results_df.columns:
        x_col = "Alternative"
    elif results_df.columns[0] in ["Candidates", "Alternatives", "DMs"]:
        x_col = results_df.columns[0]
    else:
        x_col = results_df.columns[0]  # Use first column
    
    y_col = "Total Score" if "Total Score" in results_df.columns else results_df.columns[-2]
    
    # Create bar chart
    fig = px.bar(
        results_df, 
        x=x_col, 
        y=y_col,
        title=f"{y_col} by {x_col}"
    )
    
    # Style the chart for dark theme
    fig.update_layout(
        paper_bgcolor="#1C1C1C",
        plot_bgcolor="#1C1C1C",
        font=dict(color="white"),
        margin=dict(l=50, r=50, t=100, b=50),
    )
    
    fig.update_traces(marker_color="#4285F4")
    
    chart = PlotlyChart(fig, expand=True)
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Score Visualisation", size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(
                    content=chart,
                    padding=20,
                    border=ft.border.all(1, "white"),
                    border_radius=10,
                    bgcolor="#1C1C1C",
                    expand=True,
                    height=500
                )  # Added missing closing parenthesis here
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        expand=True
    )

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

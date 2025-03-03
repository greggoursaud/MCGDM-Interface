import flet as ft
import pandas as pd
import numpy as np
from hives import hives_algorithm
from parallel_coordinate import parallel_coordinates_plot
from flet.plotly_chart import PlotlyChart
import plotly.express as px

def build_input_page(page: ft.Page):
    # State variables
    criteria_count = ft.Ref[ft.TextField]()
    alternatives_count = ft.Ref[ft.TextField]()
    decision_makers_count = ft.Ref[ft.TextField]()
    
    # Create an empty form container that will be populated with input fields
    form_container = ft.Ref[ft.Column]()

    # Data containers for generated tables
    alternatives_data = []
    weights_data = []
    
    def generate_form(e):
        try:
            c_count = int(criteria_count.current.value)
            a_count = int(alternatives_count.current.value)
            dm_count = int(decision_makers_count.current.value)
            
            if c_count <= 0 or a_count <= 0 or dm_count <= 0:
                page.snack_bar = ft.SnackBar(ft.Text("Please enter positive numbers for all fields"))
                page.snack_bar.open = True
                page.update()
                return
                
            # Clear any existing form
            form_container.current.controls.clear()
            
            # Create headers for alternatives table
            headers = ["Alternative"]
            headers.extend([f"C{i+1}" for i in range(c_count)])
            
            # Create alternatives table
            alternatives_table = ft.Column(spacing=10)
            alternatives_data.clear()
            
            # Add header row
            header_row = ft.Row([ft.Text(h, weight=ft.FontWeight.BOLD) for h in headers])
            alternatives_table.controls.append(header_row)
            
            # Add editable rows for each alternative
            for i in range(a_count):
                row_data = [f"A{i+1}"]
                row_data.extend(["" for _ in range(c_count)])
                alternatives_data.append(row_data)
                
                row_controls = [ft.Text(row_data[0], width=100)]
                for j in range(1, len(row_data)):
                    field = ft.TextField(
                        value=row_data[j],
                        width=80,
                        on_change=lambda e, r=i, c=j: update_alternatives_data(r, c, e.control.value)
                    )
                    row_controls.append(field)
                
                alternatives_table.controls.append(ft.Row(row_controls, spacing=10))
            
            # Create weights table
            weights_table = ft.Column(spacing=10)
            weights_data.clear()
            
            # Add header row for weights
            weight_headers = ["DM"]
            weight_headers.extend([f"C{i+1}" for i in range(c_count)])
            weights_table.controls.append(ft.Row([ft.Text(h, weight=ft.FontWeight.BOLD) for h in weight_headers]))
            
            # Add editable rows for each decision maker
            for i in range(dm_count):
                row_data = [f"DM{i+1}"]
                row_data.extend(["" for _ in range(c_count)])
                weights_data.append(row_data)
                
                row_controls = [ft.Text(row_data[0], width=100)]
                for j in range(1, len(row_data)):
                    field = ft.TextField(
                        value=row_data[j],
                        width=80,
                        on_change=lambda e, r=i, c=j: update_weights_data(r, c, e.control.value)
                    )
                    row_controls.append(field)
                
                weights_table.controls.append(ft.Row(row_controls, spacing=10))
            
            # Add tables to container
            form_container.current.controls.extend([
                ft.Text("Alternatives Data", style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                ft.Container(
                    content=alternatives_table,
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=5,
                    width=min(page.width, 800)
                ),
                ft.Text("Weights Data", style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                ft.Container(
                    content=weights_table,
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=5,
                    width=min(page.width, 800)
                ),
                ft.ElevatedButton(
                    text="Process Data",
                    on_click=process_data,
                    style=ft.ButtonStyle(
                        text_style=ft.TextStyle(size=16)
                    )
                )
            ])
            
            page.update()
            
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter valid numbers"))
            page.snack_bar.open = True
            page.update()
    
    def update_alternatives_data(row, col, value):
        alternatives_data[row][col] = value
    
    def update_weights_data(row, col, value):
        weights_data[row][col] = value
    
    def process_data(e):
        # Validate that all fields have numerical data
        try:
            # Convert alternatives data to pandas DataFrame
            alt_headers = ["Alternative"] + [f"C{i+1}" for i in range(len(alternatives_data[0])-1)]
            alt_df = pd.DataFrame(alternatives_data, columns=alt_headers)
            
            # Convert all except first column to numeric
            for col in alt_df.columns[1:]:
                alt_df[col] = pd.to_numeric(alt_df[col])
            
            # Convert weights data to pandas DataFrame
            weight_headers = ["DM"] + [f"C{i+1}" for i in range(len(weights_data[0])-1)]
            weight_df = pd.DataFrame(weights_data, columns=weight_headers)
            
            # Convert all except first column to numeric
            for col in weight_df.columns[1:]:
                weight_df[col] = pd.to_numeric(weight_df[col])
            
            # Save dataframes to temporary CSV files
            alt_csv_path = "temp_alternatives.csv"
            weight_csv_path = "temp_weights.csv"
            
            alt_df.to_csv(alt_csv_path, index=False)
            weight_df.to_csv(weight_csv_path, index=False)
            
            # Process with HIVES algorithm
            results = hives_algorithm(alt_csv_path, weight_csv_path)
            
            # Generate visualizations
            fig = parallel_coordinates_plot(results)  
            plot_chart = PlotlyChart(fig, expand=False)

            # Create the bar chart
            fig_bar = px.bar(
                results, 
                x="Candidates", 
                y="Total Score",
                title="<b>Candidates vs Total Scores</b>",
                labels={"Candidates": "Candidate", "Total Score": "Total Score"},
            )
            
            fig_bar.update_traces(
                marker=dict(
                    line=dict(width=2.5, color='rgba(0,0,0,0.3)')
                )
            )
            fig_bar.update_layout(
                title_font=dict(family="Roboto", size=24, color="white"),
                font=dict(family="Roboto", size=14, color="white"),
                xaxis=dict(
                    tickangle=-45,
                    showgrid=False,
                    zeroline=False,
                    linecolor='rgba(0,0,0,0.1)',
                    linewidth=2
                ),
                yaxis=dict(gridcolor='rgba(0,0,0,0.1)', zeroline=False),
                margin=dict(l=50, r=50, t=70, b=70),
                template='ggplot2',
                paper_bgcolor='grey',
                plot_bgcolor='lightgrey'
            )

            bar_chart = PlotlyChart(fig_bar, expand=False)

            # Create data table from results
            def create_data_table(data):
                if isinstance(data, pd.DataFrame):
                    headers = data.columns.tolist()
                    rows = data.values.tolist()
                else:
                    headers = data[0]
                    rows = data[1:]

                columns = [ft.DataColumn(ft.Text(header)) for header in headers]
                data_rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]) for row in rows]
                return ft.DataTable(columns=columns, rows=data_rows)

            results_table = create_data_table(results)
            
            # Create data container
            data_container = ft.Container(
                content=ft.Column( 
                    controls=[results_table],  
                    scroll=ft.ScrollMode.AUTO,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )

            def update_table(e, new_control):
                if isinstance(new_control, PlotlyChart):
                    updated_content = ft.Container(
                        content=new_control,
                        width=1400,
                        height=600,
                        alignment=ft.alignment.center,
                        expand=True
                    )
                else:
                    updated_content = ft.Column(
                        controls=[new_control],
                        scroll=ft.ScrollMode.AUTO,
                    )
                data_container.content = updated_content
                data_container.update()

            # Sidebar menu container
            menu = ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text("Results Table"),
                            on_click=lambda e: update_table(e, results_table),
                        ),
                        ft.ListTile(
                            title=ft.Text("Parallel Coordinates Plot"),
                            on_click=lambda e: update_table(e, plot_chart),
                        ),
                        ft.ListTile(
                            title=ft.Text("Bar Chart"),
                            on_click=lambda e: update_table(e, bar_chart),
                        ),
                    ]
                ),
                width=200,
                height=200,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=5,
            )

            # Create layout with menu and data container
            layout = ft.Stack(
                [
                    ft.Container(menu, left=10, top=10),
                    ft.Container(data_container, left=220, top=10, expand=False),
                ]
            )

            # Show results in a dialog
            dialog = ft.AlertDialog(
                title=ft.Text("Analysis Results"),
                content=layout,
                actions=[
                    ft.ElevatedButton("Close", on_click=lambda e: setattr(dialog, "open", False))
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            page.dialog = dialog
            dialog.open = True
            page.update()
            
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error processing data: {str(e)}"))
            page.snack_bar.open = True
            page.update()
    
    return ft.View(
        "/input",
        [
            ft.AppBar(
                bgcolor=ft.colors.BLUE_GREY_900,
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda _: page.go("/start")
                )
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Input Data Manually",
                            style=ft.TextStyle(
                                size=32,
                                weight=ft.FontWeight.BOLD
                            )
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.TextField(
                                        label="Number of Criteria",
                                        hint_text="Enter number of criteria",
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                        ref=criteria_count,
                                        width=300
                                    ),
                                    ft.TextField(
                                        label="Number of Alternatives",
                                        hint_text="Enter number of alternatives/candidates",
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                        ref=alternatives_count,
                                        width=300
                                    ),
                                    ft.TextField(
                                        label="Number of Decision Makers",
                                        hint_text="Enter number of decision makers",
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                        ref=decision_makers_count,
                                        width=300
                                    ),
                                    ft.ElevatedButton(
                                        text="Generate Form",
                                        on_click=generate_form,
                                        style=ft.ButtonStyle(
                                            text_style=ft.TextStyle(size=16)
                                        )
                                    ),
                                ],
                                spacing=20,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        ),
                        
                        # Container for the generated form
                        ft.Container(
                            content=ft.Column(ref=form_container, spacing=20),
                            alignment=ft.alignment.center,
                            padding=20
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                ),
                alignment=ft.alignment.top_center,
                padding=20,
                expand=True
            ),
        ]
    )
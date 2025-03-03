import flet as ft
import pandas as pd
import csv
from hives import hives_algorithm
from parallel_coordinate import parallel_coordinates_plot
from flet.plotly_chart import PlotlyChart
import plotly.express as px

def build_upload_page(page: ft.Page):
    uploaded_file_name_1 = ft.Ref[ft.Text]()
    uploaded_file_name_2 = ft.Ref[ft.Text]()
    csv_file_1 = None
    csv_file_2 = None

    def on_file_picked(e: ft.FilePickerResultEvent, card_id):
        nonlocal csv_file_1, csv_file_2
        if e.files:
            file = e.files[0]
            if file.name.endswith('.csv'):
                if card_id == 1:
                    uploaded_file_name_1.current.value = f"{file.name} 📄"
                    csv_file_1 = file
                elif card_id == 2:
                    uploaded_file_name_2.current.value = f"{file.name} 📄"
                    csv_file_2 = file
                page.snack_bar = ft.SnackBar(ft.Text(f"File {file.name} uploaded successfully!"))
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Please upload a CSV file."))
            page.snack_bar.open = True
            page.update()

    def read_csv(file_path):
        with open(file_path, mode='r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            return list(reader)

    def start_program(e): 
        nonlocal csv_file_1, csv_file_2
        if csv_file_1 and csv_file_2:
            print(f"Starting program with {csv_file_1} and {csv_file_2}")

            # Read CSV files
            data_1 = read_csv(csv_file_1.path)  
            data_2 = read_csv(csv_file_2.path)  

            results = hives_algorithm(csv_file_1.path, csv_file_2.path) 

            # Generate the parallel coordinates plot
            fig = parallel_coordinates_plot(results)  
            plot_chart = PlotlyChart(fig, expand=False)

            # Create the bar chart with a modern, clean template.
            fig_bar = px.bar(
                results, 
                x="Candidates", 
                y="Total Score",
                title="<b>Candidates vs Total Scores</b>",
                labels={"Candidates": "Candidate", "Total Score": "Total Score"},
                
               # Differentiate candidates by color
            )

            
            fig_bar.update_traces(
                marker=dict(
                    line=dict(width=2.5, color='rgba(0,0,0,0.3)')  # Subtle border around each bar
                )
            )

            # Update layout settings to refine the overall look.
            fig_bar.update_layout(
                title_font=dict(
                    family="Roboto",
                    size=24,
                    color="white"
                ),
                font=dict(
                    family="Roboto",
                    size=14,
                    color="white"
                ),
                xaxis=dict(
                    tickangle=-45,  # Slight tilt for readability
                    showgrid=False, # Remove vertical grid lines
                    zeroline=False,
                    linecolor='rgba(0,0,0,0.1)',  # Light vertical line for reference
                    linewidth = 2
                ),
                yaxis=dict(
                    gridcolor='rgba(0,0,0,0.1)',  # Light horizontal grid lines for reference
                    zeroline=False
                ),
                margin=dict(l=50, r=50, t=70, b=70),
                template='ggplot2',
                paper_bgcolor='grey',  # Background color of the entire figure
                plot_bgcolor='lightgrey'
            )

            bar_chart = PlotlyChart(fig_bar, expand=False)

            # Create data tables
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

            data_table_1 = create_data_table(data_1)
            data_table_2 = create_data_table(data_2)
            data_table_3 = create_data_table(results)
            data_table_4 = plot_chart

            data_container = ft.Container(
                content=ft.Column( 
                    controls=[data_table_3],  
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
                            title=ft.Text("Data 1"),
                            on_click=lambda e: update_table(e, data_table_1),
                        ),
                        ft.ListTile(
                            title=ft.Text("Data 2"),
                            on_click=lambda e: update_table(e, data_table_2),
                        ),
                        ft.ListTile(
                            title=ft.Text("Results"),
                            on_click=lambda e: update_table(e, data_table_3),
                        ),
                        ft.ListTile(
                            title=ft.Text("Parallel Coordinates Plot"),
                            on_click=lambda e: update_table(e, data_table_4),
                        ),
                        ft.ListTile(
                            title=ft.Text("Bar Chart"),
                            on_click=lambda e: update_table(e, bar_chart),
                        ),
                    ]
                ),
                width=200,
                height=300,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=5,
            )

            # Wrap in Stack to allow absolute positioning
            layout = ft.Stack(
                [
                    ft.Container(menu, left=10, top=10),  # Menu positioned inside Stack
                    ft.Container(data_container, left=220, top=10, expand=False),  # Table positioned next to menu
                ]
            )

            # Retrieve the current view
            current_view = page.views[-1]

            # Add layout to current view
            current_view.controls.append(layout)

            page.update()

            page.snack_bar = ft.SnackBar(ft.Text(f"Program completed with {csv_file_1.name} and {csv_file_2.name}"))
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Please upload both CSV files."))

        page.snack_bar.open = True
        page.update()

    file_picker_1 = ft.FilePicker(on_result=lambda e: on_file_picked(e, 1))
    file_picker_2 = ft.FilePicker(on_result=lambda e: on_file_picked(e, 2))
    page.overlay.extend([file_picker_1, file_picker_2])
    
    return ft.View(
        "/upload",
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
                            "Upload CSV Files",
                            style=ft.TextStyle(
                                size=32,
                                weight=ft.FontWeight.BOLD
                            )
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.GestureDetector(
                                        content=ft.Card(
                                            content=ft.Container(
                                                content=ft.Text("Upload CSV 1", ref=uploaded_file_name_1, style=ft.TextStyle(size=24)),
                                                alignment=ft.alignment.center,
                                                padding=20
                                            ),
                                            width=200,
                                            height=200
                                        ),
                                        on_tap=lambda _: file_picker_1.pick_files(allowed_extensions=["csv"])
                                    ),
                                    ft.GestureDetector(
                                        content=ft.Card(
                                            content=ft.Container(
                                                content=ft.Text("Upload CSV 2", ref=uploaded_file_name_2, style=ft.TextStyle(size=24)),
                                                alignment=ft.alignment.center,
                                                padding=20
                                            ),
                                            width=200,
                                            height=200
                                        ),
                                        on_tap=lambda _: file_picker_2.pick_files(allowed_extensions=["csv"])
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        ),
                        ft.ElevatedButton(
                            text="Start",
                            on_click=start_program,
                            style=ft.ButtonStyle(
                                text_style=ft.TextStyle(size=16)
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                ),
                alignment=ft.alignment.center,
                padding=20
            ),
        ]
    )
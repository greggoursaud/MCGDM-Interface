import flet as ft
import pandas as pd
import numpy as np
import time
import io
import csv
from hives import hives_algorithm
from parallel_coordinate import parallel_coordinates_plot
from flet.plotly_chart import PlotlyChart
import plotly.express as px
import random

def main(page: ft.Page):
    page.title = "Routes Example"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(font_family="Roboto", use_material3=True)

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

            
            # # Add menu to overlay
            # page.overlay.append(menu)

            page.update()


            page.snack_bar = ft.SnackBar(ft.Text(f"Program completed with {csv_file_1} and {csv_file_2}"))
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Please upload both CSV files."))

        page.snack_bar.open = True
        page.update()
    
    def create_profile_view():
        # Sample data for demonstration
        agent_data_sets = [
            {"Name": "Agent Data Set 1", "Criteria": 5, "Alternatives": 10},
            {"Name": "Agent Data Set 2", "Criteria": 4, "Alternatives": 8},
        ]
        weights_data_sets = [
            {"Name": "Weights Data Set 1", "Criteria": 5, "DMs": 3},
            {"Name": "Weights Data Set 2", "Criteria": 6, "DMs": 4},
        ]
        
        # Columns to hold the dynamically added rows
        agent_rows = ft.Column(
            controls=[
                *[
                    ft.Row(
                        controls=[
                            ft.Text(data['Name']),
                            ft.Text(str(data['Criteria'])),
                            ft.Text(str(data['Alternatives'])),
                            ft.ElevatedButton(
                                text="View",
                                on_click=lambda e, name=data['Name']: view_data(name)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=10
                    )
                    for data in agent_data_sets
                ]
            ],
            spacing=10
        )
        
        weights_rows = ft.Column(
            controls=[
                *[
                    ft.Row(
                        controls=[
                            ft.Text(data['Name']),
                            ft.Text(str(data['Criteria'])),
                            ft.Text(str(data['DMs'])),
                            ft.ElevatedButton(
                                text="View",
                                on_click=lambda e, name=data['Name']: view_data(name)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=10
                    )
                    for data in weights_data_sets
                ]
            ],
            spacing=10
        )
        
        def view_data(data_name):
            # For Agent Data Set 1, show an editable table
            if data_name == "Agent Data Set 1":
                headers = ["Alternative", "C1", "C2", "C3", "C4", "C5"]
                # Build initial sample rows with random numbers between 1 and 100
                sample_rows = []
                for i in range(1, 11):
                    row = [f"Alternative {i}"]
                    row.extend([str(random.randint(1, 100)) for _ in range(5)])
                    sample_rows.append(row)
                
                # Container that will hold the editable row displays
                rows_container = ft.Column(spacing=10)

                # A helper function to rebuild the rows_container from sample_rows
                def refresh_table():
                    rows_container.controls.clear()
                    
                    # Build a row for each sample row, adding an edit button at the end
                    for row in sample_rows:
                        def edit_row(e, row_value=row):
                            # Build text fields prefilled with current row data.
                            # The first cell (Alternative) is noneditable.
                            edit_fields = [ft.Text(row_value[0])]
                            for index in range(1, len(row_value)):
                                edit_fields.append(ft.TextField(label=headers[index], value=row_value[index]))
                            
                            # Function to submit the changes to the row.
                            def submit_edit(e, original=row_value):
                                new_row = [edit_fields[0].value] + [f.value for f in edit_fields[1:]]
                                sample_rows[sample_rows.index(original)] = new_row
                                edit_dialog.open = False
                                dialog.open = True
                                refresh_table()
                                page.update()
                            
                            edit_dialog = ft.AlertDialog(
                                title=ft.Text("Edit Row"),
                                content=ft.Container(
                                    content=ft.Column(controls=edit_fields, spacing=10),
                                    width=400,   # Square dialog width
                                    height=400,  # Square dialog height
                                    alignment=ft.alignment.center
                                ),
                                actions=[
                                    ft.ElevatedButton(text="Submit", on_click=submit_edit)
                                ],
                                actions_alignment=ft.MainAxisAlignment.END,
                                inset_padding=ft.Padding(top=20, bottom=20, left=24, right=24),
                                shape=ft.RoundedRectangleBorder(radius=10)
                            )
                            # Swap dialogs so the edit dialog comes up.
                            dialog.open = False
                            page.dialog = edit_dialog
                            edit_dialog.open = True
                            page.update()
                        
                        row_display = ft.Row(
                            controls=[ft.Text(cell) for cell in row] + [ft.IconButton(icon=ft.icons.EDIT, on_click=edit_row)],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                        rows_container.controls.append(row_display)
                    
                    # Adding a new row.
                    def add_row(e):
                        # Create text fields for each criteria (skip Alternative)
                        new_fields = [ft.TextField(label=header) for header in headers[1:]]
                        def submit_new(e):
                            new_row = [f"Alternative {len(sample_rows)+1}"] + [field.value for field in new_fields]
                            sample_rows.append(new_row)
                            add_dialog.open = False
                            dialog.open = True
                            refresh_table()
                            page.update()
                        add_dialog = ft.AlertDialog(
                            title=ft.Text("Add New Row"),
                            content=ft.Container(
                                content=ft.Column(controls=new_fields, spacing=10),
                                width=400,   # Square dialog width
                                height=400,  # Square dialog height
                                alignment=ft.alignment.center
                            ),
                            actions=[ft.ElevatedButton(text="Submit", on_click=submit_new)],
                            actions_alignment=ft.MainAxisAlignment.END,
                            inset_padding=ft.Padding(top=20, bottom=20, left=24, right=24),
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                        dialog.open = False
                        page.dialog = add_dialog
                        add_dialog.open = True
                        page.update()
                    
                    rows_container.controls.append(ft.ElevatedButton(text="Add Row", on_click=add_row))
                    page.update()

                # Initially populate the table
                refresh_table()
                
                # Create the main dialog and add the rows_container in a scrollable container.
                dialog = ft.AlertDialog(
                    title=ft.Text(f"Viewing {data_name} Data (Editable)"),
                    content=ft.Container(
                        content=rows_container,
                        width=1200,
                        height=800,
                    ),
                    actions=[
                        ft.ElevatedButton(text="Close", on_click=lambda e: [setattr(dialog, "open", False), page.update()])
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    inset_padding=ft.Padding(top=40, bottom=40, left=24, right=24),
                    shape=ft.RoundedRectangleBorder(radius=10)
                )
                page.dialog = dialog
                dialog.open = True
                page.update()
            else:
                # For other datasets, display a simple one-row table based on its keys and values.
                dataset = next((d for d in agent_data_sets if d['Name'] == data_name), None)
                if dataset is None:
                    dataset = next((d for d in weights_data_sets if d['Name'] == data_name), None)
                if dataset is None:
                    return
                headers = list(dataset.keys())
                values = list(map(str, dataset.values()))
                data_table = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text(header)) for header in headers],
                    rows=[
                        ft.DataRow(
                            cells=[ft.DataCell(ft.Text(value)) for value in values]
                        )
                    ]
                )
            
            def close_dialog(e):
                dialog.open = False
                page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text(f"Viewing {data_name} Data"),
                content=ft.Container(
                    content=data_table,
                    width=1200,
                    height=800,
                ),
                actions=[
                    ft.ElevatedButton(text="Close", on_click=close_dialog)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                inset_padding=ft.Padding(top=40, bottom=40, left=24, right=24),
                shape=ft.RoundedRectangleBorder(radius=10)
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        def show_create_dialog(data_type):
            # Decide label for third field based on data type.
            third_field_label = "Alternatives" if data_type == "Agent" else "DMs"
            name_field = ft.TextField(label="Name")
            criteria_field = ft.TextField(label="Criteria")
            third_field = ft.TextField(label=third_field_label)
            submit_button = ft.ElevatedButton(
                text="Submit", 
                on_click=lambda e: submit_new_data(data_type, name_field, criteria_field, third_field)
            )
            content_container = ft.Container(
                content=ft.Column(
                    controls=[
                        name_field,
                        criteria_field,
                        third_field
                    ],
                    spacing=10
                ),
                width=300,   # Fixed width for the dialog content
                height=200   # Fixed height for the dialog content
            )
            
            dialog = ft.AlertDialog(
                title=ft.Text(f"Add New {data_type}"),
                content=content_container,
                actions=[submit_button],
                actions_alignment=ft.MainAxisAlignment.END,
                inset_padding=ft.Padding(top=40, bottom=40, left=24, right=24),
                shape=ft.RoundedRectangleBorder(radius=10)
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        def submit_new_data(data_type, name_field, criteria_field, third_field):
            name = name_field.value
            criteria = criteria_field.value
            third_val = third_field.value
            if data_type == "Agent":
                new_view_row = ft.Row(
                    controls=[
                        ft.Text(name),
                        ft.Text(criteria),
                        ft.Text(third_val),
                        ft.ElevatedButton(
                            text="View",
                            on_click=lambda e, name=name: view_data(name)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                )
                agent_rows.controls.append(new_view_row)
                agent_rows.update()
            elif data_type == "Weight":
                new_view_row = ft.Row(
                    controls=[
                        ft.Text(name),
                        ft.Text(criteria),
                        ft.Text(third_val),
                        ft.ElevatedButton(
                            text="View",
                            on_click=lambda e, name=name: view_data(name)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10
                )
                weights_rows.controls.append(new_view_row)
                weights_rows.update()
            # Close the dialog after submission.
            page.dialog.open = False
            page.update()
        
        return ft.View(
            "/profile",
            [
                ft.AppBar(
                    title=ft.Text("Profile"),
                    bgcolor=ft.colors.BLUE_GREY_900,
                    leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: page.go("/"))
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Icon(name=ft.icons.ACCOUNT_CIRCLE, size=150, color=ft.colors.BLUE_GREY_900),
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=ft.Text("User Name", style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                                alignment=ft.alignment.center,
                            ),
                            ft.Row(
                                controls=[
                                    # Agent Data Container
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Text("Agent Datasets", style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                                                        ft.IconButton(
                                                            icon=ft.icons.FORMAT_LIST_BULLETED_ADD,
                                                            tooltip="Add New Agent Dataset",
                                                            on_click=lambda _: show_create_dialog("Agent")
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                    spacing=10
                                                ),
                                                # Header Row
                                                ft.Row(
                                                    controls=[
                                                        ft.Text("Name", weight=ft.FontWeight.BOLD),
                                                        ft.Text("Criteria", weight=ft.FontWeight.BOLD),
                                                        ft.Text("Alternatives", weight=ft.FontWeight.BOLD),
                                                        ft.Text("Actions", weight=ft.FontWeight.BOLD),
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                    spacing=10
                                                ),
                                                agent_rows
                                            ],
                                            spacing=10
                                        ),
                                        width=500,
                                        padding=20,
                                        margin=10,
                                        bgcolor=ft.colors.SURFACE_VARIANT,
                                        border_radius=5
                                    ),
                                    # Weights Data Container
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Text("Weight Datasets", style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                                                        ft.IconButton(
                                                            icon=ft.icons.FORMAT_LIST_BULLETED_ADD,
                                                            tooltip="Add New Weight Datasets",
                                                            on_click=lambda _: show_create_dialog("Weight")
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                    spacing=10
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text("Name", weight=ft.FontWeight.BOLD),
                                                        ft.Text("Criteria", weight=ft.FontWeight.BOLD),
                                                        ft.Text("DMs", weight=ft.FontWeight.BOLD),
                                                        ft.Text("Actions", weight=ft.FontWeight.BOLD),
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                    spacing=10
                                                ),
                                                weights_rows
                                            ],
                                            spacing=10
                                        ),
                                        width=500,
                                        padding=20,
                                        margin=10,
                                        bgcolor=ft.colors.SURFACE_VARIANT,
                                        border_radius=5
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20
                            )
                        ],
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


    file_picker_1 = ft.FilePicker(on_result=lambda e: on_file_picked(e, 1))
    file_picker_2 = ft.FilePicker(on_result=lambda e: on_file_picked(e, 2))
    page.overlay.extend([file_picker_1, file_picker_2])

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(
                        bgcolor=ft.colors.BLUE_GREY_900,
                        center_title=True,
                        actions=[
                            ft.TextButton(text="About", on_click=lambda _: page.go("/terms")),
                            ft.TextButton(text="Start", on_click=lambda _: page.go("/start")),
                            ft.TextButton(text="Profile", on_click=lambda _: page.go("/profile")),
                        ]
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            "Weigh In",
                                            style=ft.TextStyle(
                                                size=32,
                                                weight=ft.FontWeight.BOLD
                                            )
                                        ),
                                        ft.Text(
                                            "Simplify Group Decisions with Confidence.",
                                            style=ft.TextStyle(
                                                size=24,
                                                weight=ft.FontWeight.NORMAL
                                            )
                                        ),
                                        ft.Row(
                                            [
                                                ft.TextButton(
                                                    "Register",
                                                    on_click=lambda _: page.go("/register")
                                                ),
                                                ft.Text("|"),
                                                ft.TextButton(
                                                    "Log in",
                                                    on_click=lambda _: page.go("/login")
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=10
                                        ),
                                        ft.Container(
                                            content=ft.GestureDetector(
                                                content=ft.Card(
                                                    content=ft.Container(
                                                        content=ft.Text("Get Started", style=ft.TextStyle(size=24)),
                                                        alignment=ft.alignment.center,
                                                        padding=20
                                                    ),
                                                    width=200,
                                                    height=200
                                                ),
                                                on_tap=lambda _: page.go("/start")
                                            ),
                                            alignment=ft.alignment.center,
                                            padding=20
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=20
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.TextButton("Terms and Conditions", on_click=lambda _: page.go("/terms")),
                                            ft.TextButton("Contact", on_click=lambda _: page.go("/contact"))
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                    alignment=ft.alignment.center,
                                    padding=20
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        ),
                        alignment=ft.alignment.center,
                        padding=20,
                        expand=True
                    ),
                ]
            )
        )
        if page.route == "/start":
            page.views.append(
                ft.View(
                    "/start",
                    [
                        ft.AppBar(
                            bgcolor=ft.colors.BLUE_GREY_900,
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                on_click=lambda _: page.go("/")
                            )
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Get Started",
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
                                                            content=ft.Text("Upload Files", style=ft.TextStyle(size=24)),
                                                            alignment=ft.alignment.center,
                                                            padding=20
                                                        ),
                                                        width=200,
                                                        height=200
                                                    ),
                                                    on_tap=lambda _: page.go("/upload")
                                                ),
                                                ft.GestureDetector(
                                                    content=ft.Card(
                                                        content=ft.Container(
                                                            content=ft.Text("Input Data", style=ft.TextStyle(size=24)),
                                                            alignment=ft.alignment.center,
                                                            padding=20
                                                        ),
                                                        width=200,
                                                        height=200
                                                    ),
                                                    on_tap=lambda _: page.go("/input")
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=20
                                        ),
                                        alignment=ft.alignment.center,
                                        padding=20
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
            )
        if page.route == "/upload":
            page.views.append(
                ft.View(
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
            )
        if page.route == "/input":
            page.views.append(
                ft.View(
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
                                        "Input Data",
                                        style=ft.TextStyle(
                                            size=32,
                                            weight=ft.FontWeight.BOLD
                                        )
                                    ),
                                    # Add your input fields here
                                    ft.ElevatedButton(
                                        text="Submit",
                                        on_click=lambda _: page.go("/start"),
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
            )
        elif page.route == "/profile":
            page.views.append(create_profile_view())
        elif page.route == "/register":
            page.views.append(
                ft.View(
                    "/register",
                    [
                        ft.AppBar(
                            title=ft.Text("Register"),
                            bgcolor=ft.colors.BLUE_GREY_900,
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                on_click=lambda _: page.go("/")
                            )
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Create an Account",
                                        style=ft.TextStyle(
                                            size=32,
                                            weight=ft.FontWeight.BOLD
                                        )
                                    ),
                                    ft.TextField(
                                        label="Username",
                                        width=300
                                    ),
                                    ft.TextField(
                                        label="Email",
                                        width=300
                                    ),
                                    ft.TextField(
                                        label="Password",
                                        password=True,
                                        can_reveal_password=True,
                                        width=300
                                    ),
                                    ft.TextField(
                                        label="Confirm Password",
                                        password=True,
                                        can_reveal_password=True,
                                        width=300
                                    ),
                                    ft.ElevatedButton(
                                        text="Register",
                                        on_click=lambda _: page.go("/start")
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                                expand = True
                            ),
                            alignment=ft.alignment.top_center,
                            expand=True
                        )
                    ]
                )
            )
        elif page.route == "/login":
            page.views.append(
                ft.View(
                    "/login",
                    [
                        ft.AppBar(
                            title=ft.Text("Log in"),
                            bgcolor=ft.colors.BLUE_GREY_900,
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                on_click=lambda _: page.go("/")
                            )
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Log in to Your Account",
                                        style=ft.TextStyle(
                                            size=32,
                                            weight=ft.FontWeight.BOLD
                                        )
                                    ),
                                    ft.TextField(
                                        label="Email",
                                        width=300
                                    ),
                                    ft.TextField(
                                        label="Password",
                                        password=True,
                                        can_reveal_password=True,
                                        width=300
                                    ),
                                    ft.ElevatedButton(
                                        text="Log in",
                                        on_click=lambda _: page.go("/dashboard")
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                                expand=True
                            ),
                            alignment=ft.alignment.top_center,
                            expand=True
                        )
                    ]
                )
            )
        elif page.route == "/terms":
            page.views.append(
                ft.View(
                    "/terms",
                    [
                        ft.AppBar(
                            bgcolor=ft.colors.BLUE_GREY_900,
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                on_click=lambda _: page.go("/")
                            )
                        ),
                        ft.Container(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Terms of Service",
                                            style=ft.TextStyle(
                                                size=32,
                                                weight=ft.FontWeight.BOLD
                                            )
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                """
                                                Introduction and Definitions
                                                Welcome to Weigh In ("we," "us," "our," or the "Company"), a Software-as-a-Service (SaaS) platform that facilitates group decision-making using advanced algorithms. These Terms of Service ("Terms") govern your access to and use of the Weigh In website, applications, and related services (collectively, the "Platform").
                                                For the purposes of these Terms:

                                                "Weigh In" refers to the Company, its officers, directors, employees, and agents.
                                                "User," "you," or "your" refers to any individual or entity accessing or using the Platform.
                                                "Decision-Maker (DM)" refers to a User participating in group decision-making processes on the Platform.
                                                "Group Decision" refers to the collective outcome derived from inputs provided by multiple DMs.
                                                By accessing or using the Platform, you agree to these Terms. If you do not agree, do not use the Platform.

                                                Eligibility
                                                You must be at least 18 years old or the age of majority in your jurisdiction to use the Platform. By using Weigh In, you represent and warrant that you meet this requirement.
                                                Platform Features and Responsibilities
                                                3.1. Weigh In's Role:
                                                We provide tools for group decision-making using advanced multi-criteria methodologies like the HIVES algorithm. We do not take responsibility for decisions made based on outputs generated by the Platform.
                                                3.2. User Responsibility:
                                                Users are responsible for ensuring that the criteria and inputs they provide are accurate, relevant, and lawful.

                                                3.3. Service Availability:
                                                Weigh In reserves the right to modify, suspend, or discontinue any part of the Platform at any time without prior notice.

                                                Account Registration and Security
                                                4.1. You may need to register for an account to access certain features.
                                                4.2. You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.
                                                4.3. You agree to provide accurate and complete information during registration and keep it up-to-date.
                                                Use of the Platform
                                                5.1. You agree to use the Platform for lawful purposes only.
                                                5.2. Prohibited activities include, but are not limited to:
                                                Submitting false or misleading inputs.
                                                Attempting to manipulate group outcomes unfairly.
                                                Engaging in activities that disrupt the Platform or its Users.
                                                Privacy and Data
                                                We respect your privacy. Your use of the Platform is subject to our Privacy Policy, which outlines how we collect, store, and process data.
                                                Intellectual Property
                                                The Platform and its contents, including but not limited to text, algorithms, graphics, and software, are owned by Weigh In or its licensors and are protected by intellectual property laws. You may not copy, modify, or distribute any part of the Platform without prior written consent.
                                                Limitations of Liability
                                                8.1. The Platform is provided "as is" without warranties of any kind.
                                                8.2. Weigh In is not liable for any indirect, incidental, or consequential damages arising from your use of the Platform, including decisions made using its outputs.
                                                Modifications to Terms
                                                Weigh In reserves the right to modify these Terms at any time. We will notify you of significant changes, and continued use of the Platform constitutes acceptance of updated Terms.
                                                Governing Law
                                                These Terms are governed by and construed in accordance with the laws of [Your Jurisdiction].
                                                Contact Us
                                                For questions about these Terms, please contact us at support@weighin.app.
                                                Last updated: January 15, 2025

                                                © 2025 Weigh In. All Rights Reserved.
                                                """,
                                                style=ft.TextStyle(
                                                    size=16,
                                                    weight=ft.FontWeight.NORMAL
                                                )
                                            ),
                                            expand=True
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=20,
                                    scroll = ft.ScrollMode.AUTO,
                                    expand=True
                                ),
                                alignment=ft.alignment.center,
                                expand=True
                            ),
                            expand=True
                        ),
                    ]
                )
            )
        elif page.route == "/contact":
            page.views.append(
                ft.View(
                    "/contact",
                    [
                        ft.AppBar(
                            bgcolor=ft.colors.BLUE_GREY_900,
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                on_click=lambda _: page.go("/")
                            )
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Contact",
                                        style=ft.TextStyle(
                                            size=32,
                                            weight=ft.FontWeight.BOLD
                                        )
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        ),
                    ]
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, view=ft.AppView.FLET_APP)




###
# Create a form that allows users to essentially enter the data that would be in the CSV files
# Create a form that allows users to enter the weights for each column

##e.g.
#Number of criteria: 
#Number of agents: 
#Number of decision makers

# Dynamically creates two datatables based on inputted data
# User can then enter numbers and make adjustments if necessary 

#User can select from their dfs and start program to run the HIVES algorithm

#Portal to view thier weights df and candiadates df
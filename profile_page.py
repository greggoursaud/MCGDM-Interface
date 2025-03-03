import flet as ft
import random

def create_profile_view(page: ft.Page):
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
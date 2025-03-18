import flet as ft
import pandas as pd
import csv
from hives import hives_algorithm
from dashboard_page import build_dashboard_page

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
            try:
                # Read CSV files
                alt_df = pd.read_csv(csv_file_1.path)  
                weight_df = pd.read_csv(csv_file_2.path) 
                
                print("CSV data loaded successfully")
                
                # Process with HIVES algorithm
                results = hives_algorithm(csv_file_1.path, csv_file_2.path) 
                
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
                import traceback
                error_message = f"Error processing data: {str(e)}\n{traceback.format_exc()}"
                print(error_message)  # Print to console for debugging
                page.snack_bar = ft.SnackBar(ft.Text(f"Error processing data: {str(e)}"))
                page.snack_bar.open = True
                page.update()
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
        # Navigation Bar with back arrow like in register_page
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
                                    " - Upload Data",  # Page title addition
                                    style=ft.TextStyle(
                                        size=32,
                                        weight=ft.FontWeight.NORMAL,
                                        color="white",
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            "Upload CSV Files",
                            style=ft.TextStyle(
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="white"
                            )
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.GestureDetector(
                                        content=ft.Card(
                                            content=ft.Container(
                                                content=ft.Text("Upload Alternatives CSV", ref=uploaded_file_name_1, style=ft.TextStyle(size=18, color="white")),
                                                alignment=ft.alignment.center,
                                                padding=20,
                                                bgcolor="#333333"
                                            ),
                                            width=220,
                                            height=150
                                        ),
                                        on_tap=lambda _: file_picker_1.pick_files(allowed_extensions=["csv"])
                                    ),
                                    ft.GestureDetector(
                                        content=ft.Card(
                                            content=ft.Container(
                                                content=ft.Text("Upload Weights CSV", ref=uploaded_file_name_2, style=ft.TextStyle(size=18, color="white")),
                                                alignment=ft.alignment.center,
                                                padding=20,
                                                bgcolor="#333333"
                                            ),
                                            width=220,
                                            height=150
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
                        ft.Text(
                            "Upload the alternatives data and criteria weights as CSV files.",
                            style=ft.TextStyle(size=14, color="white")
                        ),
                        ft.ElevatedButton(
                            text="Process Data",
                            on_click=start_program,
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
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                ),
                alignment=ft.alignment.center,
                padding=20,
                expand=True,
                bgcolor="#2C2C2C"  # Dark background matching other pages
            ),
        ]
    )
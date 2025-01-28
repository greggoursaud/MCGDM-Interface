import flet as ft
import pandas as pd
import numpy as np
import time
import io
import csv
from hives import hives_algorithm
from simpledt import CSVDataTable

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

            # Read CSV files using the correct paths
            data_1 = read_csv(csv_file_1.path)
            data_2 = read_csv(csv_file_2.path)

            results = hives_algorithm(csv_file_1.path, csv_file_2.path)

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

            # Create a container to hold the data tables in a column format
            data_tables_container = ft.Container(
                content=ft.Column(
                    controls=[data_table_1, data_table_2, data_table_3],
                    scroll = ft.ScrollMode.AUTO,
                    expand=True
                ),
                alignment=ft.alignment.center,
                expand = True
            )

            # Add the container to the current view
            current_view = page.views[-1]
            current_view.controls.append(data_tables_container)

            page.snack_bar = ft.SnackBar(ft.Text(f"Program completed with {csv_file_1} and {csv_file_2}"))
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Please upload both CSV files."))

        page.snack_bar.open = True
        page.update()

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
                            ft.TextButton(text="Register", on_click=lambda _: page.go("/contact")),
                            ft.TextButton(text="About", on_click=lambda _: page.go("/terms")),
                            ft.TextButton(text="Start", on_click=lambda _: page.go("/start")),
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
                                scroll = ft.ScrollMode.AUTO,
                                expand=True
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        ),
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
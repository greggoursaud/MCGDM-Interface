import flet as ft

def build_start_page(page: ft.Page):
    return ft.View(
        "/start",
        [
            # Navigation Bar
            ft.Container(
                bgcolor="#EAEAEA",
                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: page.go("/"),
                            tooltip="Back to Home"
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
                expand=True,
                bgcolor="#2C2C2C",
                alignment=ft.alignment.top_center,
                padding=20,
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
                                    " - Get Started",  # Page title addition
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
                            "Select a method to begin your analysis",
                            style=ft.TextStyle(size=18, color="white"),
                        ),
                        
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.GestureDetector(
                                        content=ft.Card(
                                            content=ft.Container(
                                                content=ft.Column(
                                                    [
                                                        ft.Icon(ft.icons.UPLOAD_FILE, size=50, color="#2C2C2C"),
                                                        ft.Text(
                                                            "Upload Files", 
                                                            style=ft.TextStyle(
                                                                size=24, 
                                                                weight=ft.FontWeight.BOLD, 
                                                                color="#2C2C2C"
                                                            )
                                                        ),
                                                        ft.Text(
                                                            "Import your data from CSV files",
                                                            style=ft.TextStyle(
                                                                size=14,
                                                                color="#666666"
                                                            ),
                                                            text_align=ft.TextAlign.CENTER
                                                        )
                                                    ],
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    spacing=10
                                                ),
                                                alignment=ft.alignment.center,
                                                padding=20
                                            ),
                                            width=250,
                                            height=200,
                                            color="white"
                                        ),
                                        on_tap=lambda _: page.go("/upload")
                                    ),
                                    ft.GestureDetector(
                                        content=ft.Card(
                                            content=ft.Container(
                                                content=ft.Column(
                                                    [
                                                        ft.Icon(ft.icons.EDIT_DOCUMENT, size=50, color="#2C2C2C"),
                                                        ft.Text(
                                                            "Input Data", 
                                                            style=ft.TextStyle(
                                                                size=24, 
                                                                weight=ft.FontWeight.BOLD, 
                                                                color="#2C2C2C"
                                                            )
                                                        ),
                                                        ft.Text(
                                                            "Manually enter your decision data",
                                                            style=ft.TextStyle(
                                                                size=14,
                                                                color="#666666"
                                                            ),
                                                            text_align=ft.TextAlign.CENTER
                                                        )
                                                    ],
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    spacing=10
                                                ),
                                                alignment=ft.alignment.center,
                                                padding=20
                                            ),
                                            width=250,
                                            height=200,
                                            color="white"
                                        ),
                                        on_tap=lambda _: page.go("/input")
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=30
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=30,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                ),
            ),
        ]
    )
import flet as ft
from user_utils import get_navigation_controls

def build_start_page(page: ft.Page):
    # Get user data and navigation controls
    user_data = page.client_storage.get("user_data")
    nav_controls = get_navigation_controls(page, user_data)
    
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
                            icon=ft.icons.HOME,
                            on_click=lambda _: page.go("/"),
                            tooltip="Go to Home"
                        ),
                        ft.Container(expand=True),
                        # Use the nav_controls variable instead of hard-coded buttons
                        nav_controls,
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
                                    
                                    # Adding a clear "OR" between the cards
                                    ft.Container(
                                        content=ft.Text(
                                            "OR",
                                            style=ft.TextStyle(
                                                size=28,
                                                weight=ft.FontWeight.BOLD,
                                                color="white",
                                            ),
                                        ),
                                        alignment=ft.alignment.center,
                                        width=80,
                                        height=200,
                                        border_radius=30,
                                        bgcolor="#2C2C2C",
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
                                spacing=10  # Reduced spacing to accommodate the OR container
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
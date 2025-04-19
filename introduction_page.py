import flet as ft
from user_utils import get_navigation_controls

def build_introduction_page(page: ft.Page):
    # Get user data and navigation controls
    user_data = page.client_storage.get("user_data")
    nav_controls = get_navigation_controls(page, user_data)
    
    return ft.View(
        "/introduction",
        controls=[
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

            # Introduction Content
            ft.Container(
                expand=True,
                bgcolor="#2C2C2C",
                padding=ft.padding.all(40),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Introduction to Weigh",
                                    style=ft.TextStyle(
                                        size=36,
                                        weight=ft.FontWeight.BOLD,
                                        color="white",
                                    ),
                                ),
                                ft.Text(
                                    "IN",
                                    style=ft.TextStyle(
                                        size=36,
                                        weight=ft.FontWeight.BOLD,
                                        italic=True,
                                        color="white",
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        
                        ft.Container(
                            margin=ft.margin.symmetric(vertical=20),
                            content=ft.Text(
                                "Welcome to WeighIN, your solution for multi-criteria group decision making.",
                                style=ft.TextStyle(size=20, color="white"),
                                text_align=ft.TextAlign.CENTER,
                            )
                        ),
                        
                        ft.Container(
                            margin=ft.margin.only(bottom=20),
                            content=ft.Text(
                                "Our platform helps groups make complex decisions by combining individual preferences into a consensus that everyone can trust.",
                                style=ft.TextStyle(size=16, color="white"),
                                text_align=ft.TextAlign.CENTER,
                            )
                        ),
                        
                        ft.Card(
                            elevation=4,
                            color="white",
                            content=ft.Container(
                                padding=ft.padding.all(20),
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Key Features:",
                                            style=ft.TextStyle(
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                color="black",
                                            ),
                                        ),
                                        ft.Divider(height=2, color="#2C2C2C"),
                                        ft.Text(
                                            "• Advanced HIVES algorithm for accurate preference aggregation\n"
                                            "• Intuitive interface for criteria weighting and alternative comparison\n"
                                            "• Visualization tools to understand group consensus\n"
                                            "• Secure data storage and privacy protection",
                                            style=ft.TextStyle(size=16, color="black"),
                                        ),
                                    ],
                                    spacing=10,
                                )
                            )
                        ),
                        
                        ft.Container(
                            margin=ft.margin.only(top=30),
                            content=ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Get Started", 
                                        bgcolor="white", 
                                        color="black",
                                        style=ft.ButtonStyle(
                                            padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                            text_style=ft.TextStyle(size=16)
                                        ),
                                        on_click=lambda _: page.go("/start")
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                            )
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ]
    )
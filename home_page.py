import flet as ft
from user_utils import get_navigation_controls

def build_home_page(page: ft.Page):
    # Check if user is logged in
    user_data = page.client_storage.get("user_data")
    
    # Use the extracted function to get navigation controls
    nav_controls = get_navigation_controls(page, user_data)
    
    return ft.View(
        "/",
        [
            # Navigation bar
            ft.Container(
                bgcolor="#EAEAEA",
                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                content=ft.Row(
                    [
                        # Brand/logo or empty space on the left
                        ft.Container(expand=True),  # Spacer to push everything to the right
                        
                        # Right side - Resources, About, Contact, and then login controls
                        ft.Row(
                            [
                                # Navigation items - now moved to the right with reduced spacing
                                ft.TextButton("Resources", on_click=lambda _: page.go("/resources")),
                                ft.TextButton("About", on_click=lambda _: page.go("/about")),
                                ft.TextButton("Contact", on_click=lambda _: page.go("/contact")),
                                # Small divider between menu and login controls
                                ft.VerticalDivider(width=1, color="#C0C0C0"),
                                # Dynamic navigation controls (login/profile)
                                nav_controls,
                            ],
                            spacing=5  # Reduced from 15 to 5 to make buttons closer together
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=15
                )
            ),
            
            # Hero Section (Main Content)
            ft.Container(
                expand=True,
                bgcolor="#2C2C2C",
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Weigh",  # Non-italicized part
                                    style=ft.TextStyle(
                                        size=56,
                                        weight=ft.FontWeight.BOLD,
                                        color="white",
                                    ),
                                ),
                                ft.Text(
                                    "IN",  # Italicized part
                                    style=ft.TextStyle(
                                        size=56,
                                        weight=ft.FontWeight.BOLD,
                                        italic=True,  # Italic applied only to "IN"
                                        color="white",
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            "Simplify multi-criteria group decisions with confidence.",
                            style=ft.TextStyle(size=30, color="white"),  # Increased size for visibility
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Get Started", 
                                    bgcolor="white", 
                                    color="black",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(vertical=15, horizontal=30),  # Larger button
                                        text_style=ft.TextStyle(size=16)  # Larger text
                                    ),
                                    on_click=lambda _: page.go("/start")
                                ),
                                ft.ElevatedButton(
                                    "Introduction", 
                                    bgcolor="white", 
                                    color="black",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(vertical=15, horizontal=30),  # Larger button
                                        text_style=ft.TextStyle(size=16)  # Larger text
                                    ),
                                    on_click=lambda _: page.go("/introduction")
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=25  # Increased spacing to move subtext closer to the title
                )
            )
        ]
    )
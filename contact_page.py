import flet as ft
from user_utils import get_navigation_controls

def build_contact_page(page: ft.Page):

    user_data = page.client_storage.get("user_data")
    nav_controls = get_navigation_controls(page, user_data)

    return ft.View(
        "/contact",
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
                        # Use the nav_controls variable instead of hard-coding the buttons
                        nav_controls,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=15
                )
            ),
            
            # Main content
            ft.Container(
                expand=True,
                bgcolor="#2C2C2C",
                padding=ft.padding.all(40),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Contact Us",
                                    style=ft.TextStyle(
                                        size=36,
                                        weight=ft.FontWeight.BOLD,
                                        color="white",
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),

                        ft.Container(
                            margin=ft.margin.only(top=20),
                            content=ft.Card(
                                elevation=4,
                                color="white",
                                content=ft.Container(
                                    padding=ft.padding.all(20),
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "How to to Reach Us",
                                                style=ft.TextStyle(
                                                    size=20,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="black"
                                                )
                                            ),
                                            ft.Divider(height=2, color="#2C2C2C"),
                                            ft.Container(height=10),
                                            ft.Text(
                                                "Email: contact@weighin.com",
                                                style=ft.TextStyle(size=16, color="black")
                                            ),
                                            ft.Text(
                                                "Phone: +44 07123 456 7890",
                                                style=ft.TextStyle(size=16, color="black")
                                            ),
                                            ft.Text(
                                                "Address: 123 Weigh St, London, UK",
                                                style=ft.TextStyle(size=16, color="black")
                                            ),
                                        ]
                                    )
                                )
                            )
                        ),
                        
                        ft.Container(
                            margin=ft.margin.symmetric(vertical=20),
                            content=ft.Card(
                                elevation=4,
                                color="white",
                                content=ft.Container(
                                    padding=ft.padding.all(20),
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Get in Touch",
                                                style=ft.TextStyle(
                                                    size=24,
                                                    weight=ft.FontWeight.BOLD,
                                                    color="black"
                                                )
                                            ),
                                            ft.Divider(height=2, color="#2C2C2C"),
                                            ft.Container(height=20),
                                            ft.TextField(
                                                label="Name",
                                                border_color="#2C2C2C",
                                                focused_border_color="#2C2C2C",
                                            ),
                                            ft.Container(height=10),
                                            ft.TextField(
                                                label="Email",
                                                border_color="#2C2C2C",
                                                focused_border_color="#2C2C2C",
                                            ),
                                            ft.Container(height=10),
                                            ft.TextField(
                                                label="Message",
                                                multiline=True,
                                                min_lines=3,
                                                max_lines=5,
                                                border_color="#2C2C2C",
                                                focused_border_color="#2C2C2C",
                                            ),
                                            ft.Container(height=20),
                                            ft.ElevatedButton(
                                                "Send Message",
                                                bgcolor="#2C2C2C",
                                                color="white",
                                                style=ft.ButtonStyle(
                                                    padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                                    text_style=ft.TextStyle(size=16)
                                                ),
                                            )
                                        ],
                                        spacing=10
                                    )
                                )
                            )
                        ),
                        
                        ft.Container(
                            margin=ft.margin.only(top=30),
                            content=ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Back to Home", 
                                        bgcolor="white", 
                                        color="black",
                                        style=ft.ButtonStyle(
                                            padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                            text_style=ft.TextStyle(size=16)
                                        ),
                                        on_click=lambda _: page.go("/")
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            )
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ]
    )
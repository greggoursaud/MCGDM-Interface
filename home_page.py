import flet as ft

def build_home_page(page: ft.Page):
    return ft.View(
        "/",
        controls=[
            # Navigation Bar
            ft.Container(
                bgcolor="#EAEAEA",  # Light gray navbar
                padding=ft.padding.symmetric(vertical=15, horizontal=40),
                content=ft.Row(
                    [
                        ft.Text("Resources"),
                        ft.Text("About"),
                        ft.Text("Contact"),
                        ft.ElevatedButton("Sign in", bgcolor="#2C2C2C", color="white", on_click=lambda _: page.go("/login")),
                        ft.ElevatedButton("Register", bgcolor="white", color="black", on_click=lambda _: page.go("/register")),
                    ],
                    alignment=ft.MainAxisAlignment.END,
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
                                        size=48,
                                        weight=ft.FontWeight.BOLD,
                                        color="white",
                                    ),
                                ),
                                ft.Text(
                                    "IN",  # Italicized part
                                    style=ft.TextStyle(
                                        size=48,
                                        weight=ft.FontWeight.BOLD,
                                        italic=True,  # Italic applied only to "IN"
                                        color="white",
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            "Simplify group decisions with confidence.",
                            style=ft.TextStyle(size=24, color="white"),  # Increased size for visibility
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
                                    )
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20  # Increased spacing to move subtext closer to the title
                )
            )
        ]
    )
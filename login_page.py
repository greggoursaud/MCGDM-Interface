import flet as ft
from firebase_functions import login

def build_login_page(page: ft.Page):
    email_field = ft.TextField(label="Email Address", hint_text="Enter your email address", width=300)
    password_field = ft.TextField(label="Password", hint_text="Enter your password", password=True, can_reveal_password=True, width=300)
    
    def on_login_click(e):
        # Call the firebase login function (Pyrebase based)
        login(page, email_field.value, password_field.value)
    
    return ft.View(
        "/login",
        controls=[
            # Navigation Bar with Back Arrow
            ft.Container(
                bgcolor="#EAEAEA",  # Light gray navbar
                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: page.go("/")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
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
                        # Login Form Header
                        ft.Text(
                            "Login",  # Title of the login form
                            style=ft.TextStyle(
                                size=48,
                                weight=ft.FontWeight.BOLD,
                                color="white",
                            ),
                        ),
                        ft.Text(
                            "Welcome back! Please enter your details.",
                            style=ft.TextStyle(size=18, color="white"),
                        ),
                        
                        # Login Form Container
                        ft.Container(
                            width=400,  # Adjust width of the form container
                            padding=ft.padding.all(20),
                            bgcolor="white",
                            border_radius=10,
                            content=ft.Column(
                                [
                                    email_field,
                                    password_field,
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            "Login", 
                                            bgcolor="#2C2C2C", 
                                            color="white",
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                                text_style=ft.TextStyle(size=16)
                                            ),
                                            on_click=on_login_click  # Call the login function
                                        ),
                                        alignment=ft.alignment.center
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("Don't have an account? "),
                                            ft.TextButton(
                                                "Register",
                                                on_click=lambda _: page.go("/register"),
                                                style=ft.ButtonStyle(
                                                    text_style=ft.TextStyle(color=ft.colors.BLUE)
                                                )
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=5
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=15
                            )
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=30
                )
            )
        ]
    )
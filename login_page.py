import flet as ft
from firebase_functions import login

def build_login_page(page: ft.Page):
    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
    
    def on_login_click(e):
        # Call the firebase login function (Pyrebase based)
        login(page, email_field.value, password_field.value)
    
    return ft.View(
        "/login",
        [
            ft.AppBar(
                title=ft.Text("Log in"),
                bgcolor=ft.colors.BLUE_GREY_900,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: page.go("/"))
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Log in to Your Account", style=ft.TextStyle(size=32, weight=ft.FontWeight.BOLD)),
                        email_field,
                        password_field,
                        ft.ElevatedButton(text="Log in", on_click=on_login_click)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    expand=True
                ),
                alignment=ft.alignment.top_center,
                expand=True
            )
        ]
    )
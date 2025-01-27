import flet as ft

def home_page():
    return ft.Column(
        [
            ft.Text("Welcome to the Home Page!", size=30, font_family="Arial"),
            ft.Text("This is a simple home page template with a navigation bar at the top.", font_family="Arial"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
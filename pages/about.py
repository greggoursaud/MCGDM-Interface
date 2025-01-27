import flet as ft

def about_page():
    return ft.Column(
        [
            ft.Text("About Us", size=30, font_family="Arial"),
            ft.Text("This is the about page.", font_family="Arial"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
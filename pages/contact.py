import flet as ft

def contact_page():
    return ft.Column(
        [
            ft.Text("Contact Us", size=30, font_family="Arial"),
            ft.Text("This is the contact page.", font_family="Arial"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
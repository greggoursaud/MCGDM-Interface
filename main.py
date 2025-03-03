import flet as ft

# Import page components
from home_page import build_home_page
from login_page import build_login_page
from register_page import build_register_page
from profile_page import create_profile_view
from upload_page import build_upload_page
from input_page import build_input_page
from start_page import build_start_page
from terms_page import build_terms_page

def main(page: ft.Page):
    page.title = "Weigh In"
    page.theme = ft.Theme(
        font_family="Montserrat",
        color_scheme=ft.ColorScheme(
            primary="#2C2C2C",
            background="#2C2C2C",
            surface="#2C2C2C",
            on_primary="#FFFFFF",
            on_background="#FFFFFF"
        )
    )

    def route_change(route):
        page.views.clear()
        
        # Home/landing page
        if page.route == "/" or not page.route:
            page.views.append(build_home_page(page))
            
        # Start page (choose between upload and input)
        elif page.route == "/start":
            page.views.append(build_home_page(page))
            page.views.append(build_start_page(page))
            
        # Upload CSV files page
        elif page.route == "/upload":
            page.views.append(build_home_page(page))
            page.views.append(build_start_page(page))
            page.views.append(build_upload_page(page))
            
        # Manual input data page
        elif page.route == "/input":
            page.views.append(build_home_page(page))
            page.views.append(build_start_page(page))
            page.views.append(build_input_page(page))
            
        # User profile page
        elif page.route == "/profile":
            page.views.append(build_home_page(page))
            page.views.append(create_profile_view(page))
            
        # Registration page
        elif page.route == "/register":
            page.views.append(build_home_page(page))
            page.views.append(build_register_page(page))
            
        # Login page
        elif page.route == "/login":
            page.views.append(build_home_page(page))
            page.views.append(build_login_page(page))
            
        # Terms of service page
        elif page.route == "/terms":
            page.views.append(build_home_page(page))
            page.views.append(build_terms_page(page))
            
        # Contact page
        elif page.route == "/contact":
            page.views.append(build_home_page(page))
            page.views.append(
                ft.View(
                    "/contact",
                    [
                        ft.AppBar(
                            bgcolor=ft.colors.BLUE_GREY_900,
                            leading=ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                on_click=lambda _: page.go("/")
                            )
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Contact",
                                        style=ft.TextStyle(
                                            size=32,
                                            weight=ft.FontWeight.BOLD
                                        )
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        ),
                    ]
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, view=ft.AppView.FLET_APP)
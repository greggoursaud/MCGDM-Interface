import flet as ft
import pandas as pd

# Import page components
from home_page import build_home_page
from login_page import build_login_page
from register_page import build_register_page
from profile_page import create_profile_view
from upload_page import build_upload_page
from input_page import build_input_page
from start_page import build_start_page
from terms_page import build_terms_page
from introduction_page import build_introduction_page
from dashboard_page import build_dashboard_page
from parallel_coordinate import parallel_coordinates_plot

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
            
        # Introduction page
        elif page.route == "/introduction":
            page.views.append(build_home_page(page))
            page.views.append(build_introduction_page(page))
            
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
            
        # Dashboard page
        elif page.route == "/dashboard":
            # Get data from client storage
            dashboard_data = page.client_storage.get("dashboard_data")
            
            if dashboard_data:
                # Convert dictionary records back to dataframes
                results_df = pd.DataFrame(dashboard_data["results"])
                alt_df = pd.DataFrame(dashboard_data["alternatives"])
                weight_df = pd.DataFrame(dashboard_data["weights"])
                
                # Generate plot if needed
                plot_fig = None
                if dashboard_data.get("has_plot"):
                    try:
                        plot_fig = parallel_coordinates_plot(results_df)
                    except:
                        pass
                
                # Create the complete data package
                page_data = {
                    "results": results_df,
                    "plot": plot_fig,
                    "alternatives": alt_df, 
                    "weights": weight_df
                }
                
                # Build the dashboard page with the data
                page.views.append(build_dashboard_page(page, page_data))
            else:
                # No data available
                page.views.append(build_dashboard_page(page))
                
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, view=ft.AppView.FLET_APP)
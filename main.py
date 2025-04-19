import flet as ft
import pandas as pd
from firebase_functions import load_data
from profile_page import build_profile_page
from user_utils import get_navigation_controls

# Import page components
from home_page import build_home_page
from contact_page import build_contact_page
from upload_page import build_upload_page
from input_page import build_input_page
from start_page import build_start_page
from terms_page import build_terms_page
from introduction_page import build_introduction_page
from dashboard_page import build_dashboard_page
from resources_page import build_resources_page
from login_page import build_login_page
from register_page import build_register_page

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

    def route_change(e):
        print(f"Route changed to: {e.route}")
        page.views.clear()
        
        # Get user_id for protected routes check
        user_id = page.client_storage.get("user_id")

        # --- Handle /profile route ---
        if e.route == "/profile":
            print("Routing to /profile")
            print(f"User ID from storage for profile: {user_id}")

            if not user_id:
                print("No user_id found in storage, redirecting to login.")
                page.go("/login")
                page.views.append(ft.View("/", [ft.Text("Redirecting to login...")]))
            else:
                print(f"Building profile page for user_id: {user_id}")
                profile_view = build_profile_page(page, user_id)
                page.views.append(profile_view)
        
        # --- Handle /login route ---
        elif e.route == "/login":
             print("Routing to /login")
             page.views.append(build_login_page(page))

        # --- Handle /register route ---
        elif e.route == "/register":
             print("Routing to /register")
             page.views.append(build_register_page(page))

        # --- Handle /start route ---
        elif e.route == "/start":
            print("Routing to /start")
            if not user_id:
                 print("No user_id for /start, redirecting to login.")
                 page.go("/login")
                 page.views.append(ft.View("/", [ft.Text("Redirecting to login...")]))
            else:
                 page.views.append(build_start_page(page))

        # --- Handle /input route ---
        elif e.route == "/input":
            print("Routing to /input")
            if not user_id:
                 print("No user_id for /input, redirecting to login.")
                 page.go("/login")
                 page.views.append(ft.View("/", [ft.Text("Redirecting to login...")]))
            else:
                 page.views.append(build_input_page(page))

        # --- Handle /dashboard route ---
        elif e.route == "/dashboard":
            print("Routing to /dashboard")
            
            # CHANGE: First check if a session was loaded from the profile page
            loaded_session = page.client_storage.get("loaded_session")
            if loaded_session:
                print("Using loaded session from profile page")
                # Use the loaded session data instead of dashboard_data
                page.views.append(build_dashboard_page(
                    page,
                    loaded_session=loaded_session  # Pass the loaded session directly
                ))
                # Note: We don't remove loaded_session here - the dashboard_page will handle that
            else:
                # Fall back to using dashboard_data (from a new calculation)
                dashboard_data = page.client_storage.get("dashboard_data")
                if dashboard_data:
                    results_df = pd.DataFrame(dashboard_data.get("results", []))
                    alt_df = pd.DataFrame(dashboard_data.get("alternatives", []))
                    weight_df = pd.DataFrame(dashboard_data.get("weights", []))
                    optimization_data = dashboard_data.get("optimization_data")
                    parallel_plot = None

                    page.views.append(build_dashboard_page(
                        page,
                        results_df=results_df,
                        alternatives_df=alt_df, 
                        weights_df=weight_df,
                        optimization_data=optimization_data,
                        parallel_plot=parallel_plot
                    ))
                else:
                    # Handle case where dashboard data is missing (e.g., direct navigation)
                    print("No dashboard data found, redirecting to /start")
                    page.go("/start")
                    page.views.append(ft.View("/", [ft.Text("Redirecting...")]))

        # --- Handle /contact route ---
        elif e.route == "/contact":
            print("Routing to /contact")
            page.views.append(build_contact_page(page))

        # --- Handle /upload route ---
        elif e.route == "/upload":
            print("Routing to /upload")
            if not user_id:
                 print("No user_id for /upload, redirecting to login.")
                 page.go("/login")
                 page.views.append(ft.View("/", [ft.Text("Redirecting to login...")]))
            else:
                page.views.append(build_upload_page(page))

        # --- Handle /terms route ---
        elif e.route == "/terms":
            print("Routing to /terms")
            page.views.append(build_terms_page(page))

        # --- Handle /introduction route ---
        elif e.route == "/introduction":
            print("Routing to /introduction")
            page.views.append(build_introduction_page(page))

        # --- Handle /resources route ---
        elif e.route == "/resources":
            print("Routing to /resources")
            page.views.append(build_resources_page(page))

        # --- Handle / (Home) route ---
        elif e.route == "/":
            print("Routing to / (Home)")
            page.views.append(build_home_page(page))

        # --- Fallback for unknown routes ---
        else: 
            print(f"Unknown route '{e.route}', redirecting to / (Home)")
            page.views.append(build_home_page(page))

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, view=ft.AppView.FLET_APP)
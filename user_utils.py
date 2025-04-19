import flet as ft

def get_navigation_controls(page: ft.Page, user_data):
    """
    Returns appropriate navigation controls based on user login status.
    
    Args:
        page: The current page object
        user_data: User data from client storage (None if not logged in)
        
    Returns:
        ft.Row containing the appropriate navigation buttons
    """
    if user_data:
        return ft.Row(
            [
                ft.ElevatedButton(
                    "Profile", 
                    bgcolor="#34A853", 
                    color="white", 
                    on_click=lambda _: page.go("/profile"),
                    icon=ft.icons.PERSON
                )
            ],
            spacing=15
        )
    else:
        return ft.Row(
            [
                ft.ElevatedButton("Sign in", bgcolor="#2C2C2C", color="white", on_click=lambda _: page.go("/login")),
                ft.ElevatedButton("Register", bgcolor="white", color="black", on_click=lambda _: page.go("/register")),
            ],
            spacing=15
        )

import flet as ft
import pandas as pd
from datetime import datetime
from user_utils import get_navigation_controls
from firebase_functions import load_data

# Update function signature to accept user_id
def build_profile_page(page: ft.Page, user_id=None):
    """Build the profile page view. Accepts user_id as parameter."""
    # Get current user data from page storage (for consistency with other pages)
    user_data = page.client_storage.get("user_data")
    
    # Debug: print user data structure to understand what fields are available
    print(f"User data: {user_data}")
    
    # Use the user_id parameter if provided, otherwise try to get it from storage
    if not user_id:
        user_id = page.client_storage.get("user_id")
    
    # Store the user_id value securely for use in subfunctions
    current_user_id = user_id
    
    print(f"Profile page built with user_id: {current_user_id}")
    
    # Get navigation controls
    nav_controls = get_navigation_controls(page, user_data)
    
    # Load user's saved data
    saved_data = load_data(page, current_user_id)
    
    # If no user is logged in, redirect to login page
    if not user_data:
        return ft.View(
            "/profile",
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=20),
                            ft.Text("You need to sign in to view your profile", size=20, color="white"),
                            ft.Container(height=10),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Sign in",
                                        on_click=lambda _: page.go("/login"),
                                        style=ft.ButtonStyle(
                                            bgcolor="#34A853",
                                            color="white",
                                            padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                            text_style=ft.TextStyle(size=16)
                                        )
                                    ),
                                    ft.ElevatedButton(
                                        "Go to Start",
                                        on_click=lambda _: page.go("/start"),
                                        style=ft.ButtonStyle(
                                            bgcolor="#4285F4",
                                            color="white",
                                            padding=ft.padding.symmetric(vertical=15, horizontal=30),
                                            text_style=ft.TextStyle(size=16)
                                        )
                                    )
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            ft.Container(height=10),
                            ft.Text(
                                "You can use the app without signing in, but you won't be able to save your sessions.",
                                size=14, 
                                color="white70",
                                text_align=ft.TextAlign.CENTER
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                    bgcolor="#2C2C2C"
                )
            ]
        )
    
    # Get user's display name or email from multiple potential sources
    email = None
    
    # First check if we have email already stored in client storage - most reliable method
    stored_email = page.client_storage.get("user_email")
    if stored_email:
        email = stored_email
        print(f"Using email from client storage: {email}")
    
    # If no stored email, try to extract from current user_data
    elif user_data:
        # Try different potential structures
        if "email" in user_data:
            email = user_data["email"]
            # Store it for future use
            page.client_storage.set("user_email", email)
            print(f"Found and stored email: {email}")
        elif "users" in user_data and len(user_data["users"]) > 0:
            email = user_data["users"][0].get("email")
            if email:
                page.client_storage.set("user_email", email)
                print(f"Found and stored email from users array: {email}")
    
    # Use email as display name if no display name is available
    display_name = user_data.get("displayName", "") or email or "User"
    
    print(f"Using display name: {display_name}")
    
    # Create a reference for the content area that will change based on selected tab
    content_ref = ft.Ref[ft.Container]()
    
    # Create a dictionary to store loaded data
    loaded_data = {"saved_sessions": []}
    
    # Try to load the user's saved data from Firebase
    try:
        # Use the already obtained user_id, don't get it again
        firebase_data = load_data(page, current_user_id)
        
        if firebase_data and "saved_sessions" in firebase_data:
            loaded_data = firebase_data
    except Exception as e:
        # Show error message if loading fails
        page.snack_bar = ft.SnackBar(ft.Text(f"Error loading saved data: {str(e)}"))
        page.snack_bar.open = True
    
    # Function to create the Sessions tab content
    def create_sessions_tab():
        """Create content for the Sessions tab"""
        
        # Get saved sessions data
        saved_sessions = loaded_data.get("saved_sessions", [])
        
        if not saved_sessions:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Text("No saved sessions found", size=16, color="white"),
                        ft.Text(
                            "Your saved sessions will appear here after you save them from the dashboard.",
                            size=14, color="white70", italic=True
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#2C2C2C",
                border_radius=10,
                padding=20,
                expand=True,
                height=400
            )
        
        # Sort sessions by timestamp (newest first)
        sorted_sessions = sorted(
            saved_sessions, 
            key=lambda x: datetime.strptime(x.get("timestamp", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        
        # Create a card for each saved session
        session_cards = []
        
        for i, session in enumerate(sorted_sessions):
            # Extract metadata
            session_name = session.get("session_name", f"Session {i+1}")
            timestamp = session.get("timestamp", "Unknown date")
            
            # Extract data package
            data_package = session.get("data", {})
            
            # Check what types of data are included
            has_results = "results" in data_package
            has_alternatives = "alternatives" in data_package
            has_weights = "weights" in data_package
            
            # Function to load this session
            def create_load_handler(session_data):
                def load_session(e):
                    # Before loading this session, clear any existing dashboard data
                    # to prevent it from being used instead of our loaded session
                    page.client_storage.remove("dashboard_data")
                    
                    # Store the session data in client storage for the dashboard to use
                    page.client_storage.set("loaded_session", session_data)
                    
                    print(f"Loading session: {session.get('session_name', 'Unknown')}")
                    
                    # Navigate to the dashboard
                    page.go("/dashboard")
                
                return load_session
            
            # Create a card for this session
            session_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.ANALYTICS, color="#4285F4"),
                            title=ft.Text(session_name, size=18, weight=ft.FontWeight.BOLD, color="black"),
                            subtitle=ft.Text(f"Saved on: {timestamp}", color="black70"),
                        ),
                        ft.Divider(color="white24", height=1),
                        ft.Container(
                            content=ft.Row([
                                ft.ElevatedButton(
                                    "Load Session",
                                    icon=ft.icons.OPEN_IN_NEW,
                                    on_click=create_load_handler(data_package),
                                    style=ft.ButtonStyle(
                                        bgcolor="#4285F4",
                                        color="white",
                                        overlay_color=ft.colors.TRANSPARENT,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        elevation=3,
                                        shadow_color="#000000",
                                    ),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Delete Session",
                                    icon_color="#EA4335",
                                    on_click=lambda e, idx=i: delete_session(e, idx)
                                )
                            ], spacing=5, alignment=ft.MainAxisAlignment.END),
                            padding=ft.padding.only(right=15, bottom=10)
                        ),
                    ]),
                    width=400,
                    bgcolor="#1C1C1C",
                    border=ft.border.all(1, "#3C3C3C"),
                    border_radius=10,
                ),
                elevation=3
            )
            
            session_cards.append(session_card)
        
        # Function to delete a session
        def delete_session(e, index):
            # Create a confirmation dialog
            def confirm_delete(e):
                # Remove the session from the list
                loaded_data["saved_sessions"].pop(index)
                
                # Save the updated data to Firebase - use the stored user_id
                try:
                    from firebase_functions import save_data
                    save_data(page, current_user_id, loaded_data)
                    
                    # Update the content area with the new list of sessions
                    content_ref.current.content = create_sessions_tab()
                    
                    # Show success message
                    page.snack_bar = ft.SnackBar(ft.Text("Session deleted successfully"))
                    page.snack_bar.open = True
                except Exception as e:
                    # Show error message if saving fails
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error deleting session: {str(e)}"))
                    page.snack_bar.open = True
                
                # Close the dialog
                confirm_dialog.open = False
                page.update()
            
            # Create confirmation dialog
            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Deletion"),
                content=ft.Text("Are you sure you want to delete this session? This action cannot be undone."),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: setattr(confirm_dialog, 'open', False) or page.update()),
                    ft.TextButton("Delete", on_click=confirm_delete),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Show the dialog
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()
        
        # Create a grid or column layout depending on number of cards
        if len(session_cards) > 1:
            # For multiple sessions, use a responsive grid layout
            return ft.Container(
                content=ft.ResponsiveRow(
                    [
                        ft.Column([card], col={"sm": 12, "md": 6, "lg": 4})
                        for card in session_cards
                    ],
                ),
                padding=10,
                expand=True,
                bgcolor="#2C2C2C",
                border_radius=10,
            )
        else:
            # For a single session, center it in the container
            return ft.Container(
                content=ft.Column(
                    session_cards,
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                expand=True,
                bgcolor="#2C2C2C",
                border_radius=10,
            )
    
    # Function to create the Alternatives tab content
    def create_alternatives_tab():
        """Create content showing saved alternative datasets"""
        
        # Extract all unique alternatives datasets
        all_alternatives = []
        
        for session in loaded_data.get("saved_sessions", []):
            data_package = session.get("data", {})
            
            if "alternatives" in data_package:
                # Add session metadata
                alt_data = {
                    "alternatives": data_package["alternatives"],
                    "session_name": session.get("session_name", "Unnamed Session"),
                    "timestamp": session.get("timestamp", "Unknown date")
                }
                all_alternatives.append(alt_data)
        
        if not all_alternatives:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Text("No saved alternatives datasets found", size=16, color="white"),
                        ft.Text(
                            "Alternatives data from your saved sessions will appear here.",
                            size=14, color="white70", italic=True
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#2C2C2C",
                border_radius=10,
                padding=20,
                expand=True,
                height=400
            )
        
        # Sort alternatives by timestamp (newest first)
        sorted_alternatives = sorted(
            all_alternatives, 
            key=lambda x: datetime.strptime(x.get("timestamp", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        
        # Create a card for each alternatives dataset
        alt_cards = []
        
        for i, alt_data in enumerate(sorted_alternatives):
            # Get metadata
            session_name = alt_data.get("session_name", f"Alternatives {i+1}")
            timestamp = alt_data.get("timestamp", "Unknown date")
            
            # Get alternatives data
            alternatives = alt_data.get("alternatives", [])
            
            # Calculate number of alternatives and criteria
            if alternatives:
                num_alternatives = len(alternatives)
                num_criteria = len(alternatives[0]) - 1 if len(alternatives[0]) > 1 else 0
            else:
                num_alternatives = 0
                num_criteria = 0
            
            # Function to handle using this alternatives dataset
            def create_use_handler(alt_data):
                def use_alternatives(e):
                    # Store the alternatives data in client storage
                    page.client_storage.set("loaded_alternatives", alt_data["alternatives"])
                    
                    # Navigate to the input page 
                    page.go("/input")
                
                return use_alternatives
            
            # Create a card for this alternatives dataset
            alt_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.LIST_ALT, color="#FBBC05"),
                            title=ft.Text(f"Alternatives from {session_name}", 
                                         size=16, 
                                         weight=ft.FontWeight.BOLD, 
                                         color="white"),
                            subtitle=ft.Text(f"Saved on: {timestamp}", color="white70"),
                        ),
                        ft.Divider(color="white24", height=1),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"Alternatives: {num_alternatives}", color="white"),
                                ft.Text(f"Criteria: {num_criteria}", color="white"),
                            ], spacing=5),
                            padding=ft.padding.only(left=15, right=15, bottom=10)
                        ),
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Use Alternatives",
                                icon=ft.icons.OPEN_IN_NEW,
                                on_click=create_use_handler(alt_data),
                                style=ft.ButtonStyle(
                                    bgcolor="#FBBC05",
                                    color="black",
                                    overlay_color=ft.colors.TRANSPARENT,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    elevation=3,
                                    shadow_color="#000000",
                                ),
                            ),
                            padding=ft.padding.only(left=15, right=15, bottom=15),
                            alignment=ft.alignment.center
                        ),
                    ]),
                    width=350,
                    bgcolor="#1C1C1C",
                    border=ft.border.all(1, "#3C3C3C"),
                    border_radius=10,
                ),
                elevation=3
            )
            
            alt_cards.append(alt_card)
        
        # Create a responsive grid for the cards
        return ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Column([card], col={"sm": 12, "md": 6, "lg": 4})
                    for card in alt_cards
                ],
            ),
            padding=10,
            expand=True,
            bgcolor="#2C2C2C",
            border_radius=10,
        )
    
    # Function to create the Weights tab content
    def create_weights_tab():
        """Create content showing saved weights/criteria datasets"""
        
        # Extract all unique weights datasets
        all_weights = []
        
        for session in loaded_data.get("saved_sessions", []):
            data_package = session.get("data", {})
            
            if "weights" in data_package:
                # Add session metadata
                weight_data = {
                    "weights": data_package["weights"],
                    "session_name": session.get("session_name", "Unnamed Session"),
                    "timestamp": session.get("timestamp", "Unknown date")
                }
                all_weights.append(weight_data)
        
        if not all_weights:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Text("No saved weights datasets found", size=16, color="white"),
                        ft.Text(
                            "Weights data from your saved sessions will appear here.",
                            size=14, color="white70", italic=True
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#2C2C2C",
                border_radius=10,
                padding=20,
                expand=True,
                height=400
            )
        
        # Sort weights by timestamp (newest first)
        sorted_weights = sorted(
            all_weights, 
            key=lambda x: datetime.strptime(x.get("timestamp", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        
        # Create a card for each weights dataset
        weight_cards = []
        
        for i, weight_data in enumerate(sorted_weights):
            # Get metadata
            session_name = weight_data.get("session_name", f"Weights {i+1}")
            timestamp = weight_data.get("timestamp", "Unknown date")
            
            # Get weights data
            weights = weight_data.get("weights", [])
            
            # Calculate number of criteria and DMs
            if weights:
                # Get a sample of the data to analyze structure
                sample = weights[0]
                if isinstance(sample, dict) and "Criterion" in sample:
                    num_criteria = len(weights)
                    # Check if we have DM columns
                    dm_cols = [col for col in sample.keys() if col.startswith("DM")]
                    num_dms = len(dm_cols)
                else:
                    num_criteria = len(weights)
                    num_dms = 1
            else:
                num_criteria = 0
                num_dms = 0
            
            # Function to handle using this weights dataset
            def create_use_handler(weight_data):
                def use_weights(e):
                    # Store the weights data in client storage
                    page.client_storage.set("loaded_weights", weight_data["weights"])
                    
                    # Navigate to the input page
                    page.go("/input")
                
                return use_weights
            
            # Create a card for this weights dataset
            weight_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.SCALE, color="#EA4335"),
                            title=ft.Text(f"Weights from {session_name}", 
                                         size=16, 
                                         weight=ft.FontWeight.BOLD, 
                                         color="white"),
                            subtitle=ft.Text(f"Saved on: {timestamp}", color="white70"),
                        ),
                        ft.Divider(color="white24", height=1),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"Criteria: {num_criteria}", color="white"),
                                ft.Text(f"Decision Makers: {num_dms}", color="white"),
                            ], spacing=5),
                            padding=ft.padding.only(left=15, right=15, bottom=10)
                        ),
                        ft.Container(
                            content=ft.ElevatedButton(
                                "Use Weights",
                                icon=ft.icons.OPEN_IN_NEW,
                                on_click=create_use_handler(weight_data),
                                style=ft.ButtonStyle(
                                    bgcolor="#EA4335",
                                    color="white",
                                    overlay_color=ft.colors.TRANSPARENT,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    elevation=3,
                                    shadow_color="#000000",
                                ),
                            ),
                            padding=ft.padding.only(left=15, right=15, bottom=15),
                            alignment=ft.alignment.center
                        ),
                    ]),
                    width=350,
                    bgcolor="#1C1C1C",
                    border=ft.border.all(1, "#3C3C3C"),
                    border_radius=10,
                ),
                elevation=3
            )
            
            weight_cards.append(weight_card)
        
        # Create a responsive grid for the cards
        return ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Column([card], col={"sm": 12, "md": 6, "lg": 4})
                    for card in weight_cards
                ],
            ),
            padding=10,
            expand=True,
            bgcolor="#2C2C2C",
            border_radius=10,
        )
    
    # Create the tab buttons
    tabs = [
        {"text": "Saved Sessions", "icon": ft.icons.FOLDER_SPECIAL, "content": create_sessions_tab},
        {"text": "Alternatives", "icon": ft.icons.LIST_ALT, "content": create_alternatives_tab},
        {"text": "Weights", "icon": ft.icons.SCALE, "content": create_weights_tab},
    ]
    
    tab_buttons = []
    
    # Function to switch tabs
    def create_tab_click_handler(index):
        def handle_click(e):
            # Update all buttons
            for i, btn_data in enumerate(zip(tab_buttons, tabs)):
                btn, tab_info = btn_data
                icon_widget = btn.content.controls[0] # Get the Icon widget

                if i == index:
                    btn.bgcolor = "white"
                    btn.color = "#2C2C2C" # Text color
                    icon_widget.color = "#2C2C2C" # Icon color
                else:
                    btn.bgcolor = "#1C1C1C" # Use the card background color for unselected
                    btn.color = "white" # Text color
                    icon_widget.color = "white" # Icon color

            # Set the content - calling the tab content function
            content_ref.current.content = tabs[index]["content"]()

            page.update()
        return handle_click

    # Create tab buttons
    for i, tab in enumerate(tabs):
        is_selected = (i == 0)
        text_color = "#2C2C2C" if is_selected else "white"
        icon_color = "#2C2C2C" if is_selected else "white"
        bg_color = "white" if is_selected else "#1C1C1C" # Use card background for unselected

        btn = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(name=tab["icon"], size=18, color=icon_color), # Set initial icon color
                    ft.Text(tab["text"], size=14)
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            style=ft.ButtonStyle(
                bgcolor=bg_color, # Set initial background color
                color=text_color, # Set initial text color
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(12),
                elevation=0, # Keep elevation low for a flatter tab look
                overlay_color=ft.colors.with_opacity(0.1, ft.colors.WHITE if not is_selected else ft.colors.BLACK), # Subtle overlay
            ),
            # elevation=0, # Moved elevation to ButtonStyle
            on_click=create_tab_click_handler(i)
        )
        tab_buttons.append(btn)

    # Function to handle sign out
    def sign_out(e):
        # Clear all user-related data
        page.client_storage.remove("user_data")
        page.client_storage.remove("user_id")  # Make sure to remove user_id too
        page.client_storage.remove("id_token")
        page.client_storage.remove("refresh_token")
        
        # Show a message
        page.snack_bar = ft.SnackBar(ft.Text("Signed out successfully"))
        page.snack_bar.open = True
        
        # Go to home page
        page.go("/")
    
    # Return profile view
    return ft.View(
        "/profile",
        [
            # Navigation bar
            ft.Container(
                bgcolor="#EAEAEA",
                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.HOME,
                            on_click=lambda _: page.go("/"),
                            tooltip="Go to Home"
                        ),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Sign out", 
                            bgcolor="#2C2C2C", 
                            color="white", 
                            on_click=sign_out,
                            icon=ft.icons.LOGOUT
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ),
            
            # Main content
            ft.Container(
                content=ft.Column(
                    [
                        # Profile header
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Container(
                                                content=ft.CircleAvatar(
                                                    content=ft.Text(
                                                        display_name[0].upper(),
                                                        size=32,
                                                        weight=ft.FontWeight.BOLD,
                                                        color="#2C2C2C"
                                                    ),
                                                    bgcolor="#34A853",
                                                    radius=40
                                                ),
                                                margin=ft.margin.only(right=20)
                                            ),
                                            ft.Column(
                                                [
                                                    ft.Text(
                                                        display_name,
                                                        size=24,
                                                        weight=ft.FontWeight.BOLD,
                                                        color="white"
                                                    ),
                                                    ft.Text(
                                                        user_data.get("email", ""),
                                                        size=16,
                                                        color="#CCCCCC"
                                                    )
                                                ],
                                                spacing=5
                                            )
                                        ]
                                    ),
                                ],
                                spacing=20
                            ),
                            padding=30,
                            border_radius=10,
                            bgcolor="#1C1C1C",
                            width=600
                        ),
                        
                        # Tab bar
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Row(
                                        tab_buttons,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=10
                                    ),
                                    padding=ft.padding.all(10),
                                    bgcolor="#1C1C1C"
                                ),
                                elevation=4
                            ),
                            padding=ft.padding.only(top=20, bottom=5),
                        ),
                        
                        # Content area
                        ft.Container(
                            ref=content_ref,
                            content=create_sessions_tab(),  # Default to sessions tab
                            expand=True,
                            padding=ft.padding.all(5),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                    expand=True
                ),
                padding=20,
                expand=True,
                bgcolor="#2C2C2C",
                alignment=ft.alignment.top_center
            )
        ]
    )
import requests
import json
from flet import SnackBar, Text
from config import firebase_config  # Import configuration
from firebase_init import get_firebase_auth, get_firebase_db  # Import Firebase functions

def load_data(page, user_id):
    """Load user data from Firebase database using Pyrebase."""
    try:
        auth = get_firebase_auth()
        db = get_firebase_db()
        
        print("load_data: Attempting to get current user...")
        user = auth.current_user
        id_token = None

        if user and 'idToken' in user:
            id_token = user['idToken']
            print(f"load_data: Found active user token for {user.get('email', 'unknown email')}")
        else:
            print("load_data: No active user token found or user object invalid. Attempting refresh...")
            refresh_token = page.client_storage.get("refresh_token")
            if refresh_token:
                try:
                    print("load_data: Refresh token found. Calling auth.refresh...")
                    user = auth.refresh(refresh_token)
                    print("load_data: Token refresh successful.")
                    # Store refreshed tokens
                    page.client_storage.set("id_token", user['idToken'])
                    page.client_storage.set("refresh_token", user['refreshToken'])
                    page.client_storage.set("user_data", user) # Update user data
                    id_token = user['idToken'] # Use the newly refreshed token
                except Exception as refresh_error:
                    print(f"load_data: Token refresh failed: {refresh_error}")
                    handle_auth_error(page, f"Session refresh failed. Please sign in again.")
                    return None
            else:
                print("load_data: No refresh token found.")
                handle_auth_error(page, "Session expired or invalid. Please sign in again.")
                return None

        if not id_token:
             print("load_data: Failed to obtain a valid ID token after check/refresh.")
             handle_auth_error(page, "Authentication error. Please sign in again.")
             return None

        # Use Pyrebase db object to get data with the obtained token
        print(f"load_data: Fetching data for user {user_id} using token.")
        data = db.child("users").child(user_id).child("data").get(id_token).val()
        print("load_data: Data fetched successfully.")
        return data

    except Exception as e:
        # Check for specific Pyrebase auth errors (e.g., invalid token)
        error_str = str(e)
        print(f"load_data: Exception during data fetch: {error_str}") # Log the specific error
        if "Permission denied" in error_str or "Auth token is expired" in error_str or "INVALID_ID_TOKEN" in error_str:
             print("load_data: Auth error detected, calling handle_auth_error.")
             handle_auth_error(page, "Authentication error or session expired. Please sign in again.")
        else:
            page.snack_bar = SnackBar(Text(f"Error loading data: {error_str}"))
            page.snack_bar.open = True
            page.update()
        return None

def handle_auth_error(page, message):
    """Handle authentication errors by clearing tokens and redirecting to login."""
    # Clear stored tokens and user data
    page.client_storage.remove("id_token")
    page.client_storage.remove("refresh_token")
    page.client_storage.remove("user_data")
    page.client_storage.remove("user_id")  # Also remove user_id
    
    # Show message to the user
    page.snack_bar = SnackBar(Text(message))
    page.snack_bar.open = True
    
    # Redirect to login page
    page.go("/login")
    page.update()

# Add the login function using Pyrebase
def login(page, email, password):
    """Login a user using Firebase Authentication with Pyrebase."""
    try:
        auth = get_firebase_auth()
        user = auth.sign_in_with_email_and_password(email, password)

        # Store user data and tokens
        page.client_storage.set("user_data", user)
        page.client_storage.set("id_token", user['idToken'])
        page.client_storage.set("refresh_token", user['refreshToken'])
        page.client_storage.set("user_id", user['localId']) # Store user ID
        page.client_storage.set("user_email", email)  # Store email directly for easy access

        page.snack_bar = SnackBar(Text("Login successful!"))
        page.snack_bar.open = True
        # Navigate to the start page after successful login
        page.go("/")
        page.update()
        return user

    except Exception as e:
        error_message = "Login failed"
        try:
            # Attempt to parse Firebase error from requests.exceptions.HTTPError
            error_json = json.loads(e.args[1])
            error_message = error_json['error']['message']
        except (IndexError, KeyError, json.JSONDecodeError, AttributeError):
             # Fallback for other error types
             error_message = str(e)

        page.snack_bar = SnackBar(Text(f"Error: {error_message}"))
        page.snack_bar.open = True
        page.update()
        return None

def register(page, email, password):
    """Register a new user with Firebase Authentication."""
    try:
        # Get the Firebase auth instance
        auth = get_firebase_auth()
        
        # Create a new user
        user = auth.create_user_with_email_and_password(email, password)
        
        # Get authentication tokens and user ID
        id_token = user['idToken']
        refresh_token = user.get('refreshToken')
        local_id = user.get('localId')  # UID of the user
        
        # Store user data and tokens in client storage (similar to login)
        page.client_storage.set("user_data", user) # Store the full user object
        page.client_storage.set("id_token", id_token)
        page.client_storage.set("refresh_token", refresh_token)
        page.client_storage.set("user_id", local_id)
        page.client_storage.set("user_email", email)  # Store email directly for easy access
        
        # Show success message
        page.snack_bar = SnackBar(Text("Registration successful! Redirecting..."))
        page.snack_bar.open = True
        
        # Redirect to home page after successful registration (like login)
        page.go("/") 
        page.update()
        
        return user
    
    except Exception as e:
        # Extract the error message from Firebase
        error_message = "Registration failed"
        if hasattr(e, 'args') and e.args and isinstance(e.args[0], dict):
            error_data = e.args[0]
            if 'error' in error_data:
                error_info = error_data['error']
                if 'message' in error_info:
                    error_message = error_info['message']
        
        # Show error message
        page.snack_bar = SnackBar(Text(f"Error: {error_message}"))
        page.snack_bar.open = True
        page.update()
        
        return None

def save_data(page, user_id, data):
    """Save user data to Firebase database using Pyrebase."""
    try:
        auth = get_firebase_auth()
        db = get_firebase_db()

        # Get user token - Pyrebase handles refresh automatically if needed
        user = auth.current_user
        if not user or 'idToken' not in user:
            # Attempt to refresh if user object exists but token is missing (might be expired)
            refresh_token = page.client_storage.get("refresh_token")
            if refresh_token:
                try:
                    user = auth.refresh(refresh_token)
                     # Store refreshed tokens
                    page.client_storage.set("id_token", user['idToken'])
                    page.client_storage.set("refresh_token", user['refreshToken'])
                    page.client_storage.set("user_data", user) # Update user data
                except Exception as refresh_error:
                    handle_auth_error(page, f"Session refresh failed: {refresh_error}. Please sign in again.")
                    return False
            else:
                handle_auth_error(page, "Session expired or invalid. Please sign in again.")
                return False

        id_token = user['idToken']

        # Use Pyrebase db object to set data (overwrites existing data at the location)
        # Use update() instead of set() if you want to merge data
        db.child("users").child(user_id).child("data").set(data, id_token)

        # page.snack_bar = SnackBar(Text("Data saved successfully!")) # Removed to avoid duplicate messages from dashboard
        # page.snack_bar.open = True
        # page.update()
        return True

    except Exception as e:
         # Check for specific Pyrebase auth errors (e.g., invalid token)
        error_str = str(e)
        if "Permission denied" in error_str or "Auth token is expired" in error_str:
             handle_auth_error(page, "Authentication error or session expired. Please sign in again.")
        else:
            page.snack_bar = SnackBar(Text(f"Error saving data: {error_str}"))
            page.snack_bar.open = True
            page.update()
        return False
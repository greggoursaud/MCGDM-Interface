import flet as ft
from firebase_init import get_firebase_auth, get_firebase_db

def login(page: ft.Page, email, password):
    auth = get_firebase_auth()
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        page.snack_bar = ft.SnackBar(ft.Text("Login Successful!"))
        page.snack_bar.open = True
        page.go("/data")
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Login Failed: {e}"))
        page.snack_bar.open = True

def register(page: ft.Page, email, password):
    auth = get_firebase_auth()
    try:
        user = auth.create_user_with_email_and_password(email, password)
        page.snack_bar = ft.SnackBar(ft.Text("Registration Successful!"))
        page.snack_bar.open = True
        page.go("/data")
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Registration Failed: {e}"))
        page.snack_bar.open = True

def save_data(page: ft.Page, user_id, data):
    db = get_firebase_db()
    try:
        db.child("users").child(user_id).child("data").set(data)
        page.snack_bar = ft.SnackBar(ft.Text("Data Saved!"))
        page.snack_bar.open = True
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Error saving data: {e}"))
        page.snack_bar.open = True

def load_data(page: ft.Page, user_id):
    db = get_firebase_db()
    try:
        data = db.child("users").child(user_id).child("data").get()
        return data.val()  # Pyrebase returns a wrapper; use .val() to get data
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Error loading data: {e}"))
        page.snack_bar.open = True
        return None
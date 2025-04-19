import firebase_admin
from firebase_admin import credentials, auth, firestore
import argparse
import os
import json
from config import firebase_config  # Import your existing config

def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    try:
        # Check if we have a service account key file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        service_account_path = os.path.join(script_dir, "serviceAccountKey.json")
        
        if os.path.exists(service_account_path):
            print(f"Using service account file: {service_account_path}")
            cred = credentials.Certificate(service_account_path)
            
            # Initialize with database URL from config
            firebase_admin.initialize_app(cred, {
                'databaseURL': firebase_config["databaseURL"]
            })
            
            return True
        else:
            print("Service account key not found. You need to get it from Firebase console.")
            print("\nInstructions:")
            print("1. Go to Firebase Console → Project Settings → Service accounts")
            print("2. Click 'Generate new private key'")
            print("3. Save the JSON file as 'serviceAccountKey.json' in the same folder as this script")
            print("\nProject ID (for reference): " + firebase_config["projectId"])
            return False
            
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False

def delete_all_users():
    """Delete all Firebase Authentication users."""
    try:
        # Get all users (in batches of 1000)
        page = auth.list_users()
        deleted_count = 0
        
        for user in page.users:
            auth.delete_user(user.uid)
            deleted_count += 1
            print(f"Deleted user: {user.uid} ({user.email if user.email else 'no email'})")
        
        print(f"Successfully deleted {deleted_count} users")
        return True
    except Exception as e:
        print(f"Error deleting users: {e}")
        return False

def delete_all_data():
    """Delete all data from Firestore or Realtime DB based on URL."""
    db_url = firebase_config["databaseURL"]
    
    if "firestore" in db_url:
        return delete_firestore_data()
    else:
        return delete_realtime_db_data()
    
def delete_firestore_data():
    """Delete all data from Firestore."""
    try:
        db = firestore.client()
        
        # Get all collections
        collections = db.collections()
        deleted_count = 0
        
        for collection in collections:
            # Delete all documents in the collection
            docs = collection.stream()
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
                print(f"Deleted document: {doc.id} in {collection.id}")
        
        print(f"Successfully deleted {deleted_count} documents")
        return True
    except Exception as e:
        print(f"Error deleting Firestore data: {e}")
        return False

def delete_realtime_db_data():
    """Delete all data from Realtime Database."""
    try:
        # For Realtime DB we need to use a different approach
        from firebase_admin import db
        
        # Reference to the root of the database
        ref = db.reference("/")
        
        # Delete everything
        ref.delete()
        
        print("Successfully deleted all Realtime Database data")
        return True
    except Exception as e:
        print(f"Error deleting Realtime DB data: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Reset Firebase data for testing.")
    parser.add_argument("--users", action="store_true", help="Delete all users from Authentication")
    parser.add_argument("--data", action="store_true", help="Delete all data from Database")
    parser.add_argument("--all", action="store_true", help="Delete all users and data")
    
    args = parser.parse_args()
    
    if not (args.users or args.data or args.all):
        print("\n----- Firebase Data Reset Tool -----")
        print("This script will delete users and/or data from your Firebase project.")
        print("WARNING: This operation cannot be undone!\n")
        print("Available options:")
        print("  --users    Delete all users from Authentication")
        print("  --data     Delete all data from Database")
        print("  --all      Delete both users and data (most common choice)")
        print("\nExample: python reset_firebase.py --all\n")
        return
    
    # Initialize Firebase Admin SDK
    if not initialize_firebase():
        return
    
    # Ask for confirmation before proceeding
    what_to_delete = []
    if args.users or args.all:
        what_to_delete.append("ALL USERS")
    if args.data or args.all:
        what_to_delete.append("ALL DATA")
    
    print(f"\nWARNING: You are about to delete {' and '.join(what_to_delete)} from your Firebase project!")
    print("This cannot be undone!")
    confirmation = input("Type 'YES' to confirm: ")
    
    if confirmation != "YES":
        print("Operation cancelled.")
        return
    
    # Perform requested operations
    if args.users or args.all:
        delete_all_users()
    
    if args.data or args.all:
        delete_all_data()
    
    print("\nReset operation completed.")

if __name__ == "__main__":
    main()

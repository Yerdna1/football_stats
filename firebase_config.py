import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import json

def initialize_firebase():
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if using environment variables or JSON file
        if os.getenv('FIREBASE_PRIVATE_KEY'):
            # Using environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
            }
            cred = credentials.Certificate(cred_dict)
        else:
            # Using JSON file
            cred = credentials.Certificate('serviceAccountKey.json')
        
        # Initialize Firebase
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        print("Firebase initialized successfully")
        return db
    
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None
import requests
import json
import time
from requests.exceptions import RequestException, Timeout, ConnectionError
from iso3166 import countries

# -------------------------------------------------------------------
# Webex + ISS Tracker
# This program connects to Webex, monitors messages in a selected room,
# and when someone types a command like "/5", it waits that many seconds
# (up to 5), fetches the ISS location, and posts where it is.
# -------------------------------------------------------------------

def get_access_token():
    """Ask the user for a Webex token or use the default one."""
    try:
        choice = input("Do you want to use the hard-coded Webex token? (y/n): ").strip().lower()
        if choice == 'n':
            token = input("Enter your Webex access token: ").strip()
            if not token:
                print("⚠️ You must enter a token.")
                return None
            return f"Bearer {token}"
        else:
            # Normally you wouldn’t hardcode this in a real project!
            return "Bearer NzNiYTFkOGQtZjIwZS00MjU5LTliNWYtYzA1YTFmMmI3NWE0MWQ3MjZlYjAtYjA5_P0A1_636b97a0-b0af-4297-b0e7-480dd517b3f9"
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

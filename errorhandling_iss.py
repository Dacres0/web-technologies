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

def get_rooms(access_token):
    """Get a list of Webex rooms for this account."""
    try:
        response = requests.get("https://webexapis.com/v1/rooms", headers={"Authorization": access_token}, timeout=10)
        if response.status_code != 200:
            print(f"Failed to get rooms. Status code: {response.status_code}")
            return []

        data = response.json()
        rooms = data.get("items", [])
        if not rooms:
            print("No rooms found.")
            return []

        print("\nAvailable Rooms:")
        for room in rooms:
            print(f"- {room.get('title', 'Unnamed Room')} ({room.get('type', 'Unknown Type')})")
        return rooms

    except (ConnectionError, Timeout):
        print("⚠️ Network issue while trying to reach Webex.")
    except RequestException as e:
        print(f"⚠️ Request failed: {e}")
    except ValueError:
        print("⚠️ Could not decode JSON response from Webex.")
    return []


def select_room(rooms):
    """Ask the user to choose a room by typing part of its name."""
    if not rooms:
        print("⚠️ No rooms to choose from.")
        return None, None

    while True:
        name = input("\nEnter part of the room name you want to monitor: ").strip()
        if not name:
            print("Please enter a valid room name.")
            continue

        for room in rooms:
            if name.lower() in room.get("title", "").lower():
                print(f"✅ Found room: {room['title']}")
                return room["id"], room["title"]

        print("❌ No matching room found. Try again.")

def get_latest_message(room_id, access_token):
    """Get the most recent message from the specified Webex room."""
    try:
        params = {"roomId": room_id, "max": 1}
        response = requests.get("https://webexapis.com/v1/messages", params=params,
                                headers={"Authorization": access_token}, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get messages (status {response.status_code}).")
            return None

        data = response.json()
        messages = data.get("items", [])
        if not messages:
            return None

        return messages[0].get("text", "")
    except RequestException as e:
        print(f"⚠️ Error getting latest message: {e}")
        return None


def get_iss_location():
    """Get the current ISS location using the open-notify API."""
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        if response.status_code != 200:
            print("⚠️ Could not get ISS location.")
            return None

        data = response.json()
        if data.get("message") != "success":
            print("⚠️ Invalid ISS API response.")
            return None

        pos = data.get("iss_position", {})
        return {
            "lat": pos.get("latitude"),
            "lon": pos.get("longitude"),
            "timestamp": data.get("timestamp")
        }
    except RequestException as e:
        print(f"⚠️ Error contacting ISS API: {e}")
        return None

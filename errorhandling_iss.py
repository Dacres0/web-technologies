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
                print("You must enter a token.")
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
        print("Network issue while trying to reach Webex.")
    except RequestException as e:
        print(f"Request failed: {e}")
    except ValueError:
        print("Could not decode JSON response from Webex.")
    return []


def select_room(rooms):
    """Ask the user to choose a room by typing part of its name."""
    if not rooms:
        print("No rooms to choose from.")
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

        print("No matching room found. Try again.")

def get_latest_message(room_id, access_token):
    """Get the most recent message from the specified Webex room."""
    try:
        params = {"roomId": room_id, "max": 1}
        response = requests.get("https://webexapis.com/v1/messages", params=params,
                                headers={"Authorization": access_token}, timeout=10)
        if response.status_code != 200:
            print(f"Failed to get messages (status {response.status_code}).")
            return None

        data = response.json()
        messages = data.get("items", [])
        if not messages:
            return None

        return messages[0].get("text", "")
    except RequestException as e:
        print(f"Error getting latest message: {e}")
        return None


def get_iss_location():
    """Get the current ISS location using the open-notify API."""
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        if response.status_code != 200:
            print("Could not get ISS location.")
            return None

        data = response.json()
        if data.get("message") != "success":
            print("Invalid ISS API response.")
            return None

        pos = data.get("iss_position", {})
        return {
            "lat": pos.get("latitude"),
            "lon": pos.get("longitude"),
            "timestamp": data.get("timestamp")
        }
    except RequestException as e:
        print(f"Error contacting ISS API: {e}")
        return None

def reverse_geocode(lat, lon, api_key):
    """Convert coordinates to a readable address using LocationIQ."""
    try:
        params = {"key": api_key, "lat": lat, "lon": lon, "format": "json"}
        response = requests.get("https://us1.locationiq.com/v1/reverse.php", params=params, timeout=10)
        if response.status_code != 200:
            print(f"Reverse geocoding failed ({response.status_code}).")
            return None
        return response.json().get("address", {})
    except RequestException as e:
        print(f"Error in reverse geocoding: {e}")
        return None


def format_iss_message(lat, lon, timestamp, address):
    """Turn ISS data into a readable message."""
    time_str = time.ctime(timestamp)
    country_code = address.get("country_code", "XZ").upper()
    state = address.get("state", "Unknown")
    city = address.get("city", address.get("town", "Unknown"))

    try:
        country_name = countries.get(country_code).name
    except KeyError:
        country_name = "Unknown Country"

    if country_code == "XZ":
        return f"On {time_str}, the ISS was over the ocean at ({lat}°, {lon}°)."
    elif city != "Unknown":
        return f"On {time_str}, the ISS was above {city}, {state}, {country_name}.\nCoordinates: ({lat}°, {lon}°)"
    else:
        return f"On {time_str}, the ISS was above {state}, {country_name}.\nCoordinates: ({lat}°, {lon}°)"


def post_message(room_id, text, access_token):
    """Post a message to the selected Webex room."""
    try:
        headers = {"Authorization": access_token, "Content-Type": "application/json"}
        data = {"roomId": room_id, "text": text}
        response = requests.post("https://webexapis.com/v1/messages",
                                 data=json.dumps(data), headers=headers, timeout=10)
        if response.status_code == 200:
            print("Message posted successfully.")
        else:
            print(f"Failed to post message. {response.text}")
    except RequestException as e:
        print(f"Error sending message: {e}")


def monitor_room(room_id, access_token, maps_api_key):
    """Watch the selected room for '/seconds' commands."""
    print("\nMonitoring the room for messages like '/5'...\n")

    while True:
        time.sleep(1)
        msg = get_latest_message(room_id, access_token)
        if not msg:
            continue

        print(f"Last message: {msg}")

        if not msg.startswith("/"):
            continue

        cmd = msg[1:]
        if not cmd.isdigit():
            print("Invalid command. Please use /<number> (e.g. /5).")
            continue

        seconds = min(int(cmd), 5)
        print(f"Waiting {seconds} seconds...")
        time.sleep(seconds)

        iss = get_iss_location()
        if not iss:
            print("Could not get ISS location.")
            continue

        addr = reverse_geocode(iss["lat"], iss["lon"], maps_api_key)
        if not addr:
            print("Could not reverse geocode location.")
            continue

        msg = format_iss_message(iss["lat"], iss["lon"], iss["timestamp"], addr)
        print(f"Sending message: {msg}")
        post_message(room_id, msg, access_token)

#get_access_token() – handles token input
#get_rooms(access_token) – fetches available Webex rooms
#select_room(rooms) – lets the user pick which room to monitor
#get_latest_message(room_id, access_token) – polls latest message
#get_iss_location() – fetches current ISS position
#reverse_geocode(lat, lon, api_key) – gets address from coordinates
#format_iss_message(lat, lon, timestamp, address) – builds readable message
#post_message(room_id, text, access_token) – posts to Webex
#monitor_room(room_id, access_token, maps_api_key) – main loop

import requests
import json
import time
from iso3166 import countries


def get_access_token():
    choice = input("Do you wish to use the hard-coded Webex token? (y/n) ")
    if choice.lower() == 'n':
        user_token = input("Please enter your Webex access token: ")
        return f"Bearer {user_token.strip()}"
    else:
        return "Bearer YmU3NjUyNDYtYWNmMi00NzdhLWE1OGQtOWNkZGQwMmJjM2IwMWJlOTk5YjgtMTQ3_P0A1_636b97a0-b0af-4297-b0e7-480dd517b3f9"


def get_rooms(access_token):
    r = requests.get("https://webexapis.com/v1/rooms", headers={"Authorization": access_token})
    if r.status_code != 200:
        raise Exception(f"Incorrect reply from Webex API. Status code: {r.status_code}. Text: {r.text}")

    rooms = r.json()["items"]
    print("\nList of available rooms:")
    for room in rooms:
        print(f"Room Type: {room['type']} | Title: {room['title']}")
    return rooms


def select_room(rooms):
    while True:
        room_name = input("\nWhich room should be monitored for the /seconds messages? ")
        for room in rooms:
            if room_name.lower() in room["title"].lower():
                print(f"Found room: {room['title']}")
                return room["id"], room["title"]
        print("No room found. Please try again.")


def get_latest_message(room_id, access_token):
    params = {"roomId": room_id, "max": 1}
    try:
        r = requests.get("https://webexapis.com/v1/messages", params=params, headers={"Authorization": access_token}, timeout=5)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages: {e}")
        return None

    items = r.json().get("items", [])
    if not items:
        return None
    return items[0]["text"]


def get_iss_location():
    try:
        r = requests.get("http://api.open-notify.org/iss-now.json", timeout=5)
        r.raise_for_status()
        data = r.json()
        if data.get("message") != "success":
            return None
        return {
            "lat": data["iss_position"]["latitude"],
            "lon": data["iss_position"]["longitude"],
            "timestamp": data["timestamp"]
        }
    except requests.exceptions.RequestException as e:
        print(f"Error getting ISS data: {e}")
        return None


def reverse_geocode(lat, lon, api_key):
    params = {"pk.1af4b5d6f1cf9d29dfdfc6ab5c545fe5": api_key, "lat": lat, "lon": lon, "format": "json"}
    try:
        r = requests.get("https://us1.locationiq.com/v1/reverse.php", params=params, timeout=5)
        r.raise_for_status()
        return r.json().get("address", {})
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Reverse geocode error: {e}")
        return {}


def format_iss_message(lat, lon, timestamp, address):
    time_str = time.ctime(timestamp)
    country_code = address.get("country_code", "XZ").upper()
    state = address.get("state", "Unknown")
    city = address.get("city", address.get("town", "Unknown"))

    try:
        country_name = countries.get(country_code).name
    except KeyError:
        country_name = country_code

    if country_code == "XZ":
        return f"On {time_str}, the ISS was flying over a body of water at latitude {lat}° and longitude {lon}°."
    elif city != "Unknown":
        return (f"In {city}, {state}, the ISS was flying over on {time_str}.\n"
                f"Coordinates: ({lat}°, {lon}°)\nCountry: {country_name}")
    else:
        return f"On {time_str}, the ISS was flying over {state}, {country_name} at coordinates ({lat}°, {lon}°)."


def post_message(room_id, text, access_token):
    headers = {"Authorization": access_token, "Content-Type": "application/json"}
    data = {"roomId": room_id, "text": text}
    try:
        r = requests.post("https://webexapis.com/v1/messages", json=data, headers=headers, timeout=5)
        if r.status_code == 200:
            print("Message successfully posted to Webex.")
        else:
            print(f"Failed to post message: {r.status_code} {r.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Webex: {e}")


def monitor_room(room_id, access_token, maps_api_key):
    print("\nMonitoring room for /<seconds> messages...\n")
    last_message = None

    while True:
        time.sleep(1)
        message = get_latest_message(room_id, access_token)
        if not message or message == last_message:
            continue
        last_message = message

        print(f"Latest message: {message}")

        if not message.startswith("/"):
            continue

        command = message[1:]
        if not command.isdigit():
            print("Invalid command. Use /<number> (e.g. /5).")
            continue

        seconds = min(int(command), 5)
        print(f"Waiting {seconds} seconds before fetching ISS data...")
        time.sleep(seconds)

        iss = get_iss_location()
        if not iss:
            print("Error getting ISS location.")
            continue

        address = reverse_geocode(iss["lat"], iss["lon"], maps_api_key)
        if not address:
            print("Error reverse geocoding coordinates.")
            continue

        msg = format_iss_message(iss["lat"], iss["lon"], iss["timestamp"], address)
        print(f"Sending message: {msg}")
        post_message(room_id, msg, access_token)


def main():
    access_token = get_access_token()
    rooms = get_rooms(access_token)
    room_id, room_title = select_room(rooms)
    maps_api_key = input("Enter your LocationIQ API key: ")
    monitor_room(room_id, access_token, maps_api_key)


if __name__ == "__main__":
    main()

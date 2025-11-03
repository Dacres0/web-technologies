import requests
import json
import time
from iso3166 import countries


choice = input("Do you wish to use the hard-coded Webex token? (y/n) ")

if choice.lower() == 'n':
    user_token = input("Please enter your Webex access token: ")
    accessToken = f"Bearer {user_token}"
else:
    accessToken = "Bearer MGVmNDVhNzktODJkYi00OTZkLWJiYTEtOGJlYTk1YTI5NjZkOTYxMGYyM2UtMDU2_P0A1_636b97a0-b0af-4297-b0e7-480dd517b3f9"

r = requests.get("https://webexapis.com/v1/rooms", headers={"Authorization": accessToken})

if r.status_code != 200:
    raise Exception(f"Incorrect reply from Webex API. Status code: {r.status_code}. Text: {r.text}")

print("\nList of available rooms:")
rooms = r.json()["items"]
for room in rooms:
    print(f"Room Type: {room['type']} | Title: {room['title']}")

while True:
    roomNameToSearch = input("Which room should be monitored for the /seconds messages? ")
    roomIdToGetMessages = None
    roomTitleToGetMessages = None

    for room in rooms:
        if room["title"].find(roomNameToSearch) != -1:
            print(f"Found room with the word {roomNameToSearch}")
            print(room["title"])
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print(f"Found room: {roomTitleToGetMessages}")
            break

    if roomIdToGetMessages is None:
        print(f"Sorry, I didn't find any room with {roomNameToSearch} in it.")
        print("Please try again...")
    else:
        break


while True:
    time.sleep(1)
    GetParameters = {"roomId": roomIdToGetMessages, "max": 1}

    r = requests.get("https://webexapis.com/v1/messages",
                     params=GetParameters,
                     headers={"Authorization": accessToken})

    if r.status_code != 200:
        raise Exception(f"Incorrect reply from Webex API. Status code: {r.status_code}. Text: {r.text}")

    json_data = r.json()

    if len(json_data["items"]) == 0:
        print("No messages found in this room yet. Waiting for a new message...")
        continue

    messages = json_data["items"]
    message = messages[0]["text"]
    print(f"Latest message received: {message}")

    if message.startswith("/"):
        if message[1:].isdigit():
            seconds = int(message[1:])
        else:
            print("Invalid command format. Please enter /<number> (e.g. /5).")
            continue

        if seconds > 5:
            seconds = 5

        time.sleep(seconds)

        r = requests.get("http://api.open-notify.org/iss-now.json")
        json_data = r.json()

        if r.status_code != 200 or json_data.get("message") != "success":
            print("Error retrieving ISS location data.")
            continue

        lat = json_data["iss_position"]["latitude"]
        lng = json_data["iss_position"]["longitude"]
        timestamp = json_data["timestamp"]
        timeString = time.ctime(timestamp)

       
        mapsAPIGetParameters = {
            "key": "MGVmNDVhNzktODJkYi00OTZkLWJiYTEtOGJlYTk1YTI5NjZkOTYxMGYyM2UtMDU2_P0A1_636b97a0-b0af-4297-b0e7-480dd517b3f9",
            "lat": lat,
            "lon": lng,
            "format": "json"
        }

        r = requests.get("https://us1.locationiq.com/v1/reverse.php", params=mapsAPIGetParameters)
        json_data = r.json()

        if r.status_code != 200 or "address" not in json_data:
            print("Error retrieving reverse geocode data.")
            continue

        address = json_data["address"]
        CountryResult = address.get("country_code", "XZ").upper()
        StateResult = address.get("state", "Unknown")
        CityResult = address.get("city", address.get("town", "Unknown"))
        StreetResult = address.get("road", "Unknown")

        if CountryResult != "XZ":
            try:
                CountryResult = countries.get(CountryResult).name
            except KeyError:
                pass

        
        if CountryResult == "XZ":
            responseMessage = (
                f"On {timeString}, the ISS was flying over a body of water "
                f"at latitude {lat}° and longitude {lng}°."
            )
        elif CityResult != "Unknown":
            responseMessage = (
                f"In {CityResult}, {StateResult}, the ISS was flying over on {timeString}.\n"
                f"Coordinates: ({lat}°, {lng}°)\nCountry: {CountryResult}"
            )
        else:
            responseMessage = (
                f"On {timeString}, the ISS was flying over {StateResult}, {CountryResult} "
                f"at coordinates ({lat}°, {lng}°)."
            )

        print("Sending to Webex: " + responseMessage)

       
        HTTPHeaders = {
            "Authorization": accessToken,
            "Content-Type": "application/json"
        }

        PostData = {
            "roomId": roomIdToGetMessages,
            "text": responseMessage
        }

        r = requests.post("https://webexapis.com/v1/messages",
                          data=json.dumps(PostData),
                          headers=HTTPHeaders)

        if r.status_code != 200:
            print(f"Failed to post message to Webex. Status code: {r.status_code}, Text: {r.text}")
        else:
            print("Message successfully posted to Webex.")




















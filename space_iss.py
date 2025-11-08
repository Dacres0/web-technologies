import requests
import json
import time
from iso3166 import countries


choice = input("Do you wish to use the hard-coded Webex token? (y/n) ")

if choice.lower() == 'n':
    user_token = input("Please enter your Webex access token: ")
    accessToken = f"Bearer {user_token}"
else:
    accessToken = "Bearer MzhiM2Y2N2EtNDhjNC00NDk3LTgwYjktNjg2YjIyMTQyZWE4ZjY0Mzg2YzUtMzQ2_P0A1_636b97a0-b0af-4297-b0e7-480dd517b3f9"


r = requests.get("https://webexapis.com/v1/rooms", headers={"Authorization": accessToken})
if r.status_code != 200:
    raise Exception(f"Incorrect reply from Webex API. Status code: {r.status_code}. Text: {r.text}")

print("\nList of available rooms:")
rooms = r.json()["items"]
for room in rooms:
    print(f"Room Type: {room['type']} | Title: {room['title']}")


while True:
    roomNameToSearch = input("\nWhich room should be monitored for the /seconds messages? ")
    roomIdToGetMessages = None
    roomTitleToGetMessages = None

    for room in rooms:
        if roomNameToSearch.lower() in room["title"].lower():
            print(f"Found room: {room['title']}")
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            break

    if roomIdToGetMessages:
        print(f"Monitoring room: {roomTitleToGetMessages}")
        break
    else:
        print(f"No room found containing '{roomNameToSearch}'. Try again.\n")


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
        continue

    message = json_data["items"][0]["text"]
    print(f"Latest message received: {message}")

    
    if message.startswith("/"):
        if message[1:].isdigit():
            seconds = int(message[1:])
        else:
            print("Invalid format. Use /<number> (for example, /5).")
            continue

        
        if seconds > 5:
            seconds = 5

        time.sleep(seconds)

        
        print("Fetching ISS location...")
        r = requests.get("http://api.open-notify.org/iss-now.json", timeout=5)
        if r.status_code != 200:
            print("Error retrieving ISS data.")
            continue

        json_data = r.json()
        if json_data.get("message") != "success":
            print("ISS API did not return success.")
            continue

        lat = json_data["iss_position"]["latitude"]
        lng = json_data["iss_position"]["longitude"]
        timestamp = json_data["timestamp"]
        timeString = time.ctime(timestamp)

        
        mapsAPIGetParameters = {
            "key": "pk.1af4b5d6f1cf9d29dfdfc6ab5c545fe5",  # Your LocationIQ key
            "lat": lat,
            "lon": lng,
            "format": "json"
        }

        try:
            r = requests.get("https://us1.locationiq.com/v1/reverse", params=mapsAPIGetParameters, timeout=10)
#didn't know what was wrong so was looking online what may be problem, they said i should input a debug code to check whats the problem, after this i solved the problem
            print(f"[DEBUG] Reverse geocode URL: {r.url}")
            print(f"[DEBUG] Status Code: {r.status_code}")
            print(f"[DEBUG] Response Text (first 500 chars): {r.text[:500]}")

            
            if r.status_code == 404 or "Unable to geocode" in r.text:
                print("The ISS is currently over the ocean or an uninhabited area.")
                CountryResult = "XZ"
                CityResult = "Unknown"
                StateResult = "Unknown"
            elif r.status_code != 200:
                print(f"Reverse geocode failed. HTTP {r.status_code}")
                continue
            else:
                json_data = r.json()
                address = json_data.get("address", {})

                CountryResult = address.get("country_code", "XZ").upper()
                StateResult = address.get("state", "Unknown")
                CityResult = address.get("city", address.get("town", "Unknown"))
                StreetResult = address.get("road", "Unknown")

                if CountryResult != "XZ":
                    try:
                        CountryResult = countries.get(CountryResult).name
                    except KeyError:
                        pass

        except Exception as e:
            print(f"Error while getting reverse geocode: {e}")
            continue

        
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

        print("Sending to Webex:", responseMessage)

        
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
            print(f"Failed to post message. Status: {r.status_code}, Text: {r.text}")
        else:
            print("Message successfully posted to Webex.\n")















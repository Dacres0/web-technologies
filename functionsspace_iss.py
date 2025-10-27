#get_access_token() – handles token input
#get_rooms(access_token) – fetches available Webex rooms
#select_room(rooms) – lets the user pick which room to monitor
#get_latest_message(room_id, access_token) – polls latest message
#get_iss_location() – fetches current ISS position
#reverse_geocode(lat, lon, api_key) – gets address from coordinates
#format_iss_message(lat, lon, timestamp, address) – builds readable message
#post_message(room_id, text, access_token) – posts to Webex
#monitor_room(room_id, access_token, maps_api_key) – main loop

def get_access_token():
    choice = input("Do you wish to use the hard-coded Webex token? (y/n) ")
    if choice.lower() == 'n':
        user_token = input("Please enter your Webex access token: ")
        return f"Bearer {user_token}"
    else:
        return "Bearer "

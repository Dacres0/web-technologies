# 🚀 Space Bot API Investigation Sheet
**Total Marks: 30**
**Part 1: Collect Required API Documentation**
This investigation sheet helps you gather key technical information from the three
APIs required for the Space Bot project: **Webex Messaging API**, **ISS Current
Location API**, and a **Geocoding API** (LocationIQ or Mapbox or other), plus the
Python time module.
---
## Section 1: Webex Messaging API (7 marks)✅
| Criteria | Details |
|---------|---------|
| API Base URL | `[ https://webexapis.com/v1 ]` |
| Authentication Method | `Bearer Token (OAuth 2.0)` |
| Endpoint to list rooms | `/rooms` |
| Endpoint to get messages | `/messages` |
| Endpoint to send message | `/messages` |
| Required headers | `Authorization: Bearer <your_token>
| Sample full GET or POST request | `[] |
---
## Section 2: ISS Current Location API (3 marks)
| Criteria | Details |
|---------|---------|
| API Base URL | `[ http://api.open-notify.org ]` |
| Endpoint for current ISS location | `/iss-now.json` |
| Sample response format (example JSON) | ```json |
```
```
|
---
## Section 3: Geocoding API (LocationIQ or Mapbox or other) (6 marks)
| Criteria | Details |
|---------|---------|
| Provider used (circle one) | **LocationIQ / Mapbox/ other -provide detail** |
| API Base URL | `https://us1.locationiq.com/v1` |
| Endpoint for reverse geocoding | `/reverse.php` |
| Authentication method | `API Key (App Token)` |
| Required query parameters | `key (Your API key), lat, lon, format=json` |
| Sample request with latitude/longitude | `(https://us1.locationiq.com/v1/reverse.php?key=YOUR_API_KEY&lat=51.5034&lon=-0.1276&format=json)_` |
| Sample JSON response (formatted example) | ```json
```
```
|
---
## 🚀 Section 4: Epoch to Human Time Conversion (Python time module) (2 marks)
| Criteria | Details |
|---------|---------|
| Library used | `time` |
| Function used to convert epoch | `time.ctime() time.gmtime()` |
| Sample code to convert timestamp | ```python import time
```
```
|
| Output (human-readable time) | ``Mon Mar 21 09:21:12 2024` |
*changes with the date and time
---
## 🚀 Section 5: Web Architecture & MVC Design Pattern (12 marks)
### 🚀 Web Architecture – Client-Server Model
- **Client**: The user interface or application that sends requests (e.g., Space Bot on Webex)
- **Server**: Hosts the APIs (Webex API, ISS API, LocationIQ API). It processes incoming requests and returns data (JSON responses)
- (Explain the communication between them & include a block diagram )
### 🚀 RESTful API Usage
- APIs use **HTTP methods** (GET, POST) to exchange data
- Each API endpoint represents a **resource** (e.g., /messages or /iss-now.json)
- Authentication (e.g., Bearer Token or API Key)
### 🚀 MVC Pattern in Space Bot
| Component | Description |
|------------|-------------|
| **Model** | | Handles the data and API interactions. For example, Python functions that call the ISS API and LocationIQ API to retrieve or process data
| **View** | | The presentation layer – Webex messages or cards displayed to the user
| **Controller** | |  The logic layer – decides what data to fetch and what message to send based on user commands
#### Example:
- Model: Python functions `get_iss_location()` and `get_place_name(lat, lon)`
- View: Formatted Webex message showing location and time
- Controller: `spacebot.py` interprets user commands (“Where is the ISS?”) and triggers API calls
---
### 🚀 Notes
- Use official documentation for accuracy (e.g. developer.webex.com, locationiq.com
or Mapbox, open-notify.org or other ISS API).
- Be prepared to explain your findings to your instructor or demo how you retrieved
them using tools like Postman, Curl, or Python scripts.
---
### Total: /30

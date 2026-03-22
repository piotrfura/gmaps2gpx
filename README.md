# Google Maps to GPX Converter

This script takes a full Google Maps Directions URL (not a shortened link) and uses the Google Routes API to convert the route into a standard GPX file (`route.gpx`) that can be imported to GPS devices.

## Requirements

1. Python 3.x
2. A valid [Google Maps API Key](https://developers.google.com/maps/documentation/routes/cloud-setup) with the **Routes API** enabled.

## Setup

1. Install the required Python dependencies. You can do this by using the existing project package files, or installing directly via pip:
   ```bash
   pip install httpx polyline python-dotenv
   ```
2. Create a `.env` file in the root directory (or copy an example if provided) and add your API key:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Usage

Simply run the script via Python and pass your full Google Maps Directions URL as an argument inside double quotes.

**Example Command:**

```bash
python main.py "https://www.google.com/maps/dir/Warszawa/Krak%C3%B3w/@51.1397103,19.1959062,8z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x471ecc669a869f01:0x72f0be2a88ead3fc!2m2!1d21.0122287!2d52.2296756!1m5!1m1!1s0x471644c0354e18d1:0xb46bb6b576478abf!2m2!1d19.9449799!2d50.0646501!3e0!5m1!1e4?entry=ttu&g_ep=EgoyMDI2MDMxOC4xIKXMDSoASAFQAw%3D%3D"
```

The script will fetch the route directions and create a file named `route.gpx` in the same folder.

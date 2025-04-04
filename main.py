import time
import datetime
import pytz
import serial
from flask import Flask, jsonify, render_template_string
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_utc_to_est(utc_time_str):
    try:
        # Parse the UTC time string into a datetime object
        utc_time = datetime.datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Define the UTC and EST timezones
        utc_zone = pytz.utc
        est_zone = pytz.timezone('US/Eastern')
        
        # Localize the UTC time to the UTC timezone
        utc_time = utc_zone.localize(utc_time)
        
        # Convert the UTC time to EST
        est_time = utc_time.astimezone(est_zone)
        
        return est_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logging.error(f"Error converting UTC to EST: {e}")
        return None

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EST Time Display</title>
            <script>
                async function updateTime() {
                    const response = await fetch('/gps-time');
                    const data = await response.json();
                    document.getElementById('est-time').innerText = data['EST Time'];
                }
                setInterval(updateTime, 1000); // Update every second
                window.onload = updateTime;
            </script>
        </head>
        <body>
            <h1>Current EST Time</h1>
            <p id="est-time">Loading...</p>
        </body>
        </html>
    ''')

@app.route('/gps-time', methods=['GET'])
def get_gps_time():
    try:
        # Open the serial port
        with serial.Serial('COM6', baudrate=9600, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='replace')
                if line.startswith('$GPRMC'):
                    # Parse the NMEA sentence to extract UTC time
                    parts = line.split(',')
                    if parts[9]:  # Date field
                        utc_date = parts[9]
                        utc_time = parts[1]
                        utc_time_str = f"20{utc_date[4:6]}-{utc_date[2:4]}-{utc_date[0:2]}T{utc_time[0:2]}:{utc_time[2:4]}:{utc_time[4:6]}.000Z"
                        est_time = convert_utc_to_est(utc_time_str)
                        if est_time:
                            return jsonify({"UTC Time": utc_time_str, "EST Time": est_time})
                time.sleep(1)
    except Exception as e:
        logging.error(f"Error retrieving GPS time: {e}")
        return jsonify({"error": "Failed to retrieve GPS time"}), 500

def main():
    # Run the Flask server on the local network
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()

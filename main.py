import time
import datetime
import pytz
import gps3
from gps3 import gps3
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

def convert_utc_to_est(utc_time_str):
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
    # Create a GPS socket
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()

    # Connect to the GPSD
    gps_socket.connect()
    gps_socket.watch()

    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            utc_time = data_stream.TPV['time']
            if utc_time:
                est_time = convert_utc_to_est(utc_time)
                return jsonify({"UTC Time": utc_time, "EST Time": est_time})
        time.sleep(1)

def main():
    # Run the Flask server on the local network
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()

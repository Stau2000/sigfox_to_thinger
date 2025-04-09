from flask import Flask, request
import struct
import requests
import os

app = Flask(__name__)

@app.route('/sigfox', methods=['POST'])
def sigfox_callback():
    data = request.json
    payload_hex = data.get("data", "")

    if len(payload_hex) != 24:
        return {"error": "Invalid payload"}, 400

    payload = bytes.fromhex(payload_hex)

    sound = int.from_bytes(payload[0:2], "big")
    temp_raw = int.from_bytes(payload[2:4], "big", signed=True)
    air = int.from_bytes(payload[4:6], "big")
    lat_raw = int.from_bytes(payload[6:9], "big", signed=True)
    lon_raw = int.from_bytes(payload[9:12], "big", signed=True)

    # Skalering
    tempC = temp_raw / 100.0
    lat = lat_raw / 10000.0
    lon = lon_raw / 10000.0

    # Send til Thinger.io
    json_payload = {
        "sound": sound,
        "temperature": tempC,
        "air_quality": air,
        "latitude": lat,
        "longitude": lon
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('THINGER_TOKEN')}"
    }

    res = requests.post(
        f"https://backend.thinger.io/v3/users/{os.getenv('THINGER_USERNAME')}/devices/{os.getenv('THINGER_DEVICE')}/callback/data",
        headers=headers,
        json=json_payload
    )

    return {"status": "ok", "thinger_response": res.status_code}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
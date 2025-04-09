from flask import Flask, request
import struct

app = Flask(__name__)

@app.route('/sigfox', methods=['POST'])
def sigfox_callback():
    data = request.json
    payload_hex = data.get("data", "")

    print("🔔 Modtog Sigfox POST:")
    print(data)

    if len(payload_hex) != 24:
        print("❌ Forkert payload-længde:", payload_hex)
        return {"error": "Invalid payload"}, 400

    try:
        payload = bytes.fromhex(payload_hex)

        sound = int.from_bytes(payload[0:2], "big")
        temp_raw = int.from_bytes(payload[2:4], "big", signed=True)
        air = int.from_bytes(payload[4:6], "big")
        lat_raw = int.from_bytes(payload[6:9], "big", signed=True)
        lon_raw = int.from_bytes(payload[9:12], "big", signed=True)

        tempC = temp_raw / 100.0
        lat = lat_raw / 10000.0
        lon = lon_raw / 10000.0

        print("✅ Dekodet data:")
        print({
            "sound": sound,
            "temperature": tempC,
            "air_quality": air,
            "latitude": lat,
            "longitude": lon
        })

        return {"status": "ok"}

    except Exception as e:
        print("⚠️ Fejl ved dekodning:", str(e))
        return {"error": "Internal error"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
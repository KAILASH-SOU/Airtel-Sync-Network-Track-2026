import http.server
import socketserver
import json
import urllib.parse
import os
import sys

from telemetry_sim import StadiumTelemetryEngine
from ml_engine import StadiumMLEngine
from ric_controller import ORANNearRTRICController

telemetry_engine = StadiumTelemetryEngine()
ml_engine = StadiumMLEngine()
ric_controller = ORANNearRTRICController()

class StadiumRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_file(self, filename, content_type="text/html"):
        if not os.path.exists(filename):
            self.send_error(404, "File not found")
            return
        with open(filename, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in ["/", "/index.html", "/stadium_twin.html", "/app"]:
            self._send_file("stadium_twin.html", "text/html")
            return

        if path == "/api/simulate":
            attendance = int(query.get("attendance", [100000])[0])
            phase = query.get("phase", ["21:00"])[0]
            capex = query.get("capex", ["true"])[0].lower() == "true"
            sig = query.get("sig", ["true"])[0].lower() == "true"
            qos = query.get("qos", ["true"])[0].lower() == "true"

            ric_controller.configure_xapps(capex, sig, qos)
            res = telemetry_engine.simulate_stadium(attendance, phase, capex, sig, qos)
            self._send_json(res)
            return

        if path == "/api/dimensioning":
            attendance = int(query.get("attendance", [100000])[0])
            res = telemetry_engine.calculate_dimensioning(attendance)
            self._send_json(res)
            return

        if path == "/api/dbscan":
            num_users = int(query.get("users", [7200])[0])
            phase = query.get("phase", ["21:00"])[0]
            coords = ml_engine.generate_user_coordinates(num_users, phase)
            coords, hotspots = ml_engine.cluster_hotspots_dbscan(coords)
            self._send_json({"clusters": hotspots, "sample_coords": coords[:200]})
            return

        if path == "/api/forecast":
            phase = query.get("phase", ["21:00"])[0]
            forecast = ml_engine.forecast_surge_15min_ahead(phase)
            self._send_json(forecast)
            return

        if path == "/api/emergency_call":
            trace = ric_controller.simulate_emergency_call()
            self._send_json({"success": True, "trace": trace})
            return

        if path == "/api/logs":
            self._send_json(ric_controller.event_log)
            return

        self.send_error(404, "Endpoint not found")

    def log_message(self, format, *args):

        pass

def start_server(port=8501):

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), StadiumRequestHandler) as httpd:
            print("=" * 70)
            print("AIRTEL SYNC: STADIUM SURGE DIGITAL TWIN & O-RAN NEAR-RT RIC PROTOTYPE")
            print("=" * 70)
            print(f"Server running at:  http://localhost:{port}/")
            print(f"Open in browser:    file://{os.path.abspath('stadium_twin.html')}")
            print("=" * 70)
            print("Press Ctrl+C to terminate.")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            alt_port = port + 1
            print(f"Port {port} busy, attempting port {alt_port}...")
            start_server(alt_port)
        else:
            raise e

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
    start_server(port)

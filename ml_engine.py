import math
import random

class StadiumMLEngine:
    def __init__(self, random_seed=42):
        self.random_seed = random_seed
        self._try_init_sklearn()

    def _try_init_sklearn(self):
        self.has_sklearn = False
        try:
            from sklearn.cluster import DBSCAN
            import numpy as np
            self.DBSCAN = DBSCAN
            self.np = np
            self.has_sklearn = True
        except Exception:
            self.has_sklearn = False

    def generate_user_coordinates(self, num_users=7200, match_phase="21:00"):
        random.seed(self.random_seed + hash(match_phase) % 1000)
        coords = []

        if match_phase == "17:00":
            w_bowl = 0.35
            w_concourse = 0.25
            w_perimeter = 0.40
        elif match_phase == "21:00":
            w_bowl = 0.30
            w_concourse = 0.60
            w_perimeter = 0.10
        elif match_phase == "22:45":
            w_bowl = 0.85
            w_concourse = 0.10
            w_perimeter = 0.05
        else:
            w_bowl = 0.20
            w_concourse = 0.30
            w_perimeter = 0.50

        n_bowl = int(num_users * w_bowl)
        n_concourse = int(num_users * w_concourse)
        n_perimeter = num_users - n_bowl - n_concourse

        for _ in range(n_bowl):
            r = random.uniform(25, 90)
            theta = random.uniform(0, 2 * math.pi)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            coords.append({"x": round(x, 1), "y": round(y, 1), "zone": "Bowl", "r": r, "theta": theta})

        food_court_angles = [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]
        for _ in range(n_concourse):
            base_angle = random.choice(food_court_angles)
            theta = base_angle + random.gauss(0, 0.22)
            r = random.gauss(145, 12)
            r = max(115, min(175, r))
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            coords.append({"x": round(x, 1), "y": round(y, 1), "zone": "Concourse", "r": r, "theta": theta})

        gate_angles = [0, math.pi/2, math.pi, 3*math.pi/2]
        for _ in range(n_perimeter):
            base_angle = random.choice(gate_angles)
            theta = base_angle + random.gauss(0, 0.28)
            r = random.uniform(260, 420)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            coords.append({"x": round(x, 1), "y": round(y, 1), "zone": "Perimeter", "r": r, "theta": theta})

        return coords

    def cluster_hotspots_dbscan(self, coords, eps=25.0, min_samples=35):
        pts = [(c["x"], c["y"]) for c in coords]
        labels = []

        if self.has_sklearn:
            try:
                X = self.np.array(pts)
                db = self.DBSCAN(eps=eps, min_samples=min_samples).fit(X)
                labels = db.labels_.tolist()
            except Exception:
                labels = self._pure_python_dbscan(pts, eps, min_samples)
        else:
            labels = self._pure_python_dbscan(pts, eps, min_samples)

        clusters = {}
        for idx, (lbl, pt, item) in enumerate(zip(labels, pts, coords)):
            item["cluster_id"] = lbl
            if lbl == -1:
                continue
            if lbl not in clusters:
                clusters[lbl] = {"id": lbl, "points": [], "zone": item["zone"]}
            clusters[lbl]["points"].append(pt)

        hotspot_summary = []
        for cid, data in clusters.items():
            pts_in_c = data["points"]
            count = len(pts_in_c)
            avg_x = sum(p[0] for p in pts_in_c) / count
            avg_y = sum(p[1] for p in pts_in_c) / count
            r = math.sqrt(avg_x**2 + avg_y**2)
            angle_deg = math.degrees(math.atan2(avg_y, avg_x)) % 360

            rec_downtilt = 30.0 if r < 100 else (15.0 if r < 200 else 8.0)

            hotspot_summary.append({
                "cluster_id": cid,
                "user_count": count,
                "center_x": round(avg_x, 1),
                "center_y": round(avg_y, 1),
                "center_radius_m": round(r, 1),
                "center_angle_deg": round(angle_deg, 1),
                "zone": data["zone"],
                "recommended_downtilt_deg": rec_downtilt,
                "recommended_beamwidth_deg": 30.0
            })

        hotspot_summary.sort(key=lambda h: h["user_count"], reverse=True)
        return coords, hotspot_summary

    def _pure_python_dbscan(self, points, eps, min_samples):
        cell_size = eps
        grid = {}
        for i, (x, y) in enumerate(points):
            gx = int(x // cell_size)
            gy = int(y // cell_size)
            key = (gx, gy)
            if key not in grid:
                grid[key] = []
            grid[key].append(i)

        def get_neighbors(i):
            x, y = points[i]
            gx = int(x // cell_size)
            gy = int(y // cell_size)
            neighbors = []
            eps_sq = eps * eps
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    neighbor_cell = grid.get((gx + dx, gy + dy), [])
                    for j in neighbor_cell:
                        nx, ny = points[j]
                        dist_sq = (x - nx)**2 + (y - ny)**2
                        if dist_sq <= eps_sq:
                            neighbors.append(j)
            return neighbors

        labels = [None] * len(points)
        cluster_id = 0

        for i in range(len(points)):
            if labels[i] is not None:
                continue
            neighbors = get_neighbors(i)
            if len(neighbors) < min_samples:
                labels[i] = -1
                continue

            labels[i] = cluster_id
            queue = [idx for idx in neighbors if idx != i]
            while queue:
                q_idx = queue.pop()
                if labels[q_idx] == -1:
                    labels[q_idx] = cluster_id
                if labels[q_idx] is not None:
                    continue
                labels[q_idx] = cluster_id
                q_neighbors = get_neighbors(q_idx)
                if len(q_neighbors) >= min_samples:
                    queue.extend(q_neighbors)
            cluster_id += 1

        return [lbl if lbl is not None else -1 for lbl in labels]

    def forecast_surge_15min_ahead(self, match_time="21:00", current_prb=76.0):
        predictions = {
            "17:00": {
                "next_event": "Innings Start (17:30)",
                "concourse_surge_risk": "Low (Fans moving to seats)",
                "predicted_bowl_prb_delta": "+18.5%",
                "predicted_concourse_prb_delta": "-12.0%",
                "ric_action": "Tilt macro beams outward to plaza; prepare bowl small cells"
            },
            "21:00": {
                "next_event": "2nd Innings Resumption (21:30)",
                "concourse_surge_risk": "CRITICAL (Massive food & UPI rush)",
                "predicted_bowl_prb_delta": "-15.0%",
                "predicted_concourse_prb_delta": "+38.4%",
                "ric_action": "Pre-allocate Concourse Small Cell PRBs & activate QCI 6 UPI slice"
            },
            "22:45": {
                "next_event": "Final Over & Trophy Presentation (23:00)",
                "concourse_surge_risk": "Low",
                "predicted_bowl_prb_delta": "+42.0% (Uplink video flood)",
                "predicted_concourse_prb_delta": "-8.0%",
                "ric_action": "Switch TDD slot format from 8:2 to 6:4 to prevent TCP ACK starvation"
            },
            "23:15": {
                "next_event": "Venue Egress & Station Transit (23:45)",
                "concourse_surge_risk": "Moderate (Plaza exits)",
                "predicted_bowl_prb_delta": "-35.0%",
                "predicted_concourse_prb_delta": "+28.0% (Gates)",
                "ric_action": "Power up CoW perimeter sectors; re-route egress traffic to outer macros"
            }
        }
        return predictions.get(match_time, predictions["21:00"])

if __name__ == "__main__":
    ml = StadiumMLEngine()
    print("Testing ML Engine...")
    coords = ml.generate_user_coordinates(7200, "21:00")
    print(f"Generated {len(coords)} user coordinates.")
    coords, hotspots = ml.cluster_hotspots_dbscan(coords, eps=30.0, min_samples=30)
    print(f"Detected {len(hotspots)} spatial hotspot clusters.")
    for h in hotspots[:3]:
        print(f"Cluster {h['cluster_id']} in {h['zone']}: {h['user_count']} users at {h['center_radius_m']}m, rec downtilt {h['recommended_downtilt_deg']}°")
    forecast = ml.forecast_surge_15min_ahead("21:00")
    print("15-min Forecast for 21:00:", forecast)

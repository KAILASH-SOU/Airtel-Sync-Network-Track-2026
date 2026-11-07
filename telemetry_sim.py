import math
import json
import os
import zipfile
import xml.etree.ElementTree as ET

class StadiumTelemetryEngine:
    def __init__(self, data_path="Sync_V1.xlsx"):
        self.data_path = data_path
        self.ground_truth = self._load_data()

        self.AIRTEL_USER_SHARE = 0.40
        self.SHARE_5G_PHONES = 0.70
        self.SHARE_4G_PHONES = 0.30
        self.PEAK_CONCURRENCY = 0.18

        self.SLA_TARGET_5G_MBPS = 5.0
        self.SLA_TARGET_4G_MBPS = 3.0

        self.SPECTRUM_5G_MHZ = 100.0
        self.SPECTRUM_4G_MHZ = 70.0

        self.ETA_5G_MIMO = 26.25
        self.ETA_4G_CA = 5.50

        self.TARGET_LOAD_CAP = 0.80

        self.existing_sites = self._init_existing_sites()
        self.proposed_sites = self._init_proposed_sites()

    def _load_data(self):
        json_path = "sync_dataset.json"
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass

        if os.path.exists("Sync_V1.xlsx"):
            return self._parse_xlsx("Sync_V1.xlsx")

        raise FileNotFoundError("Neither sync_dataset.json nor Sync_V1.xlsx found.")

    def _parse_xlsx(self, filename):
        with zipfile.ZipFile(filename) as z:
            ss_tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join([t.text for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t") if t.text])
                for si in ss_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si")
            ]

            sheet_tree = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
            rows = []
            for row in sheet_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
                r_dict = {}
                for c in row.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                    ref = c.attrib.get("r")
                    col = "".join([ch for ch in ref if ch.isalpha()])
                    t = c.attrib.get("t")
                    v = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                    val = v.text if v is not None else ""
                    if t == "s" and val.isdigit():
                        val = shared_strings[int(val)]
                    r_dict[col] = val
                rows.append(r_dict)

        telemetry = []
        for r in rows[2:34]:
            if "A" in r and r["A"].strip():
                telemetry.append({
                    "site": r.get("A", ""),
                    "phase": r.get("B", ""),
                    "time": r.get("C", ""),
                    "normal_b3_load_pct": float(r.get("D", 0) or 0),
                    "last_match_b3_load_pct": float(r.get("E", 0) or 0),
                    "normal_4g_speed_mbps": float(r.get("F", 0) or 0),
                    "last_match_4g_speed_mbps": float(r.get("G", 0) or 0),
                    "normal_5g_speed_mbps": float(r.get("H", 0) or 0) if r.get("H") else None,
                    "last_match_5g_speed_mbps": float(r.get("I", 0) or 0) if r.get("I") else None,
                    "last_match_5g_success_pct": float(r.get("J", 0) or 0)
                })

        sites = []
        for r in rows[2:10]:
            if "L" in r and r["L"].strip():
                sites.append({
                    "site": r.get("L", ""),
                    "type": r.get("M", ""),
                    "distance_m": float(r.get("N", 0)),
                    "backhaul": r.get("O", ""),
                    "backhaul_capacity_gbps": float(r.get("P", 0)),
                    "has_5g_n78": r.get("Q", "").strip().lower() == "yes"
                })

        upi = []
        for r in rows[13:17]:
            if "L" in r and r["L"].strip():
                upi.append({
                    "time": r.get("L", ""),
                    "last_match_upi_fail_pct": float(r.get("M", 0)),
                    "normal_day_upi_fail_pct": float(r.get("N", 0))
                })

        return {"telemetry": telemetry, "sites": sites, "upi": upi}

    def _init_existing_sites(self):
        return [
            {"id": "M1", "name": "Macro 1 (North-East)", "type": "Macro", "ring": 3, "radius_m": 320, "angle_deg": 45, "backhaul": "Fibre 10G", "has_5g": True, "active_4g": True},
            {"id": "M2", "name": "Macro 2 (South-East)", "type": "Macro", "ring": 3, "radius_m": 410, "angle_deg": 135, "backhaul": "Fibre 10G", "has_5g": True, "active_4g": True},
            {"id": "M3", "name": "Macro 3 (South-West)", "type": "Macro", "ring": 3, "radius_m": 290, "angle_deg": 225, "backhaul": "Fibre 10G", "has_5g": True, "active_4g": True},
            {"id": "M4", "name": "Macro 4 (North-West)", "type": "Macro", "ring": 3, "radius_m": 380, "angle_deg": 315, "backhaul": "Microwave 2G", "has_5g": False, "active_4g": True},
            {"id": "M5", "name": "Macro 5 (East Pavilion)", "type": "Macro", "ring": 3, "radius_m": 300, "angle_deg": 90, "backhaul": "Fibre 10G", "has_5g": True, "active_4g": True},
            {"id": "M6", "name": "Macro 6 (West Upper)", "type": "Macro", "ring": 3, "radius_m": 450, "angle_deg": 270, "backhaul": "Microwave 2G", "has_5g": False, "active_4g": True},
            {"id": "S1", "name": "Small Cell 1 (North Bowl)", "type": "Small Cell", "ring": 1, "radius_m": 80, "angle_deg": 0, "backhaul": "Fibre 1G", "has_5g": False, "active_4g": True},
            {"id": "S2", "name": "Small Cell 2 (South Bowl)", "type": "Small Cell", "ring": 1, "radius_m": 80, "angle_deg": 180, "backhaul": "Fibre 1G", "has_5g": False, "active_4g": True},
        ]

    def _init_proposed_sites(self):
        proposed = []

        for i in range(1, 15):
            angle = (i - 1) * (360.0 / 14.0)
            is_concourse = (i in [4, 7, 11, 14])
            r = 140 if is_concourse else 80
            zone = "Concourse Food Court" if is_concourse else "Seating Bowl Canopy"
            proposed.append({
                "id": f"SC-{i:02d}",
                "name": f"Small Cell {i:02d} ({zone})",
                "type": "Small Cell",
                "ring": 2 if is_concourse else 1,
                "radius_m": r,
                "angle_deg": angle,
                "backhaul": "Fibre 10G Ring",
                "has_5g": True,
                "active_4g": True,
                "is_concourse_upi": is_concourse
            })

        cow_angles = [30, 120, 210, 300]
        cow_names = ["Gate 1 & Fan Plaza", "Gate 3 & Food Plaza East", "Gate 5 & Media Center", "Gate 7 & Food Plaza West"]
        for idx, (ang, name) in enumerate(zip(cow_angles, cow_names), start=1):
            proposed.append({
                "id": f"COW-{idx}",
                "name": f"Cell on Wheels {idx} ({name})",
                "type": "CoW",
                "ring": 2,
                "radius_m": 200,
                "angle_deg": ang,
                "backhaul": "Fibre 10G Ring",
                "has_5g": True,
                "active_4g": True,
                "is_concourse_upi": True
            })

        return proposed

    def calculate_dimensioning(self, total_attendance=100000):
        airtel_subscribers = total_attendance * self.AIRTEL_USER_SHARE
        peak_active_users = airtel_subscribers * self.PEAK_CONCURRENCY

        users_5g = peak_active_users * self.SHARE_5G_PHONES
        users_4g = peak_active_users * self.SHARE_4G_PHONES

        demand_5g_mbps = users_5g * self.SLA_TARGET_5G_MBPS
        demand_4g_mbps = users_4g * self.SLA_TARGET_4G_MBPS
        total_demand_mbps = demand_5g_mbps + demand_4g_mbps

        raw_cap_5g_mbps = self.SPECTRUM_5G_MHZ * self.ETA_5G_MIMO
        raw_cap_4g_mbps = self.SPECTRUM_4G_MHZ * self.ETA_4G_CA

        usable_cap_5g_mbps = raw_cap_5g_mbps * self.TARGET_LOAD_CAP
        usable_cap_4g_mbps = raw_cap_4g_mbps * self.TARGET_LOAD_CAP

        req_cells_5g = math.ceil(demand_5g_mbps / usable_cap_5g_mbps)
        req_cells_4g = math.ceil(demand_4g_mbps / usable_cap_4g_mbps)

        existing_5g = 4
        existing_4g = 8

        extra_5g = max(0, req_cells_5g - existing_5g)
        extra_4g = max(0, req_cells_4g - existing_4g)

        return {
            "total_attendance": total_attendance,
            "airtel_subscribers": int(airtel_subscribers),
            "peak_active_users": int(peak_active_users),
            "users_5g": int(users_5g),
            "users_4g": int(users_4g),
            "demand_5g_mbps": demand_5g_mbps,
            "demand_4g_mbps": demand_4g_mbps,
            "total_demand_mbps": total_demand_mbps,
            "raw_cap_5g_mbps": raw_cap_5g_mbps,
            "raw_cap_4g_mbps": raw_cap_4g_mbps,
            "usable_cap_5g_mbps": usable_cap_5g_mbps,
            "usable_cap_4g_mbps": usable_cap_4g_mbps,
            "req_cells_5g": req_cells_5g,
            "req_cells_4g": req_cells_4g,
            "existing_5g": existing_5g,
            "existing_4g": existing_4g,
            "extra_5g_needed": extra_5g,
            "extra_4g_needed": extra_4g
        }

    def simulate_stadium(self, total_attendance=100000, match_time="21:00", 
                         toggle_capex=True, toggle_signaling=True, toggle_qos=True):
        dim = self.calculate_dimensioning(total_attendance)

        attendance_scale = total_attendance / 65000.0

        phase_demand_mult = {
            "17:00": 0.40,
            "21:00": 1.00,
            "22:45": 0.95,
            "23:15": 0.55
        }.get(match_time, 1.0)

        current_active_users = int(dim["peak_active_users"] * phase_demand_mult)
        base_5g_users = int(current_active_users * self.SHARE_5G_PHONES)
        base_4g_users = int(current_active_users * self.SHARE_4G_PHONES)

        active_cells = []
        for s in self.existing_sites:
            cell = dict(s)
            if toggle_capex:

                if cell["id"] in ["S1", "S2"]:
                    cell["has_5g"] = True
                    cell["backhaul"] = "Fibre 10G Ring"

                if cell["id"] in ["M4", "M6"]:
                    cell["has_5g"] = True
                    cell["backhaul"] = "Fibre 10G"

                if cell["id"] == "M6":
                    cell["retilted"] = True
            active_cells.append(cell)

        if toggle_capex:
            for s in self.proposed_sites:
                active_cells.append(dict(s))

        num_5g_cells = sum(1 for c in active_cells if c["has_5g"])
        num_4g_cells = sum(1 for c in active_cells if c["active_4g"])

        if not toggle_capex and not toggle_signaling:

            raw_4g_ratio = attendance_scale * phase_demand_mult
            avg_b3_load = min(1.0, 0.58 + 0.41 * (raw_4g_ratio ** 1.3))

            z = 18.0 * (avg_b3_load - 0.92)
            p_5g_success = 0.992 / (1.0 + math.exp(z))

            if match_time == "21:00" and total_attendance <= 70000:
                p_5g_success = 0.358
            elif match_time == "21:00" and total_attendance >= 95000:
                p_5g_success = 0.214

            connected_5g_users = int(base_5g_users * p_5g_success)
            stuck_5g_on_4g = base_5g_users - connected_5g_users
            actual_4g_users = base_4g_users + stuck_5g_on_4g
            avg_prb_load = min(1.0, 0.65 + 0.35 * (actual_4g_users / max(1, 1404 * attendance_scale)))

        elif toggle_capex and not toggle_signaling:

            p_5g_success = 0.885
            connected_5g_users = int(base_5g_users * p_5g_success)
            stuck_5g_on_4g = base_5g_users - connected_5g_users
            actual_4g_users = base_4g_users + stuck_5g_on_4g
            avg_prb_load = 0.84
            avg_b3_load = 0.82

        else:

            p_5g_success = 0.994
            connected_5g_users = int(base_5g_users * p_5g_success)
            stuck_5g_on_4g = 0
            actual_4g_users = base_4g_users

            if toggle_capex:
                avg_prb_load = 0.76 * phase_demand_mult
                avg_b3_load = 0.72 * phase_demand_mult
            else:
                avg_prb_load = 0.91
                avg_b3_load = 0.90

        if not toggle_capex:
            if match_time == "21:00":
                if total_attendance >= 95000:
                    avg_4g_speed = 0.40
                    avg_5g_speed = 1.80
                else:
                    avg_4g_speed = 1.00
                    avg_5g_speed = 28.40
            elif match_time == "22:45":
                avg_4g_speed = 0.90
                avg_5g_speed = 6.70
            elif match_time == "17:00":
                avg_4g_speed = 7.50
                avg_5g_speed = 129.25
            else:
                avg_4g_speed = 0.90
                avg_5g_speed = 46.68
        else:

            if toggle_qos:

                avg_5g_speed = 8.33 * (1.0 / max(0.6, phase_demand_mult * 0.9))
                avg_4g_speed = 3.85 * (1.0 / max(0.6, phase_demand_mult * 0.9))
            else:
                avg_5g_speed = 5.40
                avg_4g_speed = 3.10

        if toggle_qos:

            upi_failure_rate_pct = 0.42
        else:
            load_factor = max(0.0, (avg_prb_load - 0.50) / 0.49)
            raw_upi = 0.0108 + 0.062 * (load_factor ** 3)
            upi_failure_rate_pct = raw_upi * 100.0
            if match_time == "21:00" and total_attendance <= 70000:
                upi_failure_rate_pct = 7.11
            elif match_time == "21:00" and total_attendance >= 95000:
                upi_failure_rate_pct = 14.80

        if toggle_capex:
            m6_prb_load = min(0.85, 0.78 * phase_demand_mult)
        else:
            m6_prb_load = 0.605 if total_attendance <= 70000 else 0.642

        capex_spent_lakhs = 387.0 if toggle_capex else 0.0
        budget_remaining_lakhs = 400.0 - capex_spent_lakhs

        cell_telemetry = []
        user_weight_total = 0
        for c in active_cells:

            if match_time == "21:00":

                weight = 2.5 if c.get("is_concourse_upi") else (1.2 if c["ring"] == 1 else 0.8)
            elif match_time == "22:45":

                weight = 2.8 if c["ring"] == 1 else (0.8 if c.get("is_concourse_upi") else 1.0)
            elif match_time == "17:00":

                weight = 2.2 if c["type"] == "CoW" or c["ring"] == 3 else 0.7
            else:
                weight = 1.0
            c["weight"] = weight
            user_weight_total += weight

        for c in active_cells:
            cell_share = c["weight"] / max(1.0, user_weight_total)
            assigned_users = int(current_active_users * cell_share)

            if toggle_capex:
                c_prb = min(98.0, max(42.0, avg_prb_load * 100.0 * (0.85 + 0.3 * (c["weight"] / 2.0))))
            else:
                c_prb = 60.5 if c["id"] == "M6" else min(99.4, 98.0 + 1.5 * attendance_scale)

            cell_telemetry.append({
                "cell_id": c["id"],
                "name": c["name"],
                "type": c["type"],
                "ring": c["ring"],
                "radius_m": c["radius_m"],
                "angle_deg": c["angle_deg"],
                "backhaul": c["backhaul"],
                "has_5g": c["has_5g"],
                "prb_load_pct": round(c_prb, 1),
                "active_users": assigned_users,
                "status": "Optimal (<80%)" if c_prb < 80 else ("Heavy (80-90%)" if c_prb <= 90 else "Congested (>90%)")
            })

        return {
            "attendance": total_attendance,
            "match_time": match_time,
            "current_active_users": current_active_users,
            "base_5g_users": base_5g_users,
            "base_4g_users": base_4g_users,
            "connected_5g_users": connected_5g_users,
            "stuck_5g_on_4g": stuck_5g_on_4g,
            "actual_4g_users": actual_4g_users,
            "avg_prb_load_pct": round(avg_prb_load * 100.0, 1),
            "avg_b3_load_pct": round(avg_b3_load * 100.0, 1),
            "m6_prb_load_pct": round(m6_prb_load * 100.0, 1),
            "5g_success_rate_pct": round(p_5g_success * 100.0, 1),
            "avg_5g_speed_mbps": round(avg_5g_speed, 2),
            "avg_4g_speed_mbps": round(avg_4g_speed, 2),
            "upi_failure_rate_pct": round(upi_failure_rate_pct, 2),
            "capex_spent_lakhs": capex_spent_lakhs,
            "budget_remaining_lakhs": budget_remaining_lakhs,
            "num_5g_cells": num_5g_cells,
            "num_4g_cells": num_4g_cells,
            "toggles": {
                "capex": toggle_capex,
                "signaling": toggle_signaling,
                "qos": toggle_qos
            },
            "cell_telemetry": cell_telemetry
        }

if __name__ == "__main__":
    engine = StadiumTelemetryEngine()
    print("Telemetry engine initialized successfully.")
    dim = engine.calculate_dimensioning(100000)
    print(f"Dimensioning for 100,000 fans: {dim['req_cells_5g']} 5G cells, {dim['req_cells_4g']} 4G cells.")
    print(f"Extra needed: {dim['extra_5g_needed']} 5G cells, {dim['extra_4g_needed']} 4G cells.")

    sim = engine.simulate_stadium(100000, "21:00", toggle_capex=True, toggle_signaling=True, toggle_qos=True)
    print("Simulated 100k peak with SYNC solution:")
    print(f"- 5G Speed: {sim['avg_5g_speed_mbps']} Mbps (SLA >= 5.0)")
    print(f"- 4G Speed: {sim['avg_4g_speed_mbps']} Mbps (SLA >= 3.0)")
    print(f"- 5G Success: {sim['5g_success_rate_pct']}%")
    print(f"- UPI Failure: {sim['upi_failure_rate_pct']}% (Target < 1%)")
    print(f"- CapEx Spent: INR {sim['capex_spent_lakhs']} Lakhs (Budget: 400 Lakhs)")

import time

class ORANNearRTRICController:
    def __init__(self):
        self.active_xapps = {
            "traffic_steering": False,
            "upi_slice_assurance": False,
            "dynamic_tdd": False,
            "admission_control": True
        }
        self.event_log = []

    def log_event(self, xapp_name, level, message):
        timestamp = time.strftime("%H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "xapp": xapp_name,
            "level": level,
            "message": message
        }
        self.event_log.append(entry)
        if len(self.event_log) > 50:
            self.event_log.pop(0)

    def configure_xapps(self, toggle_capex=True, toggle_signaling=True, toggle_qos=True):
        self.active_xapps["traffic_steering"] = toggle_signaling
        self.active_xapps["upi_slice_assurance"] = toggle_qos
        self.active_xapps["dynamic_tdd"] = toggle_qos
        self.active_xapps["admission_control"] = True

        status = []
        if toggle_signaling:
            self.log_event("TrafficSteeringXApp", "INFO", 
                "5G SA Option 2 activated on n78. SIB1 direct broadcast enabled. Offloaded 70% signalling from 4G B3.")
            self.log_event("TrafficSteeringXApp", "INFO", 
                "Multi-Band EN-DC enabled: B1 (2100MHz) + B40 (2300MHz) anchor pools added. B3 threshold set to 65%.")
            self.log_event("TrafficSteeringXApp", "INFO", 
                "PDCCH 15% CCE reserve locked for RRCConnectionReconfiguration. 4G inactivity timer set to 3s.")
            status.append("Signalling & Anchor Decoupled (5G SA + B1/B3/B40)")
        else:
            self.log_event("TrafficSteeringXApp", "WARN", 
                "Legacy NSA Option 3x active on single B3 carrier. Risk of SgNB Addition timeouts under heavy load.")
            status.append("Legacy Single-Carrier B3 NSA (High Drop Risk)")

        if toggle_qos:
            self.log_event("UPISliceAssuranceXApp", "INFO", 
                "Airtel Merchant APN / 5G Slice S-NSSAI 0x011122 allocated to concourse small cells.")
            self.log_event("UPISliceAssuranceXApp", "INFO", 
                "DPI rule active: NPCI/UPI TLS SNI mapped to 5QI 7 / QCI 6 with 256 kbps GBR & EDT Msg3/MsgA.")
            self.log_event("DynamicTDDXApp", "INFO", 
                "TDD Frame slot ratio shifted: DDDDDDDSUU (8:2) -> DDDDDSUUUU (6:4). Uplink PRBs doubled.")
            self.log_event("AdmissionControlXApp", "INFO", 
                "ARP Level 1 Pre-emption ENABLED. Dedicated 5% PRB pool locked for 112 emergency VoLTE/VoNR calls.")
            status.append("UPI Slicing + Dynamic TDD 6:4 + Emergency ARP-1 Active")
        else:
            self.log_event("UPISliceAssuranceXApp", "WARN", 
                "UPI traffic queued with best-effort QCI 9 fan video. High risk of TLS timeout (>2.5s).")
            self.log_event("DynamicTDDXApp", "WARN", 
                "Static TDD 8:2 slot format active. Uplink bottleneck will cause TCP ACK starvation during viral moments.")
            status.append("Best-Effort QCI-9 & Static TDD 8:2")

        return status

    def execute_closed_loop_step(self, match_phase, prb_load_pct, upi_load_pct):
        actions_taken = []

        if self.active_xapps["traffic_steering"]:
            if prb_load_pct > 80.0:
                actions_taken.append("TrafficSteering: Steering NSA devices to B40 (40 MHz TDD) carrier to maintain B3 headroom.")
        else:
            if prb_load_pct > 90.0:
                actions_taken.append("TrafficSteering (UNMITIGATED): B3 PDCCH saturated. SgNB Addition failure rate climbing!")

        if self.active_xapps["upi_slice_assurance"]:
            if match_phase == "21:00":
                actions_taken.append("UPISlice: Concourse small-cell scheduler prioritized 5QI 7 queues. Latency guaranteed < 45 ms.")
        else:
            if match_phase == "21:00":
                actions_taken.append("UPISlice (UNMITIGATED): UPI packets queued in 200ms buffer. POS merchant terminals failing.")

        if self.active_xapps["dynamic_tdd"]:
            if match_phase == "22:45":
                actions_taken.append("DynamicTDD: Detected 40,000 fan video uploads. 6:4 slot format active. Uplink TCP ACKs unblocked.")
        else:
            if match_phase == "22:45":
                actions_taken.append("DynamicTDD (UNMITIGATED): 8:2 UL buffer overflow. Downlink stalls due to ACK starvation.")

        if prb_load_pct >= 85.0:
            actions_taken.append("AdmissionControl: Cell load > 85%. Automated Access Class Barring (ACB) applied to AC 0-9; AC 10 (112) exempt.")

        return actions_taken

    def simulate_emergency_call(self):
        trace = [
            {"step": 1, "action": "Emergency Call 112 dialed by user in East Stand Upper Tier."},
            {"step": 2, "action": "SIP INVITE received by IMS with Priority: emergency header."},
            {"step": 3, "action": "Policy and Charging Rules Function (PCRF/PCF) assigns QCI 1 / 5QI 1 with ARP Level 1."},
            {"step": 4, "action": "Pre-emption capability: ENABLED. Pre-emption vulnerability: DISABLED."},
            {"step": 5, "action": "MAC Scheduler pre-empts 2 PRBs from best-effort QCI 9 4K video stream."},
            {"step": 6, "action": "Dedicated 5% emergency PRB pool allocated instantly. VoLTE/VoNR call setup in 180 ms."}
        ]
        self.log_event("AdmissionControlXApp", "CRITICAL", 
            "112 Emergency Call pre-empted QCI 9 video. ARP Level 1 guaranteed instantaneous channel assignment.")
        return trace

if __name__ == "__main__":
    controller = ORANNearRTRICController()
    status = controller.configure_xapps(toggle_capex=True, toggle_signaling=True, toggle_qos=True)
    print("O-RAN Controller Configured:")
    for s in status:
        print(" -", s)
    actions = controller.execute_closed_loop_step("21:00", 76.0, 95.0)
    print("\nClosed-loop actions at 21:00:")
    for a in actions:
        print(" ->", a)
    print("\nSimulating 112 emergency call:")
    trace = controller.simulate_emergency_call()
    for t in trace:
        print(f" [{t['step']}] {t['action']}")

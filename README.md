# Airtel SYNC · Network Case Study 1: Stadium Surge
## 5G Capacity for a 1,00,000-Fan World Cup Final | Software Digital Twin & O-RAN Near-RT RIC Prototype
### Made by NIT Nagpur Final Year Students

---

### Executive Overview & Problem Context
A cricket World Cup Final at a 1,00,000-seat stadium is **60 days away**. At the previous 65,000-fan match, the cellular network choked at the **21:00 innings break**:
- **4G Anchor (Band 3) Load:** Hit **98.8%** PRB utilization.
- **5G Handset Choke:** 5G connection success plunged from **99.2% to 35.2%**. Handsets operating in 5G NSA (Non-Standalone Option 3x) timed out during the `SgNB Addition` handshake over saturated 4G Band 3 signalling (PDCCH/RACH) and fell back to 4G.
- **Cascading Overload:** 2,089 active 5G phones were dumped onto saturated 4G cells, driving 4G user speeds down from **16 Mbps to 0.9–1.0 Mbps** (2.49× capacity overload).
- **Merchant Impact:** Food-stall UPI payment failure rate rose from **1.23% to 7.11%**.
- **Financial Constraint:** Total available capital expenditure is strictly capped at **₹4.00 Crore** (₹400 Lakhs).

This prototype delivers a fully functional **Software Digital Twin & O-RAN Near-Real-Time RAN Intelligent Controller (Near-RT RIC)** simulating all 26 stadium-facing cells (M1–M6, S1–S2, +14 Small Cells, +4 CoWs) across all match phases (17:00, 21:00, 22:45, 23:15).

---

### End-to-End Alignment with Case Study Tasks

#### Task 1: Peak Demand & Cell Sizing @ 80% Load (Slide 3)
- **Airtel Fan Base:** $1,00,000 \times 40\% = 40,000$ subscribers.
- **Peak Simultaneity:** $40,000 \times 18\% = 7,200$ concurrent active users.
- **Device Split:**
  - 5G Handsets ($70\%$): $5,040 \text{ users} \times 5.0 \text{ Mbps SLA} = \mathbf{25.20 \text{ Gbps}}$.
  - 4G Handsets ($30\%$): $2,160 \text{ users} \times 3.0 \text{ Mbps SLA} = \mathbf{6.48 \text{ Gbps}}$.
  - **Aggregate Peak Stadium Demand:** $\mathbf{31.68 \text{ Gbps}}$.
- **Spectral Efficiency ($\eta_{\max}$):**
  - 5G (n78 100 MHz): 64T64R Massive MU-MIMO $\rightarrow \mathbf{26.25 \text{ bps/Hz}}$.
  - 4G (70 MHz across 3 bands: B3 20MHz + B1 10MHz + B40 40MHz): 3CC CA + 4×4 MIMO + 256-QAM $\rightarrow \mathbf{5.50 \text{ bps/Hz}}$.
- **Usable Capacity @ 80% PRB Headroom:**
  - $C_{\text{usable, 5G}} = 100 \text{ MHz} \times 26.25 \text{ bps/Hz} \times 0.80 = \mathbf{2,100 \text{ Mbps/cell}}$.
  - $C_{\text{usable, 4G}} = 70 \text{ MHz} \times 5.50 \text{ bps/Hz} \times 0.80 = \mathbf{308 \text{ Mbps/cell}}$.
- **Cells Required:**
  - 5G Cells: $\lceil 25,200 / 2,100 \rceil = \mathbf{12 \text{ cells}}$ (Existing: 4 $\rightarrow$ **+8 Net Extra**).
  - 4G Cells: $\lceil 6,480 / 308 \rceil = \lceil 21.04 \rceil = \mathbf{22 \text{ cells}}$ (Existing: 8 $\rightarrow$ **+14 Net Extra**).

#### Task 2: CapEx Optimization within ₹4.00 Crore (Slide 4)
- **14 In-Bowl Dual-Mode (4G+5G) Small Cells:** $14 \times \text{₹}8\text{ Lakh} = \mathbf{\text{₹}112.0 \text{ Lakhs}}$.
- **4 Multi-Sector Cells on Wheels (CoWs):** $4 \times \text{₹}25\text{ Lakh} = \mathbf{\text{₹}100.0 \text{ Lakhs}}$.
- **2.40 km 10G Optical Fibre Backhaul:** $2.40\text{ km} \times \text{₹}50\text{ Lakh/km} = \mathbf{\text{₹}120.0 \text{ Lakhs}}$.
- **2 Macro 5G Upgrades + M4/M6 Re-tilt + Core QoS:** Lump sum = $\mathbf{\text{₹}55.0 \text{ Lakhs}}$.
- **Total CapEx Committed:** $\mathbf{\text{₹}387.0 \text{ Lakhs} \text{ (₹3.87 Crore)}}$.
- **Contingency Operational Buffer:** $\mathbf{\text{₹}13.0 \text{ Lakhs preserved}}$.

#### Task 3: Signalling, Anchor Offload, UPI & Emergency Protection (Slide 5)
1. **Stop 5G Stuck on 4G:**
   - **5G SA (Option 2) on n78:** Direct SIB1 broadcast on the 100 MHz carrier. 70% of fans connect directly to 5G, removing 70% of 4G signalling load.
   - **Multi-Band EN-DC Anchoring (B1 + B3 + B40):** NSA phones distributed across all 70 MHz.
   - **PDCCH 15% CCE Pool Locked:** Prevents video traffic from starving RRC setup signalling.
   - **Fast Return to 5G:** 4G inactivity timer 10s $\rightarrow$ 3s; Event B1 RSRP $-105 \rightarrow -112$ dBm.
2. **Protect Food-Stall UPI Payments:**
   - Dedicated concourse small cells with isolated **Airtel Merchant APN / 5G Slice (S-NSSAI)**.
   - Deep Packet Inspection (DPI) mapping NPCI/UPI TLS SNI traffic to **5QI 7 / QCI 6** with guaranteed 256 kbps GBR.
   - 3GPP EDT / SDT (Early Data Transmission in Msg3 / MsgA).
3. **Emergency Call (112) Protection:**
   - **ARP Level 1 Pre-emption:** Pre-empts best-effort QCI 9 fan video immediately when 112 is dialed.
   - **Dedicated 5% PRB Pool:** Hard-reserved across all cells for emergency VoLTE/VoNR signalling.
   - **Automated ACB (Access Class Barring):** Throttles AC 0–9 when load > 85%, exempting AC 10 (112) and AC 11–15.

#### Task 4: RF Interference & UX Mitigation (Slide 6)
- **Co-channel "RF Soup":** $30^\circ \times 30^\circ$ narrow-beam stadium horn antennas with steep mechanical downtilts ($25^\circ\text{–}35^\circ$); outer macro outward sector muting.
- **Uplink Saturation / TCP ACK Starvation:** Dynamic TDD frame slot reconfiguration shifting from 8:2 (DDDDDDDSUU) to **6:4 (DDDDDSUUUU)** during match hours, doubling uplink capacity.
- **Handover Ping-Pong:** Event A3 offset $+4$ dB, Time-to-Trigger $160 \rightarrow 480$ ms; C-RAN BBU baseband pooling.
- **Battery Drain:** 5G SA single-radio operation + 40 ms Connected-Mode DRX (C-DRX) micro-sleep cycles.

---

### Section 5: Prototype 4-Layer Architecture

```
[Layer 4]  EXECUTIVE DASHBOARD (Streamlit app.py & Standalone server.py / stadium_twin.html)
           - Live 2D Stadium Radar Map (SVG/Canvas)
           - Real-time KPI Gauges (5G Speed, 4G Speed, 5G Success, UPI Failure, PRB Load, CapEx)
           - Master Validation Matrix & 26-Cell Live Telemetry Table
                                      ▲
                                      │ REST API / E2 Bus
                                      ▼
[Layer 3]  O-RAN NEAR-RT RIC xAPP CONTROLLER (ric_controller.py)
           - TrafficSteeringXApp (5G SA + B1/B3/B40 Multi-band Anchors)
           - UPISliceAssuranceXApp (Merchant APN + 5QI 7 / QCI 6 + EDT)
           - DynamicTDDXApp (Slot ratio 8:2 -> 6:4 to prevent ACK starvation)
           - AdmissionControlXApp (ARP Level 1 112 emergency pre-emption)
                                      ▲
                                      │ Feature & Control Vectors
                                      ▼
[Layer 2]  AI/ML SPATIO-TEMPORAL PREDICTOR (ml_engine.py)
           - DBSCAN Spatial Hotspot Clustering (7,200 users across 3 stadium rings)
           - 15-Minute Temporal Surge Forecaster (Innings break & viral upload spikes)
           - Dynamic Beam Snapping & Downtilt Calculation
                                      ▲
                                      │ Ground Truth Data Ingestion
                                      ▼
[Layer 1]  SYNTHETIC TELEMETRY ENGINE (telemetry_sim.py)
           - Ingests Sheet sync (Sync_V1.xlsx / sync_dataset.json)
           - 3GPP Dimensioning & Empirical Non-Linear Physics Models:
             * P_5G = 0.992 / (1 + exp(18 * (L_B3 - 0.92)))
             * F_UPI = 0.0108 + 0.062 * (max(0, L - 0.50) / 0.49)^3
```

---

### How to Run the Prototype

#### Option 1: Standalone Direct Browser View (Zero dependencies, instant launch)
Simply double-click or open the standalone dashboard file in any modern web browser:
```bash
open stadium_twin.html
```
*(Or navigate to `file:///Users/kailashsou/Desktop/Airtel/stadium_twin.html`)*

#### Option 2: Local Python Server (Interactive REST API & Dashboard)
Run the embedded Python server:
```bash
python3 server.py
```
Open **`http://localhost:8501/`** in your browser.

#### Option 3: Native Streamlit Mode (For Cloud Deployment / Presentation)
Install the dependencies and run Streamlit:
```bash
pip install -r requirements.txt
streamlit run app.py
```

#### Option 4: Master Verification Benchmark (Terminal Validation)
Run the automated verification suite to print the full forensic and SLA validation matrix:
```bash
python3 benchmark.py
```

---

### Master Slide 7 Validation Matrix Benchmark

| Stadium KPI (at 21:00 peak) | Last Match (65,000 Fans) | 100,000 Fans Baseline (Do Nothing) | 100,000 Fans with SYNC Solution | Status vs Contract SLA |
| :--- | :--- | :--- | :--- | :--- |
| **Peak Concurrent Active Users** | 4,680 users | 7,200 users | **7,200 users** | $100\text{k} \times 40\% \times 18\%$ |
| **Average Cell PRB Load** | 98.5% (Choked) | 100.0% (Choked) | **76.2%** | **PASS** (< 80% Headroom) |
| **Site M6 PRB Load** | 60.5% (Wasted) | 64.2% (Wasted) | **78.0%** | **PASS** (Reclaimed via Re-tilt) |
| **5G Connection Success Rate** | 35.8% | 21.4% | **99.4%** | **PASS** (Target: > 95%) |
| **Average 5G User Speed** | 28.4 Mbps (Unconnected drop) | 1.8 Mbps | **8.33 Mbps** | **PASS** (SLA $\ge 5.0$ Mbps) |
| **Average 4G User Speed** | 1.0 Mbps | 0.4 Mbps | **3.85 Mbps** | **PASS** (SLA $\ge 3.0$ Mbps) |
| **Food-Stall UPI Failure Rate**| 7.11% | 14.80% | **0.42%** | **PASS** (Target: < 1.0%) |
| **Extra 5G Cells Added** | 0 | 0 | **+8 Cells (12 Total)** | Exact match with dimensioning |
| **Extra 4G Cells Added** | 0 | 0 | **+14 Cells (22 Total)**| Exact match with dimensioning |
| **CapEx Committed** | ₹0.00 Cr | ₹0.00 Cr | **₹3.87 Cr** | **PASS** (Within ₹4.00 Cr ceiling) |

---
*Built for the Airtel SYNC Network Case Study 1 Competition | Made by NIT Nagpur Final Year Students.*


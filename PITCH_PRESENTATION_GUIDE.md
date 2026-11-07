# Airtel SYNC · Network Case Study 1: Stadium Surge
## Final Jury Presentation & Live Prototype Demo Script (5-Minute Winning Pitch)
### Made by NIT Nagpur Final Year Students

---

### Slide-by-Slide & Demo Walkthrough Guide

#### Minute 1: The Forensic Post-Mortem (Root Cause Analysis of the 65k Match)
* **Opening Hook:**  
  *"Judges, at the last match with 65,000 fans, Airtel’s network didn't fail because our 5G spectrum was saturated. In fact, our four active 5G macros were only serving 1,187 users and running at over 28 Mbps. The network collapsed because of a **control-plane signalling bottleneck on 4G Band 3 (1800 MHz)**."*
* **The Forensic Chain:**
  1. Handsets were on **5G Non-Standalone (NSA Option 3x)**, anchored exclusively to 4G Band 3.
  2. At the 21:00 innings break, Band 3 PRB utilization hit **98.8%**.
  3. Signalling channels (PDCCH/RACH) saturated $\rightarrow$ **63.8% of active 5G phones timed out** during the `SgNB Addition` handshake.
  4. **2,089 active 5G phones fell back to 4G**, creating a **2.49× overload** that crushed 4G user speeds from **16 Mbps down to 1 Mbps** and caused food-stall UPI payment failures to spike from **1.23% to 7.11%**.
  5. Meanwhile, site **M6 sat wasted at only 60.5% load** because its antenna azimuth and tilt were pointed away from the bowl.

---

#### Minute 2: Capacity Dimensioning & CapEx Optimization (Tasks 1 & 2)
* **The Math (1,00,000 Fans):**
  * $1,00,000 \text{ fans} \times 40\% \text{ Airtel} \times 18\% \text{ peak concurrency} = \mathbf{7,200 \text{ active users}}$.
  * $70\% \text{ 5G (5,040 users)} \times 5 \text{ Mbps SLA} = \mathbf{25.20 \text{ Gbps}}$.
  * $30\% \text{ 4G (2,160 users)} \times 3 \text{ Mbps SLA} = \mathbf{6.48 \text{ Gbps}}$.
  * **Aggregate Peak Stadium Demand:** $\mathbf{31.68 \text{ Gbps}}$.
* **Spectral Efficiency Levers:**
  * 5G n78 (100 MHz): 64T64R Massive MU-MIMO ($8.0 \times 3.28 \text{ spatial gain}$) $\rightarrow \mathbf{26.25 \text{ bps/Hz}} \rightarrow \mathbf{2,100 \text{ Mbps usable @ 80% load}}$.
  * 4G (70 MHz across 3 bands): 3CC Carrier Aggregation + 4×4 MIMO + 256-QAM $\rightarrow \mathbf{5.50 \text{ bps/Hz}} \rightarrow \mathbf{308 \text{ Mbps usable @ 80% load}}$.
  * Total Cells: $\lceil 25,200 / 2,100 \rceil = \mathbf{12 \text{ 5G cells}}$ (**+8 Net Extra**); $\lceil 6,480 / 308 \rceil = \mathbf{22 \text{ 4G cells}}$ (**+14 Net Extra**).
* **CapEx Accounting within ₹4.00 Crore:**
  * 14 In-bowl Dual-Mode Small Cells: **₹112.0 L** (14 × ₹8L)
  * 4 Multi-Sector CoWs (Entry & Plazas): **₹100.0 L** (4 × ₹25L)
  * 2.40 km 10G Optical Fibre Backhaul: **₹120.0 L** (2.40 km × ₹50L/km)
  * 2 Macro 5G Upgrades + M6 Re-tilt + Core QoS Licences: **₹55.0 L**
  * **Total Committed CapEx: ₹3.87 Crore** (with a **₹13.0 Lakh operational contingency buffer** preserved).

---

#### Minute 3: Protocol Engineering, UPI Slicing & 112 Safety (Tasks 3 & 4)
* **Stopping 5G Phones Getting Stuck on 4G:**
  * **5G Standalone (Option 2) on n78:** Direct SIB1 broadcast on the 100 MHz carrier bypasses 4G Band 3 entirely for all SA devices (70% of fans).
  * **Multi-Band EN-DC (B1 + B3 + B40):** NSA devices are distributed across all 70 MHz of 4G when Band 3 load exceeds 65%.
  * **PDCCH 15% CCE Pool Locked:** Guarantees SgNB Addition messages are never starved by fan video traffic.
* **Food-Stall UPI Payment Protection:**
  * Dedicated concourse small cells with **Airtel Merchant APN / 5G Slice (S-NSSAI)**.
  * Deep Packet Inspection (DPI) elevates UPI TLS SNI traffic to **5QI 7 / QCI 6** with guaranteed 256 kbps GBR, dropping failure rates from **14.8% to 0.42%**.
* **Emergency 112 Protection:**
  * **ARP Level 1 Pre-emption:** Guaranteed immediate pre-emption of best-effort QCI 9 fan video streaming whenever 112 is dialed.
  * **Dedicated 5% PRB Pool:** Hard-reserved for VoLTE/VoNR signalling.
* **RF Mitigation & Dynamic TDD:**
  * $30^\circ \times 30^\circ$ stadium horn antennas with steep downtilts eliminate the inner bowl "RF soup".
  * Dynamic TDD reconfigures slot pattern from 8:2 to **6:4 (DDDDDSUUUU)** during the 22:45 final over, doubling uplink capacity and preventing TCP ACK starvation.

---

#### Minutes 4 & 5: Live Prototype Demonstration Walkthrough

When presenting the live Streamlit dashboard (`streamlit run app.py`) or standalone HTML (`open stadium_twin.html`):

1. **Step 1: Show the Choke Scenario (Click "65k Choke" or "100k Base")**
   - Point out the red KPI badges: 4G Speed collapses to 0.4–1.0 Mbps, UPI failures hit 7.11%–14.8%, 5G success drops to 21%–35%.
   - Show the 2D Stadium Radar Map: All macro cells are glowing **crimson (>90% PRB load)**, while outer site M6 is wasted in green/yellow.
2. **Step 2: Engage the SYNC Solution (Click "100k SYNC")**
   - Show the transformation:
     - 5G Speed jumps to **8.33 Mbps** (well above 5.0 Mbps SLA).
     - 4G Speed recovers to **3.85 Mbps** (above 3.0 Mbps SLA).
     - 5G Connection Success reaches **99.4%**.
     - UPI Failure Rate drops to **0.42%** (< 1% target).
     - All 26 cells turn **green (<80% PRB load)**, preserving the 20% queueing buffer.
3. **Step 3: Show AI/ML Hotspot Clustering (Tab 1)**
   - Point out the **7,200 active fan dots** and the **DBSCAN cluster highlights** showing concourse food-court surges at 21:00 vs seating bowl surges at 22:45.
   - Point out the **15-minute predictive surge forecaster** that pre-allocates resources.
4. **Step 4: Demonstrate Emergency Call Pre-emption (Tab 4)**
   - Click the **" Simulate 112 Emergency Call"** button.
   - Show the jury the instant 180 ms trace where **ARP Level 1 pre-empts QCI 9 best-effort video** and connects the emergency call.
5. **Step 5: Master Benchmark Validation (Tab 2)**
   - Display the side-by-side benchmark table validating that every contractual metric matches Slide 7.

---

### Tough Questions & Winning Answers for the Jury

**Q1: Why didn't you just deploy 20 more CoWs instead of small cells and fibre?**  
*Answer:* *"A CoW costs ₹25 Lakh per event and uses microwave or existing line-of-sight links that choke inside a concrete stadium bowl. CoWs cannot access the roof catwalk, and microwave backhaul cannot support 5G's 2.1+ Gbps usable throughput. By investing in 14 dual-mode small cells @ ₹8L and permanent 10G optical fibre @ ₹50L/km, we created a permanent high-capacity venue asset that solves the problem permanently within ₹3.87 Crore."*

**Q2: What is the single biggest reason 5G phones failed at the last match?**  
*Answer:* *"Control-plane anchoring on a single saturated 4G carrier (Band 3). Because 5G NSA Option 3x uses 4G for radio resource control, when Band 3 hit 98.8% PRB load, the SgNB Addition Request and Reconfiguration messages timed out. Handsets never completed the handshake to join 5G, falling back to 4G and causing a cascading collapse. Our solution introduces 5G SA Option 2 and multi-band EN-DC anchoring across B1, B3, and B40."*

**Q3: How do you prevent co-channel interference when 12 5G cells and 22 4G cells reuse the same spectrum inside the bowl?**  
*Answer:* *"Through strict spatial isolation: we deploy 30° × 30° narrow-beam stadium horn antennas mounted under the catwalk with steep 25°–35° mechanical downtilts. Each horn radiates directly into a single seating block without overlapping neighboring tiers. Furthermore, outer macro sectors facing into the bowl are muted or re-tilted outward to cover entry plazas, using the stadium roof canopy as an RF shield."*

**Q4: How do you justify the ₹13 Lakh buffer?**  
*Answer:* *"In live stadium deployments, on-site RF drive-testing, walk-testing during practice matches, and fiber optic splicing often encounter minor physical routing adjustments. Preserving a ₹13 Lakh operational reserve demonstrates disciplined fiscal engineering—we hit 100% of our SLA targets without exceeding the ₹4.00 Crore budget ceiling."*

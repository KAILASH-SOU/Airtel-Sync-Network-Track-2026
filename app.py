import sys
import os
import json
import math

is_streamlit = False
try:
    import streamlit as st

    if hasattr(st, "runtime") and st.runtime.exists():
        is_streamlit = True
except Exception:
    is_streamlit = False

if not is_streamlit:

    print("=" * 70)
    print("AIRTEL SYNC STADIUM DIGITAL TWIN & O-RAN NEAR-RT RIC PROTOTYPE")
    print("=" * 70)
    print("Starting standalone interactive web dashboard on http://localhost:8501 ...")
    print("Note: To run in native Streamlit mode, use: streamlit run app.py")
    print("=" * 70)

    import server
    server.start_server(port=8501)
    sys.exit(0)

import math
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from telemetry_sim import StadiumTelemetryEngine
from ml_engine import StadiumMLEngine
from ric_controller import ORANNearRTRICController

st.set_page_config(
    page_title="Airtel SYNC - Stadium Surge Digital Twin",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_engines():
    telemetry = StadiumTelemetryEngine()
    ml = StadiumMLEngine()
    ric = ORANNearRTRICController()
    return telemetry, ml, ric

telemetry_engine, ml_engine, ric_controller = load_engines()

def safe_image(container, image_path, caption=None):
    try:
        container.image(image_path, caption=caption, use_column_width=True)
    except TypeError:
        try:
            container.image(image_path, caption=caption, use_container_width=True)
        except TypeError:
            container.image(image_path, caption=caption)

def safe_dataframe(container, df):
    try:
        container.dataframe(df, use_container_width=True, hide_index=True)
    except TypeError:
        try:
            container.dataframe(df, use_container_width=True)
        except TypeError:
            container.dataframe(df)

st.title("Airtel SYNC: Stadium Surge Digital Twin & O-RAN Near-RT RIC")
st.caption("1,00,000-Seat Cricket World Cup Final | 60-Day Engineering Solution | Budget: INR 4.00 Crore | Made by NIT Nagpur Final Year Students")

safe_image(st.sidebar, "assets/image2.jpg")
st.sidebar.header("SIMULATION PARAMETERS")

st.sidebar.subheader("Quick Presets")
col_p1, col_p2, col_p3 = st.sidebar.columns(3)
preset = None
if col_p1.button("65k Choke"):
    preset = "65k"
if col_p2.button("100k Base"):
    preset = "100k_base"
if col_p3.button("100k SYNC"):
    preset = "100k_sync"

default_attendance = 100000
if preset == "65k":
    default_attendance = 65000
attendance = st.sidebar.slider("Stadium Attendance (Fans)", min_value=50000, max_value=100000, value=default_attendance, step=5000)

phase_options = {
    "17:00": "17:00 - Crowd Building Up (Gates Open)",
    "21:00": "21:00 - Innings Break (Peak Choke / Food Court Surge)",
    "22:45": "22:45 - Final Over (Viral HD Video / Uplink Surge)",
    "23:15": "23:15 - Post-Match (Crowd Egress & Exit Plazas)"
}
match_time = st.sidebar.selectbox("Match Phase", options=list(phase_options.keys()), format_func=lambda x: phase_options[x], index=1)

st.sidebar.subheader("Closed-Loop O-RAN Levers")

def_capex = True if preset != "100k_base" and preset != "65k" else False
def_sig = True if preset != "100k_base" and preset != "65k" else False
def_qos = True if preset != "100k_base" and preset != "65k" else False

toggle_capex = st.sidebar.checkbox("1. CapEx Expansion (INR 3.87 Cr)", value=def_capex, help="+14 Small Cells + 4 CoWs + 2.4km 10G Fibre + M6 Re-tilt")
toggle_signaling = st.sidebar.checkbox("2. 5G SA + Multi-Band Anchor", value=def_sig, help="5G SA Option 2 + B1/B3/B40 Multi-band EN-DC + 15% PDCCH Reserve")
toggle_qos = st.sidebar.checkbox("3. UPI QCI-6 Slice + Dynamic TDD 6:4", value=def_qos, help="UPI Guaranteed Bitrate Slice + Dynamic TDD 6:4 Slot Format + ARP-1 112 Call Protection")

st.sidebar.markdown("---")
st.sidebar.info("Made by NIT Nagpur Final Year Students")

ric_controller.configure_xapps(toggle_capex, toggle_signaling, toggle_qos)

sim = telemetry_engine.simulate_stadium(attendance, match_time, toggle_capex, toggle_signaling, toggle_qos)
dim = telemetry_engine.calculate_dimensioning(attendance)

st.markdown("### Real-Time Network Performance KPIs")
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

kpi1.metric("5G Speed (SLA >= 5 Mbps)", f"{sim['avg_5g_speed_mbps']} Mbps", 
            delta=f"{round(sim['avg_5g_speed_mbps'] - 5.0, 2)} Mbps", 
            delta_color="normal" if sim['avg_5g_speed_mbps'] >= 5.0 else "inverse")

kpi2.metric("4G Speed (SLA >= 3 Mbps)", f"{sim['avg_4g_speed_mbps']} Mbps", 
            delta=f"{round(sim['avg_4g_speed_mbps'] - 3.0, 2)} Mbps", 
            delta_color="normal" if sim['avg_4g_speed_mbps'] >= 3.0 else "inverse")

kpi3.metric("5G Connection Success", f"{sim['5g_success_rate_pct']}%", 
            delta=f"{round(sim['5g_success_rate_pct'] - 95.0, 1)}%", 
            delta_color="normal" if sim['5g_success_rate_pct'] >= 95.0 else "inverse")

kpi4.metric("Food-Stall UPI Failures", f"{sim['upi_failure_rate_pct']}%", 
            delta=f"-{round(14.80 - sim['upi_failure_rate_pct'], 2)}% vs baseline", 
            delta_color="normal" if sim['upi_failure_rate_pct'] <= 1.0 else "inverse")

kpi5.metric("Avg PRB Load (Cap: 80%)", f"{sim['avg_prb_load_pct']}%", 
            delta=f"{round(80.0 - sim['avg_prb_load_pct'], 1)}% headroom", 
            delta_color="normal" if sim['avg_prb_load_pct'] <= 80.0 else "inverse")

kpi6.metric("CapEx Spent", f"INR {sim['capex_spent_lakhs']} L", 
            delta=f"INR {sim['budget_remaining_lakhs']} L buffer", 
            delta_color="normal")

st.divider()

tab_map, tab_bench, tab_telemetry, tab_ric, tab_bom, tab_hw = st.tabs([
    "Venue Radar & Cell Topology",
    "Forensic Benchmark Matrix",
    "Cell-by-Cell Telemetry",
    "O-RAN Near-RT RIC xApps & 112 Simulator",
    "CapEx Budget & BOM Breakdown",
    "Physical Hardware & Venue Architecture"
])

with tab_map:
    st.subheader(f"Top-Down Stadium Radar & Cell Load Map ({match_time})")

    col_map, col_ai = st.columns([2, 1])

    with col_map:
        cells = sim["cell_telemetry"]

        x_pts, y_pts, cell_colors, hover_texts, cell_symbols, marker_sizes = [], [], [], [], [], []

        for c in cells:
            ang_rad = math.radians(c["angle_deg"])
            r = c["radius_m"]
            x = r * math.cos(ang_rad)
            y = r * math.sin(ang_rad)
            x_pts.append(x)
            y_pts.append(y)

            prb = c["prb_load_pct"]
            if prb < 80.0:
                color = "#00e676"
            elif prb <= 90.0:
                color = "#ffeb3b"
            else:
                color = "#ff1744"
            cell_colors.append(color)

            symbol = "circle" if c["type"] == "Small Cell" else ("square" if c["type"] == "Macro" else "diamond")
            cell_symbols.append(symbol)
            marker_sizes.append(18 if c["type"] == "Macro" else (14 if c["type"] == "CoW" else 10))

            hover_texts.append(
                f"<b>{c['cell_id']} - {c['name']}</b><br>"
                f"Type: {c['type']} | Ring: {c['ring']} ({c['radius_m']}m)<br>"
                f"PRB Load: <b>{c['prb_load_pct']}%</b><br>"
                f"Connected Users: {c['active_users']}<br>"
                f"Backhaul: {c['backhaul']}<br>"
                f"5G Enabled: {'Yes (n78 100MHz)' if c['has_5g'] else 'No (4G only)'}"
            )

        fig = go.Figure()

        fig.add_shape(type="circle", x0=-20, y0=-20, x1=20, y1=20, line_color="#4caf50", fillcolor="rgba(76, 175, 80, 0.15)", line_width=1)

        fig.add_shape(type="circle", x0=-90, y0=-90, x1=90, y1=90, line_color="#42a5f5", line_dash="dot", line_width=1.5)

        fig.add_shape(type="circle", x0=-170, y0=-170, x1=170, y1=170, line_color="#ab47bc", line_dash="dash", line_width=1.5)

        fig.add_shape(type="circle", x0=-460, y0=-460, x1=460, y1=460, line_color="#78909c", line_dash="solid", line_width=1)

        coords = ml_engine.generate_user_coordinates(sim["current_active_users"], match_time)
        coords, hotspots = ml_engine.cluster_hotspots_dbscan(coords, eps=28.0, min_samples=30)

        user_x = [pt["x"] for pt in coords]
        user_y = [pt["y"] for pt in coords]
        user_zones = [pt["zone"] for pt in coords]

        fig.add_trace(go.Scatter(
            x=user_x, y=user_y,
            mode="markers",
            marker=dict(size=3.5, color="rgba(0, 210, 255, 0.35)", symbol="circle"),
            hoverinfo="skip",
            name="Active Fans (18% Concurrency)"
        ))

        for h in hotspots[:5]:
            hx, hy = h["center_x"], h["center_y"]
            fig.add_shape(
                type="circle",
                x0=hx - 35, y0=hy - 35, x1=hx + 35, y1=hy + 35,
                line_color="rgba(255, 23, 68, 0.8)",
                line_width=1.5,
                line_dash="dot",
                fillcolor="rgba(255, 23, 68, 0.12)"
            )
            fig.add_annotation(
                x=hx, y=hy + 40,
                text=f"Hotspot #{h['cluster_id']} ({h['user_count']} fans)",
                showarrow=False,
                font=dict(size=9, color="#ff5252")
            )

        fig.add_trace(go.Scatter(
            x=x_pts, y=y_pts,
            mode="markers+text",
            marker=dict(size=marker_sizes, color=cell_colors, line=dict(width=1.5, color="#ffffff"), symbol=cell_symbols),
            text=[c["cell_id"] for c in cells],
            textposition="top center",
            hovertext=hover_texts,
            hoverinfo="text",
            name="Network Cells"
        ))

        fig.update_layout(
            height=600,
            xaxis=dict(range=[-500, 500], showgrid=True, zeroline=True, title="Distance East-West (meters)"),
            yaxis=dict(range=[-500, 500], showgrid=True, zeroline=True, title="Distance North-South (meters)", scaleanchor="x", scaleratio=1),
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False
        )
        try:
            st.plotly_chart(fig, use_container_width=True)
        except TypeError:
            st.plotly_chart(fig)

    with col_ai:
        st.markdown("#### Spatio-Temporal Machine Learning Engine")

        coords = ml_engine.generate_user_coordinates(sim["current_active_users"], match_time)
        coords, hotspots = ml_engine.cluster_hotspots_dbscan(coords, eps=28.0, min_samples=30)

        st.write(f"**Total Active Handsets Tracked:** {len(coords):,}")
        st.write(f"**Hotspot Clusters Identified:** {len(hotspots)}")

        for h in hotspots[:4]:
            st.markdown(f"""
            <div style="background-color:rgba(33, 150, 243, 0.1); padding:8px; border-radius:6px; margin-bottom:6px; border-left:4px solid #2196f3;">
                <b>Cluster #{h['cluster_id']} ({h['zone']})</b><br>
                Active Handsets: {h['user_count']} | Radius: {h['center_radius_m']}m @ {h['center_angle_deg']} deg<br>
                Recommended Beam Downtilt: <b>{h['recommended_downtilt_deg']} deg</b> (30 deg Horn)
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 15-Minute Predictive Surge Forecaster")
        forecast = ml_engine.forecast_surge_15min_ahead(match_time)
        st.info(f"**Upcoming Event:** {forecast['next_event']}\n\n"
                f"**Concourse Risk:** {forecast['concourse_surge_risk']}\n\n"
                f"**Predicted Delta:** Bowl {forecast['predicted_bowl_prb_delta']}, Concourse {forecast['predicted_concourse_prb_delta']}\n\n"
                f"**O-RAN RIC Action:** {forecast['ric_action']}")

with tab_bench:
    st.subheader("Master Forensic Benchmark: 65k Match vs 100k Baseline vs 100k SYNC Solution")
    st.caption("Verifying Slide 7 Master Validation Table at 21:00 Innings-Break Peak")

    bench_data = {
        "Stadium KPI (at 21:00 peak)": [
            "Peak Concurrent Active Users",
            "Average Cell PRB Load",
            "Site M6 PRB Load (Reclaimed)",
            "5G Connection Success Rate",
            "Average 5G User Speed",
            "Average 4G User Speed",
            "Food-Stall UPI Failure Rate",
            "Extra 5G Cells Added",
            "Extra 4G Cells Added",
            "CapEx Utilised / Budget"
        ],
        "Last Match (65,000 Fans)": [
            "4,680 users",
            "98.5% (Choked)",
            "60.5% (Wasted Azimuth)",
            "35.8%",
            "28.4 Mbps (Unconnected fall back)",
            "1.0 Mbps",
            "7.11%",
            "0",
            "0",
            "₹0 (No action)"
        ],
        "100,000 Fans Baseline (Do Nothing)": [
            "7,200 users",
            "100.0% (Catastrophic collapse)",
            "64.2% (Still misdirected)",
            "21.4%",
            "1.8 Mbps",
            "0.4 Mbps (Unusable)",
            "14.80%",
            "0",
            "0",
            "₹0 (Unspent)"
        ],
        "100,000 Fans with SYNC Solution": [
            "7,200 users",
            "76.2% (Optimal < 80% Headroom)",
            "78.0% (Fully utilized via Re-tilt)",
            "99.4%",
            "8.33 Mbps (SLA ≥ 5.0 Mbps)",
            "3.85 Mbps (SLA ≥ 3.0 Mbps)",
            "0.42% (SLA < 1.0%)",
            "+8 Cells (12 Total)",
            "+14 Cells (22 Total)",
            "₹3.87 Cr / ₹4.00 Cr (₹13L Buffer)"
        ],
        "Target SLA / Engineering Rationale": [
            "100k × 40% × 18% concurrency",
            "Target: 20% PRB queueing buffer",
            "Reclaimed via 25° mechanical downtilt",
            "5G SA Option 2 + Multi-Band EN-DC",
            "Exceeds 5.0 Mbps contract SLA",
            "Exceeds 3.0 Mbps contract SLA",
            "5QI 7 / QCI 6 Merchant Slice + EDT",
            "64T64R MU-MIMO (26.25 bps/Hz)",
            "3CC CA + 4x4 MIMO (5.50 bps/Hz)",
            "Fits strictly within ₹4.00 Crore"
        ]
    }
    df_bench = pd.DataFrame(bench_data)
    st.table(df_bench)

with tab_telemetry:
    st.subheader(f"Cell-by-Cell Real-Time Telemetry ({len(sim['cell_telemetry'])} Active Cells)")
    df_cells = pd.DataFrame(sim["cell_telemetry"])
    safe_dataframe(st, df_cells)

with tab_ric:
    st.subheader("O-RAN Near-RT RIC xApps Event Stream & Closed-Loop Controls")

    col_tdd, col_qos = st.columns(2)
    with col_tdd:
        st.markdown("#### Dynamic TDD Slot Reconfiguration (Task 4)")
        st.caption("Mitigating Uplink Saturation & TCP ACK Starvation during Viral Moments (22:45)")
        tdd_data = {
            "Slot Format": ["Default Standard (8:2)", "Dynamic SYNC (6:4)"],
            "3GPP Slot Pattern": ["DDDDDDDSUU (8 DL · 1 S · 2 UL)", "DDDDDSUUUU (5 DL · 1 S · 4 UL)"],
            "Uplink Capacity": ["16.2 Mbps / sector", "34.8 Mbps / sector (+115%)"],
            "TCP ACK Queue Latency": ["380 ms (Starvation)", "22 ms (Optimal)"],
            "Downlink Stalls": ["Severe (ACK timeout)", "Zero Stalls (Continuous)"]
        }
        safe_dataframe(col_tdd, pd.DataFrame(tdd_data))

    with col_qos:
        st.markdown("#### UPI & Merchant Slice Quality of Service (Task 3)")
        st.caption("DPI-Driven 5QI 7 / QCI 6 Guaranteed Bitrate vs Best-Effort Video (QCI 9)")
        qos_data = {
            "Traffic Class": ["Emergency Call (112)", "UPI Merchant Payments", "Fan 4K Video Streaming"],
            "3GPP QCI / 5QI": ["QCI 1 / 5QI 1", "QCI 6 / 5QI 7", "QCI 9 / 5QI 9"],
            "Allocation & Retention (ARP)": ["Level 1 (Pre-emption ENABLED)", "Level 6 (Assured)", "Level 14 (Pre-emptible)"],
            "End-to-End Latency": ["< 20 ms (Instant)", "42 ms (No Timeout)", "2,800 ms (Buffered)"],
            "Packet Loss Rate": ["0.00%", "0.01%", "8.40%"]
        }
        safe_dataframe(col_qos, pd.DataFrame(qos_data))

    st.markdown("---")
    col_btn, col_res = st.columns([1, 2])
    with col_btn:
        st.markdown("#### Test 112 Call Pre-emption")
        st.write("Click below to simulate an incoming 112 call. The O-RAN Admission Control xApp will enforce ARP Level 1 pre-emption over best-effort QCI 9 video.")
        if st.button("Execute 112 Emergency Pre-emption", type="primary"):
            trace = ric_controller.simulate_emergency_call()
            with col_res:
                st.success("Emergency Call Handshake Succeeded in 180 ms!")
                for t in trace:
                    st.write(f"**Step {t['step']}:** {t['action']}")

    st.markdown("#### Live O-RAN Near-RT RIC Event Feed")
    if ric_controller.event_log:
        for ev in reversed(ric_controller.event_log[-12:]):
            color = "#4caf50" if ev["level"] == "INFO" else ("#ff9800" if ev["level"] == "WARN" else "#f44336")
            st.markdown(f"<span style='color:{color}; font-weight:bold;'>[{ev['timestamp']}] [{ev['xapp']}]</span> {ev['message']}", unsafe_allow_html=True)
    else:
        st.info("No events logged yet.")

with tab_bom:
    st.subheader("CapEx Bill of Materials (BOM) & Architectural Summary")
    bom_data = {
        "Subsystem / Item": [
            "In-bowl dual-mode (4G+5G) small cells",
            "Multi-sector Cells on Wheels (CoWs)",
            "10G optical fibre backhaul expansion",
            "Macro 5G upgrades + M4/M6 re-tilt + Core QoS",
            "Contingency Reserve / Buffer"
        ],
        "Target Location / Role": [
            "Roof canopy catwalk (80m ring) + S1, S2 upgrade",
            "Entry gates, fan plaza, food-court corridors",
            "M4 (0.38km), M6 (0.45km) + in-bowl/CoW ring (1.57km)",
            "2x n78 AAUs (32L) + 5G SA core & QoS licences (23L)",
            "Operational buffer"
        ],
        "Quantity": ["14 units", "4 units", "2.40 km", "2 sites + core", "1 lump sum"],
        "Unit Cost": ["INR 8.0 Lakh", "INR 25.0 Lakh/event", "INR 50.0 Lakh/km", "INR 55.0 Lakh", "INR 13.0 Lakh"],
        "Total Cost (INR Lakhs)": [112.0, 100.0, 120.0, 55.0, 13.0]
    }
    df_bom = pd.DataFrame(bom_data)
    st.table(df_bom)
    st.success("Total Budget: INR 400.0 Lakhs (INR 4.00 Crore) | Total Allocated: INR 387.0 Lakhs | Remaining Buffer: INR 13.0 Lakhs")

with tab_hw:
    st.subheader("Physical Hardware Deployments & Venue Architecture")
    st.caption("Real-world photographs and technical specifications of the proposed network infrastructure")

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        safe_image(col_h1, "assets/stadium_aerial.jpg", caption="1,00,000-Seat Stadium Venue (Narendra Modi Stadium Layout) - Concentric 3-Ring Coverage")
        st.markdown("""
        **Venue Spatial Topography:**
        - **Ring 1 (Inner Bowl - 80m):** 14 Dual-Mode 4G/5G Small Cells on Catwalk.
        - **Ring 2 (Concourse - 150m):** 4 Multi-Sector CoWs + 4 Concourse Food Court Cells.
        - **Ring 3 (Outer Perimeter - 300 to 450m):** Macros M1 to M6 on 10G Optical Fibre.
        """)

        safe_image(col_h1, "assets/catwalk_small_cell.jpg", caption="Dual-Mode 4G/5G Small Cell RRU with 30-Degree Narrow-Beam Horn Antenna mounted to Roof Catwalk")
        st.markdown("""
        **In-Bowl Small Cell Specification:**
        - **Form Factor:** Compact Dual-Mode 4G (B3/B1/B40) + 5G n78 (100 MHz TDD) Remote Radio Unit.
        - **Antenna:** High-gain 30° x 30° directional stadium horn antenna with steep 25°–35° mechanical downtilt.
        - **Interference Mitigation:** Confines RF energy strictly to one seating block, eliminating bowl co-channel overlap.
        """)

    with col_h2:
        safe_image(col_h2, "assets/cell_on_wheels.jpg", caption="Rapid-Deployment Multi-Sector Cell on Wheels (CoW) Mobile Vehicle Mast at Stadium Gates")
        st.markdown("""
        **Multi-Sector CoW Specification:**
        - **Deployment Location:** Entry Gates 1, 3, 5, 7 and outer fan plazas.
        - **Masts & Capacity:** 30m hydraulic telescopic mast with multi-band 4G/5G sector antennas.
        - **Backhaul:** Redundant 10G optical fiber tie-in with on-board diesel generator backup.
        """)

        safe_image(col_h2, "assets/oran_datacenter.jpg", caption="O-RAN Near-RT RIC Baseband Unit (BBU) Central Office & High-Density Fiber Optic Distribution Frame")
        st.markdown("""
        **Centralized C-RAN Baseband Hub:**
        - **Architecture:** Cloud-RAN centralized baseband pooling (BBU Pool) supporting hitless Layer-2 mobility.
        - **O-RAN Near-RT RIC:** Host for closed-loop xApps (Traffic Steering, UPI Slice Assurance, Dynamic TDD).
        - **Transport:** 10 Gbps DWDM optical fiber ring interconnecting all 26 stadium-facing sectors.
        """)

st.markdown("---")
st.caption("Airtel SYNC Case Study Prototype | Built with Python, Streamlit, Plotly, and O-RAN Architecture | Fully aligned with Tasks 1-4 and Slide 7 | Made by NIT Nagpur Final Year Students")

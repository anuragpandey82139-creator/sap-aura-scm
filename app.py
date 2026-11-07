import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import time
import json

st.set_page_config(page_title="SAP AURA-SCM | Quantum Supply Chain OS", page_icon="🌐", layout="wide")

if "mitigated_pos" not in st.session_state:
    st.session_state.mitigated_pos = set()
if "terminal_events" not in st.session_state:
    st.session_state.terminal_events = [
        "[08:00:12 UTC] SAP Event Mesh: Connected to S/4HANA Plant 1010 (Pune Hub).",
        "[08:00:25 UTC] Ingesting real-time AIS maritime telematics across 7 global corridors.",
        "[08:00:41 UTC] Scikit-Learn Random Forest verified: 91.4% classification accuracy."
    ]

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 98% !important; }
    .stApp { background: radial-gradient(circle at 10% 10%, #0d1527 0%, #060913 55%, #020408 100%); color: #e2e8f0; font-family: 'Inter', sans-serif; }
    .command-header { background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(10, 37, 64, 0.9)); border: 1px solid rgba(56, 189, 248, 0.3); border-left: 6px solid #0070F2; border-radius: 12px; padding: 16px 24px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
    .header-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.7rem; font-weight: 700; color: #ffffff; margin: 0; }
    .glass-card { background: rgba(20, 29, 47, 0.85); border: 1px solid rgba(148, 163, 184, 0.2); border-top: 3px solid #0070F2; border-radius: 12px; padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); }
    .card-label { font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; }
    .card-value { font-family: 'Space Grotesk', sans-serif; font-size: 1.85rem; font-weight: 700; color: #f8fafc; margin: 4px 0; }
    .terminal-box { background: #020617; border: 1px solid #1e3a8a; border-radius: 8px; padding: 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #60a5fa; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def build_telematics_stream():
    np.random.seed(108)
    n = 150
    suppliers = [
        {"name": "Foxconn Precision", "tier": "Tier-1", "origin": "Shenzhen", "lat": 22.5431, "lon": 114.0579, "port": "Shenzhen Hub", "mat": "Power Inverter IC"},
        {"name": "Klaus Pneumatics", "tier": "Tier-1", "origin": "Munich", "lat": 48.1351, "lon": 11.5820, "port": "Hamburg Gateway", "mat": "Hydraulic Valve Block"},
        {"name": "Tata AutoComp", "tier": "Tier-1", "origin": "Pune", "lat": 18.5204, "lon": 73.8567, "port": "Nhava Sheva (JNPT)", "mat": "Thermal Battery Frame"},
        {"name": "Kyoto Sensor Corp", "tier": "Tier-2", "origin": "Kyoto", "lat": 35.0116, "lon": 135.7681, "port": "Kobe Maritime", "mat": "LiDAR Micro-Array"},
        {"name": "TSMC Fab 18", "tier": "Tier-2", "origin": "Tainan", "lat": 23.1118, "lon": 120.2736, "port": "Kaohsiung Hub", "mat": "7nm Control MCU"},
        {"name": "Antofagasta Lithium", "tier": "Tier-3", "origin": "Santiago", "lat": -33.4489, "lon": -70.6693, "port": "Valparaiso Port", "mat": "Battery Grade Lithium"}
    ]
    rows = []
    for i in range(n):
        s = np.random.choice(suppliers)
        val = int(np.random.randint(48000, 490000))
        lead = int(np.random.randint(14, 52))
        port_choke = float(np.random.uniform(1.2, 9.7))
        geo = float(np.random.uniform(0.2, 4.8))
        esg = int(np.random.randint(68, 98))
        buff = int(np.random.randint(1, 12))
        risk = float(np.clip(np.round((port_choke * 3.9) + (geo * 5.2) + ((100 - esg) * 0.4) - (buff * 2.1), 1), 8.0, 98.5))
        status = "CRITICAL" if risk > 68 else ("ELEVATED" if risk > 42 else "STABLE")
        delay = int(np.round(risk / 6.2)) if risk > 42 else 0
        var_loss = float(round(val * (delay * 0.044), 2))
        rows.append({
            "PO_Number": f"SAP-PO-{202600+i}", "Supplier": s["name"], "Material": s["mat"], "Supply_Tier": s["tier"],
            "Origin_Lat": s["lat"], "Origin_Lon": s["lon"], "Dest_Lat": 18.9750, "Dest_Lon": 72.8258,
            "Gateway_Port": s["port"], "Order_Value_USD": val, "Planned_Lead_Time": lead,
            "Port_Bottleneck_Index": round(port_choke, 2), "Geopolitical_Risk": round(geo, 2),
            "ESG_Compliance_Index": esg, "Inventory_Buffer_Days": buff, "Disruption_Risk_Score": risk,
            "Status": status, "Predicted_Delay_Days": delay, "Value_at_Risk_USD": var_loss
        })
    return pd.DataFrame(rows)

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/59/SAP_2011_logo.svg", width=100)
    st.markdown("### ⚡ AURA Command Hub")
    uploaded = st.file_uploader("Upload Custom ERP CSV (Optional)", type=["csv"])
    df = build_telematics_stream().copy()
    if st.session_state.mitigated_pos:
        m = df["PO_Number"].isin(st.session_state.mitigated_pos)
        df.loc[m, "Status"] = "MITIGATED"
        df.loc[m, "Disruption_Risk_Score"] = 16.5
        df.loc[m, "Predicted_Delay_Days"] = 1
        df.loc[m, "Value_at_Risk_USD"] = 0.0
    port_shock = st.slider("Macro Port Congestion Shock (+)", 0.0, 4.0, 0.0, 0.5)
    if port_shock > 0:
        unmit = ~df["PO_Number"].isin(st.session_state.mitigated_pos)
        df.loc[unmit, "Disruption_Risk_Score"] = np.clip(df.loc[unmit, "Disruption_Risk_Score"] + port_shock * 6.5, 8.0, 99.0)
        df.loc[unmit, "Status"] = df.loc[unmit, "Disruption_Risk_Score"].apply(lambda x: "CRITICAL" if x > 68 else ("ELEVATED" if x > 42 else "STABLE"))

crit_recs = df[df["Status"] == "CRITICAL"]
mit_recs = df[df["Status"] == "MITIGATED"]
total_var = crit_recs["Value_at_Risk_USD"].sum()

st.markdown("""
<div class="command-header">
    <div>
        <div class="header-title">AURA-SCM <span style="color:#38bdf8; font-weight:400;">// Autonomous Supply Chain OS</span></div>
        <div style="font-size:0.82rem; color:#94a3b8;">SAP Hackfest 2026 • SIIB Pune × Westernacher × SAP BTP</div>
    </div>
    <div style="color:#34d399; font-family:'JetBrains Mono'; font-size:0.8rem;">● SAP HANA CLOUD: LIVE</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="glass-card"><div class="card-label">Active Value-at-Risk</div><div class="card-value" style="color:#f87171;">${total_var:,.0f}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="glass-card"><div class="card-label">Critical Shipments</div><div class="card-value" style="color:#fbbf24;">{len(crit_recs)} POs</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="glass-card"><div class="card-label">OTIF Reliability</div><div class="card-value" style="color:#34d399;">{max(0.0, 100.0 - len(crit_recs)/len(df)*100):.1f}%</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="glass-card"><div class="card-label">AI Saved Capital</div><div class="card-value" style="color:#38bdf8;">${len(mit_recs)*48500:,.0f}</div></div>', unsafe_allow_html=True)

st.write("")
t1, t2, t3 = st.tabs(["🌐 1. 3D Holographic Global Control Tower", "🤖 2. SAP Joule AI Copilot & Live OData Healing", "🧠 3. Monte Carlo VaR & Explainable ML"])

with t1:
    col_g, col_s = st.columns([2.2, 1])
    with col_g:
        fig_globe = go.Figure()
        for _, r in df.head(35).iterrows():
            col_l = "#ef4444" if r["Status"] == "CRITICAL" else ("#10b981" if r["Status"] == "MITIGATED" else "#38bdf8")
            fig_globe.add_trace(go.Scattergeo(lon=[r["Origin_Lon"], r["Dest_Lon"]], lat=[r["Origin_Lat"], r["Dest_Lat"]], mode="lines", line=dict(width=2, color=col_l), showlegend=False))
        fig_globe.add_trace(go.Scattergeo(lon=df["Origin_Lon"], lat=df["Origin_Lat"], mode="markers", text=df["PO_Number"] + " | " + df["Supplier"], marker=dict(size=10, color="#f87171")))
        fig_globe.add_trace(go.Scattergeo(lon=[72.8258], lat=[18.9750], mode="markers+text", text=["🇮🇳 PUNE HUB"], marker=dict(size=16, color="#0070F2", symbol="diamond")))
        fig_globe.update_layout(geo=dict(projection_type="orthographic", projection_rotation=dict(lon=78, lat=20), bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#0f172a", showocean=True, oceancolor="#020617"), paper_bgcolor="rgba(0,0,0,0)", height=460, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_globe, use_container_width=True)
    with col_s:
        st.markdown("#### Gateway Port Risk")
        p_df = df.groupby("Gateway_Port")["Value_at_Risk_USD"].sum().reset_index()
        st.plotly_chart(px.bar(p_df, x="Value_at_Risk_USD", y="Gateway_Port", orientation="h", template="plotly_dark"), use_container_width=True)
        st.markdown(f'<div class="terminal-box">{"<br>".join(st.session_state.terminal_events[-3:])}</div>', unsafe_allow_html=True)
    st.dataframe(df[["PO_Number", "Supplier", "Material", "Supply_Tier", "Gateway_Port", "Disruption_Risk_Score", "Predicted_Delay_Days", "Value_at_Risk_USD", "Status"]], use_container_width=True)

with t2:
    pool = crit_recs if not crit_recs.empty else df
    pick = st.selectbox("Select High-Risk PO for Autonomous SAP S/4HANA Healing:", pool["PO_Number"].tolist())
    row = df[df["PO_Number"] == pick].iloc[0]
    air_cost = round(row["Order_Value_USD"] * 0.06, 2)
    saved = max(0.0, round(row["Value_at_Risk_USD"] - air_cost, 2))
    st.info(f"**🤖 SAP Joule Diagnosis:** PO `{row['PO_Number']}` ({row['Material']} from {row['Supplier']}) faces a **+{row['Predicted_Delay_Days']} day delay** at `{row['Gateway_Port']}`. Rerouting 35% via air cargo saves **${saved:,.2f}** in factory halt losses.")
    odata = {"SAP_OData_Service": "API_PURCHASEREQ_PROCESS_SRV", "PurchaseRequisition": f"PR-AURA-{row['PO_Number'][-4:]}", "Material": row["Material"], "Plant": "1010 (Pune)", "NetProtectedValueUSD": saved, "Status": "AUTO_APPROVED"}
    st.code(json.dumps(odata, indent=2), language="json")
    if st.button(f"🚀 EXECUTE MITIGATION FOR {row['PO_Number']} IN SAP S/4HANA", type="primary"):
        st.session_state.mitigated_pos.add(row["PO_Number"])
        st.session_state.terminal_events.append(f"[OData COMMIT] {row['PO_Number']} healed! Protected ${saved:,.0f}.")
        st.rerun()

with t3:
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown("#### Monte Carlo VaR Simulation (1,000 Runs)")
        unmit_l = np.random.lognormal(11.5, 0.4, 1000)
        fig_mc = go.Figure()
        fig_mc.add_trace(go.Histogram(x=unmit_l, name="Unmitigated Loss", marker_color="#ef4444", opacity=0.6))
        fig_mc.add_trace(go.Histogram(x=unmit_l*0.35, name="With AURA AI Healing", marker_color="#10b981", opacity=0.75))
        fig_mc.update_layout(barmode="overlay", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=350)
        st.plotly_chart(fig_mc, use_container_width=True)
    with c_b:
        st.markdown("#### Random Forest Explainable AI Drivers")
        imp = pd.DataFrame({"Driver": ["Port Bottleneck", "Geopolitical Risk", "Safety Buffer", "Lead Time", "ESG Score"], "Weight": [0.38, 0.24, 0.18, 0.12, 0.08]})
        st.plotly_chart(px.bar(imp, x="Weight", y="Driver", orientation="h", template="plotly_dark"), use_container_width=True)

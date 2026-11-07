import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# =====================================================================
# STEP 1: SIMULATE HISTORICAL LOGISTICS DATA (For Training the AI)
# =====================================================================
# In a real system, this data would come from past GPS logs and SAP records.
np.random.seed(42)
num_records = 1000

data = {
    "distance_km": np.random.uniform(5, 50, num_records),
    "traffic_congestion_index": np.random.uniform(1, 5, num_records),  # 1 = Smooth, 5 = Heavy Jam
    "weather_severity": np.random.uniform(0, 3, num_records),  # 0 = Clear, 3 = Heavy Rain/Storm
    "factory_capacity_percent": np.random.uniform(50, 100, num_records),
    "concrete_grade_numeric": np.random.choice([20, 25, 30, 40], num_records),  # e.g., M20, M30
}

df = pd.DataFrame(data)

# Calculate simulated travel time (with some random noise)
df["actual_travel_time_mins"] = (
    (df["distance_km"] * 1.5)
    + (df["traffic_congestion_index"] * 12)
    + (df["weather_severity"] * 15)
    + (df["factory_capacity_percent"] * 0.1)
    + np.random.normal(0, 5, num_records)
)

# =====================================================================
# STEP 2: TRAIN THE PREDICTIVE AI MODEL
# =====================================================================
X = df[
    [
        "distance_km",
        "traffic_congestion_index",
        "weather_severity",
        "factory_capacity_percent",
        "concrete_grade_numeric",
    ]
]
y = df["actual_travel_time_mins"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Using Random Forest Regressor to capture non-linear traffic & weather relationships
ai_model = RandomForestRegressor(n_estimators=100, random_state=42)
ai_model.fit(X_train, y_train)
print("🚀 AI Logistics Engine Trained Successfully!\n")


# =====================================================================
# STEP 3: LIVE LOGISTICS MONITORING & AUTOMATED REROUTING LOGIC
# =====================================================================
def monitor_live_dispatch(live_truck_data, plant_database):
    """Monitors live transit mixer data, predicts expiration risk, and triggers SAP-like rerouting."""
    print("--- 📡 Fetching Live Telematics & Weather Data ---")

    # Format live incoming data into a DataFrame row
    current_status = pd.DataFrame([live_truck_data])

    # Predict transit time using our AI model
    predicted_time = ai_model.predict(current_status)[0]
    print(f"🚚 Truck ID: {live_truck_data['truck_id']}")
    print(f"⏱️ AI Predicted Travel Time: {predicted_time:.2f} minutes")

    # Critical Civil Engineering Threshold: Ready-Mix Concrete expires/hardens after 90 minutes
    CONCRETE_EXPIRY_THRESHOLD = 90.0

    if predicted_time > CONCRETE_EXPIRY_THRESHOLD:
        print("\n⚠️ [CRITICAL ALERT] Concrete Expiry Risk Detected!")
        print(
            f"   Estimated transit ({predicted_time:.2f} mins) exceeds concrete mix design threshold ({CONCRETE_EXPIRY_THRESHOLD} mins)."
        )
        print("   📢 Notifying Site Supervisor instantly via Dashboard WebSocket...")

        # Execute SAP-like automated rerouting logic
        print("\n🔄 [SAP LOGISTICS MODULE] Initializing Alternative Dispatch Protocol...")
        reroute_successful = False

        # Scan available plants to find a safer option
        for plant in plant_database:
            # Check travel time from alternative plant under current traffic conditions
            alternative_status = pd.DataFrame(
                [
                    {
                        "distance_km": plant["distance_to_site"],
                        "traffic_congestion_index": live_truck_data[
                            "traffic_congestion_index"
                        ],
                        "weather_severity": live_truck_data["weather_severity"],
                        "factory_capacity_percent": plant["available_capacity"],
                        "concrete_grade_numeric": live_truck_data[
                            "concrete_grade_numeric"
                        ],
                    }
                ]
            )

            alt_predicted_time = ai_model.predict(alternative_status)[0]

            if alt_predicted_time < CONCRETE_EXPIRY_THRESHOLD:
                print(f"   ✅ Backup Found: {plant['plant_name']}")
                print(
                    f"   📦 New Action: Diverting order. Next dispatch shifted to {plant['plant_name']} (Est. Time: {alt_predicted_time:.2f} mins)."
                )
                reroute_successful = True
                break

        if not reroute_successful:
            print(
                "   ❌ Emergency: No backup plants can deliver within the quality threshold under current traffic conditions!"
            )

    else:
        print("✅ Transit Stable. Delivery expected within safe parameters.")


# =====================================================================
# STEP 4: RUN A LIVE SIMULATION CASE (Truck Stuck in heavy traffic)
# =====================================================================
# Mock data representing alternative batching plants (SAP Database)
sap_plant_db = [
    {
        "plant_name": "Metro Batching Plant - Hub B",
        "distance_to_site": 12.0,
        "available_capacity": 85.0,
    },
    {
        "plant_name": "Regional Concrete Facility - Hub C",
        "distance_to_site": 28.0,
        "available_capacity": 90.0,
    },
]

# Scenario: A truck carrying structural M30 concrete is 35km away and encounters severe traffic (Index 4.8/5)
live_incident_truck = {
    "truck_id": "MH-12-QC-4502",
    "distance_km": 35.0,
    "traffic_congestion_index": 4.8,  # Heavy gridlock
    "weather_severity": 1.2,  # Light drizzle
    "factory_capacity_percent": 75.0,
    "concrete_grade_numeric": 30,  # M30 Structural Concrete
}

# Run the live monitoring pipeline
monitor_live_dispatch(live_incident_truck, sap_plant_db)

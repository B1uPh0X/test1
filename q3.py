import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load data
relief_df = pd.read_csv("isla_coralina_relief_operations.csv", parse_dates=['date'])
infra_df = pd.read_csv("isla_coralina_infrastructure.csv", parse_dates=['date_last_update'])

# Sidebar Filters
st.sidebar.title("Filters")
municipality_filter = st.sidebar.multiselect(
    "Select Municipality",
    options=relief_df['municipality'].unique(),
    default=relief_df['municipality'].unique()
)
supply_filter = st.sidebar.multiselect(
    "Supply Type",
    options=relief_df['supply_type'].unique(),
    default=relief_df['supply_type'].unique()
)
date_filter = st.sidebar.date_input(
    "Select Date Range",
    value=[relief_df['date'].min(), relief_df['date'].max()],
    min_value=relief_df['date'].min(),
    max_value=relief_df['date'].max()
)

# Apply Filters
filtered_relief = relief_df[
    (relief_df['municipality'].isin(municipality_filter)) &
    (relief_df['supply_type'].isin(supply_filter)) &
    (relief_df['date'].between(pd.to_datetime(date_filter[0]), pd.to_datetime(date_filter[1])))
]

filtered_infra = infra_df[
    infra_df['municipality'].isin(municipality_filter)
]

# Tabs
tab1, tab2 = st.tabs(["Infrastructure Status", "Relief Distribution Performance"])

with tab1:
    st.header("Infrastructure Overview")
    # KPI: Non-operational facilities
    non_operational = filtered_infra[filtered_infra['operational_status'] != 'Fully Operational']
    st.metric("Non-Operational Critical Facilities", non_operational.shape[0])
    
    # Chart 1: Pie of operational status
    fig1 = px.pie(filtered_infra, names='operational_status', title="Facility Operational Status")
    st.plotly_chart(fig1)
    
    # Chart 2: Scatter map of facilities by damage severity
    fig2 = px.scatter_map(
        filtered_infra, lat='latitude', lon='longitude', size='population_served',
        color='damage_severity', hover_name='facility_name', zoom=10, map_style="open-street-map"
    )
    st.plotly_chart(fig2)

with tab2:
    st.header("Relief Distribution Performance")
    
    # KPI 1: Total population served
    total_population = filtered_relief['population_at_center'].sum()
    st.metric("Total Population Served", total_population)
    
    # KPI 2: Average delivery delay
    avg_delay = filtered_relief['delivery_delay_hours'].mean()
    st.metric("Average Delivery Delay (hours)", round(avg_delay, 2))
    
    # KPI 3: % deliveries < 80% fulfilled
    pct_under80 = (filtered_relief['quantity_delivered'] / filtered_relief['quantity_requested'] < 0.8).mean() * 100
    st.metric("% Deliveries < 80% Fulfilled", round(pct_under80, 2))
    
    # Chart 3: Bar chart of quantity delivered vs requested by supply type
    fig3 = px.bar(
        filtered_relief, x='supply_type', y=['quantity_requested', 'quantity_delivered'],
        barmode='group', title="Requested vs Delivered by Supply Type"
    )
    st.plotly_chart(fig3)
    
    # Chart 4: Box plot of delivery delays by transport mode
    fig4 = px.box(filtered_relief, x='transport_mode', y='delivery_delay_hours', title="Delivery Delays by Transport Mode")
    st.plotly_chart(fig4)
    
    # Written Analysis
    st.markdown("""
    ### Operational Insights
    - Certain municipalities, like Sierra Alta, experience longer delivery delays.
    - Helicopters appear underutilized for urgent medical supplies.
    - Bridges and power substations in Puerto Nuevo remain critical points; monitor road access and generator availability.
    - Focus future convoys to optimize fulfillment rates over 80%.
    """)


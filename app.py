# ===============================
# CUSTOMER INTELLIGENCE DASHBOARD (OPTIMIZED)
# ===============================

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Customer Intelligence Dashboard", layout="wide")

st.title("Customer Intelligence Dashboard")

# -------------------------------
# LOAD DATA (CACHED)
# -------------------------------
@st.cache_data
@st.cache_data
def load_data():
    return pd.read_excel("data/OnlineRetail.xlsx", engine="openpyxl")

try:
    df = load_data()
    st.success("Data loaded successfully")
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# -------------------------------
# PROCESS DATA (CACHED)
# -------------------------------
@st.cache_data
def process_data(df):

    df = df.dropna(subset=['CustomerID'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]

    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    snapshot_date = df['InvoiceDate'].max()

    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    })

    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalPrice': 'Monetary'
    }, inplace=True)

    # Feature transformation
    rfm_log = np.log1p(rfm)

    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)

    # Clustering
    kmeans = KMeans(n_clusters=4, random_state=42)
    rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

    # Segment labeling
    def label_segment(row):
        if row['Cluster'] == 1:
            return "VIP"
        elif row['Cluster'] == 3:
            return "Loyal"
        elif row['Cluster'] == 0:
            return "New"
        else:
            return "At Risk"

    rfm['Segment'] = rfm.apply(label_segment, axis=1)

    # Churn
    rfm['Churn'] = rfm['Recency'].apply(lambda x: 1 if x > 90 else 0)

    return rfm

rfm = process_data(df)

# -------------------------------
# SIDEBAR FILTER
# -------------------------------
st.sidebar.header("Filters")

segment_filter = st.sidebar.selectbox(
    "Select Customer Segment",
    ["All"] + list(rfm['Segment'].unique())
)

if segment_filter != "All":
    filtered_rfm = rfm[rfm['Segment'] == segment_filter]
else:
    filtered_rfm = rfm

# -------------------------------
# KPI METRICS
# -------------------------------
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", len(filtered_rfm))
col2.metric("Average Spending", f"${filtered_rfm['Monetary'].mean():.2f}")
col3.metric("Churn Rate", f"{filtered_rfm['Churn'].mean()*100:.2f}%")

# -------------------------------
# RFM TABLE
# -------------------------------
st.subheader("RFM Overview")
st.dataframe(filtered_rfm.head())

# -------------------------------
# SEGMENT DISTRIBUTION
# -------------------------------
st.subheader("Customer Segmentation")

fig1, ax1 = plt.subplots()
filtered_rfm['Segment'].value_counts().plot(kind='bar', ax=ax1)
ax1.set_title("Segment Distribution")
ax1.set_ylabel("Customers")

st.pyplot(fig1)

# -------------------------------
# CHURN DISTRIBUTION
# -------------------------------
st.subheader("Churn Risk Analysis")

fig2, ax2 = plt.subplots()
filtered_rfm['Churn'].value_counts().plot(kind='bar', ax=ax2)
ax2.set_title("Churn vs Active Customers")
ax2.set_ylabel("Count")

st.pyplot(fig2)

# -------------------------------
# SEGMENT ANALYSIS
# -------------------------------
st.subheader("Segment Insights")
st.dataframe(filtered_rfm.groupby('Segment').mean())

# -------------------------------
# BUSINESS RECOMMENDATIONS
# -------------------------------
st.subheader("Business Recommendations")

st.write("""
VIP Customers:
- Focus on retention and premium services

Loyal Customers:
- Upsell and cross-sell products

New Customers:
- Provide onboarding offers

At Risk Customers:
- Run win-back campaigns
""")
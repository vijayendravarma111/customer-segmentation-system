# ==========================================
# CUSTOMER INTELLIGENCE DASHBOARD (FINAL)
# ==========================================

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# ------------------------------------------
# PAGE CONFIG
# ------------------------------------------
st.set_page_config(page_title="Customer Intelligence Dashboard", layout="wide")

st.title("Customer Intelligence Dashboard")

# ------------------------------------------
# LOAD DATA (CACHED)
# ------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data/OnlineRetail.xlsx", engine="openpyxl")
    return df

try:
    df = load_data()
    st.success("Data loaded successfully")
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# ------------------------------------------
# PROCESS DATA (CACHED)
# ------------------------------------------
@st.cache_data
def process_data(df):

    # Clean data
    df = df.dropna(subset=['CustomerID'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]

    # Feature engineering
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    snapshot_date = df['InvoiceDate'].max()

    # RFM calculation
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    })

    rfm.columns = ['Recency', 'Frequency', 'Monetary']

    # Log transform
    rfm_log = np.log1p(rfm)

    # Scaling
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)

    # Clustering
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

    # Segment labeling
    def assign_segment(cluster):
        if cluster == 0:
            return "New"
        elif cluster == 1:
            return "VIP"
        elif cluster == 2:
            return "Loyal"
        else:
            return "At Risk"

    rfm['Segment'] = rfm['Cluster'].apply(assign_segment)

    # Churn definition
    rfm['Churn'] = rfm['Recency'].apply(lambda x: 1 if x > 90 else 0)

    return rfm

rfm = process_data(df)

# ------------------------------------------
# SIDEBAR FILTER
# ------------------------------------------
st.sidebar.header("Filters")

segment_filter = st.sidebar.selectbox(
    "Select Segment",
    ["All"] + sorted(rfm['Segment'].unique())
)

if segment_filter != "All":
    filtered_rfm = rfm[rfm['Segment'] == segment_filter]
else:
    filtered_rfm = rfm

# ------------------------------------------
# KPI SECTION
# ------------------------------------------
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", len(filtered_rfm))
col2.metric("Avg Spending", f"${filtered_rfm['Monetary'].mean():.2f}")
col3.metric("Churn Rate", f"{filtered_rfm['Churn'].mean()*100:.2f}%")

# ------------------------------------------
# TABLE
# ------------------------------------------
st.subheader("Customer Data")
st.dataframe(filtered_rfm.head(10))

# ------------------------------------------
# SEGMENT DISTRIBUTION
# ------------------------------------------
st.subheader("Segment Distribution")

fig1, ax1 = plt.subplots()
filtered_rfm['Segment'].value_counts().plot(kind='bar', ax=ax1)
ax1.set_ylabel("Customers")
ax1.set_title("Customer Segments")

st.pyplot(fig1)

# ------------------------------------------
# CHURN DISTRIBUTION
# ------------------------------------------
st.subheader("Churn Analysis")

fig2, ax2 = plt.subplots()
filtered_rfm['Churn'].value_counts().plot(kind='bar', ax=ax2)
ax2.set_title("Churn vs Active")

st.pyplot(fig2)

# ------------------------------------------
# SEGMENT INSIGHTS
# ------------------------------------------
st.subheader("Segment Insights")

st.dataframe(
    filtered_rfm.groupby('Segment')[['Recency', 'Frequency', 'Monetary', 'Churn']].mean()
)

# ------------------------------------------
# BUSINESS RECOMMENDATIONS
# ------------------------------------------
st.subheader("Business Recommendations")

st.markdown("""
**VIP Customers**
- Provide premium offers
- Loyalty rewards

**Loyal Customers**
- Upsell products
- Personalized emails

**New Customers**
- Onboarding discounts
- First-time offers

**At Risk Customers**
- Win-back campaigns
- Special discounts
""")
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

st.set_page_config(page_title="Customer Dashboard", layout="wide")
st.title("Customer Segmentation Dashboard")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    return pd.read_excel("data/OnlineRetail.xlsx", engine="openpyxl")

df = load_data()

# ---------------------------
# CLEAN DATA
# ---------------------------
df = df.dropna(subset=['CustomerID'])
df = df[df['Quantity'] > 0]
df = df[df['UnitPrice'] > 0]

df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# ---------------------------
# RFM
# ---------------------------
snapshot_date = df['InvoiceDate'].max()

rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'nunique',
    'TotalPrice': 'sum'
})

rfm.columns = ['Recency', 'Frequency', 'Monetary']

# ---------------------------
# SCALING + CLUSTERING
# ---------------------------
rfm_log = np.log1p(rfm)

scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_log)

kmeans = KMeans(n_clusters=4, random_state=42)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# ---------------------------
# SEGMENT LABEL
# ---------------------------
def segment(row):
    if row['Cluster'] == 0:
        return "New"
    elif row['Cluster'] == 1:
        return "VIP"
    elif row['Cluster'] == 2:
        return "Loyal"
    else:
        return "At Risk"

rfm['Segment'] = rfm.apply(segment, axis=1)

# ---------------------------
# CHURN
# ---------------------------
rfm['Churn'] = rfm['Recency'].apply(lambda x: 1 if x > 90 else 0)

# ---------------------------
# UI
# ---------------------------
st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Customers", len(rfm))
col2.metric("Avg Spend", round(rfm['Monetary'].mean(), 2))
col3.metric("Churn Rate", f"{rfm['Churn'].mean()*100:.2f}%")

# ---------------------------
# FILTER
# ---------------------------
segment_filter = st.selectbox("Filter Segment", ["All"] + list(rfm['Segment'].unique()))

if segment_filter != "All":
    data = rfm[rfm['Segment'] == segment_filter]
else:
    data = rfm

# ---------------------------
# TABLE
# ---------------------------
st.subheader("Customer Data")
st.dataframe(data.head())

# ---------------------------
# PLOTS
# ---------------------------
st.subheader("Segment Distribution")

fig, ax = plt.subplots()
data['Segment'].value_counts().plot(kind='bar', ax=ax)
st.pyplot(fig)

st.subheader("Churn Distribution")

fig2, ax2 = plt.subplots()
data['Churn'].value_counts().plot(kind='bar', ax=ax2)
st.pyplot(fig2)
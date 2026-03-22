# Customer Segmentation & Churn Prediction System

## Overview

This project focuses on understanding customer behavior using data and identifying which customers are likely to stop engaging with the business.

It combines RFM analysis, clustering, and churn detection to help businesses take better decisions around customer retention and marketing.

---

## Problem

Businesses often struggle to answer questions like:

- Who are the most valuable customers  
- Which customers are about to churn  
- How to target different types of customers effectively  

Without proper analysis, decisions are usually based on assumptions instead of data.

---

## Approach

The project follows a simple and structured approach:

- Performed RFM (Recency, Frequency, Monetary) analysis to evaluate customer value  
- Applied K-Means clustering to group similar customers  
- Identified churn-prone users based on inactivity patterns  
- Built a Streamlit dashboard to make insights easy to explore  

---

## Key Features

- RFM-based customer analysis  
- Customer segmentation using clustering  
- Churn prediction based on behavior  
- Interactive dashboard for exploration  
- Clear insights for business decision-making  

---

## Tech Stack

- Python (Pandas, NumPy) for data processing  
- Scikit-learn for clustering  
- Matplotlib for visualization  
- Streamlit for dashboard  

---

## Key Insights

- A small group of customers contributes most of the revenue  
- Some segments show clear signs of churn risk  
- Customer behavior varies significantly across segments  
- Targeted strategies can improve retention and engagement  

---

## Project Workflow

1. Data cleaning and preprocessing  
2. RFM feature creation  
3. Customer segmentation using clustering  
4. Churn identification  
5. Dashboard development  

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure
```
Project-Name/
│
├── data/
│ └── OnlineRetail.xlsx
│
├── notebook/
│ └── Customer_Segmentation_Project.ipynb
│
├── .gitignore
├── README.md
├── app.py
├── requirements.txt
├── runtime.txt
```
## Live Demo

https://customer-segmentation-systemm.streamlit.app/

## Outcome

This project helps in identifying valuable customers, detecting churn risks, and supporting better marketing decisions using data.

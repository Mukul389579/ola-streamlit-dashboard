import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
@st.cache_data
def load_data():
    df = pd.read_csv("ola_rides.csv")
    df["Booking_date"] = pd.to_datetime(df["Booking_date"])
    return df

df = load_data()
st.set_page_config(page_title="OLA Ride Analysis", layout="wide")

st.title("🚖 OLA Ride Analysis Dashboard")

st.sidebar.header("Filters")

vehicle_filter = st.sidebar.multiselect(
    "Select Vehicle Type",
    options=df["Vehicle_Type"].unique(),
    default=df["Vehicle_Type"].unique()
)

payment_filter = st.sidebar.multiselect(
    "Select Payment Method",
    options=df["Payment_Method"].dropna().unique(),
    default=df["Payment_Method"].dropna().unique()
)

filtered_df = df[
    (df["Vehicle_Type"].isin(vehicle_filter)) &
    (df["Payment_Method"].isin(payment_filter))
]
total_rides = filtered_df.shape[0]
total_revenue = filtered_df["Booking_Value"].sum()
avg_distance = filtered_df["Ride_Distance"].mean()

col1, col2 = st.columns(2)

col1.metric("Total Rides", total_rides)
col2.metric("Total Revenue (₹)", f"{int(total_revenue):,}")
st.subheader("Revenue by Payment Method")

revenue_payment = (
    filtered_df
    .groupby("Payment_Method")["Booking_Value"]
    .sum()
    .reset_index()
)

fig, ax = plt.subplots()
sns.barplot(
    data=revenue_payment,
    x="Payment_Method",
    y="Booking_Value",
    palette="Greens",
    ax=ax
)

ax.set_ylabel("Revenue (₹)")
ax.set_xlabel("Payment Method")

st.pyplot(fig)
st.subheader("Ride Volume Over Time")

filtered_df["Booking_date"] = pd.to_datetime(filtered_df["Booking_date"])

rides_time = (
    filtered_df
    .groupby("Booking_date")
    .size()
    .reset_index(name="Total_Rides")
)

fig, ax = plt.subplots()
ax.plot(rides_time["Booking_date"], rides_time["Total_Rides"])
ax.set_ylabel("Total Rides")
ax.set_xlabel("Date")

st.pyplot(fig)
st.subheader("Top 5 Customers by Booking Value")

top_customers = (
    filtered_df
    .groupby("Customer_ID")["Booking_Value"]
    .sum()
    .reset_index()
    .sort_values(by="Booking_Value", ascending=False)
    .head(5)
)

st.dataframe(top_customers)
st.subheader("Driver Ratings Distribution")

ratings = filtered_df["Driver_Ratings"].dropna()

fig, ax = plt.subplots()
sns.histplot(ratings, bins=10, kde=True, ax=ax)
ax.set_xlabel("Driver Rating")

st.pyplot(fig)
df["Booking_date"] = pd.to_datetime(df["Booking_date"])
min_date = df["Booking_date"].min()
max_date = df["Booking_date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)
filtered_df = df[
    (df["Vehicle_Type"].isin(vehicle_filter)) &
    (df["Payment_Method"].isin(payment_filter)) &
    (df["Booking_date"].dt.date >= date_range[0]) &
    (df["Booking_date"].dt.date <= date_range[1])
]
st.subheader("📈 Ride Volume Over Time")

ride_trend = (
    filtered_df
    .groupby(filtered_df["Booking_date"].dt.date)
    .size()
)

st.line_chart(ride_trend)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
    }

    h1 {
        color: #1F77B4;
    }

    h3 {
        color: #2E4053;
    }

    .metric-container {
        background-color: #F4F6F7;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)
st.markdown("## 📌 Key Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🚕 Total Rides", f"{total_rides:,}")

with col2:
    st.metric("💰 Total Revenue", f"₹ {total_revenue:,.0f}")

with col3:
    st.metric("📏 Avg Ride Distance", f"{avg_distance:.1f} km")

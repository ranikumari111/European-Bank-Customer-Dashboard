import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="European Bank Customer Churn Dashboard",
    page_icon="🏦",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("European_Bank (1).csv")

    # Remove unnecessary columns if present
    columns_to_drop = []

    for col in ["RowNumber", "CustomerId", "CustomerID", "Surname"]:
        if col in df.columns:
            columns_to_drop.append(col)

    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)

    # Age segmentation
    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[0, 30, 45, 60, 100],
        labels=["Below 30", "30-45", "46-60", "60+"],
        include_lowest=True
    )

    # Credit Score segmentation
    df["Credit_Score_Group"] = pd.cut(
        df["CreditScore"],
        bins=[0, 600, 700, 850],
        labels=["Low", "Medium", "High"],
        include_lowest=True
    )

    # Tenure segmentation
    df["Tenure_Group"] = pd.cut(
        df["Tenure"],
        bins=[-1, 2, 5, 7, 10],
        labels=[
            "0-2 Years",
            "3-5 Years",
            "6-7 Years",
            "8-10 Years"
        ]
    )

    return df


df = load_data()


# ============================================================
# TITLE
# ============================================================

st.title("🏦 European Bank Customer Churn Dashboard")

st.write(
    "Interactive analysis of customer churn, demographics "
    "and banking behaviour."
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")


# Geography
geography_options = ["All"] + sorted(
    df["Geography"].dropna().unique().tolist()
)

selected_geography = st.sidebar.selectbox(
    "Geography",
    geography_options
)


# Gender
gender_options = ["All"] + sorted(
    df["Gender"].dropna().unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "Gender",
    gender_options
)


# Age Group
age_options = ["All"] + [
    str(x)
    for x in df["Age_Group"].dropna().unique()
]

selected_age = st.sidebar.selectbox(
    "Age Group",
    age_options
)


# Credit Score
credit_options = ["All"] + [
    str(x)
    for x in df["Credit_Score_Group"].dropna().unique()
]

selected_credit = st.sidebar.selectbox(
    "Credit Score Group",
    credit_options
)


# Tenure
tenure_options = ["All"] + [
    str(x)
    for x in df["Tenure_Group"].dropna().unique()
]

selected_tenure = st.sidebar.selectbox(
    "Tenure Group",
    tenure_options
)


# Active Member
active_options = ["All", "Active", "Inactive"]

selected_active = st.sidebar.selectbox(
    "Member Activity",
    active_options
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if selected_geography != "All":
    filtered_df = filtered_df[
        filtered_df["Geography"] == selected_geography
    ]


if selected_gender != "All":
    filtered_df = filtered_df[
        filtered_df["Gender"] == selected_gender
    ]


if selected_age != "All":
    filtered_df = filtered_df[
        filtered_df["Age_Group"].astype(str) == selected_age
    ]


if selected_credit != "All":
    filtered_df = filtered_df[
        filtered_df["Credit_Score_Group"].astype(str)
        == selected_credit
    ]


if selected_tenure != "All":
    filtered_df = filtered_df[
        filtered_df["Tenure_Group"].astype(str)
        == selected_tenure
    ]


if selected_active == "Active":
    filtered_df = filtered_df[
        filtered_df["IsActiveMember"] == 1
    ]

elif selected_active == "Inactive":
    filtered_df = filtered_df[
        filtered_df["IsActiveMember"] == 0
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_customers = len(filtered_df)

total_churned = filtered_df["Exited"].sum()

if total_customers > 0:
    churn_rate = (
        total_churned / total_customers
    ) * 100
else:
    churn_rate = 0

retention_rate = 100 - churn_rate


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Total Customers",
        f"{total_customers:,}"
    )


with col2:
    st.metric(
        "Churned Customers",
        f"{total_churned:,}"
    )


with col3:
    st.metric(
        "Overall Churn Rate",
        f"{churn_rate:.2f}%"
    )


with col4:
    st.metric(
        "Retention Rate",
        f"{retention_rate:.2f}%"
    )


# ============================================================
# NO DATA MESSAGE
# ============================================================

if total_customers == 0:

    st.warning(
        "No customers match the selected filters."
    )

    st.stop()


# ============================================================
# ROW 1 - OVERALL CHURN + GEOGRAPHY
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Overall Churn Distribution
# ------------------------------------------------------------

with col1:

    st.subheader("Overall Churn Distribution")

    churn_counts = (
        filtered_df["Exited"]
        .value_counts()
        .sort_index()
    )

    churn_counts.index = [
        "Stayed",
        "Churned"
    ]

    fig, ax = plt.subplots()

    churn_counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Customer Status")
    ax.set_ylabel("Number of Customers")
    ax.set_title("Stayed vs Churned Customers")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ------------------------------------------------------------
# Geography Churn
# ------------------------------------------------------------

with col2:

    st.subheader("Churn Rate by Geography")

    geo_data = (
        filtered_df.groupby("Geography")["Exited"]
        .mean()
        .mul(100)
    )

    fig, ax = plt.subplots()

    geo_data.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Geography")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Geography-wise Churn Rate")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ============================================================
# ROW 2 - AGE + CREDIT SCORE
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Age Group
# ------------------------------------------------------------

with col1:

    st.subheader("Churn Rate by Age Group")

    age_data = (
        filtered_df.groupby(
            "Age_Group",
            observed=False
        )["Exited"]
        .mean()
        .mul(100)
    )

    fig, ax = plt.subplots()

    age_data.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Age Group")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Age Group-wise Churn")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ------------------------------------------------------------
# Credit Score
# ------------------------------------------------------------

with col2:

    st.subheader("Churn Rate by Credit Score")

    credit_data = (
        filtered_df.groupby(
            "Credit_Score_Group",
            observed=False
        )["Exited"]
        .mean()
        .mul(100)
    )

    fig, ax = plt.subplots()

    credit_data.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Credit Score Group")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Credit Score-wise Churn")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ============================================================
# ROW 3 - TENURE + GENDER
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Tenure
# ------------------------------------------------------------

with col1:

    st.subheader("Churn Rate by Tenure")

    tenure_data = (
        filtered_df.groupby(
            "Tenure_Group",
            observed=False
        )["Exited"]
        .mean()
        .mul(100)
    )

    fig, ax = plt.subplots()

    tenure_data.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Tenure Group")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Tenure-wise Churn")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ------------------------------------------------------------
# Gender
# ------------------------------------------------------------

with col2:

    st.subheader("Churn Rate by Gender")

    gender_data = (
        filtered_df.groupby("Gender")["Exited"]
        .mean()
        .mul(100)
    )

    fig, ax = plt.subplots()

    gender_data.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Gender")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Gender-wise Churn")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ============================================================
# ROW 4 - ACTIVE MEMBER + PRODUCTS
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Active Member
# ------------------------------------------------------------

with col1:

    st.subheader("Churn Rate by Member Activity")

    active_data = (
        filtered_df.groupby("IsActiveMember")["Exited"]
        .mean()
        .mul(100)
    )

    active_data.index = [
        "Inactive",
        "Active"
    ]

    fig, ax = plt.subplots()

    active_data.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Member Status")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Active vs Inactive Members")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ------------------------------------------------------------
# Number of Products
# ------------------------------------------------------------

with col2:

    st.subheader("Churn Rate by Number of Products")

    product_data = (
        filtered_df.groupby("NumOfProducts")["Exited"]
        .mean()
        .mul(100)
    )

    fig, ax = plt.subplots()

    product_data.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Number of Products")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_title("Product-wise Churn")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ============================================================
# ROW 5 - CREDIT SCORE & BALANCE
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Average Credit Score
# ------------------------------------------------------------

with col1:

    st.subheader("Average Credit Score by Churn Status")

    credit_avg = (
        filtered_df.groupby("Exited")["CreditScore"]
        .mean()
    )

    credit_avg.index = [
        "Stayed",
        "Churned"
    ]

    fig, ax = plt.subplots()

    credit_avg.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Customer Status")
    ax.set_ylabel("Average Credit Score")
    ax.set_title("Credit Score Comparison")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ------------------------------------------------------------
# Average Balance
# ------------------------------------------------------------

with col2:

    st.subheader("Average Balance by Churn Status")

    balance_avg = (
        filtered_df.groupby("Exited")["Balance"]
        .mean()
    )

    balance_avg.index = [
        "Stayed",
        "Churned"
    ]

    fig, ax = plt.subplots()

    balance_avg.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Customer Status")
    ax.set_ylabel("Average Balance")
    ax.set_title("Balance Comparison")

    plt.xticks(rotation=0)

    st.pyplot(fig)


# ============================================================
# DATA TABLE
# ============================================================

st.subheader("📋 Filtered Customer Data")

st.dataframe(
    filtered_df.head(100),
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.write(
    "European Bank Customer Churn Analysis | "
    "Python + Pandas + Streamlit"
)
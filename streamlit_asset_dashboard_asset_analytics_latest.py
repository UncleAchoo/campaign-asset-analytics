import streamlit as st
import pandas as pd

st.set_page_config(page_title="Asset Analytics Dashboard", layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Asset_Analytics_Impressions_by_Account_2026_03_10.csv")
    return df

df = load_data()

asset_df = df[df["row_type"] == "asset"].copy()
account_df = df[df["row_type"] == "audience_member"].copy()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Filters")

status_filter = st.sidebar.selectbox(
    "Campaign status",
    ["All", "Active", "Archived"]
)

if status_filter == "Active":
    asset_df = asset_df[asset_df["deleted"] == False]

elif status_filter == "Archived":
    asset_df = asset_df[asset_df["deleted"] == True]


# -----------------------------
# ASSET SELECTOR (LEFT COLUMN)
# -----------------------------
st.sidebar.subheader("Inspect asset")

selected_asset = st.sidebar.selectbox(
    "Choose asset",
    sorted(asset_df["asset_name"].unique())
)


# Audience member filter
audience_keys = sorted(account_df["audience_member_key"].dropna().unique())

selected_accounts = st.sidebar.multiselect(
    "Audience member key",
    audience_keys
)

if selected_accounts:
    account_df = account_df[
        account_df["audience_member_key"].isin(selected_accounts)
    ]


# -----------------------------
# HEADER
# -----------------------------
st.title("Asset Analytics")
st.caption("Understand which accounts and assets are driving engagement")

# -----------------------------
# KPIs
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Views", int(asset_df["visits"].sum()))
col2.metric("Clicks", int(asset_df["total_clicks"].sum()))
col3.metric("Unique Visitors", int(asset_df["unique_visitors"].sum()))

st.divider()

# -----------------------------
# ASSET PERFORMANCE TABLE
# -----------------------------
st.subheader("All Asset performance")

asset_table = asset_df[
    [
        "asset_name",
        "visits",
        "total_clicks",
        "unique_visitors",
        "avg_time_seconds"
    ]
].sort_values("visits", ascending=False)

asset_table.rename(
    columns={
        "asset_name": "Asset",
        "visits": "Total Views",
        "total_clicks": "Clicks",
        "unique_visitors": "Unique Visitors",
        "avg_time_seconds": "Avg Time (s)"
    },
    inplace=True
)

asset_table.insert(0, "Rank", range(1, len(asset_table) + 1))

st.dataframe(asset_table, use_container_width=True)

# -----------------------------
# ACCOUNT BREAKDOWN
# -----------------------------
st.subheader(f"Account engagement for: {selected_asset}")

asset_accounts = account_df[
    account_df["asset_name"] == selected_asset
]

if len(asset_accounts) == 0:

    st.info("No audience member activity for this asset.")

else:

    breakdown = asset_accounts[
        [
            "audience_member_key",
            "visits",
            "total_clicks",
            "unique_visitors",
            "avg_time_seconds"
        ]
    ].sort_values("total_clicks", ascending=False)

    breakdown.rename(
        columns={
            "audience_member_key": "Audience Member",
            "visits": "Total Views",
            "total_clicks": "Clicks",
            "unique_visitors": "Unique Visitors",
            "avg_time_seconds": "Avg Time (s)"
        },
        inplace=True
    )

    breakdown.insert(0, "Rank", range(1, len(breakdown) + 1))

    st.dataframe(breakdown, use_container_width=True)


# -----------------------------
# FOOTER
# -----------------------------
st.divider()

st.caption(
"""
Notes

• Asset rows represent full campaign engagement  
• Audience member rows represent company/domain level engagement  
• Clicks are the most reliable account-level signal
"""
)
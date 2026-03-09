
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Asset Analytics Dashboard", layout="wide")

st.title("Campaign Asset Analytics")

def find_default_csv():
    candidates = [
        Path.cwd() / "Asset_Analytics_for_a_Company_2026_03_09.csv",
        Path(__file__).resolve().parent / "Asset_Analytics_for_a_Company_2026_03_09.csv",
        Path.home() / "Downloads" / "Asset_Analytics_for_a_Company_2026_03_09.csv",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

@st.cache_data
def load_data(uploaded):
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        default = find_default_csv()
        if default:
            df = pd.read_csv(default)
        else:
            st.info("Upload the dataset to begin.")
            st.stop()

    df.columns = [c.strip() for c in df.columns]

    numeric_cols = ["visits","unique_visitors","total_clicks","avg_time_seconds","subcategory_clicks"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "last_click_at" in df.columns:
        df["last_click_at"] = pd.to_datetime(df["last_click_at"], errors="coerce")

    if "deleted" in df.columns:
        if df["deleted"].dtype != bool:
            df["deleted"] = df["deleted"].astype(str).str.lower().isin(["true","1","t","yes"])
    else:
        df["deleted"] = False

    return df


uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
df = load_data(uploaded)

assets = df[df["row_type"]=="asset"].copy()
breakdown = df[df["row_type"]=="audience_member"].copy()

st.sidebar.header("Filters")

asset_filter = st.sidebar.multiselect(
    "Asset",
    sorted(assets["asset_name"].dropna().unique())
)

status_filter = st.sidebar.multiselect(
    "Campaign status",
    ["Active","Archived"],
    default=["Active","Archived"]
)

audience_filter = st.sidebar.multiselect(
    "Audience member key",
    sorted(breakdown["audience_member_key"].dropna().unique())
)

key_type_filter = st.sidebar.multiselect(
    "Key type",
    sorted(breakdown["audience_member_key_type"].dropna().unique())
)

filtered_assets = assets.copy()
filtered_breakdown = breakdown.copy()

if asset_filter:
    filtered_assets = filtered_assets[filtered_assets["asset_name"].isin(asset_filter)]
    filtered_breakdown = filtered_breakdown[filtered_breakdown["asset_name"].isin(asset_filter)]

if status_filter:
    allowed_deleted = [s=="Archived" for s in status_filter]
    filtered_assets = filtered_assets[filtered_assets["deleted"].isin(allowed_deleted)]
    filtered_breakdown = filtered_breakdown[filtered_breakdown["deleted"].isin(allowed_deleted)]

if audience_filter:
    filtered_breakdown = filtered_breakdown[filtered_breakdown["audience_member_key"].isin(audience_filter)]

if key_type_filter:
    filtered_breakdown = filtered_breakdown[filtered_breakdown["audience_member_key_type"].isin(key_type_filter)]

if audience_filter or key_type_filter:
    valid_campaigns = filtered_breakdown["campaign_id"].unique()
    filtered_assets = filtered_assets[filtered_assets["campaign_id"].isin(valid_campaigns)]

remaining_campaigns = filtered_assets["campaign_id"].unique()
filtered_breakdown = filtered_breakdown[filtered_breakdown["campaign_id"].isin(remaining_campaigns)]

st.subheader("Overview")

c1,c2,c3,c4 = st.columns(4)

c1.metric("Assets", len(filtered_assets))
c2.metric("Visits", int(filtered_assets["visits"].fillna(0).sum()))
c3.metric("Unique visitors", int(filtered_assets["unique_visitors"].fillna(0).sum()))
c4.metric("Total clicks", int(filtered_assets["total_clicks"].fillna(0).sum()))

st.divider()

asset_table = filtered_assets[[
    "asset_name",
    "visits",
    "unique_visitors",
    "total_clicks",
    "avg_time_seconds",
    "deleted",
    "campaign_id"
]].copy()

asset_table = asset_table.sort_values("visits", ascending=False).reset_index(drop=True)
asset_table.insert(0,"Rank", range(1,len(asset_table)+1))

asset_table["Status"] = asset_table["deleted"].apply(lambda x: "Archived" if x else "Active")

st.subheader("Asset Performance")

st.dataframe(
    asset_table[[
        "Rank",
        "asset_name",
        "Status",
        "visits",
        "unique_visitors",
        "total_clicks",
        "avg_time_seconds"
    ]],
    use_container_width=True
)

st.divider()

st.subheader("Click Breakdown")

asset_options = asset_table["asset_name"].unique()

if len(asset_options)==0:
    st.info("No assets match current filters.")
    st.stop()

selected_asset = st.selectbox("Select asset", asset_options)

campaign_ids = filtered_assets[filtered_assets["asset_name"]==selected_asset]["campaign_id"].unique()

bd = filtered_breakdown[filtered_breakdown["campaign_id"].isin(campaign_ids)].copy()

bd = bd.sort_values("subcategory_clicks", ascending=False)
bd.insert(0,"Rank", range(1,len(bd)+1))

st.dataframe(
    bd[[
        "Rank",
        "audience_member_key",
        "audience_member_key_type",
        "subcategory_clicks",
        "last_click_at"
    ]],
    use_container_width=True
)

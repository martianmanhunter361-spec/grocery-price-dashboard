import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="BigBasket vs JioMart Dashboard",
    page_icon="🛒",
    layout="wide",
)

st.title("🛒 BigBasket vs JioMart Price Comparison")


@st.cache_data
def load_data():
    df = pd.read_csv("grocery_prices.csv")
    df["price_diff"] = (df["bigbasket_price"] - df["jiomart_price"]).abs()

    def get_cheaper(row):
        if row["bigbasket_price"] < row["jiomart_price"]:
            return "BigBasket"
        elif row["jiomart_price"] < row["bigbasket_price"]:
            return "JioMart"
        return "Equal"

    df["cheaper_at"] = df.apply(get_cheaper, axis=1)
    return df


try:
    df = load_data()

    # KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Items", len(df))
    c2.metric("Avg BigBasket Price", f"₹{df['bigbasket_price'].mean():.2f}")
    c3.metric("Avg JioMart Price", f"₹{df['jiomart_price'].mean():.2f}")

    jm_wins = (df["cheaper_at"] == "JioMart").sum()
    bb_wins = (df["cheaper_at"] == "BigBasket").sum()
    c4.metric(
        "Cheaper Overall",
        "JioMart" if jm_wins > bb_wins else "BigBasket",
        f"JioMart cheaper on {jm_wins} items",
    )

    st.markdown("---")

    # Filters
    col_search, col_cat = st.columns([2, 1])
    search = col_search.text_input("🔍 Search Product or Brand:")
    category = col_cat.selectbox(
        "Category:", ["All"] + list(df["category"].unique())
    )

    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df["product_name"].str.contains(search, case=False)
            | filtered_df["brand"].str.contains(search, case=False)
        ]
    if category != "All":
        filtered_df = filtered_df[filtered_df["category"] == category]

    # Chart
    st.subheader("📊 Price Visualizer")
    if not filtered_df.empty:
        melted = filtered_df.melt(
            id_vars=["product_name"],
            value_vars=["bigbasket_price", "jiomart_price"],
            var_name="Platform",
            value_name="Price (₹)",
        )
        melted["Platform"] = melted["Platform"].replace(
            {"bigbasket_price": "BigBasket", "jiomart_price": "JioMart"}
        )

        fig = px.bar(
            melted,
            x="product_name",
            y="Price (₹)",
            color="Platform",
            barmode="group",
            color_discrete_map={"BigBasket": "#388e3c", "JioMart": "#0288d1"},
        )
        fig.update_layout(xaxis_tickangle=-45, height=450)
        st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader("📋 Itemized Comparison")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error loading project: {e}")
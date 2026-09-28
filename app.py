import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="BigBasket vs JioMart Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Modern Dark Mode CSS UI Styling
st.markdown(
    """
    <style>
    /* Dark Theme Background */
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Container Styling */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 24px;
    }
    
    /* Custom Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 700;
    }
    
    /* Custom Table Container */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #334155;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 3. Data Processing Pipeline
@st.cache_data
def load_and_process_data():
    df = pd.read_csv("grocery_prices.csv")

    # Lowercase column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Calculate Savings & Lower Price Platform
    df["price_diff"] = (df["bigbasket_price"] - df["jiomart_price"]).abs()

    def get_cheaper(row):
        if row["bigbasket_price"] < row["jiomart_price"]:
            return "BigBasket"
        elif row["jiomart_price"] < row["bigbasket_price"]:
            return "JioMart"
        return "Equal"

    df["cheaper_at"] = df.apply(get_cheaper, axis=1)

    # Calculate Savings Percentage
    df["savings_pct"] = (
        df["price_diff"] / df[["bigbasket_price", "jiomart_price"]].max(axis=1)
    ) * 100
    return df


try:
    df = load_and_process_data()

    # --- HEADER SECTION ---
    st.markdown(
        """
        <div class="main-header">
            <h1 style="margin:0; font-size: 2rem; color: #f8fafc;">🛒 BigBasket vs JioMart Price Intelligence</h1>
            <p style="margin-top:8px; color:#94a3b8; font-size:1rem;">
                Real-time price comparisons across 60 essential grocery items in India
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # --- KPI SUMMARY METRIC CARDS ---
    m1, m2, m3, m4 = st.columns(4)

    total_items = len(df)
    bb_avg = df["bigbasket_price"].mean()
    jm_avg = df["jiomart_price"].mean()

    jm_wins = (df["cheaper_at"] == "JioMart").sum()
    bb_wins = (df["cheaper_at"] == "BigBasket").sum()

    m1.metric("Tracked Products", f"{total_items} Items")
    m2.metric(
        "Avg BigBasket Price",
        f"₹{bb_avg:.2f}",
        delta=f"₹{bb_avg - jm_avg:+.2f} vs JioMart",
        delta_color="inverse",
    )
    m3.metric(
        "Avg JioMart Price",
        f"₹{jm_avg:.2f}",
        delta=f"₹{jm_avg - bb_avg:+.2f} vs BigBasket",
        delta_color="inverse",
    )
    m4.metric(
        "Cheapest Store Overall",
        "JioMart" if jm_wins > bb_wins else "BigBasket",
        delta=f"Cheaper on {max(jm_wins, bb_wins)}/60 items",
    )

    st.write("")

    # --- FILTERS SECTION ---
    col_search, col_cat, col_cheaper = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input(
            "🔍 Search Products or Brands:",
            placeholder="Search e.g. Atta, Oil, Tata...",
        )

    with col_cat:
        category_list = ["All Categories"] + sorted(
            list(df["category"].dropna().unique())
        )
        selected_cat = st.selectbox("Category:", category_list)

    with col_cheaper:
        selected_platform = st.selectbox(
            "Cheaper At:", ["All Stores", "JioMart", "BigBasket", "Equal"]
        )

    # Apply Filters
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df["product_name"].str.contains(
                search_query, case=False, na=False
            )
            | filtered_df["brand"].str.contains(
                search_query, case=False, na=False
            )
        ]

    if selected_cat != "All Categories":
        filtered_df = filtered_df[filtered_df["category"] == selected_cat]

    if selected_platform != "All Stores":
        filtered_df = filtered_df[
            filtered_df["cheaper_at"] == selected_platform
        ]

    st.markdown("---")

    # --- INTERACTIVE VISUALIZATION ---
    st.subheader("📊 Price Comparison Visualizer")

    if not filtered_df.empty:
        # Melt DataFrame for Plotly Grouped Bar Chart
        melted = filtered_df.melt(
            id_vars=["product_name", "brand", "quantity"],
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
            hover_data=["brand", "quantity"],
            color_discrete_map={"BigBasket": "#84cc16", "JioMart": "#0288d1"},
            template="plotly_dark",
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Product Name",
            yaxis_title="Price in INR (₹)",
            font=dict(color="#94a3b8"),
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor="#334155"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title="",
            ),
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No products match your current search filters.")

    # --- DATA TABLE SECTION ---
    st.subheader("📋 Itemized Grocery Breakdown")

    # Format dataframe for display
    display_df = filtered_df[
        [
            "product_name",
            "category",
            "brand",
            "quantity",
            "bigbasket_price",
            "jiomart_price",
            "price_diff",
            "cheaper_at",
        ]
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "product_name": st.column_config.TextColumn(
                "Product", width="medium"
            ),
            "category": st.column_config.TextColumn("Category"),
            "brand": st.column_config.TextColumn("Brand"),
            "quantity": st.column_config.TextColumn("Quantity"),
            "bigbasket_price": st.column_config.NumberColumn(
                "BigBasket (₹)", format="₹%d"
            ),
            "jiomart_price": st.column_config.NumberColumn(
                "JioMart (₹)", format="₹%d"
            ),
            "price_diff": st.column_config.NumberColumn(
                "Difference (₹)", format="₹%d"
            ),
            "cheaper_at": st.column_config.TextColumn("Cheapest Option"),
        },
    )

except Exception as e:
    st.error(f"Error rendering dashboard: {e}")
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="BigBasket vs JioMart Price Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Inject Replit-Style Dark Theme CSS
st.markdown(
    """
    <style>
    /* Dark background matching Replit app */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Hide top Streamlit padding & header line */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Custom Header Container */
    .dashboard-header {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .dashboard-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .dashboard-subtitle {
        color: #9ca3af;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Replit-style Card Box for Metrics */
    div[data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
    }
    
    div[data-testid="stMetric"] label {
        color: #9ca3af !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* Input & Select Box styling */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        color: #f3f4f6 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: #3b82f6 !important;
    }

    /* Styled DataFrame Grid */
    .stDataFrame {
        border: 1px solid #1f2937;
        border-radius: 12px;
        overflow: hidden;
        background-color: #111827;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 3. Data Loading & Processing
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

    # --- TOP HEADER ---
    st.markdown(
        """
        <div class="dashboard-header">
            <div class="dashboard-title">
                <span>🛒</span> BigBasket vs JioMart Price Dashboard
            </div>
            <div class="dashboard-subtitle">
                Real-time price comparison across key grocery products and categories
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # --- KPI SUMMARY CARDS ---
    c1, c2, c3, c4 = st.columns(4)

    total_items = len(df)
    bb_avg = df["bigbasket_price"].mean()
    jm_avg = df["jiomart_price"].mean()
    jm_wins = (df["cheaper_at"] == "JioMart").sum()
    bb_wins = (df["cheaper_at"] == "BigBasket").sum()

    c1.metric("Total Items", f"{total_items}")
    c2.metric(
        "Avg BigBasket",
        f"₹{bb_avg:.1f}",
        delta=f"₹{bb_avg - jm_avg:+.1f} vs JM",
        delta_color="inverse",
    )
    c3.metric(
        "Avg JioMart",
        f"₹{jm_avg:.1f}",
        delta=f"₹{jm_avg - bb_avg:+.1f} vs BB",
        delta_color="inverse",
    )
    c4.metric(
        "Cheapest Store",
        "JioMart" if jm_wins > bb_wins else "BigBasket",
        delta=f"Cheaper on {max(jm_wins, bb_wins)} items",
    )

    st.write("")

    # --- CONTROLS & FILTERS ---
    f1, f2, f3 = st.columns([2, 1, 1])

    with f1:
        search = st.text_input(
            "Search Product / Brand",
            placeholder="Type e.g. Atta, Tata, Rice...",
            label_visibility="collapsed",
        )

    with f2:
        categories = ["All Categories"] + sorted(list(df["category"].unique()))
        selected_cat = st.selectbox(
            "Category", categories, label_visibility="collapsed"
        )

    with f3:
        platforms = ["All Platforms", "JioMart", "BigBasket", "Equal"]
        selected_platform = st.selectbox(
            "Cheaper Option", platforms, label_visibility="collapsed"
        )

    # Apply Filtering
    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df["product_name"].str.contains(search, case=False)
            | filtered_df["brand"].str.contains(search, case=False)
        ]

    if selected_cat != "All Categories":
        filtered_df = filtered_df[filtered_df["category"] == selected_cat]

    if selected_platform != "All Platforms":
        filtered_df = filtered_df[
            filtered_df["cheaper_at"] == selected_platform
        ]

    st.write("")

    # --- PRICE COMPARISON CHART ---
    st.markdown(
        "<h3 style='color:#ffffff; font-size:1.1rem; font-weight:600; margin-bottom:12px;'>📊 Price Comparison Overview</h3>",
        unsafe_allow_html=True,
    )

    if not filtered_df.empty:
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
            # Matching Replit accent colors (Green for BB, Blue for JioMart)
            color_discrete_map={"BigBasket": "#22c55e", "JioMart": "#3b82f6"},
            template="plotly_dark",
        )

        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            margin=dict(l=20, r=20, t=20, b=80),
            xaxis_title=None,
            yaxis_title="Price (₹)",
            font=dict(color="#9ca3af", family="sans-serif"),
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor="#1f2937"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=None,
            ),
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No items match the selected filter criteria.")

    # --- PRODUCT DATA TABLE ---
    st.markdown(
        "<h3 style='color:#ffffff; font-size:1.1rem; font-weight:600; margin-top:20px; margin-bottom:12px;'>📦 Product Price List</h3>",
        unsafe_allow_html=True,
    )

    st.dataframe(
        filtered_df[
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
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "product_name": st.column_config.TextColumn("Product Name"),
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
            "cheaper_at": st.column_config.TextColumn("Cheaper Option"),
        },
    )

except Exception as e:
    st.error(f"Error loading dashboard data: {e}")

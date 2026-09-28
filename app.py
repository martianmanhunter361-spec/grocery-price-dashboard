import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="BigBasket vs JioMart | Campus Price Lab",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Inject Light Theme & Replit Dashboard Styling
st.markdown(
    """
    <style>
    /* Light Grid Background */
    .stApp {
        background-color: #f8f9fa;
        background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
        background-size: 20px 20px;
        color: #111827;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    header[data-testid="stHeader"] {
        background: transparent;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* Sub-header badge */
    .badge-lab {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #0284c7;
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
    }

    /* Header Title Styling */
    .header-title {
        font-size: 2.75rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 12px;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }
    .header-title .vs {
        color: #f59e0b;
        font-weight: 700;
    }
    
    .header-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 12px;
    }
    
    .data-sources {
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 24px;
    }
    .source-tag {
        background: #f1f5f9;
        color: #334155;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
    }

    /* Search and Filter Container Card */
    .filter-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .filter-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }

    /* Modern Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .metric-value-blue {
        font-size: 1.85rem;
        font-weight: 800;
        color: #2563eb;
    }
    .metric-value-purple {
        font-size: 1.85rem;
        font-weight: 800;
        color: #7c3aed;
    }
    .metric-value-dark {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Section Cards for Visualizations */
    .chart-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-top: 20px;
    }
    .chart-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
    }
    .chart-subheader {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 16px;
    }

    /* Style Streamlit Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 3. Data Processing Pipeline
@st.cache_data
def load_data():
    df = pd.read_csv("grocery_prices.csv")
    df.columns = [c.strip().lower() for c in df.columns]

    df["price_diff"] = (df["bigbasket_price"] - df["jiomart_price"]).abs()

    def get_cheaper(row):
        if row["bigbasket_price"] < row["jiomart_price"]:
            return "BigBasket"
        elif row["jiomart_price"] < row["bigbasket_price"]:
            return "JioMart"
        return "Same price"

    df["cheaper_at"] = df.apply(get_cheaper, axis=1)
    return df


try:
    df = load_data()

    # --- TOP TITLE HEADER ---
    st.markdown(
        """
        <div class="badge-lab">🧺 Campus Price Lab</div>
        <div class="header-title">BigBasket <span class="vs">vs</span> JioMart</div>
        <div class="header-subtitle">
            A quick, transparent read on where everyday groceries cost less. Built for classroom demos with illustrative sample data.
        </div>
        <div class="data-sources">
            DATA SOURCES 
            <span class="source-tag">API Server</span>
            <span class="source-tag">Illustrative sample</span>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # --- FILTER SECTION ---
    st.markdown(
        '<div class="filter-title">🔍 EXPLORE THE SAMPLE</div>',
        unsafe_allow_html=True,
    )
    col_search, col_cat, col_count = st.columns([3, 1.5, 1])

    with col_search:
        search_query = st.text_input(
            "Search",
            placeholder="Search a product or brand",
            label_visibility="collapsed",
        )

    with col_cat:
        categories = ["All categories"] + sorted(list(df["category"].unique()))
        selected_cat = st.selectbox(
            "Category", categories, label_visibility="collapsed"
        )

    # Filter Logic
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

    if selected_cat != "All categories":
        filtered_df = filtered_df[filtered_df["category"] == selected_cat]

    with col_count:
        st.markdown(
            f"""
            <div style="background:#f1f5f9; padding: 10px; border-radius: 8px; text-align: center; font-size: 0.85rem; font-weight: 600; color: #475569;">
                {len(filtered_df)} of {len(df)} products shown
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --- TOP 5 METRIC CARDS ---
    m1, m2, m3, m4, m5 = st.columns(5)

    total_prods = len(filtered_df)
    bb_total = filtered_df["bigbasket_price"].sum()
    jm_total = filtered_df["jiomart_price"].sum()
    avg_diff = filtered_df["price_diff"].mean() if total_prods > 0 else 0

    bb_wins = (filtered_df["cheaper_at"] == "BigBasket").sum()
    jm_wins = (filtered_df["cheaper_at"] == "JioMart").sum()

    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">PRODUCTS COMPARED</div>
                <div class="metric-value-blue">{total_prods}</div>
                <div class="metric-sub">matching current filters</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">BIGBASKET BASKET</div>
                <div class="metric-value-blue">₹{bb_total:,.2f}</div>
                <div class="metric-sub">visible products total</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">JIOMART BASKET</div>
                <div class="metric-value-purple">₹{jm_total:,.2f}</div>
                <div class="metric-sub">visible products total</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">AVERAGE DIFFERENCE</div>
                <div class="metric-value-purple">₹{avg_diff:.2f}</div>
                <div class="metric-sub">across visible products</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with m5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">PLATFORM WINS</div>
                <div class="metric-value-blue">{bb_wins} / <span style="color:#7c3aed">{jm_wins}</span></div>
                <div class="metric-sub">BigBasket / JioMart</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --- ROW 1: AVERAGE PRICE BY CATEGORY & AVERAGE PLATFORM PRICE ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown(
            """
            <div class="chart-header">Average price by category</div>
            <div class="chart-subheader">Typical item price in each category</div>
        """,
            unsafe_allow_html=True,
        )

        if not filtered_df.empty:
            cat_df = (
                filtered_df.groupby("category")[
                    ["bigbasket_price", "jiomart_price"]
                ]
                .mean()
                .reset_index()
            )
            fig_cat = go.Figure()
            fig_cat.add_trace(
                go.Bar(
                    x=cat_df["category"],
                    y=cat_df["bigbasket_price"],
                    name="BigBasket",
                    marker_color="#2563eb",
                )
            )
            fig_cat.add_trace(
                go.Bar(
                    x=cat_df["category"],
                    y=cat_df["jiomart_price"],
                    name="JioMart",
                    marker_color="#8b5cf6",
                )
            )

            fig_cat.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
                yaxis=dict(
                    tickprefix="₹",
                    showgrid=True,
                    gridcolor="#f1f5f9",
                    zerolinecolor="#cbd5e1",
                ),
                xaxis=dict(showgrid=False),
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5
                ),
            )
            st.plotly_chart(fig_cat, use_container_width=True)

    with col_chart2:
        st.markdown(
            """
            <div class="chart-header">Average platform price</div>
            <div class="chart-subheader">Average listed price across the visible basket</div>
        """,
            unsafe_allow_html=True,
        )

        if not filtered_df.empty:
            avg_bb = filtered_df["bigbasket_price"].mean()
            avg_jm = filtered_df["jiomart_price"].mean()

            fig_avg = go.Figure()
            fig_avg.add_trace(
                go.Bar(
                    x=["BigBasket", "JioMart"],
                    y=[avg_bb, avg_jm],
                    marker_color=["#2563eb", "#8b5cf6"],
                    width=0.5,
                )
            )

            fig_avg.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
                yaxis=dict(
                    tickprefix="₹",
                    showgrid=True,
                    gridcolor="#f1f5f9",
                    zerolinecolor="#cbd5e1",
                ),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_avg, use_container_width=True)

    # --- ROW 2: WHO WINS MORE OFTEN? & LARGEST PRICE GAPS ---
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        st.markdown(
            """
            <div class="chart-header">Who wins more often?</div>
            <div class="chart-subheader">Count of cheaper listings by platform</div>
        """,
            unsafe_allow_html=True,
        )

        if not filtered_df.empty:
            wins_counts = filtered_df["cheaper_at"].value_counts().reset_index()
            wins_counts.columns = ["Platform", "Count"]

            fig_donut = px.pie(
                wins_counts,
                values="Count",
                names="Platform",
                hole=0.65,
                color="Platform",
                color_discrete_map={
                    "BigBasket": "#2563eb",
                    "JioMart": "#8b5cf6",
                    "Same price": "#16a34a",
                },
            )
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
                legend=dict(
                    orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0
                ),
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart4:
        st.markdown(
            """
            <div class="chart-header">Largest price gaps</div>
            <div class="chart-subheader">Where the comparison has the most room to save</div>
        """,
            unsafe_allow_html=True,
        )

        if not filtered_df.empty:
            top_gaps = filtered_df.sort_values(by="price_diff", ascending=True).tail(6)

            fig_gaps = go.Figure()
            fig_gaps.add_trace(
                go.Bar(
                    x=top_gaps["price_diff"],
                    y=top_gaps["product_name"],
                    orientation="h",
                    marker_color="#22c55e",
                )
            )

            fig_gaps.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
                xaxis=dict(
                    tickprefix="₹",
                    showgrid=True,
                    gridcolor="#f1f5f9",
                    zerolinecolor="#cbd5e1",
                ),
                yaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_gaps, use_container_width=True)

    # --- ITEMISED TABLE ---
    st.markdown("---")
    st.markdown(
        "<h3 style='color:#0f172a; font-size:1.2rem; font-weight:700;'>📋 Itemized Price List</h3>",
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
                "BigBasket Price", format="₹%d"
            ),
            "jiomart_price": st.column_config.NumberColumn(
                "JioMart Price", format="₹%d"
            ),
            "price_diff": st.column_config.NumberColumn(
                "Price Difference", format="₹%d"
            ),
            "cheaper_at": st.column_config.TextColumn("Cheapest Store"),
        },
    )

except Exception as e:
    st.error(f"Error rendering app: {e}")

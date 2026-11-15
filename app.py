
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

from pathlib import Path

try:
    from streamlit_geolocation import streamlit_geolocation
    GEOLOCATION_AVAILABLE = True
except ImportError:
    GEOLOCATION_AVAILABLE = False


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="BloodLink | Healthcare Network Analytics",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

PAGES = [
    "Home Dashboard",
    "Find Blood Banks",
    "Network Resilience",
    "Interactive Network Map",
    "Nearest Blood Bank Finder",
    "Hospital Blood Bank Search & Request"
]

BURGUNDY = "#641D38"
DARK_WINE = "#4A142B"
WINE = "#842D4F"
ROSE = "#B66A83"
LIGHT_ROSE = "#E8CCD6"
GOLD = "#C69A75"
BACKGROUND = "#F5ECEF"
CARD = "#FFFCFA"
TEXT = "#38232D"
MUTED = "#755D67"
BORDER = "#E2CDD4"

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "dataset" / "cleaned" / "blood_banks_cleaned.csv"
NODES_PATH = BASE_DIR / "results" / "bloodlink_network_nodes.csv"
EDGES_PATH = BASE_DIR / "results" / "bloodlink_network_edges.csv"


# ==========================================================
# 2. SESSION STATE
# ==========================================================

if "bloodlink_lat" not in st.session_state:
    st.session_state.bloodlink_lat = None

if "bloodlink_lon" not in st.session_state:
    st.session_state.bloodlink_lon = None

if "bloodlink_accuracy" not in st.session_state:
    st.session_state.bloodlink_accuracy = None


# ==========================================================
# 3. CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #F5ECEF !important;
    color: #38232D !important;
}

.main .block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

.stApp p,
.stApp label,
.stApp li,
.stMarkdown p {
    color: #38232D;
    line-height: 1.6;
}

h1, h2 {
    color: #641D38 !important;
    font-weight: 750 !important;
}

h3 {
    color: #842D4F !important;
    font-weight: 700 !important;
}

/* SIDEBAR BACKGROUND */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #351020 0%,
        #641D38 55%,
        #4A142B 100%
    ) !important;
}

/* SIDEBAR GENERAL TEXT */

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    color: #FFFFFF !important;
}

/* SIDEBAR NAVIGATION LABEL */

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #FFFFFF !important;
    font-weight: 650 !important;
}

/* RADIO BUTTON TEXT */

[data-testid="stSidebar"] [data-testid="stRadio"] label p,
[data-testid="stSidebar"] [data-testid="stRadio"] label span,
[data-testid="stSidebar"] [data-testid="stRadio"] label div {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

/* RADIO BUTTON SPACING */

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 10px !important;
}

/* RADIO BUTTON HIGHLIGHT */

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background-color: rgba(255, 255, 255, 0.06) !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
    margin-bottom: 3px !important;
}

/* RADIO BUTTON HOVER */

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: #842D4F !important;
}

/* RADIO BUTTON CIRCLES */

[data-testid="stSidebar"] [data-testid="stRadio"] input {
    accent-color: #E8CCD6 !important;
}

/* SIDEBAR DIVIDERS */

[data-testid="stSidebar"] hr {
    border-color: #B66A83 !important;
}

/* SIDEBAR PROJECT OVERVIEW */

[data-testid="stSidebar"] .stMarkdown {
    color: #FFFFFF !important;
}

/* DROPDOWNS */

div[data-baseweb="select"] > div {
    background-color: #FFFCFA !important;
    border: 1px solid #C69AAA !important;
    border-radius: 8px !important;
    min-height: 42px;
}

div[data-baseweb="select"] input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #38232D !important;
}

div[data-baseweb="select"] svg {
    fill: #641D38 !important;
    color: #641D38 !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"] {
    background-color: #FFFCFA !important;
}

li[role="option"],
div[role="option"] {
    background-color: #FFFCFA !important;
    color: #38232D !important;
}

li[role="option"]:hover,
div[role="option"]:hover,
li[aria-selected="true"],
div[aria-selected="true"] {
    background-color: #E8CCD6 !important;
    color: #4A142B !important;
}

/* TEXT INPUTS */

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    color: #38232D !important;
    background: #FFFCFA !important;
    border: 1px solid #CBA8B4 !important;
    border-radius: 8px !important;
}

/* CHECKBOXES AND SLIDERS */

[data-testid="stCheckbox"] label,
[data-testid="stSlider"] label {
    color: #38232D !important;
}

/* METRIC CARDS */

[data-testid="stMetric"] {
    background: #FFFCFA !important;
    border: 1px solid #E2CDD4 !important;
    border-top: 4px solid #842D4F !important;
    padding: 16px !important;
    border-radius: 10px !important;
    box-shadow: 0 3px 8px rgba(74,20,43,0.07);
    min-height: 105px;
}

[data-testid="stMetric"] * {
    color: #641D38 !important;
    opacity: 1 !important;
}

[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    font-weight: 650 !important;
}

[data-testid="stMetricValue"] {
    font-size: 25px !important;
    font-weight: 750 !important;
}

/* BUTTONS */

.stButton > button,
.stDownloadButton > button {
    background: #641D38 !important;
    color: #FFFFFF !important;
    border: 1px solid #641D38 !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    padding: 9px 15px !important;
}

.stButton > button p,
.stDownloadButton > button p {
    color: #FFFFFF !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #842D4F !important;
    color: #FFFFFF !important;
    border-color: #C69A75 !important;
}

/* PAGE HEADER */

.bloodlink-header {
    background: linear-gradient(120deg, #351020, #842D4F);
    padding: 28px;
    border-radius: 12px;
    border-left: 7px solid #C69A75;
    margin-bottom: 22px;
}

.bloodlink-header h1 {
    color: #FFFFFF !important;
    font-size: 34px;
    margin: 0;
}

.bloodlink-header p {
    color: #F8E8ED !important;
    font-size: 15px;
    margin-top: 9px;
    margin-bottom: 0;
}

.header-label {
    color: #E3BFA0;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.section-label {
    color: #9B526C;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

/* SELECTION BANNER */

.selected-region {
    background: linear-gradient(120deg, #4A142B, #842D4F);
    border-left: 6px solid #C69A75;
    border-radius: 10px;
    padding: 15px 20px;
    margin: 12px 0 20px 0;
}

.selected-region p {
    color: #F8E8ED !important;
    margin: 0;
    font-size: 12px;
}

.selected-region h2 {
    color: #FFFFFF !important;
    margin: 5px 0;
    font-size: 23px;
}

/* INFORMATION PANELS */

.info-panel {
    background: #FFFCFA;
    border: 1px solid #E2CDD4;
    border-left: 5px solid #842D4F;
    border-radius: 9px;
    padding: 16px;
    margin: 10px 0;
}

/* EXPANDERS */

[data-testid="stExpander"] {
    background: #FFFCFA;
    border: 1px solid #E2CDD4;
    border-radius: 10px;
}

/* TABLES */

[data-testid="stDataFrame"] {
    border: 1px solid #E2CDD4;
    border-radius: 8px;
    overflow: hidden;
}

/* FOOTER */

.bloodlink-footer {
    border-top: 1px solid #DEC9D0;
    padding: 20px 0;
    text-align: center;
    color: #755D67;
    font-size: 13px;
}

hr {
    border-color: #E2CDD4 !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# 4. LOAD DATA
# ==========================================================

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH)

    for col in ["state", "district", "name", "category"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    for col in ["lat", "lon"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


@st.cache_data
def load_network_data():

    nodes = pd.read_csv(NODES_PATH)
    edges = pd.read_csv(EDGES_PATH)

    required_nodes = [
        "bank_id", "name", "state", "district", "lat", "lon"
    ]

    required_edges = [
        "source", "target", "weight", "distance_km"
    ]

    if not set(required_nodes).issubset(nodes.columns):
        raise ValueError("Network nodes file has missing columns.")

    if not set(required_edges).issubset(edges.columns):
        raise ValueError("Network edges file has missing columns.")

    nodes = nodes.copy()
    edges = edges.copy()

    for col in ["bank_id", "state", "district", "name"]:
        nodes[col] = (
            nodes[col].fillna("").astype(str).str.strip()
        )

    nodes["bank_id"] = nodes["bank_id"].astype(str)
    edges["source"] = edges["source"].astype(str)
    edges["target"] = edges["target"].astype(str)

    for col in ["lat", "lon"]:
        nodes[col] = pd.to_numeric(
            nodes[col], errors="coerce"
        )

    for col in ["weight", "distance_km"]:
        edges[col] = pd.to_numeric(
            edges[col], errors="coerce"
        )

    nodes = nodes.drop_duplicates(subset="bank_id")
    edges = edges.dropna(
        subset=["weight", "distance_km"]
    )

    graph = nx.Graph()

    for _, row in nodes.iterrows():

        graph.add_node(
            row["bank_id"],
            name=row["name"],
            state=row["state"],
            district=row["district"],
            lat=row["lat"],
            lon=row["lon"]
        )

    for _, row in edges.iterrows():

        if row["source"] in graph and row["target"] in graph:

            graph.add_edge(
                row["source"],
                row["target"],
                weight=float(row["weight"]),
                distance_km=float(row["distance_km"])
            )

    return nodes, edges, graph


try:
    data = load_data()

except Exception as error:
    st.error(f"Unable to load directory dataset: {error}")
    st.stop()


required_columns = {"state", "district", "name"}

if not required_columns.issubset(data.columns):
    st.error("The directory dataset is missing required columns.")
    st.stop()


# ==========================================================
# 5. COMMON FUNCTIONS
# ==========================================================

def page_header(label, title, description):

    st.markdown(
        f"""
        <div class="bloodlink-header">
            <div class="header-label">{label}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def selection_banner(title, description):

    st.markdown(
        f"""
        <div class="selected-region">
            <p>YOUR CURRENT SELECTION</p>
            <h2>📍 {title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def region_filter(prefix):

    st.markdown(
        '<div class="section-label">REGION FILTER</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    state_options = sorted(
        data.loc[
            data["state"] != "",
            "state"
        ].unique().tolist()
    )

    with col1:

        selected_state = st.selectbox(
            "Select State",
            ["All States"] + state_options,
            key=f"{prefix}_state"
        )

    region_base = data.copy()

    if selected_state != "All States":

        region_base = region_base[
            region_base["state"] == selected_state
        ]

    district_options = sorted(
        region_base.loc[
            region_base["district"] != "",
            "district"
        ].unique().tolist()
    )

    with col2:

        selected_district = st.selectbox(
            "Select District",
            ["All Districts"] + district_options,
            key=f"{prefix}_district_{selected_state}"
        )

    filtered = region_base.copy()

    if selected_district != "All Districts":

        filtered = filtered[
            filtered["district"] == selected_district
        ]

    if selected_state == "All States":

        region_label = "All India"

        description = (
            "Showing records across all available "
            "states and districts."
        )

    elif selected_district == "All Districts":

        region_label = selected_state

        description = (
            f"Showing records across all listed districts "
            f"in {selected_state}."
        )

    else:

        region_label = f"{selected_district}, {selected_state}"

        description = (
            f"Showing records for {selected_district} "
            f"district in {selected_state}."
        )

    selection_banner(region_label, description)

    return filtered, selected_state, selected_district


def chart_theme(fig, height=420):

    fig.update_layout(
        height=height,
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(
            family="Arial",
            size=12,
            color=TEXT
        ),
        title_font=dict(
            size=18,
            color=BURGUNDY
        ),
        margin=dict(
            l=25,
            r=25,
            t=65,
            b=35
        )
    )

    fig.update_xaxes(
        tickfont=dict(color=TEXT),
        title_font=dict(color=BURGUNDY),
        gridcolor="#EDE2E5"
    )

    fig.update_yaxes(
        tickfont=dict(color=TEXT),
        title_font=dict(color=BURGUNDY),
        gridcolor="#EDE2E5"
    )

    return fig


def haversine_distances(lat, lon, latitudes, longitudes):

    earth_radius = 6371.0

    lat1 = np.radians(float(lat))
    lon1 = np.radians(float(lon))

    lat2 = np.radians(
        pd.to_numeric(latitudes, errors="coerce")
    )

    lon2 = np.radians(
        pd.to_numeric(longitudes, errors="coerce")
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    a = np.clip(a, 0, 1)

    c = 2 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1 - a)
    )

    return earth_radius * c


def get_region_data(df, selected_state, selected_district):

    result = df.copy()

    if selected_state != "All States":

        result = result[
            result["state"] == selected_state
        ]

    if selected_district != "All Districts":

        result = result[
            result["district"] == selected_district
        ]

    return result


def get_region_label(selected_state, selected_district):

    if selected_state == "All States":
        return "All India"

    if selected_district == "All Districts":
        return selected_state

    return f"{selected_district}, {selected_state}"


def load_graph_for_region(
    nodes,
    graph,
    selected_state,
    selected_district
):

    filtered_nodes = get_region_data(
        nodes,
        selected_state,
        selected_district
    )

    allowed_ids = set(
        filtered_nodes["bank_id"].astype(str)
    )

    return graph.subgraph(allowed_ids).copy(), filtered_nodes


def location_map(reference_lat, reference_lon, nearby):

    fig = go.Figure()

    if not nearby.empty:

        fig.add_trace(
            go.Scattergeo(
                lon=nearby["lon"],
                lat=nearby["lat"],
                mode="markers",
                marker=dict(
                    size=10,
                    color=WINE,
                    line=dict(
                        color="white",
                        width=1
                    )
                ),
                text=nearby["name"],
                customdata=nearby[
                    ["district", "state", "distance_km"]
                ].to_numpy(),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "District: %{customdata[0]}<br>"
                    "State: %{customdata[1]}<br>"
                    "Distance: %{customdata[2]:.2f} km"
                    "<extra></extra>"
                ),
                name="Nearby Blood Banks"
            )
        )

    fig.add_trace(
        go.Scattergeo(
            lon=[reference_lon],
            lat=[reference_lat],
            mode="markers",
            marker=dict(
                size=17,
                color=GOLD,
                symbol="star",
                line=dict(
                    color=BURGUNDY,
                    width=1.5
                )
            ),
            name="Reference Location"
        )
    )

    fig.update_geos(
        scope="asia",
        projection_type="mercator",
        center=dict(
            lat=reference_lat,
            lon=reference_lon
        ),
        showland=True,
        landcolor="#F0E5E8",
        showocean=True,
        oceancolor="#E7EDF1",
        showcountries=True,
        countrycolor="#B99AA6",
        showcoastlines=True,
        coastlinecolor="#B99AA6",
        bgcolor=CARD
    )

    fig.update_layout(
        height=570,
        paper_bgcolor=CARD,
        font=dict(color=TEXT),
        margin=dict(
            l=5,
            r=5,
            t=25,
            b=10
        ),
        legend=dict(
            orientation="h",
            y=0
        )
    )

    return fig


# ==========================================================
# 6. SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown("""
        <div style="text-align:center; padding:15px 5px;">
            <div style="font-size:42px;">🩸</div>
            <h2 style="color:#FFFFFF !important; margin-bottom:0;">
                BloodLink
            </h2>
            <p style="color:#F8E8ED !important; font-size:12px;">
                Healthcare Network Analytics
            </p>
        </div>
        <hr style="border:1px solid #B66A83;">
    """, unsafe_allow_html=True)

    st.markdown(
        '<h3 style="color:#FFFFFF !important;">🧭 Navigation</h3>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Select a page",
        PAGES,
        key="bloodlink_navigation",
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown(
        '<h3 style="color:#FFFFFF !important;">🩸 Project Overview</h3>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div style="
        background-color:rgba(255,255,255,0.08);
        padding:12px;
        border-radius:9px;
        border:1px solid #B66A83;
    ">
        <p style="color:#FFFFFF !important;">
            <b>BloodLink</b> is a healthcare network analytics
            platform that explores the geographical distribution
            and connectivity of blood banks.
        </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="
        text-align:center;
        color:#F8E8ED;
        font-size:11px;
        padding:8px;
    ">
        Social Network Analysis Project<br>
        BloodLink © 2026
    </div>
    """, unsafe_allow_html=True)


# ==========================================================
# 7. HOME DASHBOARD
# ==========================================================

if page == "Home Dashboard":

    page_header(
        "HEALTHCARE NETWORK INTELLIGENCE",
        "🩸 BloodLink",
        "Understanding blood bank distribution and geographical connectivity across India."
    )

    region_data, selected_state, selected_district = region_filter(
        "home"
    )

    st.markdown(
        '<div class="section-label">REGIONAL OVERVIEW</div>',
        unsafe_allow_html=True
    )

    st.subheader("Blood Bank Directory at a Glance")

    total_banks = len(region_data)

    total_states = (
        region_data["state"]
        .replace("", pd.NA)
        .nunique()
    )

    total_districts = (
        region_data["district"]
        .replace("", pd.NA)
        .nunique()
    )

    valid_locations = (
        region_data.dropna(
            subset=["lat", "lon"]
        ).shape[0]
        if {"lat", "lon"}.issubset(region_data.columns)
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Blood Banks", f"{total_banks:,}")
    c2.metric("States / UTs", f"{total_states:,}")
    c3.metric("Districts", f"{total_districts:,}")
    c4.metric("Geocoded Records", f"{valid_locations:,}")

    st.divider()

    col1, col2 = st.columns([1.35, 1])

    with col1:

        st.markdown(
            '<div class="section-label">GEOGRAPHICAL DISTRIBUTION</div>',
            unsafe_allow_html=True
        )

        st.subheader("Top 10 States")

        state_counts = (
            region_data[
                region_data["state"] != ""
            ]
            .groupby("state")
            .size()
            .reset_index(name="Blood Banks")
            .sort_values(
                "Blood Banks",
                ascending=False
            )
            .head(10)
            .sort_values("Blood Banks")
        )

        if not state_counts.empty:

            fig = px.bar(
                state_counts,
                x="Blood Banks",
                y="state",
                orientation="h",
                text="Blood Banks",
                color_discrete_sequence=[WINE]
            )

            fig.update_traces(
                textposition="outside",
                textfont_color=TEXT
            )

            st.plotly_chart(
                chart_theme(fig, 440),
                use_container_width=True
            )

        else:

            st.info("No state data available for this selection.")

    with col2:

        st.markdown(
            '<div class="section-label">INSTITUTION CLASSIFICATION</div>',
            unsafe_allow_html=True
        )

        st.subheader("Blood Bank Categories")

        if "category" in region_data.columns:

            categories = (
                region_data["category"]
                .replace("", "Not Specified")
                .value_counts()
                .reset_index()
            )

            categories.columns = [
                "Category",
                "Blood Banks"
            ]

            if not categories.empty:

                fig = px.pie(
                    categories,
                    names="Category",
                    values="Blood Banks",
                    hole=0.52,
                    color_discrete_sequence=[
                        "#641D38",
                        "#963B5C",
                        "#B66A83",
                        "#DFA6B8",
                        "#C69A75",
                        "#EBD9DF"
                    ]
                )

                fig.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    textfont_color="white"
                )

                st.plotly_chart(
                    chart_theme(fig, 440),
                    use_container_width=True
                )

    st.divider()

    st.subheader("About the Blood Bank Directory")

    info1, info2 = st.columns(2)

    with info1:

        st.markdown("""
        **Available information**

        - Blood bank names and addresses
        - State and district information
        - Contact numbers and helplines
        - Institution categories
        - Facility information
        - Latitude and longitude
        """)

    with info2:

        st.markdown("""
        **Analytical applications**

        - National distribution analysis
        - Geographical proximity networks
        - Centrality and community analysis
        - Network resilience simulation
        - Interactive geographical mapping
        - Nearest blood bank distance analysis
        """)

    st.warning(
        "This application analyses directory information. "
        "It does not show live blood stock, donor availability "
        "or confirmed blood transfer relationships."
    )


# ==========================================================
# 8. FIND BLOOD BANKS
# ==========================================================

elif page == "Find Blood Banks":

    page_header(
        "BLOOD BANK DIRECTORY",
        "Find Blood Banks",
        "Explore blood bank details by state and district."
    )

    region_data, selected_state, selected_district = region_filter(
        "directory"
    )

    st.markdown(
        '<div class="section-label">DIRECTORY SEARCH</div>',
        unsafe_allow_html=True
    )

    st.subheader("Search Blood Banks")

    search_name = st.text_input(
        "Search by Blood Bank Name",
        placeholder="Type a blood bank name..."
    )

    filtered = region_data.copy()

    if search_name.strip():

        filtered = filtered[
            filtered["name"].str.contains(
                search_name.strip(),
                case=False,
                na=False,
                regex=False
            )
        ]

    a, b = st.columns([1, 3])

    a.metric(
        "Matching Records",
        f"{len(filtered):,}"
    )

    b.markdown(
        """
        <div class="info-panel">
            The directory automatically follows the state and district
            selected above.
        </div>
        """,
        unsafe_allow_html=True
    )

    display_cols = [
        "name",
        "state",
        "district",
        "address",
        "phone",
        "helpline",
        "category"
    ]

    display_cols = [
        col for col in display_cols
        if col in filtered.columns
    ]

    if not filtered.empty:

        st.dataframe(
            filtered[display_cols],
            use_container_width=True,
            hide_index=True,
            height=450
        )

    else:

        st.info("No matching blood banks found in this region.")

    st.download_button(
        "⬇️ Download Filtered Directory",
        data=filtered[display_cols].to_csv(
            index=False
        ).encode("utf-8"),
        file_name="bloodlink_filtered_directory.csv",
        mime="text/csv"
    )


# ==========================================================
# 9. NETWORK RESILIENCE
# ==========================================================

elif page == "Network Resilience":

    page_header(
        "ADVANCED SOCIAL NETWORK ANALYSIS",
        "Network Resilience Simulator",
        "Explore how removing a blood bank affects geographical connectivity."
    )

    _, selected_state, selected_district = region_filter(
        "resilience"
    )

    try:

        nodes, edges, original_full_graph = load_network_data()

    except Exception as error:

        st.error(f"Unable to load network files: {error}")
        st.stop()

    original_graph, filtered_nodes = load_graph_for_region(
        nodes,
        original_full_graph,
        selected_state,
        selected_district
    )

    if original_graph.number_of_nodes() == 0:

        st.warning("No network nodes are available for this region.")
        st.stop()

    st.subheader("Regional Network Overview")

    c = st.columns(4)

    c[0].metric(
        "Network Nodes",
        f"{original_graph.number_of_nodes():,}"
    )

    c[1].metric(
        "Network Edges",
        f"{original_graph.number_of_edges():,}"
    )

    c[2].metric(
        "Connected Components",
        f"{nx.number_connected_components(original_graph):,}"
    )

    c[3].metric(
        "Isolated Banks",
        f"{len(list(nx.isolates(original_graph))):,}"
    )

    st.divider()

    st.subheader("Select a Blood Bank to Remove")

    bank_details = filtered_nodes.set_index("bank_id")

    bank_options = filtered_nodes["bank_id"].tolist()

    selected_bank = st.selectbox(
        "Choose a blood bank",
        bank_options,
        format_func=lambda bank_id: (
            f"{bank_id} | {bank_details.loc[bank_id, 'name']} | "
            f"{bank_details.loc[bank_id, 'district']}, "
            f"{bank_details.loc[bank_id, 'state']}"
        ),
        key="resilience_selected_bank"
    )

    selected_row = bank_details.loc[selected_bank]

    selection_banner(
        str(selected_row["name"]),
        f"Selected bank: {selected_bank} | "
        f"{selected_row['district']}, {selected_row['state']} | "
        f"Geographical connections: {original_graph.degree(selected_bank)}"
    )

    simulated_graph = original_graph.copy()
    simulated_graph.remove_node(selected_bank)

    def get_network_metrics(graph):

        components = list(
            nx.connected_components(graph)
        )

        node_count = graph.number_of_nodes()

        average_degree = (
            round(
                sum(dict(graph.degree()).values()) / node_count,
                2
            )
            if node_count else 0
        )

        return {
            "Blood Banks": node_count,
            "Connections": graph.number_of_edges(),
            "Connected Components": len(components),
            "Isolated Banks": len(list(nx.isolates(graph))),
            "Largest Component": (
                max(map(len, components))
                if components else 0
            ),
            "Average Degree": average_degree,
            "Network Density": round(
                nx.density(graph), 5
            )
        }

    original_metrics = get_network_metrics(original_graph)

    simulated_metrics = get_network_metrics(simulated_graph)

    newly_isolated = []

    for bank_id in original_graph.nodes():

        if bank_id == selected_bank:
            continue

        if (
            original_graph.degree(bank_id) > 0
            and simulated_graph.degree(bank_id) == 0
        ):

            newly_isolated.append(bank_id)

    st.divider()

    st.subheader("Before and After Removal")

    before, after = st.columns(2)

    with before:

        st.markdown("### Before Removal")

        for key in [
            "Blood Banks",
            "Connections",
            "Connected Components",
            "Isolated Banks"
        ]:

            st.metric(
                key,
                f"{original_metrics[key]:,}"
            )

    with after:

        st.markdown("### After Removal")

        for key in [
            "Blood Banks",
            "Connections",
            "Connected Components",
            "Isolated Banks"
        ]:

            st.metric(
                key,
                f"{simulated_metrics[key]:,}",
                delta=(
                    simulated_metrics[key]
                    - original_metrics[key]
                ),
                delta_color="inverse"
            )

    st.divider()

    st.subheader("Impact Analysis")

    impact = st.columns(3)

    impact[0].metric(
        "Newly Isolated Banks",
        f"{len(newly_isolated):,}"
    )

    impact[1].metric(
        "Largest Component Before",
        f"{original_metrics['Largest Component']:,}"
    )

    impact[2].metric(
        "Largest Component After",
        f"{simulated_metrics['Largest Component']:,}"
    )

    comparison = pd.DataFrame({
        "Metric": [
            "Average Degree",
            "Network Density",
            "Largest Component"
        ],
        "Before Removal": [
            original_metrics["Average Degree"],
            original_metrics["Network Density"],
            original_metrics["Largest Component"]
        ],
        "After Removal": [
            simulated_metrics["Average Degree"],
            simulated_metrics["Network Density"],
            simulated_metrics["Largest Component"]
        ]
    })

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    if newly_isolated:

        st.warning(
            f"{len(newly_isolated)} previously connected "
            "blood bank(s) became isolated."
        )

        with st.expander("View newly isolated blood banks"):

            st.dataframe(
                filtered_nodes[
                    filtered_nodes["bank_id"].isin(newly_isolated)
                ][
                    ["bank_id", "name", "state", "district"]
                ],
                use_container_width=True,
                hide_index=True
            )

    else:

        st.success(
            "No additional blood banks became isolated "
            "after this node was removed."
        )

    st.subheader("Local Network Neighbours")

    neighbors = sorted(
        list(original_graph.neighbors(selected_bank)),
        key=lambda bank: original_graph.degree(bank),
        reverse=True
    )[:60]

    if not neighbors:

        st.info("This blood bank has no geographical connections.")

    else:

        def local_network_figure(
            graph,
            selected_id,
            neighbor_ids
        ):

            display_ids = set(neighbor_ids)
            display_ids.add(selected_id)

            local = graph.subgraph(display_ids)

            fig = go.Figure()

            for source, target in local.edges():

                s = local.nodes[source]
                t = local.nodes[target]

                if any(
                    pd.isna(v)
                    for v in [
                        s["lat"], s["lon"],
                        t["lat"], t["lon"]
                    ]
                ):
                    continue

                fig.add_trace(
                    go.Scatter(
                        x=[s["lon"], t["lon"], None],
                        y=[s["lat"], t["lat"], None],
                        mode="lines",
                        line=dict(
                            color="#D8B7C3",
                            width=1.5
                        ),
                        hoverinfo="skip",
                        showlegend=False
                    )
                )

            xs, ys, colors, sizes, labels = (
                [], [], [], [], []
            )

            for bank_id in local.nodes():

                row = bank_details.loc[bank_id]

                if pd.isna(row["lat"]) or pd.isna(row["lon"]):
                    continue

                xs.append(row["lon"])
                ys.append(row["lat"])

                if bank_id == selected_id:

                    colors.append(GOLD)
                    sizes.append(17)

                else:

                    colors.append(WINE)
                    sizes.append(10)

                labels.append(
                    f"{row['name']}<br>"
                    f"{row['district']}, {row['state']}<br>"
                    f"ID: {bank_id}"
                )

            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="markers",
                    marker=dict(
                        size=sizes,
                        color=colors,
                        line=dict(
                            color=CARD,
                            width=1.5
                        )
                    ),
                    text=labels,
                    hovertemplate="%{text}<extra></extra>",
                    showlegend=False
                )
            )

            fig.update_layout(
                height=430,
                paper_bgcolor=CARD,
                plot_bgcolor=CARD,
                font=dict(color=TEXT),
                margin=dict(
                    l=20,
                    r=20,
                    t=25,
                    b=20
                ),
                xaxis_title="Longitude",
                yaxis_title="Latitude"
            )

            fig.update_xaxes(gridcolor="#EDE2E5")

            fig.update_yaxes(
                gridcolor="#EDE2E5",
                scaleanchor="x",
                scaleratio=1
            )

            return fig

        left, right = st.columns(2)

        with left:

            st.markdown("**Before Removal**")

            st.plotly_chart(
                local_network_figure(
                    original_graph,
                    selected_bank,
                    neighbors
                ),
                use_container_width=True
            )

        with right:

            st.markdown("**After Removal**")

            st.plotly_chart(
                local_network_figure(
                    simulated_graph,
                    selected_bank,
                    neighbors
                ),
                use_container_width=True
            )

        st.caption(
            "Gold represents the selected blood bank. "
            "Burgundy represents neighbouring banks."
        )

    st.warning(
        "This is a hypothetical node-removal experiment on a "
        "geographical proximity network. It does not represent "
        "actual blood supply disruption or hospital operations."
    )


# ==========================================================
# 10. INTERACTIVE NETWORK MAP
# ==========================================================

elif page == "Interactive Network Map":

    page_header(
        "GEOSPATIAL NETWORK INTELLIGENCE",
        "Interactive Blood Bank Network Map",
        "Explore geographical locations and proximity connections."
    )

    _, selected_state, selected_district = region_filter(
        "network_map"
    )

    try:

        nodes, edges, graph = load_network_data()

    except Exception as error:

        st.error(f"Unable to load network files: {error}")
        st.stop()

    map_nodes = get_region_data(
        nodes,
        selected_state,
        selected_district
    ).copy()

    map_nodes = map_nodes.dropna(
        subset=["lat", "lon"]
    )

    map_nodes = map_nodes[
        map_nodes["lat"].between(-90, 90)
        & map_nodes["lon"].between(-180, 180)
    ]

    if map_nodes.empty:

        st.warning(
            "No valid geographical coordinates are available for this region."
        )
        st.stop()

    st.subheader("Map Display Options")

    show_connections = st.checkbox(
        "Show geographical proximity connections",
        value=False
    )

    visible_ids = set(
        map_nodes["bank_id"].astype(str)
    )

    filtered_edges = edges[
        edges["source"].isin(visible_ids)
        & edges["target"].isin(visible_ids)
    ].copy()

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Blood Bank Locations",
        f"{len(map_nodes):,}"
    )

    m2.metric(
        "Geographical Connections",
        f"{len(filtered_edges):,}"
    )

    m3.metric(
        "Districts Represented",
        f"{map_nodes['district'].nunique():,}"
    )

    st.divider()

    st.subheader(
        f"Blood Bank Map – "
        f"{get_region_label(selected_state, selected_district)}"
    )

    fig = go.Figure()

    if show_connections and not filtered_edges.empty:

        lookup = map_nodes.set_index("bank_id")

        line_lons = []
        line_lats = []

        for _, edge in filtered_edges.iterrows():

            source = edge["source"]
            target = edge["target"]

            if (
                source not in lookup.index
                or target not in lookup.index
            ):
                continue

            s = lookup.loc[source]
            t = lookup.loc[target]

            if any(
                pd.isna(v)
                for v in [
                    s["lat"], s["lon"],
                    t["lat"], t["lon"]
                ]
            ):
                continue

            line_lons.extend([
                s["lon"],
                t["lon"],
                None
            ])

            line_lats.extend([
                s["lat"],
                t["lat"],
                None
            ])

        if line_lons:

            fig.add_trace(
                go.Scattergeo(
                    lon=line_lons,
                    lat=line_lats,
                    mode="lines",
                    line=dict(
                        width=0.7,
                        color=GOLD
                    ),
                    opacity=0.35,
                    hoverinfo="skip",
                    name="Proximity Connections"
                )
            )

    hover = [
        f"<b>{row['name']}</b><br>"
        f"State: {row['state']}<br>"
        f"District: {row['district']}<br>"
        f"Bank ID: {row['bank_id']}"
        for _, row in map_nodes.iterrows()
    ]

    fig.add_trace(
        go.Scattergeo(
            lon=map_nodes["lon"],
            lat=map_nodes["lat"],
            mode="markers",
            marker=dict(
                size=7,
                color=WINE,
                opacity=0.88,
                line=dict(
                    width=0.6,
                    color="white"
                )
            ),
            text=hover,
            hovertemplate="%{text}<extra></extra>",
            name="Blood Banks"
        )
    )

    if selected_state == "All States":

        center_lat, center_lon = 22.5, 79

        lon_range = [67, 99]
        lat_range = [5, 38]

    else:

        center_lat = map_nodes["lat"].mean()
        center_lon = map_nodes["lon"].mean()

        lon_range = None
        lat_range = None

    geo_settings = dict(
        scope="asia",
        projection_type="mercator",
        center=dict(
            lat=center_lat,
            lon=center_lon
        ),
        showland=True,
        landcolor="#F0E5E8",
        showocean=True,
        oceancolor="#E7EDF1",
        showcountries=True,
        countrycolor="#B99AA6",
        showsubunits=True,
        subunitcolor="#D8C3CB",
        showcoastlines=True,
        coastlinecolor="#B99AA6",
        bgcolor=CARD
    )

    if lon_range:

        geo_settings["lonaxis"] = dict(
            range=lon_range
        )

        geo_settings["lataxis"] = dict(
            range=lat_range
        )

    fig.update_geos(**geo_settings)

    fig.update_layout(
        height=650,
        paper_bgcolor=CARD,
        font=dict(
            family="Arial",
            size=12,
            color=TEXT
        ),
        margin=dict(
            l=5,
            r=5,
            t=20,
            b=10
        ),
        legend=dict(
            orientation="h",
            y=0.01
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True
        }
    )

    st.caption(
        "Hover over a marker to view the blood bank's name, "
        "state, district and unique ID."
    )

    st.divider()

    st.subheader("Blood Bank Locations in Selected Region")

    display_cols = [
        "bank_id",
        "name",
        "state",
        "district",
        "lat",
        "lon"
    ]

    st.dataframe(
        map_nodes[display_cols].sort_values(
            ["state", "district", "name"]
        ),
        use_container_width=True,
        hide_index=True,
        height=350
    )

    st.warning(
        "Lines represent geographical proximity connections "
        "in the project network. They do not represent actual "
        "partnerships, blood transfers, stock availability "
        "or operational relationships."
    )


# ==========================================================
# 11. NEAREST BLOOD BANK FINDER
# ==========================================================

elif page == "Nearest Blood Bank Finder":

    page_header(
        "GEOGRAPHICAL DISTANCE ANALYSIS",
        "📍 Nearest Blood Bank Finder",
        "Find geographically nearby blood banks using your location."
    )

    try:

        nodes, edges, graph = load_network_data()

    except Exception as error:

        st.error(f"Unable to load network files: {error}")
        st.stop()

    location_nodes = nodes.copy()

    location_nodes["lat"] = pd.to_numeric(
        location_nodes["lat"],
        errors="coerce"
    )

    location_nodes["lon"] = pd.to_numeric(
        location_nodes["lon"],
        errors="coerce"
    )

    location_nodes = location_nodes.dropna(
        subset=["lat", "lon"]
    )

    location_nodes = location_nodes[
        location_nodes["lat"].between(-90, 90)
        & location_nodes["lon"].between(-180, 180)
    ].copy()

    if location_nodes.empty:

        st.warning(
            "No valid geographical coordinates are available."
        )
        st.stop()

    # LOCATION SOURCE

    st.subheader("Choose Your Reference Location")

    location_method = st.radio(
        "How would you like to set your location?",
        [
            "Detect My Current Location",
            "Enter Coordinates Manually",
            "Select a Blood Bank"
        ],
        key="location_method"
    )

    reference_lat = None
    reference_lon = None
    reference_id = None
    current_accuracy = None

    # ------------------------------------------------------
    # OPTION 1: BROWSER LOCATION
    # ------------------------------------------------------

    if location_method == "Detect My Current Location":

        st.info(
            "Click the location button and allow your browser "
            "to access your location. The app needs HTTPS or localhost."
        )

        if GEOLOCATION_AVAILABLE:

            try:

                location = streamlit_geolocation()

                if isinstance(location, dict):

                    lat_value = location.get("latitude")
                    lon_value = location.get("longitude")
                    accuracy_value = location.get("accuracy")

                    if (
                        lat_value is not None
                        and lon_value is not None
                    ):

                        test_lat = float(lat_value)
                        test_lon = float(lon_value)

                        if (
                            np.isfinite(test_lat)
                            and np.isfinite(test_lon)
                            and -90 <= test_lat <= 90
                            and -180 <= test_lon <= 180
                        ):

                            st.session_state.bloodlink_lat = test_lat
                            st.session_state.bloodlink_lon = test_lon

                            st.session_state.bloodlink_accuracy = (
                                float(accuracy_value)
                                if accuracy_value is not None
                                else None
                            )

            except Exception as error:

                st.warning(
                    f"Browser location could not be read: {error}"
                )

            saved_lat = st.session_state.bloodlink_lat
            saved_lon = st.session_state.bloodlink_lon

            if saved_lat is not None and saved_lon is not None:

                reference_lat = float(saved_lat)
                reference_lon = float(saved_lon)

                current_accuracy = (
                    st.session_state.bloodlink_accuracy
                )

                st.success("Location coordinates received.")

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Latitude",
                    f"{reference_lat:.6f}"
                )

                c2.metric(
                    "Longitude",
                    f"{reference_lon:.6f}"
                )

                c3.metric(
                    "Accuracy",
                    (
                        f"±{current_accuracy:.0f} metres"
                        if current_accuracy is not None
                        else "Not provided"
                    )
                )

                if st.button(
                    "Clear Saved Location",
                    key="clear_browser_location"
                ):

                    st.session_state.bloodlink_lat = None
                    st.session_state.bloodlink_lon = None
                    st.session_state.bloodlink_accuracy = None

                    st.rerun()

            else:

                st.warning(
                    "No coordinates have been received yet. "
                    "Click the location control above and allow permission."
                )

        else:

            st.error(
                "Geolocation package is not installed. "
                "Run: pip install streamlit-geolocation"
            )

    # ------------------------------------------------------
    # OPTION 2: MANUAL COORDINATES
    # ------------------------------------------------------

    elif location_method == "Enter Coordinates Manually":

        st.info(
            "Enter the latitude and longitude of your location. "
            "You can obtain them from Google Maps by selecting a point "
            "and copying its coordinates."
        )

        col1, col2 = st.columns(2)

        with col1:

            manual_lat = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=12.9716,
                step=0.0001,
                format="%.6f",
                key="manual_latitude"
            )

        with col2:

            manual_lon = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=77.5946,
                step=0.0001,
                format="%.6f",
                key="manual_longitude"
            )

        reference_lat = float(manual_lat)
        reference_lon = float(manual_lon)

        st.success(
            "Manual reference coordinates selected. "
            "Replace the example values with your actual coordinates."
        )

    # ------------------------------------------------------
    # OPTION 3: SELECT A BLOOD BANK
    # ------------------------------------------------------

    elif location_method == "Select a Blood Bank":

        manual_nodes = location_nodes.copy()

        manual_nodes["display_name"] = (
            manual_nodes["name"].fillna("").astype(str)
            + " | "
            + manual_nodes["district"].fillna("").astype(str)
            + ", "
            + manual_nodes["state"].fillna("").astype(str)
        )

        selected_bank = st.selectbox(
            "Select a reference blood bank",
            manual_nodes["bank_id"].tolist(),
            format_func=lambda bank_id: manual_nodes.loc[
                manual_nodes["bank_id"] == bank_id,
                "display_name"
            ].iloc[0],
            key="nearest_bank_selector"
        )

        reference = manual_nodes[
            manual_nodes["bank_id"] == selected_bank
        ].iloc[0]

        reference_lat = float(reference["lat"])
        reference_lon = float(reference["lon"])
        reference_id = selected_bank

        selection_banner(
            str(reference["name"]),
            f"{reference['district']}, {reference['state']} | "
            f"Bank ID: {selected_bank}"
        )

    # ------------------------------------------------------
    # CHECK REFERENCE LOCATION
    # ------------------------------------------------------

    if reference_lat is None or reference_lon is None:

        st.warning(
            "Set a valid reference location to view nearby blood banks."
        )
        st.stop()

    st.divider()

    st.subheader("Nearby Blood Bank Search")

    limit_to_region = st.checkbox(
        "Limit results to a selected state and district",
        value=False
    )

    if limit_to_region:

        nearby_source, _, _ = region_filter("nearest")

    else:

        nearby_source = location_nodes.copy()

    nearby_source = nearby_source.copy()

    # Use only records with valid coordinates.
    nearby_source["lat"] = pd.to_numeric(
        nearby_source["lat"],
        errors="coerce"
    )

    nearby_source["lon"] = pd.to_numeric(
        nearby_source["lon"],
        errors="coerce"
    )

    nearby_source = nearby_source.dropna(
        subset=["lat", "lon"]
    )

    nearby_source["distance_km"] = haversine_distances(
        reference_lat,
        reference_lon,
        nearby_source["lat"],
        nearby_source["lon"]
    )

    if reference_id is not None:

        nearby_source = nearby_source[
            nearby_source["bank_id"] != reference_id
        ]

    nearby = nearby_source.sort_values(
        "distance_km"
    ).reset_index(drop=True)

    col1, col2 = st.columns(2)

    with col1:

        number_to_show = st.slider(
            "Number of nearby blood banks",
            min_value=5,
            max_value=30,
            value=10,
            step=5
        )

    with col2:

        maximum_distance = st.slider(
            "Maximum distance (km)",
            min_value=5,
            max_value=500,
            value=100,
            step=5
        )

    nearby_filtered = nearby[
        nearby["distance_km"] <= maximum_distance
    ].head(number_to_show).copy()

    # RESULT METRICS

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Nearby Banks Found",
        f"{len(nearby_filtered):,}"
    )

    r2.metric(
        "Maximum Search Distance",
        f"{maximum_distance} km"
    )

    r3.metric(
        "Closest Distance",
        (
            f"{nearby_filtered.iloc[0]['distance_km']:.2f} km"
            if not nearby_filtered.empty
            else "No results"
        )
    )

    st.divider()

    st.subheader("Ranked Nearby Blood Banks")

    if nearby_filtered.empty:

        st.warning(
            "No blood banks were found within the selected distance. "
            "Increase the search distance or change the region filter."
        )

    else:

        display_nearby = nearby_filtered[
            ["name", "district", "state", "distance_km"]
        ].copy()

        display_nearby.insert(
            0,
            "Rank",
            range(1, len(display_nearby) + 1)
        )

        display_nearby = display_nearby.rename(
            columns={
                "name": "Blood Bank",
                "district": "District",
                "state": "State",
                "distance_km": "Distance (km)"
            }
        )

        st.dataframe(
            display_nearby.round(
                {"Distance (km)": 2}
            ),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Geographical Visualization")

        fig = location_map(
            reference_lat,
            reference_lon,
            nearby_filtered
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    st.subheader("How the Finder Works")

    st.markdown("""
    1. Obtain browser coordinates or enter a reference location.
    2. Read the blood bank geographical coordinates.
    3. Calculate straight-line distances using the Haversine formula.
    4. Rank the blood banks by ascending distance.
    5. Display the nearest locations in a table and map.
    """)

    st.warning(
        "Distances are straight-line estimates, not road distances "
        "or travel times. The directory does not provide guaranteed "
        "live blood stock, donor availability or operating status."
    )


# ==========================================================
# 12. HOSPITAL BLOOD BANK SEARCH & REQUEST
# ==========================================================

elif page == "Hospital Blood Bank Search & Request":

    page_header(
        "HOSPITAL SUPPORT MODULE",
        "🏥 Hospital Blood Bank Search & Request",
        "Find registered blood banks and prepare blood requirement requests."
    )

    st.info(
        "This module helps hospital staff identify registered blood banks "
        "and prepare contact requests. Blood stock and availability must "
        "be confirmed directly with each blood bank."
    )

    # ------------------------------------------------------
    # HOSPITAL DETAILS
    # ------------------------------------------------------

    st.subheader("1. Hospital Information")

    with st.form("hospital_request_form"):

        col1, col2 = st.columns(2)

        with col1:

            hospital_name = st.text_input(
                "Hospital Name *",
                placeholder="Enter hospital name"
            )

            hospital_contact = st.text_input(
                "Contact Person",
                placeholder="Enter staff name"
            )

            hospital_phone = st.text_input(
                "Hospital Contact Number *",
                placeholder="Enter contact number"
            )

        with col2:

            blood_group = st.selectbox(
                "Required Blood Group",
                [
                    "A+", "A-", "B+", "B-",
                    "AB+", "AB-", "O+", "O-"
                ]
            )

            units_required = st.number_input(
                "Required Units",
                min_value=1,
                max_value=100,
                value=1,
                step=1
            )

            urgency = st.selectbox(
                "Request Priority",
                [
                    "Routine",
                    "Urgent",
                    "Emergency"
                ]
            )

        additional_notes = st.text_area(
            "Additional Notes",
            placeholder="Enter any relevant request details (optional)"
        )

        submitted = st.form_submit_button(
            "Prepare Hospital Request",
            use_container_width=True
        )

    if submitted:

        if not hospital_name.strip():
            st.error("Please enter the hospital name.")

        elif not hospital_phone.strip():
            st.error("Please enter the hospital contact number.")

        else:

            st.session_state["hospital_request"] = {
                "Hospital Name": hospital_name.strip(),
                "Contact Person": hospital_contact.strip(),
                "Hospital Phone": hospital_phone.strip(),
                "Required Blood Group": blood_group,
                "Required Units": int(units_required),
                "Priority": urgency,
                "Additional Notes": additional_notes.strip()
            }

            st.success(
                "Hospital request details prepared successfully."
            )

    # ------------------------------------------------------
    # REQUEST SUMMARY
    # ------------------------------------------------------

    if "hospital_request" in st.session_state:

        request = st.session_state["hospital_request"]

        st.divider()

        st.subheader("2. Hospital Request Summary")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Blood Group",
            request["Required Blood Group"]
        )

        c2.metric(
            "Required Units",
            request["Required Units"]
        )

        c3.metric(
            "Priority",
            request["Priority"]
        )

        st.write("**Hospital:**", request["Hospital Name"])
        st.write("**Contact Person:**", request["Contact Person"])
        st.write("**Contact Number:**", request["Hospital Phone"])

        if request["Additional Notes"]:
            st.write("**Additional Notes:**", request["Additional Notes"])

        request_df = pd.DataFrame([request])

        st.download_button(
            "⬇️ Download Hospital Request",
            data=request_df.to_csv(index=False).encode("utf-8"),
            file_name="bloodlink_hospital_request.csv",
            mime="text/csv",
            use_container_width=True
        )

    # ------------------------------------------------------
    # FIND REGISTERED BLOOD BANKS
    # ------------------------------------------------------

    st.divider()

    st.subheader("3. Find Registered Blood Banks")

    st.write(
        "Select the region where the hospital wants to search "
        "for registered blood banks."
    )

    hospital_banks, hospital_state, hospital_district = region_filter(
        "hospital"
    )

    st.metric(
        "Registered Blood Banks Found",
        f"{len(hospital_banks):,}"
    )

    if not hospital_banks.empty:

        contact_columns = [
            "name",
            "state",
            "district",
            "address",
            "phone",
            "helpline",
            "website"
        ]

        contact_columns = [
            col for col in contact_columns
            if col in hospital_banks.columns
        ]

        st.dataframe(
            hospital_banks[contact_columns],
            use_container_width=True,
            hide_index=True,
            height=400
        )

        st.download_button(
            "⬇️ Download Blood Bank Contact Directory",
            data=hospital_banks[contact_columns]
                .to_csv(index=False)
                .encode("utf-8"),
            file_name="bloodlink_hospital_blood_bank_contacts.csv",
            mime="text/csv"
        )

    else:

        st.warning(
            "No registered blood banks found for the selected region."
        )

    # ------------------------------------------------------
    # IMPORTANT LIMITATIONS
    # ------------------------------------------------------

    st.divider()

    st.subheader("4. Important Information")

    st.markdown("""
    - BloodLink displays registered blood bank directory information.
    - The selected blood group is a hospital requirement, not a stock filter.
    - Blood group availability must be confirmed directly with the blood bank.
    - Hospital requests are prepared as downloadable records.
    - No request is automatically transmitted to a blood bank.
    - Emergency requests must be handled through verified hospital and
      blood bank communication channels.
    """)

    st.warning(
        "BloodLink does not currently provide live blood stock, "
        "cross-matching, transfusion management or confirmed availability. "
        "Do not rely on this directory alone for emergency treatment."
    )


# ==========================================================
# 13. FOOTER
# ==========================================================

st.markdown("""
<div class="bloodlink-footer">
    <strong style="color:#641D38;">🩸 BloodLink</strong>
    &nbsp; | &nbsp;
    Healthcare Network Analytics
    <br>
    <span style="font-size:11px;color:#755D67;">
        Social Network Analysis Mini Project
        · Directory-based geographical analysis
    </span>
</div>
""", unsafe_allow_html=True)

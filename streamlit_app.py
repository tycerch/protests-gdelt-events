import altair as alt
import pandas as pd
import streamlit as st
import pydeck as pdk

# Show the page title and description.
st.set_page_config(page_title="US Civil Unrest Analysis", page_icon="📢")
st.title("📢 US Civil Unrest Analysis")
st.markdown(
    """
    # About This App
    
    This app visualizes protest and political dissent events across the
    United States using the GDELT Events dataset from
    Google BigQuery Public Datasets.

    ### Dataset Details:
    - Events are filtered for the United States
    - Contains CAMEO event code 14 (Protest)
    - Includes events with average tone < -5 (indicating negative sentiment)
    - Covers various forms of protests from demonstrations to political dissent
    
    Use the filters below to explore protest patterns across different
    categories and years.
    """
)


# Load the data from a CSV. We're caching this so it doesn't reload every time
# the app reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/protest_events_gdelt_bq.csv")
    return df


df = load_data()
#  print(df.columns)

# Show a multiselect widget with the genres using `st.multiselect`.
categories = st.multiselect(
    "Protest Category",
    df.ProtestCategory.unique(),
    ["Demonstration/Rally", "Hunger Strike", "Strike/Boycott",
     "Obstruction/Blockade", "Violent Protest/Riot", 
     "Other Political Dissent"],
)

# Show a slider widget with the years using `st.slider`.
years = st.slider("Years", 2020, 2025, (2020, 2024))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["ProtestCategory"].isin(categories)) &
                 (df["Year"].between(years[0], years[1]))]

# Add placeholder record column for counting events
df_filtered["RecordCount"] = 1
#  print(df_filtered.head())
df_reshaped = df_filtered.pivot_table(
    index="Year", columns="ProtestCategory", values="RecordCount", 
    aggfunc="count", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="Year", ascending=False)

# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"Year": st.column_config.TextColumn("Year")},
)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="Year",
    var_name="category", value_name="protests"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("protests:Q", title="Number of Protests"),
        color="category:N",
    )
    .properties(height=420)
)

st.altair_chart(chart, use_container_width=True)

# Display the protest map using st.pydeck so we can show density of events and
# add tooltip, st.map cannot do that

st.subheader("Protest Event Locations")
st.markdown(
    """
    The map below shows the locations of protests across the United States.
    Each hexagon represents a cluster of protest events weighted by impact
    (# of mentions).
    """
)

with st.spinner('Loading map... This may take a few moments.'):
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            # Update to center of US
            initial_view_state=pdk.ViewState(
                latitude=39.8283,
                longitude=-98.5795,
                zoom=3,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=df_filtered,
                    get_position=["ActionGeo_Long", "ActionGeo_Lat"],
                    get_weight="NumMentions",
                    radius=60000,  # Hex size in meters
                    coverage=0.9,  # how much area to cover with hexagons
                    extruded=False,
                    auto_highlight=True,  # Highlight on hover
                    pickable=True,  # Enable tooltips
                    upper_percentile=80,  # Cap extreme values
                    opacity=0.3,
                    aggregation='SUM'
                ),
            ],
            tooltip={
                "html": "<b>Total Media Mentions:</b> {elevationValue}<br/>",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
        )
    )

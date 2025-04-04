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
    United States using the [GDELT Events](https://www.gdeltproject.org/) 
    dataset from Google BigQuery Public Datasets.

    ### Dataset Details:
    - Events are filtered for the United States
    - Contains CAMEO event code 14 (Protest)
    - Includes events with average tone < -5 (indicating negative sentiment)
    - Covers various forms of protests from demonstrations to political dissent
    - Data is static and ends 4/3/2025
    
    Use the filters below to explore protest patterns across different
    categories and years.
    """
)


# Load the data from a CSV. We're caching this so it doesn't reload every time
# the app reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():

    columns = [
        'Year',
        'SQLDATE',
        'ActionGeo_Lat',
        'ActionGeo_Long',
        'ActionGeo_FullName',
        'ProtestCategory',
        'NumMentions',
        'NumArticles',
        'HeadlineSegment'
    ]

    df = pd.read_csv("data/protest_events_gdelt_bq.csv",
                     usecols=columns,
                     dtype={
                         'Year': 'int16',
                         'SQLDATE': 'int32',
                         'ActionGeo_Lat': 'float32',
                         'ActionGeo_Long': 'float32',
                         'ActionGeo_FullName': 'category',
                         'ProtestCategory': 'category',
                         'NumMentions': 'int16',
                         'NumArticles': 'int16',
                         'HeadlineSegment': 'string'
                     })
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
# print(df_filtered.head())
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
    .properties(height=520)
)

st.altair_chart(chart, use_container_width=True)

# Display the protest map using st.pydeck so we can show density of events and
# add tooltip, st.map cannot do that

st.subheader("Protest Event Locations")
st.markdown(
    """
    The map below shows the locations of protests across the United States.
    The heatmap intensity represents areas with more media coverage (number of articles),
    while individual dots show specific event locations. Highlight any dot for event details.
    """
)


# Function to format SQL date to human readable format
def format_date(sqldate):
    return pd.to_datetime(str(sqldate), format='%Y%m%d').strftime('%Y-%m-%d')


with st.spinner('Loading map... This may take a few moments.'):
    # Format date
    df_filtered['FormattedDate'] = df_filtered['SQLDATE'].apply(format_date)

    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=df_filtered,
        id="heatmap-layer",
        get_position=["ActionGeo_Long", "ActionGeo_Lat"],
        get_weight="NumArticles",
        aggregation='SUM',
        opacity=0.3,
        radiusPixels=40,  # size of the heatmap radius
        intensity=2,  # intensity of the heatmap, brighter areas
        threshold=0.05  # threshold for the heatmap, hides faint areas

    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_filtered,
        id="scatter-layer",
        get_position=["ActionGeo_Long", "ActionGeo_Lat"],
        get_radius=2000,  # size of the scatterplot radius
        pickable=True,
        auto_highlight=True,
        opacity=0.3,
        stroked=True,
        filled=True,
        radius_scale=1,  # radius multiplier
        get_fill_color=[255, 0, 0, 180],
        get_line_color=[0, 0, 0, 150]
    )

    chart_event = st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=39.8283,
                longitude=-98.5795,
                zoom=3,
                pitch=0
            ),
            layers=[heatmap_layer, scatter_layer],
            tooltip={
                "html": "<b>{ActionGeo_FullName}</b><br/>"
                        "Date: {FormattedDate}<br/>"
                        "Category: {ProtestCategory}<br/>"
                        "Articles: {NumArticles}<br/>"
                        "Mentions: {NumMentions}<br/>"
                        "Headline: {HeadlineSegment}"
            },
        ),
        use_container_width=True
    )

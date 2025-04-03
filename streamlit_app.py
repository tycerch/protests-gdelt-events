import altair as alt
import pandas as pd
import streamlit as st
import numpy as np

# Show the page title and description.
st.set_page_config(page_title="USA Protest Events Explorer", page_icon="📢")
st.title("📢 Protest Events Explorer (USA)")
st.write(
    """
    This app explores the Protest GDELT Events dataset from Bigquery, filtered for USA.  CAMEO event code 14 with average event tone of < -5.
    """
)


# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/protest_events_gdelt_bq.csv")
    return df


df = load_data()
print(df.columns)

# Show a multiselect widget with the genres using `st.multiselect`.
categories = st.multiselect(
    "Protest Category",
    df.ProtestCategory.unique(),
    ["Demonstration/Rally", "Hunger Strike", "Strike/Boycott", "Obstruction/Blockade", "Violent Protest/Riot", "Other Political Dissent"],
)

# Show a slider widget with the years using `st.slider`.
years = st.slider("Years", 2020, 2025, (2020, 2024))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["ProtestCategory"].isin(categories)) & (df["Year"].between(years[0], years[1]))]
df_filtered["RecordCount"] = 1
print(df_filtered.head())
df_reshaped = df_filtered.pivot_table(
    index="Year", columns="ProtestCategory", values="RecordCount", aggfunc="count", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="Year", ascending=False)

# Display map of protests
st.subheader("Protest Event Locations")
st.map(df_filtered, latitude="ActionGeo_Lat", longitude="ActionGeo_Long")

# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"Year": st.column_config.TextColumn("Year")},
)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="Year", var_name="category", value_name="protests"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("protests:Q", title="Number of Protests"),
        color="category:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
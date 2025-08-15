import streamlit as st
import pandas as pd
from millify import millify
import plotly.express as px
import altair as alt
import requests



def style_metric_cards(
    color: str = "#232323",
    background_color: str = "#FFF",
    border_size_px: int = 1,
    border_color: str = "#CCC",
    border_radius_px: int = 5,
    border_left_color: str = "#9AD8E1",
    box_shadow: bool = True,
):
    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            .metric-card-container {{
                background-color: #91c8f1;
                border: {border_size_px}px solid {border_color};
                padding: 1rem;
                border-radius: {border_radius_px}px;
                margin-bottom: 1rem;
                color: {color};
                {box_shadow_str}
            }}
            .metric-card-value {{
                font-size: 2rem;
                font-weight: bold;
            }}
            .metric-card-label {{
                font-size: 2rem;
            }}
            .metric-card-delta {{
                font-size: 1rem;
            }}
            .metric-card-icon {{
                font-size: 3rem;
                margin-right: 0.5rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Define page layout
st.set_page_config(
    page_title="City Of Payrs Olympics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",  # Set sidebar initially open
)

# Custom styling for the sidebar
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("<h2 style='text-align: center;'>City Of Parys Olympics</h2>", unsafe_allow_html=True)
    st.write("")
with st.sidebar:
    st.sidebar.image('logo.png', caption='Faster, Higher, Stronger – Together', use_column_width=True)
    st.markdown("Welcome to the City of Parys Olympic Website Analytics dashboard that serves to give insight about the useage of the  olymic webiste viewership.")



# Define your Flask API endpoint
# API_ENDPOINT = "http://localhost:5000/get_data"

# Function to fetch data from Flask API
#def fetch_data_from_api():
   ## response = requests.get(API_ENDPOINT)
    #if response.status_code == 200:
    #    return pd.DataFrame(response.json())
   # else:
    #    st.error("Failed to fetch data from the API")


def fetch_data_from_flask_api():
    response = requests.get("https://kefentsemothusi.pythonanywhere.com/get_data")
    data = response.json()
    
    return pd.DataFrame.from_dict(data)

# Load data
df = fetch_data_from_flask_api()

 # @st.cache
def load_data(df):
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d/%m/%Y %H:%M")
    df["date"] = df["Timestamp"].dt.date
    return df

df = load_data(df)


# Filter data based on date range
date_range = st.sidebar.slider("Select Date Range", min_value=df["date"].min(), max_value=df["date"].max(), value=(df["date"].min(), df["date"].max()))
df_filtered = df[(df["date"] >= date_range[0]) & (df["date"] <= date_range[1])]

# Main content
with st.container():
  #  st.markdown("<h2 style='text-align: center;'>City Of Payrs Olympics</h2>", unsafe_allow_html=True)
 #   st.write("")

    # Calculations for metrics
    daily_counts = df_filtered.groupby(df_filtered["Timestamp"].dt.date)["IP Address"].count()
    successful_requests = df_filtered[df_filtered["Response Code"] == "Succesful Request"].shape[0]
    total_requests = df_filtered.shape[0]
    percentage_successful_requests = (successful_requests / total_requests) * 100
    average_visits_per_day = daily_counts.mean()
    target_success_rate = 70

    # Styling for metric cards
    style_metric_cards()

    # Metric cards
    col1, col2, col3 = st.columns(3)

    col1.markdown(
        f"""
        <div class="metric-card-container" style="border-left: 1rem solid #052945 ; text-align: center; ">
            <div class="metric-card-value">{total_requests}</div>
            <div class="metric-card-label">Total Visits</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col2.markdown(
        f"""
        <div class="metric-card-container" style="border-left: 1rem solid #052945 ; text-align: center; ">
            <div class="metric-card-value">{millify(average_visits_per_day, precision=0)}</div>
            <div class="metric-card-label">Daily Average</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col3.markdown(
        f"""
        <div class="metric-card-container" style="border-left: 1rem solid #052945 ;text-align: center; ">
            <div class="metric-card-value">{millify(percentage_successful_requests, precision=0)}%</div>
            <div class="metric-card-label">Successful Request Rate</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def make_choropleth(df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(
        df,
        locations=input_id,
        color=input_column,
        locationmode="country names",
        color_continuous_scale=input_color_theme,
        range_color=(0, 500),
        scope="world",
        labels={"count": "Views"},
    )
    choropleth.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=350,
    )
    return choropleth


# plots grp1
with st.container():
    col1, col2 = st.columns(2)
    top_pages = df_filtered["Requested URL"].value_counts()
    top_pages = pd.DataFrame(top_pages).reset_index()

    status_codes = df_filtered["Response Code"].value_counts()
    status_codes = pd.DataFrame(status_codes).reset_index()

    with col1:
        st.markdown("#### Requested Pages and Response Codes")
        chart = alt.Chart(df_filtered).mark_bar(opacity=0.9).encode(
            y=alt.Y("count():Q", sort="-x", title="Vists"),
            x=alt.X("Requested URL:O", title="Requested Page"),
            color="Response Code:N",
        )

        st.altair_chart(chart, use_container_width=True)

    with col2:
        st.markdown("#### Visits Per Country")
        views = df_filtered["Country"].value_counts()
        views = pd.DataFrame(views).reset_index()

        choropleth = make_choropleth(views,"Country","count", "plasma")

        st.plotly_chart(choropleth, use_container_width=True)


with st.container():
  #  df_filtered["Date"] = df_filtered["Timestamp"].dt.date
    daily_viewership = df_filtered["date"].value_counts()
    daily_viewership = pd.DataFrame(daily_viewership).reset_index()
 #   daily_viewership["date"] = pd.to_datetime(df_filtered["Date"], format="%d/%m/%Y")
    daily_viewership = daily_viewership.sort_values("date")

    chart = alt.Chart(daily_viewership).mark_line(opacity=0.9).encode(
        x="date:T", y="count:Q"
    ).properties(title="Viewership Trend")
    st.altair_chart(chart, use_container_width=True)

with st.container():
    with st.expander("View Data"):
        st.write(df_filtered.iloc[:500,1:20].style.background_gradient(cmap="Oranges"))


    # Download original DataSet
    csv = df.to_csv(index=False).encode('utf-8')  # Convert DataFrame to CSV bytes
    st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")

with st.container():
    st.markdown(
        """
<footer style="text-align:center; padding: 10px; border-top: 1px solid #ccc;">
    Made by Nomnom Analytics
</footer>
""",
        unsafe_allow_html=True,
    )

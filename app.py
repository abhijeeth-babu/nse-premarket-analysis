import streamlit as st
import pandas as pd
import numpy as np
import nsepython as nse
import datetime as dt

# Set the page width using HTML/CSS
st.set_page_config(layout="wide")


# # Function to refresh the page
# def refresh_page():
#     st.experimental_rerun()


# # Add a button to trigger the refresh
# if st.button("Refresh Page", key="refresh_button", help="Click to refresh the page"):
#     refresh_page()


@st.cache_data
def nse_preopen(key="ALL"):
    try:
        api = "https://www.nseindia.com/api/market-data-pre-open?key="
        positions = nse.nsefetch(api + key)
        idf = pd.DataFrame(positions["data"])
        df = pd.json_normalize(idf["metadata"])[
            ["symbol", "pChange", "lastPrice", "totalTurnover"]
        ].dropna()
        adv_dec = np.array(
            [[positions["advances"], positions["declines"], positions["unchanged"]]]
        )
        return df, adv_dec
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None


# Holidays
@st.cache_data
def fetch_holidays():
    try:
        idf = nse.nse_holidays()
        df = pd.json_normalize(idf["CBM"])[["tradingDate", "weekDay", "description"]]
        df["description"] = df["description"].str.strip()
        return df
    except Exception as e:
        st.error(f"Error fetching holidays: {e}")
        return None


def is_holiday(today, holidays):
    today_str = today.strftime("%d-%b-%Y")
    is_weekend = today.weekday() >= 5

    if is_weekend or (today_str in holidays["tradingDate"].values):
        holiday_info = holidays[holidays["tradingDate"] == today_str]
        if not holiday_info.empty:
            return True, holiday_info.iloc[0]["description"]
        return True, "Weekend"

    return False, None


# Display the current date and check if it's a holiday
holidays = fetch_holidays()
current_date = dt.datetime.now().strftime("%d-%b-%Y")
is_holiday_today, holiday_description = is_holiday(dt.datetime.now(), holidays)

st.title(f"Market Data for {current_date}")
if is_holiday_today:
    st.warning(f"Today is a holiday: {holiday_description}.")
elif holiday_description == "Weekend":
    st.warning("Today is a weekend.")

# Increase font size for select index
st.subheader("Select Index")
# Load the initial data
key_options = ["NIFTY", "BANKNIFTY", "SME", "FO", "OTHERS", "ALL"]
selected_key = st.selectbox(
    "Choose index from dropdown.", key_options, index=key_options.index("ALL")
)

df, adv_dec = nse_preopen(selected_key)

# Add a button to refresh the data
refresh_data = st.button("Refresh Data")

# Fetch data or use cached data
refresh_status = st.empty()  # Placeholder for the refresh status message
if refresh_data:
    refresh_status.warning("Data is being refreshed. This may take a moment.")
    df, adv_dec = nse_preopen(selected_key)
    refresh_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    refresh_status.success(f"Data has been refreshed at {refresh_time}!")


# Add filters for numerical columns
st.sidebar.header("Filters")

# Filter 1: Gainer Percent Change
min_gainer_chg_per = st.sidebar.number_input(
    "Min Gainer % Change", min_value=-10.0, max_value=10.0, value=0.9
)
max_gainer_chg_per = st.sidebar.number_input(
    "Max Gainer % Change", min_value=-10.0, max_value=10.0, value=3.0
)
q_gain = "@min_gainer_chg_per < pChange < @max_gainer_chg_per"
# Filter 2: Loser Percent Change
min_loser_chg_per = st.sidebar.number_input(
    "Min Loser % Change", min_value=-10.0, max_value=10.0, value=-3.0
)
max_loser_chg_per = st.sidebar.number_input(
    "Max Loser % Change", min_value=-10.0, max_value=10.0, value=-0.9
)
q_loss = "@min_loser_chg_per < pChange < @max_loser_chg_per"

# Filter 3: Price
min_price, max_price = st.sidebar.slider(
    "Price", min_value=0, max_value=2000, value=(10, 1500)
)
q_price = "@min_price < lastPrice < @max_price"
# Filter 4: Total Turnover
min_turnover = st.sidebar.number_input(
    "Total Turnover (Min)", min_value=0, value=500_000
)
q_turn = "totalTurnover > @min_turnover"

# Create top gainers and top losers from filtered_df
top_gainers = (
    df.query(f"{q_gain} and {q_price} and {q_turn}")
    # .nlargest(20, "pChange")
    .sort_values("pChange", ascending=False).reset_index(drop=True)
)
top_losers = (
    df.query(f"{q_loss} and {q_price} and {q_turn}")
    # .nsmallest(20, "pChange")
    .sort_values("pChange").reset_index(drop=True)
)

# Show turnover or not
show_turnover = st.checkbox("Show Total Turnover", value=False)

# Display the Top Gainers and Top Losers side by side with solid color
st.markdown(
    """
    <style>
        table {
            width: 90%;
            margin: 0 auto;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.header("Premarket Analysis")

# Display Top Gainers and Top Losers side by side
col1, col2 = st.columns(2)

turnover_subset = ["pChange", "lastPrice", "totalTurnover"]
if not show_turnover:
    top_gainers = top_gainers.iloc[:, :-1]
    top_losers = top_losers.iloc[:, :-1]
    turnover_subset = turnover_subset[:-1]

with col1:
    st.subheader("Top Gainers")
    st.dataframe(
        top_gainers.style.format("{:.2f}", subset=turnover_subset).background_gradient(
            axis=0, gmap=top_gainers["pChange"], cmap="Greens"
        )
    )

with col2:
    st.subheader("Top Losers")
    st.dataframe(
        top_losers.style.format("{:.2f}", subset=turnover_subset).background_gradient(
            axis=0, gmap=-1 * top_losers["pChange"], cmap="Reds"
        )
    )

# Display the Counts for Advances, Declines, and Unchanged
st.subheader("Market Status")
st.text(
    f"Advances: {adv_dec[0, 0]} | Declines: {adv_dec[0, 1]} | Unchanged: {adv_dec[0, 2]}"
)

# Streamlit NSE Pre-Market Analysis App

This Streamlit app displays pre-market data for NSE indices and stocks. It provides information on top gainers, top losers, market status, and allows users to apply filters based on various criteria.

Find the app on [Streamlit Sharing](https://abhijeeth-babu-nse-premarket-analysis-app-uewntx.streamlit.app/)

## Features

- **Select Index:** Choose from different NSE indices, including NIFTY, BANKNIFTY, SME, FO, OTHERS, and view pre-market data.

- **Refresh Data:** Users can manually refresh the data by clicking the "Refresh Data" button.

- **Filters:** Apply filters to customize the data based on gainer/loser percent change, price, and total turnover.

- **Top Gainers and Losers:** The app displays top gainers and top losers in a tabular format with color-coded styling.

- **Market Status:** Provides the current status of advances, declines, and unchanged stocks.

## How to Run

1. Install the required dependencies using the provided `requirements.txt` file.
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit app.
   ```bash
   streamlit run app.py
   ```

3. Open the provided URL in your web browser to access the app.

## Filters

The sidebar provides options to filter the data based on:

- **Gainer Percent Change:** Specify minimum and maximum percentage change for gainers.

- **Loser Percent Change:** Specify minimum and maximum percentage change for losers.

- **Price:** Set the price range for stocks.

- **Total Turnover:** Set the minimum total turnover for stocks.

## Development

To contribute or make changes to the app:

1. Clone this repository.
   ```bash
   git clone https://github.com/your-username/streamlit-nse-market-data
   ```
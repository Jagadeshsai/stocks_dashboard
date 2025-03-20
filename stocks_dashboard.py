import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta

# Function to fetch stock data
def get_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)

        if data is None or data.empty:
            st.error(f"⚠ No data available for {ticker}. Please check the symbol and try again.")
            return None

        # Fix column index if MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        if 'Close' not in data.columns:
            st.error("'Close' column is missing. Unable to compute indicators.")
            return None

        return data

    except Exception as e:
        st.error(f" Error fetching data for {ticker}: {str(e)}")
        return None

# Function to calculate indicators
def calculate_indicators(data, show_sma, sma_period, show_ema, ema_period, show_bollinger, show_rsi, show_macd):
    if data is None or data.empty:
        return None
    
    data = data.dropna(subset=['Close'], how='any')

    if show_sma and len(data) > sma_period:
        data[f'SMA_{sma_period}'] = ta.trend.sma_indicator(data['Close'], window=sma_period)

    if show_ema and len(data) > ema_period:
        data[f'EMA_{ema_period}'] = ta.trend.ema_indicator(data['Close'], window=ema_period)

    if show_bollinger and len(data) > 20:
        indicator_bb = ta.volatility.BollingerBands(close=data["Close"], window=20, window_dev=2)
        data['BB_high'] = indicator_bb.bollinger_hband()
        data['BB_low'] = indicator_bb.bollinger_lband()

    if show_rsi and len(data) > 14:
        data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()

    if show_macd and len(data) > 26:
        macd = ta.trend.MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['MACD_signal'] = macd.macd_signal()

    return data

# Function to plot stock data
def plot_stock_data(data, ticker, show_sma, sma_period, show_ema, ema_period, show_bollinger, show_rsi, show_macd):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price', line=dict(color='blue')))

    if show_sma and f'SMA_{sma_period}' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data[f'SMA_{sma_period}'], mode='lines', name=f'SMA {sma_period}', line=dict(color='orange')))

    if show_ema and f'EMA_{ema_period}' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data[f'EMA_{ema_period}'], mode='lines', name=f'EMA {ema_period}', line=dict(color='green')))

    if show_bollinger and 'BB_high' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_high'], mode='lines', name='Bollinger High', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_low'], mode='lines', name='Bollinger Low', line=dict(color='purple')))

    fig.update_layout(title=f"{ticker} Stock Price", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig)

    if show_rsi and 'RSI' in data.columns:
        st.subheader("Relative Strength Index (RSI)")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='yellow')))
        fig_rsi.add_hline(y=70, line_dash="dot", line=dict(color="red"))
        fig_rsi.add_hline(y=30, line_dash="dot", line=dict(color="green"))
        st.plotly_chart(fig_rsi)

    if show_macd and 'MACD' in data.columns:
        st.subheader("MACD Indicator")
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='cyan')))
        fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], mode='lines', name='Signal Line', line=dict(color='magenta')))
        st.plotly_chart(fig_macd)

# Streamlit App
def main():
    st.title("📈 Stock Market Dashboard")
    st.sidebar.header("Stock Selection")

    # Dropdown menu for stock selection
    stock_list = {
        "Apple (AAPL)": "AAPL",
        "Tesla (TSLA)": "TSLA",
        "Amazon (AMZN)": "AMZN",
        "Microsoft (MSFT)": "MSFT",
        "Google (GOOGL)": "GOOGL",
        "NVIDIA (NVDA)": "NVDA",
        "Meta (META)": "META",
        "Netflix (NFLX)": "NFLX"
    }

    selected_stock = st.sidebar.selectbox("Choose a stock:", list(stock_list.keys()))
    ticker = stock_list[selected_stock]

    start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))
    end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

    # Indicator Selection
    show_sma = st.sidebar.checkbox("Show SMA", value=True)
    sma_period = st.sidebar.slider("SMA Period", min_value=5, max_value=100, value=20)

    show_ema = st.sidebar.checkbox("Show EMA", value=False)
    ema_period = st.sidebar.slider("EMA Period", min_value=5, max_value=100, value=20)

    show_bollinger = st.sidebar.checkbox("Show Bollinger Bands", value=False)
    show_rsi = st.sidebar.checkbox("Show RSI", value=False)
    show_macd = st.sidebar.checkbox("Show MACD", value=False)

    # Fetch Data
    data = get_stock_data(ticker, start_date, end_date)

    if data is not None:
        data = calculate_indicators(data, show_sma, sma_period, show_ema, ema_period, show_bollinger, show_rsi, show_macd)
        if data is not None:
            plot_stock_data(data, ticker, show_sma, sma_period, show_ema, ema_period, show_bollinger, show_rsi, show_macd)
        else:
            st.error(" No valid data for plotting.")
    else:
        st.error("Failed to fetch stock data. Check the ticker symbol or try again later.")

if __name__ == "__main__":
    main()

import pandas as pd
import yfinance as yf
import numpy as np
import ta
import matplotlib.pyplot as plt


def calculate_bollinger_band_and_RSI(df, n=20):
    """Function to calculate Bollinger Band and RSI"""
    df["MA"] = df["Close"].rolling(window=n).mean()
    df["BB_up"] = df["MA"] + 2 * df["Close"].rolling(window=n).std()
    df["BB_down"] = df["MA"] - 2 * df["Close"].rolling(window=n).std()
    df["RSI"] = ta.momentum.rsi(df["Close"], window=n)
    return df


def trading_strategy(df, capital=100000000):
    """Function to implement the trading strategy"""
    df = calculate_bollinger_band_and_RSI(df)
    position = 0
    stop_loss = 0.05
    take_profit = 0.10
    transaction_log = []
    for i in range(len(df)):
        close = df["Close"].iloc[i]
        if np.isnan(close):
            continue
        # check if the stock price hit the lower bound of Bollinger band
        elif (
            close <= df["BB_down"].iloc[i] and df["RSI"].iloc[i] < 30 and position == 0
        ):
            position = capital / close  # take a LONG position
            transaction_value = position * close
            capital -= transaction_value  # update capital after transaction value is calculated
            transaction_log.append(
                [df.index[i], "BUY", close, position, transaction_value, 0, capital]
            )
        elif close >= df["BB_up"].iloc[i] and df["RSI"].iloc[i] > 70 and position != 0:
            transaction_value = position * close
            profit = transaction_value - (position * df["MA"].iloc[i])
            capital += transaction_value  # sell and take a SHORT position
            transaction_log.append(
                [
                    df.index[i],
                    "SELL",
                    close,
                    position,
                    transaction_value,
                    profit,
                    capital,
                ]
            )
            position = 0
        elif position * close >= position * df["Close"].iloc[i - 1] * (1 + take_profit):
            transaction_value = position * close
            profit = transaction_value - (position * df["MA"].iloc[i])
            capital += transaction_value  # sell with profit
            transaction_log.append(
                [
                    df.index[i],
                    "SELL",
                    close,
                    position,
                    transaction_value,
                    profit,
                    capital,
                ]
            )
            position = 0
        elif position * close <= position * df["Close"].iloc[i - 1] * (1 - stop_loss):
            transaction_value = position * close
            profit = transaction_value - (position * df["MA"].iloc[i])
            capital += transaction_value  # sell with loss
            transaction_log.append(
                [
                    df.index[i],
                    "SELL",
                    close,
                    position,
                    transaction_value,
                    profit,
                    capital,
                ]
            )
            position = 0
    transaction_df = pd.DataFrame(
        transaction_log,
        columns=[
            "Date",
            "Action",
            "Price",
            "Quantity",
            "Transaction Value",
            "Profit/Loss",
            "Remaining Balance",
        ],
    )
    return capital, transaction_df


# Download historical data as dataframe
df = yf.download("AAPL", "2022-01-01", "2023-01-01")

# Run the strategy
final_capital, transaction_df = trading_strategy(df)
print(f"Final capital after one year: {final_capital}")
print("Transaction Log:")
print(transaction_df)

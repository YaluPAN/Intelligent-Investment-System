import pandas as pd
import numpy as np
import talib
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.offline import plot


class TradingBot:
    def __init__(self, df):
        self.df = df
        self.close_price = df["Close"]
        self.df["RSI"] = self.cal_RSI(14)
        self.RSI = self.df["RSI"]
        (
            self.df["Middle Band"],
            self.df["Upper Band"],
            self.df["Lower Band"],
        ) = self.cal_Bollinger_bands(30, 2)
        self.middle_band = self.df["Middle Band"]
        self.upper_band = self.df["Upper Band"]
        self.lower_band = self.df["Lower Band"]
        self.df["touch_upper"], self.df["touch_lower"] = self.check_touch_bands(0.05)
        self.touch_upper, self.touch_lower = (
            self.df["touch_upper"],
            self.df["touch_lower"],
        )
        self.df["Long Entry"] = False
        self.df["Long Exit"] = False
        self.df["Short Entry"] = False
        self.df["Short Exit"] = False
        self.df["Long Profit"] = 0.0
        self.df["Short Profit"] = 0.0
        self.df["Balance"] = 0.0
        self.long_entry = self.df["Long Entry"]
        self.long_exit = self.df["Long Exit"]
        self.short_entry = self.df["Short Entry"]
        self.short_exit = self.df["Short Exit"]
        self.long_profit = self.df["Long Profit"]
        self.short_profit = self.df["Short Profit"]
        self.balance = self.df["Balance"]

    def cal_RSI(self, window_length):
        close_price_delta = self.close_price.diff()
        avg_gain, avg_loss = close_price_delta.copy(), close_price_delta.copy()
        avg_gain[avg_gain < 0] = 0
        avg_loss[avg_loss > 0] = 0

        avg_gain = avg_gain.rolling(window=window_length).mean()
        avg_loss = abs(avg_loss.rolling(window=window_length).mean())

        RS = avg_gain / avg_loss
        RSI = 100 - (100 / (1 + RS))

        print("cal_RSI is called")

        return RSI

    def cal_Bollinger_bands(self, window_length, num_std):
        SMA = self.close_price.rolling(window=window_length).mean()
        SD_SMA = self.close_price.rolling(window=window_length).std()

        middle_band = SMA
        upper_band = SMA + (SD_SMA * num_std)
        lower_band = SMA - (SD_SMA * num_std)

        return middle_band, upper_band, lower_band

    def check_touch_bands(self, threshold):
        upper_distance = self.upper_band - self.close_price
        lower_distance = self.close_price - self.lower_band

        touch_upper = upper_distance <= threshold
        touch_lower = lower_distance <= threshold

        return touch_upper, touch_lower

    def trades_on_date(self):
        long_counter = 0
        short_counter = 0

        for i in range(1, len(self.df)):
            # print("determine_trades: for loop is called")
            if (
                self.touch_lower.iloc[i] == True
                and self.RSI.iloc[i] > 30
                and self.RSI.iloc[i - 1] < 30
            ):
                print("determine_trades: long_entry is found")
                self.long_entry.iloc[i] = True
                long_counter = 3
            # Long Exit
            # elif long_counter == 0 and self.long_entry.iloc[i - 3]:
            #     print("determine_trades: long_exit is found")
            #     self.long_exit.iloc[i] = True

            # Long Exit
            elif long_counter > 0:  # We are in a long trade
                if not self.touch_lower.iloc[i]:  # Price didn't touch the Lower Band
                    long_counter += 1  # Increase the counter
                    if (
                        long_counter >= 3 and self.RSI.iloc[i] > 40
                    ):  # 3 days passed and RSI > 40
                        print("determine_trades: long_exit is found")
                        self.long_exit.iloc[i] = True
                        long_counter = 0  # Reset the counter
                else:  # Price touched the Lower Band
                    long_counter = 1  # Reset the counter to 1

    # return: average day traded on 3% profit
    def trades_on_profit(self):
        # trade the stock based on the 3% earning profit.
        # calculate the average days that needs to wait to achieve the 3% earning profit
        long_entry_price = 0.0
        entry_day = 0
        total_days = 0
        total_trades = 0

        for i in range(1, len(self.df)):
            # Long Entry
            if (
                self.touch_lower.iloc[i] == True
                and self.RSI.iloc[i] > 30
                and self.RSI.iloc[i - 1] < 30
            ):
                self.long_entry.iloc[i] = True
                long_entry_price = self.close_price.iloc[i]
                entry_day = i

            # Long Exit
            elif (
                long_entry_price > 0
                and (self.close_price.iloc[i] - long_entry_price)
                / long_entry_price
                * 100
                >= 3
                # or (self.close_price.iloc[i] - long_entry_price)
                # / long_entry_price
                # * 100
                # <= -3
            ):
                self.long_exit.iloc[i] = True
                long_entry_price = 0.0
                total_days += i - entry_day
                total_trades += 1

        # Calculate the average day for this strategy
        ad_strategy = total_days / total_trades if total_trades > 0 else 0
        return ad_strategy

    def plot_trades(self, filename="trades.png"):
        plt.figure(figsize=(14, 7))
        plt.plot(
            self.df.index,
            self.close_price,
            label="Close Price",
            color="black",
            alpha=1,
        )

        plt.plot(
            self.df.index,
            self.df["Upper Band"],
            label="Upper Band",
            color="blue",
            linestyle="--",
        )
        plt.plot(
            self.df.index,
            self.df["Lower Band"],
            label="Lower Band",
            color="pink",
            linestyle="--",
        )
        plt.plot(
            self.df.index,
            self.df["Middle Band"],
            label="Lower Band",
            color="purple",
            linestyle="--",
        )

        long_entry = self.df[self.df["Long Entry"] == True]
        plt.scatter(
            long_entry.index,
            long_entry["Close"],
            color="green",
            label="Long Entry",
            marker="^",
            alpha=1,
        )

        long_exit = self.df[self.df["Long Exit"] == True]
        plt.scatter(
            long_exit.index,
            long_exit["Close"],
            color="red",
            label="Long Exit",
            marker="v",
            alpha=1,
        )

        plt.title("Stock Price with Entry & Exit Points")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.legend(loc="best")
        plt.grid(True)
        plt.savefig(filename, dpi=300)
        plt.close()

    def plot_trades_online(self, ticker):
        # Create traces
        trace_close_price = go.Scatter(
            x=self.df.index,
            y=self.df["Close"],
            mode="lines",
            name="Close Price",
            line=dict(color="black", width=1),
        )

        trace_long_entry = go.Scatter(
            x=self.df[self.df["Long Entry"] == True].index,
            y=self.df[self.df["Long Entry"] == True]["Close"],
            mode="markers",
            name="Long Entry",
            marker=dict(color="green", symbol="triangle-up", size=10),
        )

        trace_long_exit = go.Scatter(
            x=self.df[self.df["Long Exit"] == True].index,
            y=self.df[self.df["Long Exit"] == True]["Close"],
            mode="markers",
            name="Long Exit",
            marker=dict(color="red", symbol="triangle-down", size=10),
        )

        trace_upper_band = go.Scatter(
            x=self.df.index,
            y=self.df["Upper Band"],
            mode="lines",
            name="Upper Band",
            line=dict(dash="dash", color="orange", width=1),
        )

        trace_lower_band = go.Scatter(
            x=self.df.index,
            y=self.df["Lower Band"],
            mode="lines",
            name="Lower Band",
            line=dict(dash="dash", color="blue", width=1),
        )

        trace_RSI = go.Scatter(
            x=self.df.index,
            y=self.df["RSI"],
            name="RSI",
            line=dict(width=1),
            yaxis="y2",
        )

        data = [
            trace_close_price,
            trace_long_entry,
            trace_long_exit,
            trace_lower_band,
            trace_upper_band,
            trace_RSI,
        ]

        layout = go.Layout(
            title=ticker
            + "  Stock Price with Entry & Exit Points, Bollinger Bands and RSI",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Close Price"),
            yaxis2=dict(
                title="RSI",
                titlefont=dict(color="blue"),
                tickfont=dict(color="blue"),
                overlaying="y",
                side="right",
                range=[0, 180],
            ),
            shapes=[
                dict(
                    type="line",
                    yref="y2",
                    y0=30,
                    y1=30,
                    xref="paper",
                    x0=0,
                    x1=1,
                    line=dict(color="LightSeaGreen", width=1, dash="dash"),
                ),
                dict(
                    type="line",
                    yref="y2",
                    y0=70,
                    y1=70,
                    xref="paper",
                    x0=0,
                    x1=1,
                    line=dict(color="LightSeaGreen", width=1, dash="dash"),
                ),
            ],
        )

        fig = go.Figure(data=data, layout=layout)
        # fig.show()
        # plot(fig, filename=f'{ticker}.html')
        # plot(fig, filename="plots/{}.html".format(ticker))
        # plot(fig, filename=f"w30n2/{ticker}.html")
        try:
            plot(fig, filename=f"w20n2/{ticker}.html")
        except Exception as e:
            print(str(e))
        print("plot_trades_online is called")

    # return: total profit
    def calculate_profits(self):
        long_entry_price = 0.0
        total_profit = 0.0
        for i in range(1, len(self.df)):
            # print("calculate_profits: for loop is called")
            if self.long_entry.iloc[i]:
                long_entry_price = self.close_price.iloc[i]
                print("long_entry_price is calculated")
            elif self.long_exit.iloc[i] and long_entry_price != 0:
                self.long_profit.iloc[i] = self.close_price.iloc[i] - long_entry_price
                print("long_profit is calculated")
                long_entry_price = 0
                total_profit += self.long_profit.iloc[i]

        print("calculate_profits is called")
        return total_profit

    # return: return ratio
    def calculate_return_ratios(self, total_profit):
        total_investment = 0.0
        long_entry_price = 0.0

        for i in range(1, len(self.df)):
            # Long Entry
            if self.long_entry.iloc[i]:
                long_entry_price = self.close_price.iloc[i]
                total_investment += long_entry_price

        return_ratio = total_profit / total_investment if total_investment > 0 else 0
        return return_ratio

    # return: sharpe ratio
    def calculate_sharpen_ratios(self, closing_reference_rate):
        # closing_reference_rates = 4.028 * 0.01, 5 year
        risk_free_rate = closing_reference_rate * 0.01

        # Calculate daily returns
        self.df["Daily Return"] = self.df["Close"].pct_change()

        # Calculate mean return and standard deviation of returns
        mean_daily_return = self.df["Daily Return"].mean()
        std_daily_return = self.df["Daily Return"].std()

        # Calculate Sharpe Ratio
        sharpe_ratio = (mean_daily_return - (risk_free_rate / 252)) / std_daily_return

        return sharpe_ratio

    # return: count num of true values in long entry and long exit
    def print_true_counts(self, total_profit):
        columns = ["Long Entry", "Long Exit"]
        counts = {}
        for col in columns:
            count = self.df[col].sum()
            print(f"The column '{col}' has {count} True values.")
            return_ratio = self.calculate_return_ratios(total_profit)
            print(f"The return ratio is {return_ratio}")
            return_ratio_average_days = self.trade_on_return_ratio(return_ratio)
            print(
                f"The return ratio trading average days is {return_ratio_average_days}"
            )

            counts[col] = count
        return counts

    # return: average day traded on return ratios
    def trade_on_return_ratio(
        self, return_ratio
    ):  # calculate average days that needs to wait to achieve the return ratio (which is same as the return ratio that produced by technical indicators strategy)
        # Initialize variables
        entry_price = self.close_price.iloc[0]
        entry_day = 0
        total_days = 0
        total_trades = 0

        for i in range(1, len(self.df)):
            # Exit and re-enter trade based on return ratio
            if (
                entry_price > 0
                and (self.close_price.iloc[i] - entry_price) / entry_price
                >= return_ratio
            ):
                total_days += i - entry_day
                total_trades += 1
                # Re-enter the trade
                entry_price = self.close_price.iloc[i]
                entry_day = i

        # Calculate the average holding period
        # ad_ratio: the average day that needs to wait to achieve the return ratio
        ad_ratio = total_days / total_trades if total_trades > 0 else 0
        return ad_ratio

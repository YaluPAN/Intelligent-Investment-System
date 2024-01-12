from Price import Price
import pandas as pd
import numpy as np
import yfinance as yf


class Trading:
    def __init__(self, df):
        self.df = df
        self.close_price = df["Close"]
        self.RSI = Price(df).cal_RSI(df["Close"], 14)
        # self.RSI = df["RSI"]
        self.middle_band, self.upper_band, self.lower_band = Price(
            df
        ).cal_Bollinger_bands(df["Close"], 20, 2, df)
        df["Long Entry"] = False
        df["Long Exit"] = False
        df["Short Entry"] = False
        df["Short Exit"] = False
        df["Long Profit"] = 0.0
        df["Short Profit"] = 0.0
        self.long_entry = df["Long Entry"]
        self.long_exit = df["Long Exit"]
        self.short_entry = df["Short Entry"]
        self.short_exit = df["Short Exit"]
        self.long_profit = df["Long Profit"]
        self.short_profit = df["Short Profit"]

    def determine_trades(self):
        # 初始化计数器
        long_counter = 0
        short_counter = 0
        # 确定交易
        for i in range(1, len(self.df)):
            # Long Entry
            touch_upper, touch_lower = Price(self.df).check_touch_bands(
                self.close_price[i], 20, 2, 0.05
            )
            if touch_lower == True and self.RSI[i] > 30 and self.RSI[i - 1] < 30:
                self.df.loc[i, "Long Entry"] = True
                long_counter = 5
            # Long Exit
            elif long_counter == 0 and self.long_entry[i - 5]:
                self.df.loc[i, "Long Exit"] = True

            # Short Entry
            if touch_upper == True and self.RSI[i] < 70 and self.RSI[i - 1] > 70:
                self.df.loc[i, "Short Entry"] = True
                short_counter = 5
            # Short Exit
            elif short_counter == 0 and self.short_entry[i - 5]:
                self.df.loc[i, "Short Exit"] = True

            # 更新计数器
            if long_counter > 0:
                long_counter -= 1
            if short_counter > 0:
                short_counter -= 1

        return self.df

    def calculate_profits(self):
        # 计算利润
        long_entry_price = 0.0
        short_entry_price = 0.0
        for i in range(1, len(self.df)):
            # Long Entry
            if self.long_entry[i]:
                long_entry_price = self.close_price[i]
            # Long Exit
            elif self.long_exit[i] and long_entry_price != 0:
                self.df.loc[i, "Long Profit"] = self.close_price[i] - long_entry_price
                long_entry_price = 0

            # Short Entry
            if self.short_entry[i]:
                short_entry_price = self.close_price[i]
            # Short Exit
            elif self.short_exit[i] and short_entry_price != 0:
                self.df.loc[i, "Short Profit"] = short_entry_price - self.close_price[i]
                short_entry_price = 0

        return self.df

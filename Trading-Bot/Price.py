import pandas as pd
import numpy as np
import talib


class Price:
    def __init__(self, df):
        self.df = df
        close_price = df["Close"]

    def cal_RSI(close_price, window_length, df):
        # RS = avg_gain/avg_loss
        # avg_gain: the average gain over the last 14 days
        # avg_loss: the average loss over the last 14 days
        # RSI = 100 - 100/(1+RS)

        # window_length = 14

        close_price_delta = close_price.diff()
        avg_gain, avg_loss = close_price_delta.copy(), close_price_delta.copy()
        avg_gain[avg_gain < 0] = 0
        avg_loss[avg_loss > 0] = 0

        avg_gain = avg_gain.rolling(window=window_length).mean()
        avg_loss = abs(avg_loss.rolling(window=window_length).mean())

        RS = avg_gain / avg_loss
        RSI = 100 - (100 / (1 + RS))

        df["RSI"] = talib.RSI(close_price, timeperiod=window_length)

        return RSI

    def cal_Bollinger_bands(close_price, window_length, num_std, df):
        # recommended parameters: window_length = 20, num_std = 2
        # num_std: number of standard deviation
        # upper_band = SMA + SD_SMA * num_std
        # (SD_SMA: standard deviation of SMA)
        # lower_band = SMA - SD_SMA * num_std

        SMA = close_price.rolling(window=window_length).mean()
        SD_SMA = close_price.rolling(window=window_length).std()

        middle_band = SMA
        upper_band = SMA + (SD_SMA * num_std)
        lower_band = SMA - (SD_SMA * num_std)

        df["Middle Band"], df["Upper Band"], df["Lower Band"] = (
            middle_band,
            upper_band,
            lower_band,
        )

        return middle_band, upper_band, lower_band

    def check_touch_bands(close_price, window_length, num_std, threshold):
        middle_band, upper_band, lower_band = Price.cal_Bollinger_bands(
            close_price, window_length, num_std
        )

        upper_distance = upper_band - close_price
        lower_distance = close_price - lower_band

        touch_upper = upper_distance <= threshold  # 如果小于或等于threshold，结果为True
        touch_lower = lower_distance <= threshold

        return touch_upper, touch_lower

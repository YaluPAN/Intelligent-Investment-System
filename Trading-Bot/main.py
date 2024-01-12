import TradingBot as tb
import yfinance as yf
import pandas as pd


def process_data(ticker):
    print(f"------------******** Processing for {ticker}... ********------------")
    df = yf.download(ticker, "2018-01-01", "2023-01-01")

    # bot1 will be traded on profits: earning 3%
    bot1 = tb.TradingBot(df)
    average_day1 = bot1.trades_on_profit()
    total_profit1 = bot1.calculate_profits()
    profit1 = total_profit1
    print("********************8 profit1*******************" + str(profit1))
    return_ratio1 = bot1.calculate_return_ratios(profit1)
    closing_reference_rate = 4.028
    sharpen_ratio1 = bot1.calculate_sharpen_ratios(closing_reference_rate)
    average_day_return_ratio1 = bot1.trade_on_return_ratio(return_ratio1)
    # bot1.plot_trades_online(ticker)
    # df.to_csv(f"w20n1/{ticker}.csv")
    # 将所有股票的数据存储到csv文件中
    true_counts1 = bot1.print_true_counts(profit1)
    result1 = pd.Series(
        {
            **true_counts1,
            "Profits(Per Share)": total_profit1,
            "Return ratios": return_ratio1,
            "Sharpen ratios": sharpen_ratio1,
            "Average days": average_day1,
            "Average days to achieve return ratio": average_day_return_ratio1,
        },
        name=f"{ticker}",
    )

    # bot2 will be traded on dates: 3 days
    bot2 = tb.TradingBot(df)
    average_day2 = bot2.trades_on_profit()
    total_profit2 = bot2.calculate_profits()
    profit2 = total_profit2
    print("********************8 profit2*******************" + str(profit2))
    return_ratio2 = bot2.calculate_return_ratios(profit2)
    closing_reference_rate = 4.028
    sharpen_ratio2 = bot2.calculate_sharpen_ratios(closing_reference_rate)
    average_day_return_ratio2 = bot2.trade_on_return_ratio(return_ratio2)
    # bot2.plot_trades_online(ticker)
    # df.to_csv(f"w20n1/{ticker}.csv")
    # 将所有股票的数据存储到csv文件中
    true_counts2 = bot2.print_true_counts(profit2)
    result2 = pd.Series(
        {
            **true_counts2,
            "Profits(Per Share)": total_profit2,
            "Return ratios": return_ratio2,
            "Sharpen ratios": sharpen_ratio2,
            "Average days": average_day2,
            "Average days to achieve return ratio": average_day_return_ratio2,
        },
        name=f"{ticker}",
    )

    print(f"------------******** Processing for {ticker} done! ********------------")
    # return pd.Series(true_counts, name=ticker)
    return pd.concat([result1, result2])


def main():
    # tickers = [
    #     "AAPL",
    #     "GOOGL",
    #     "MSFT",
    #     "AMZN",
    #     "FB",
    #     "TSLA",
    #     "BRK-B",
    #     "V",
    #     "JNJ",
    #     "WMT",
    #     "PG",
    # ]

    tickers = [
        "0005.HK",  # HSBC Holdings
        "1299.HK",  # AIA
        "0700.HK",  # Tencent
        "0941.HK",  # China Mobile
        "3988.HK",  # Bank of China
        "0939.HK",  # China Construction Bank
        "1398.HK",  # Industrial and Commercial Bank of Chin(ICBC)
        "2318.HK",  # Ping An Insurance (Group) Company of China
        "0388.HK",  # Hong Kong Exchanges and Clearing
        "0883.HK",  # CNOOC
        "0011.HK",  # Hang Seng Bank
        "0027.HK",  # Galaxy Entertainment
        "0066.HK",  # MTR Corporation
        "0083.HK",  # Sino Land
        "0101.HK",  # Hang Lung Properties
        "0175.HK",  # Geely Automobile
        "0267.HK",  # CITIC
        "0291.HK",  # China Resources Beer
        "0322.HK",  # Tingyi (Cayman Islands) Holding Corp.
        "0330.HK",  # Esprit Holdings
        "0386.HK",  # Sinopec Corp
        "0669.HK",  # Techtronic Industries
        "0688.HK",  # China Overseas Land & Investment
        "0728.HK",  # China Telecom
        "0762.HK",  # China Unicom
        "0823.HK",  # Link REIT
        "0857.HK",  # PetroChina Co.
        "0916.HK",  # China Longyuan Power
        "1038.HK",  # CK Infrastructure Holdings
        "1044.HK",  # Hengan International
    ]

    results = pd.DataFrame()
    series_list = []

    for ticker in tickers:
        result_series = process_data(ticker)
        # Convert the result to a pandas Series and append to the DataFrame
        series_list.append(result_series)
    results = pd.concat(series_list, axis=1).T

    # Save the results to a csv file
    results.to_csv("w30n2results.csv")
    # for ticker in tickers:
    #     process_data(ticker)
    print("main is called")


if __name__ == "__main__":
    main()

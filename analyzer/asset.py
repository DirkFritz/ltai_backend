import pandas as pd
import datetime


class Asset:
    def __init__(self, stocks_db_df, companies, symbols_index):

        self.stocks_prices_df = stocks_db_df
        self.companies = companies
        self.companies = self.companies.reset_index()

        self.stocks_symbols = symbols_index

        self.market_cap_period_df = pd.DataFrame()
        self.ticker_symbols = []

        self.market_cap_period_groups = pd.DataFrame(
            columns=[
                "Group",
                "DateTime",
                "Market Cap",
                "Percent",
                "Winner Period",
                "Volume Percent",
            ]
        )

    def create_market_cap_period(
        self, group_name, symbols_group, compare_date1, compare_date2
    ):
        df = self.companies.set_index("Symbol")

        for symbol in symbols_group:

            number_shares = df.loc[symbol]["Shares"]
            stock_prices_start = self.stocks_prices_df[
                (self.stocks_prices_df["DateTime"] >= compare_date1)
                & (self.stocks_prices_df["Symbol"] == symbol)
            ]["Close"]
            volume_prices_start = self.stocks_prices_df[
                (self.stocks_prices_df["DateTime"] >= compare_date1)
                & (self.stocks_prices_df["Symbol"] == symbol)
            ]["Volume"]
            price_per_stock = self.stocks_prices_df.loc[
                (self.stocks_prices_df["DateTime"] >= compare_date1)
                & (self.stocks_prices_df["DateTime"] <= compare_date2)
                & (self.stocks_prices_df["Symbol"] == symbol)
            ]
            price_per_stock.loc[:, "Market Cap"] = (
                price_per_stock["Close"] * number_shares
            )

            price_per_stock.loc[:, "Percent"] = (
                price_per_stock["Close"] / stock_prices_start.values[0]
            ) * 100 - 100

            if volume_prices_start.values[0] != 0:
                price_per_stock.loc[:, "Volume Percent"] = (
                    price_per_stock["Volume"] / volume_prices_start.values[0]
                ) * 100 - 100
            else:
                price_per_stock.loc[:, "Volume Percent"] = (
                    price_per_stock["Volume"] / volume_prices_start.values[1]
                ) * 100 - 100

            price_per_stock.loc[:, "Winner Period"] = 0

            price_per_stock.loc[price_per_stock["Percent"] >= 0, "Winner Period"] = 1

            price_per_stock["Group"] = group_name

            self.market_cap_period_df = pd.concat(
                [self.market_cap_period_df, price_per_stock]
            )

    def create_market_cap_period_groups(self, group_name):
        dates = self.market_cap_period_df["DateTime"].unique()

        group_first_date = self.market_cap_period_df[
            (self.market_cap_period_df["Group"] == group_name)
            & (self.market_cap_period_df["DateTime"] == dates[0])
        ]

        for date in dates:
            group_per_date = self.market_cap_period_df[
                (self.market_cap_period_df["Group"] == group_name)
                & (self.market_cap_period_df["DateTime"] == date)
            ]

            market_cap = group_per_date["Market Cap"].sum()

            percent_average = group_per_date["Percent"].sum() / len(
                group_per_date["Symbol"].unique()
            )

            volume_percent_average = (
                group_per_date["Volume"].sum() / group_first_date["Volume"].sum()
            ) * 100 - 100

            winners_period = (
                group_per_date["Winner Period"].sum()
                / len(group_per_date["Symbol"].unique())
                * 100
            )

            data_record = [
                [
                    group_name,
                    date,
                    market_cap,
                    percent_average,
                    winners_period,
                    volume_percent_average,
                ]
            ]
            self.market_cap_period_groups = pd.concat(
                [
                    self.market_cap_period_groups,
                    pd.DataFrame(
                        data_record,
                        columns=[
                            "Group",
                            "DateTime",
                            "Market Cap",
                            "Average Percent",
                            "Winner Period",
                            "Volume Percent",
                        ],
                    ),
                ]
            )

        market_cap_start_date = self.market_cap_period_groups[
            (self.market_cap_period_groups["Group"] == group_name)
            & (self.market_cap_period_groups["DateTime"] == dates[0])
        ]["Market Cap"]

        market_cap_end_date = self.market_cap_period_groups[
            (self.market_cap_period_groups["Group"] == group_name)
        ]["Market Cap"]

        self.market_cap_period_groups.loc[
            self.market_cap_period_groups["Group"] == group_name, "Percent"
        ] = (
            (market_cap_end_date - market_cap_start_date) / self.market_cap_start_all
        ) * 100

    def date_correction(self, date):
        i = 0
        while i < 5:
            if self.stocks_prices_df["DateTime"].isin([date]).any() == False:
                date = date + datetime.timedelta(days=1)
            else:
                break
            i = i + 1
        return date

import pandas as pd
from analyzer.asset import Asset


pd.options.mode.chained_assignment = None  # default='warn'


class Stock(Asset):
    def __init__(self, stocks_db_df, companies, symbols_stocks):
        super().__init__(stocks_db_df, companies, symbols_stocks)

    def get_last_day(self):
        return self.stocks_prices_df["DateTime"].max()

    def get_max_draw_down(self, compare_date1, compare_date2, symbols=[]):

        compare_date1 = self.date_correction(compare_date1)
        compare_date2 = self.date_correction(compare_date2)

        self.stocks = self.companies.loc[
            self.companies["Symbol"].isin(self.stocks_symbols)
        ]
        draw_downs = {}
        for symbol in symbols:
            price_per_stock = self.stocks_prices_df.loc[
                (self.stocks_prices_df["DateTime"] >= compare_date1)
                & (self.stocks_prices_df["DateTime"] <= compare_date2)
                & (self.stocks_prices_df["Symbol"] == symbol)
            ]

            draw_down = (
                price_per_stock["Close"].min() * 100 / price_per_stock["Close"].max()
            ) - 100
            draw_downs[symbol] = draw_down

        return draw_downs

    def set_compare_dates(self, compare_date1, compare_date2, symbols=[]):

        compare_date1 = self.date_correction(compare_date1)
        compare_date2 = self.date_correction(compare_date2)

        self.stocks = self.companies.loc[
            self.companies["Symbol"].isin(self.stocks_symbols)
        ]

        self.create_market_cap_period(
            "ALL",
            self.stocks["Symbol"].tolist(),
            compare_date1,
            compare_date2,
        )
        self.market_cap_period_df.loc[
            self.market_cap_period_df["Symbol"].isin(["GOOG", "GOOGL"]), ["Market Cap"]
        ] *= 0.5

        market_cap_period_single = self.market_cap_period_df.loc[
            (
                self.market_cap_period_df["Symbol"].isin(symbols)
                & self.market_cap_period_df["Group"].isin(["ALL"])
            ),
            :,
        ]

        perfomrance_single_start = self.market_cap_period_df.loc[
            (
                self.market_cap_period_df["Symbol"].isin(self.stocks_symbols)
                & self.market_cap_period_df["Group"].isin(["ALL"])
                & self.market_cap_period_df["DateTime"].isin([compare_date1])
            ),
            :,
        ]

        perfomrance_single = self.market_cap_period_df.loc[
            (
                self.market_cap_period_df["Symbol"].isin(self.stocks_symbols)
                & self.market_cap_period_df["Group"].isin(["ALL"])
                & self.market_cap_period_df["DateTime"].isin([compare_date2])
            ),
            :,
        ]

        perfomrance_single_start.reset_index(drop=True, inplace=True)

        perfomrance_single.loc[:, "Market Cap Change"] = 0
        perfomrance_single.loc[:, "Market Cap Change"] = (
            perfomrance_single["Market Cap"] - perfomrance_single_start["Market Cap"]
        )

        self.market_cap_start_all = self.market_cap_period_df[
            (
                self.market_cap_period_df["Symbol"].isin(self.stocks_symbols)
                & self.market_cap_period_df["Group"].isin(["ALL"])
                & self.market_cap_period_df["DateTime"].isin([compare_date1])
            )
        ]["Market Cap"].sum()

        self.market_cap_period_df.reset_index(drop=True, inplace=True)
        self.create_market_cap_period_groups("ALL")

        return (
            self.market_cap_period_groups,
            market_cap_period_single,
        )

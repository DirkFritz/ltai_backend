from flask import Flask
from flask_cors import CORS
from datetime import datetime
import pandas as pd
from db.dbqueries import get_idx_data

app = Flask(__name__)
CORS(app)


def get_index_symbols(ndx):
    idx_symbols = None

    # print("Index", ndx)
    if ndx:
        idx_symbols = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[3][
            "Ticker"
        ].to_list()
    else:
        idx_data = pd.read_html(
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        )[0]
        idx_data["Symbol"] = idx_data["Symbol"].str.replace(".", " ", regex=True)

        idx_symbols = idx_data["Symbol"].to_list()

    return idx_symbols


@app.route("/indexanalysis")
def index_analysis():

    index_ndx100_active = True
    start_date = "2022-06-16"
    end_date = "2022-07-16"
    symbols = ["nvda", "APPL", "GOOGL", "TSLA", "MSFT"]
    sector = "Technology"

    end_date = datetime.strptime(end_date + " 16:00:00", "%Y-%m-%d %H:%M:%S")
    start_date = datetime.strptime(start_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")

    idx_symbols = get_index_symbols(index_ndx100_active)

    symbols = [symbol for symbol in symbols if symbol in idx_symbols]

    idxgroups_df, ndxperfomrance_df = get_idx_data(
        start_date.date(), end_date.date(), symbols, idx_symbols, sector
    )

    idx_group = idxgroups_df[idxgroups_df["Group"] == "ALL"]

    idx_out = {
        "date": idx_group["DateTime"].to_list(),
        "mcap_change": idx_group["Percent"].to_list(),
    }

    print(idx_out)

    return idx_out


@app.route("/")
def lt_ai_backend():
    return "<p>LT-AI Backend</p>"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

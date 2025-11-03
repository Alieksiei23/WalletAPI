import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from src.enums.enum import CurrencyEnum


CSV_PATH = "src/db/data/data.csv"

load_dotenv()

engine = create_engine(
        f"postgresql+psycopg2://"
        f"{os.getenv("DB_USER")}:"
        f"{os.getenv("DB_PASS")}@"
        f"{os.getenv("DB_HOST")}:"
        f"{os.getenv("DB_PORT")}/"
        f"{os.getenv("DB_NAME")}")


def load_user_and_balance() -> None:
    df = pd.read_csv(CSV_PATH)

    df_user = df[['email', 'status', 'created']]

    with engine.begin() as conn:
        df_user.to_sql('user', conn, if_exists='append', index=False)
        for currency in CurrencyEnum:
            df_balance = df[['id', 'amount', 'created']].rename(columns={'id': 'user_id'})
            df_balance['currency'] = currency
            df_balance.to_sql('user_balance', conn, if_exists='append', index=False)


if __name__ == "__main__":
    load_user_and_balance()

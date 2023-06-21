from sqlalchemy import create_engine
import sqlalchemy.types as types
import pandas as pd

BIGINT = "BIGINT"
STRING = "String"
FLOAT = "Float"
BOOLEAN = "Boolean"
DATETIME = "DateTime"
DATE = "Date"
TIME = "Time"
INTEGER = "Integer"
NUMERIC = "Numeric"
BYTES = "LargeBinary"
JSON = "JSON"


def clean_validate_part():
    url = r"https://www-genesis.destatis.de/genesis/downloads/00/tables/46251-0021_00.csv"

    col_names = ["date", "CIN", "name", "petrol", "diesel", "gas", "electro", "hybrid", "plugInHybrid",
                 "others"]
    # Drop all other columns
    # Make sure to preserve the german special letters like “ü” or “ä”
    # Ignore the first 6 lines and last 4 lines as metadata
    # Keep only the following columns, rename them to the new name given here (M-BU contain summary data)
    df = pd.read_csv(url, skiprows=7, skipfooter=4, engine='python', encoding="latin1", delimiter=";",
                     header=None, parse_dates=['date'], converters={'CIN': str},
                     dayfirst=True, index_col=False,
                     usecols=[0, 1, 2, 12, 22, 32, 42, 52, 62, 72], na_values='-',
                     names=col_names)
    # drop all rows that contain invalid values
    df.dropna(inplace=True)
    # CINs are Community Identification Numbers, must be strings with 5 characters and can have a leading 0
    df.drop(df[df["CIN"].apply(lambda cin: len(cin) != 5)].index,
            inplace=True)
    # drop values smaller than 0
    for col_name in col_names[3:]:
        df.drop(df[df[col_name].apply(lambda x: int(x) < 0)].index, inplace=True)
    return df


def sql_part(df):
    # sql part
    # Creating the db
    TABLE_NAME = "cars"
    engine = create_engine(f'sqlite:///{TABLE_NAME}.sqlite')
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=False,
              dtype={
                  "date": types.DATETIME,
                  "CIN": types.String,
                  "name": types.String,
                  "petrol": types.Integer,
                  "diesel": types.Integer,
                  "gas": types.Integer,
                  "electro": types.Integer,
                  "hybrid": types.Integer,
                  "plugInHybrid": types.Integer,
                  "others": types.Integer, }, )
    return 0


def main():
    df = clean_validate_part()
    sql_part(df)


if __name__ == "__main__":
    main()

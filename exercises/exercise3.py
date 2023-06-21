import decimal
import datetime
import pandas
from sqlalchemy import create_engine, text
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


def python_type_to_sqlalchemy_type(python_type, value):
    if python_type is int:
        # Differentiate between BIGINT and INT
        if value in range(-2147483648, 2147483647):
            return INTEGER
        else:
            return BIGINT
    elif python_type is float:
        return FLOAT
    elif python_type is str:
        return STRING
    elif python_type is bool:
        return types.Boolean
    # smartass pandas always treats a datetime as Timestamp if to_pydatetime is not called
    elif python_type is datetime.datetime or pandas.Timestamp:
        return DATETIME
    elif python_type is datetime.date:
        return DATE
    elif python_type is datetime.time:
        return DATE
    elif python_type is decimal.Decimal:
        return NUMERIC
    elif python_type is bytes:
        return BYTES
    elif python_type is list:
        return JSON
    else:
        raise Exception("error")


def clean_validate_part():
    url = r"https://www-genesis.destatis.de/genesis/downloads/00/tables/46251-0021_00.csv"

    col_names = ["date", "CIN", "name", "petrol", "diesel", "gas", "electro", "hybrid", "plugInHybrid",
                 "others"]
    # Drop all other columns
    # Make sure to preserve the german special letters like “ü” or “ä”
    # Ignore the first 6 lines and last 4 lines as metadata
    # Keep only the following columns, rename them to the new name given here (M-BU contain summary data)
    df = pd.read_csv(url, skiprows=7, skipfooter=4, engine='python', encoding="latin1", delimiter=";",
                     header=None, parse_dates=['date'],converters={'CIN': str},
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
    results = []
    # once again at runtime determine the best fit, without relying on checking the data manually
    # Iterate over the DataFrame columns
    for column_name, column_values in df.items():
        current_value_type = None
        current_column_name = column_name
        for index, value in column_values.items():
            value_type = python_type_to_sqlalchemy_type(type(value), value)
            # first case is current_value_type is None, which is okay, we simply set the value
            if not current_value_type:
                current_value_type = value_type
            # if not None current_value_type is set, and we check if it´s the same value as the value_type,
            elif current_value_type == value_type:
                # perfect, just like expected both are the same value
                continue
            else:
                # something happened, the type changed apparently
                if current_value_type == STRING and value_type == FLOAT:
                    # our value was String and suddenly we have float --> nan is interpreted as Float, it´s okay if we stay with string
                    continue
                else:
                    raise Exception("whyyyyyyyyyyyy")
        results.append((current_column_name, current_value_type))
    create_table_query = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (\n"
    for column in results:
        new_line = f"{column[0]} {column[1]},\n"
        create_table_query += new_line
    create_table_query = create_table_query[:-2]
    create_table_query += ")"
    #    print(create_table_query)
    engine = create_engine(f'sqlite:///{TABLE_NAME}.sqlite')
    with engine.connect() as connection:
        connection.execute(text(create_table_query))
    # now insert df
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=False)
    return 0


def main():
    df = clean_validate_part()
    sql_part(df)


if __name__ == "__main__":
    main()

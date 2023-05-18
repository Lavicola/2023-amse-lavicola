import decimal
import datetime
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
    elif python_type is datetime.datetime:
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


def main():
    df = pd.read_csv(
        r"https://opendata.rhein-kreis-neuss.de/api/v2/catalog/datasets/rhein-kreis-neuss-flughafen-weltweit/exports/csv",
        delimiter=';')

    TABLE_NAME = "airports"

    results = []
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
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=True)
    return 0


if __name__ == "__main__":
    main()

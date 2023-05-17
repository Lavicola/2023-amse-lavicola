import json
import sqlite3
import pandas as pd
import json


def main(json_list: list[json]):
    """

    """
    json_dict = {}

    # Establish a connection to the database
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()

    # sort the different json elements to their entry and delete the tablename
    for json_element in json_list:
        if json_element["tablename"] not in json_dict.keys():
            json_dict[json_element["tablename"]] = []
        tablename = json_element["tablename"]
        del json_element["tablename"]
        json_dict[tablename].append(json_element)
    # once done create for every key the table,
    for tablename in json_dict.keys():
        df = pd.json_normalize(json_dict[tablename][0])
        a = df.columns
        # Create the table if it doesn't exist
        create_table_query = f"CREATE TABLE IF NOT EXISTS {tablename} ({', '.join(df.columns)});"
        cursor.execute(create_table_query)
    connection.commit()

    # and now insert the data
    chunksize = 5000
    for tablename in json_dict.keys():
        for json_element in json_dict[tablename]:
            df = pd.json_normalize(json_element, errors='ignore')
            df.to_sql(tablename, connection, if_exists="append",chunksize=chunksize, index=False, method="multi")

    connection.commit()
    cursor.close()
    connection.close()

    return


if __name__ == "__main__":
    main(None)

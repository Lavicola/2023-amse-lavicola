import json
import sqlite3
import pandas as pd
import json
import logging
import time


def store_in_database(json_list: list[json], database_path: str):
    """

    :param json_list:
    :param database_path:
    :return:
    """
    json_dict = {}

    # Establish a connection to the database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    # Sort the different JSON elements to their entry and delete the tablename
    for json_element in json_list:
        if json_element["tablename"] not in json_dict.keys():
            json_dict[json_element["tablename"]] = []
        tablename = json_element["tablename"]
        del json_element["tablename"]
        json_dict[tablename].append(json_element)

    # Create tables and insert data
    cursor.execute("BEGIN TRANSACTION;")
    chunksize = 10000

    for tablename, elements in json_dict.items():
        if len(elements) <= 0:
            logging.info(f"{tablename} has no rows")
            break

        df = pd.json_normalize(elements[0])
        df_columns = df.columns.tolist()
        create_table_query = f"CREATE TABLE IF NOT EXISTS {tablename} ({', '.join(df_columns)});"
        cursor.execute(create_table_query)

        for i in range(0, len(elements), chunksize):
            chunk = elements[i:i + chunksize]
            values = [[element.get(column, None) for column in df_columns] for element in chunk]
            placeholders = ", ".join(["?"] * len(df_columns))
            insert_statement = f"INSERT INTO {tablename} VALUES ({placeholders});"
            cursor.executemany(insert_statement, values)

    cursor.execute("COMMIT;")
    cursor.close()
    connection.close()

    return


def save_intermediate(json_list: list[json], file_path: str):
    """
    This Method stores the intermediate data into a file.
    :param json_list:
    :param file_path:
    :return: None
    """
    json_string = json.dumps(json_list)
    logging.info(f"Trying to open file{file_path}")
    try:
        with open(file_path, "w") as file:
            logging.info("Writing Intermediate Data into File")
            file.write(json_string)
    except (PermissionError, FileNotFoundError, IOError) as e:
        logging.info("Error writing the File")
    return


def load_intermediate_data(file_path: str):
    """
    This Method is called to read the intermediatee file
    :param file_path:
    :return: list[json]
    """

    logging.info(f"Trying to read file{file_path} for intermediate values")
    try:
        with open(file_path, "r") as file:
            logging.info("File is open, trying to read values")
            json_string = file.read()
    except (PermissionError, FileNotFoundError, IsADirectoryError, IOError) as e:
        raise Exception("Error reading the File", e)from e

    return json.loads(json_string)


if __name__ == "__main__":
    print("dont execute me!")

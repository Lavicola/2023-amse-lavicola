import json
import sqlite3
import pandas as pd
import json
import logging

def main(json_list: list[json], database_path: str):
    """

    :param json_list:
    :param database_path:
    :return:
    """
    json_dict = {}

    # Establish a connection to the database
    connection = sqlite3.connect(f"{database_path}")
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
            df.to_sql(tablename, connection, if_exists="append", chunksize=chunksize, index=False, method="multi")

    connection.commit()
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
    main(None)

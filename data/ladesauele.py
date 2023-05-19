#!/usr/bin/env python
# coding: utf-8
import shutil

import requests
import re
import os
import pandas as pd
import re
import json
import random
import logging
TABLE_NAME = "Ladesaulen"

url = "https://bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Energie/Unternehmen_Institutionen/E_Mobilitaet/Ladesaeulenregister_CSV.csv?__blob=publicationFile&v=46"


def download_file(link: str, fileending: str, file_name="", params=""):
    """
    This Method downloads an excel file in the current directory.
    If no Name is given the Name of the file will be extracted
    link
    return: str(filepath)
    """
    # if no name is given try to extract a name
    if not file_name:
        # /filename.xlsx or filename.xlsx
        pattern = r"(?:/)?(\w+\.{0})".format(fileending)
        match = re.search(pattern, link)
        if match:
            file_name = match.group(1)
        else:
            # notice user and generate a filename which is not already taken
            logging.info(f"file name could be not extracted for {link}")
            while True:
                file_name = f"file_{random.randint(1, 99999)}.xlsx"
                if not os.path.exists(file_name):
                    break
                    # actually download the file now we got a name for it
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        # the file has an unkown file format and therefore before we can actually read it, we have to change some things first
        new_content = clean_file(response.content)
        with open(file_name, 'wb') as file:
            file.write(new_content)
            logging.info("file sucessfully written!")
    else:
        logging.info("Failed to download the file.")
    return os.path.join(os.getcwd(), file_name)


def clean_file(content: bytes):
    """
    cleans the corrupted file with removing duplicate ";"
    and text
    """

    # first convert to a string with the right encoding
    content = content.decode("Windows-1252")
    # remove content until we reach the first column
    match = re.search(r'Betreiber;', content)
    if match:
        start_index = match.start()
        new_content = content[start_index:]
    else:
        raise Exception("Error, could not clean the file")
    return new_content.encode("Windows-1252")


def extract_csv_data(file_path: str):
    """
    this method extracts the data of the file and adds for every row one new value
    which represents the tablename
    
    return list[json]
    
    """
    df = pd.read_csv(file_path, delimiter=";", encoding='Windows-1252')
    # Convert DataFrame to a list of dictionaries
    data = df.to_dict(orient='records')
    # add tablename as key to all entries
    updated_list_of_dicts = [{**d, 'tablename': f'{TABLE_NAME}'} for d in data]
    # convert to json Object
    json_data = json.loads(json.dumps(updated_list_of_dicts))
    return json_data


def get_json_data():
    """
    Download and Clean the ladesaulenfile
    Convert the data to a list of json objects with an additional key called tablename
    
    """
    file_path = download_file(url, "csv", "", {"__blob": "publicationFile", "v": "46"})
    json_data = extract_csv_data(file_path)
    try:
        os.remove(file_path)
    except OSError:
        logging.critical(f"Could not remove File: {file_path}")


    return json_data


if __name__ == "__main__":
    get_json_data()

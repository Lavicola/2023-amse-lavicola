#!/usr/bin/env python
# coding: utf-8


import requests
from bs4 import BeautifulSoup
import time
import re
import random
import os
from urllib.parse import urljoin, urlparse
import pandas as pd
import json
import datetime
import shutil
import logging

TABLE_NAME = "car_registration"


def get_table(tables: "bs4.element.ResultSet", keyword: str):
    """
    This function checks the caption of a table,
    The first table which contains this keyword will
    be returned
    """
    for table in tables:
        caption = table.find("caption")
        if not caption:
            continue
        if keyword in caption.text:
            return table


def get_column_names_column_index(columns: "bs4.element.ResultSet", key_columns: list[str]):
    """
    This Method checks the number of columns we are looking for and returns them 
    in form of a dict[column_name] = index
    
    """
    index = 0
    column_dict = {}
    for column in columns:
        text = column.text.split("\n")[0]
        for keyword in key_columns:
            if text.encode("unicode_escape") in keyword.encode("unicode_escape"):
                column_dict[text] = index
                break
        index += 1
    return column_dict


def get_rows(bs_rows: "bs4.element.ResultSet", column_dict: dict[str]):
    """
    this function gets all rows and the column_dict.
    With this Arguements the function creates an array
    which contains only the important cell values determined by the column_dict
    
    """

    rows = []

    for row in bs_rows:
        # the result represents a list which represents the row
        rows.append([cell for cell in row.text.split("\n") if cell.strip()])

    results = []
    result = []

    for i in range(1, len(rows) - 1):
        for key, value in column_dict.items():
            result.append(f"{key}:{rows[i][value]}")
        results.append(result)
        result = []

    return results


# ### kba download strategy, depending if table exists or not


def download_list_of_files_strategy(url: str, fileending: str, keywords: list[str], folder_path):
    """
    
    
    """

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        soup_links_to_download = soup.find(class_="links downloads").find_all("li")
        links = find_links_to_download(url, soup_links_to_download, keywords)
        if links:
            if not os.path.isdir(folder_path):
                os.mkdir(folder_path)
        for link in links:
            logging.info(f"trying to download {link}")
            download_file(folder_path, link, fileending)
            time.sleep(1)
    else:
        logging.info(f"request for {url} was not successful, error code {response.status_code}")


def download_table_strategy(response: "requests.models.Response"):
    """
    
    
    """

    # parse it
    soup = BeautifulSoup(response.content, 'html.parser')
    # check if a table exists, if yes we can extract via table stratehy
    tables = soup.find_all('table')
    if not tables:
        logging.info(f"Table site did exist, but could not found table for {response.url}")
        # the table contains always "absolut"
    table = get_table(tables, "absolut")
    # get the header
    thead = table.find('thead')
    if not thead:
        logging.info("no thead found")
        return
    # get the column elements
    column_names = thead.find_all("th")
    if not column_names:
        logging.info("no column names found (th)")
        return
    column_dict = get_column_names_column_index(column_names, ["Elektro", "Elektro (BEV)", "Land"])
    if not column_dict:
        logging.info("columns not found")
    # get rows of the table
    rows = table.find_all("tr")
    if not rows:
        logging.info("rows not found")
        return
    elements_to_be_stored = get_rows(rows, column_dict)
    if not elements_to_be_stored:
        logging.info("No elements to be stored")
        return
    return elements_to_be_stored


# ### kba find download links and download files


def find_links_to_download(website: str, soup_links: "bs4.element.ResultSet", keywords: list[str]):
    """
    This Method checks the Website for download links which contain a keyword(s) given to the method.
    if the path is relative it will build the the whole url using the knowledge of the website url
    """
    links = []
    # the container holds the list elements
    list_elements = soup_links
    for link in list_elements:
        if not link:
            logging.info("link not found")
            continue
        for keyword in keywords:
            if keyword.encode("unicode_escape") in link.encode("unicode_escape"):
                # link is in an anchor element
                link = link.find("a")
                if not link:
                    continue
                    # check if the link is absolute or relative
                parsed_url = urlparse(link.get("href"))
                if not parsed_url.netloc:
                    link = urljoin(website, link.get("href"))
                links.append(link)
    return links


def download_file(folder_path: str, link: str, fileending: str, file_name=""):
    """
    This Method downloads an excel file in the current directory.
    If no Name is given the Name of the file will be extracted
    link
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
                if not os.path.exists(os.path.join(folder_path, file_name)):
                    break
    file_path = os.path.join(folder_path, file_name)
    # actually download the file now we got a name for it
    response = requests.get(link)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        logging.info("Failed to download the file.")


# ### kba extract table and table data


def get_table(tables: "bs4.element.ResultSet", keyword: str):
    """
    This function checks the caption of a table,
    The first table which contains this keyword will
    be returned
    """
    for table in tables:
        caption = table.find("caption")
        if not caption:
            continue
        if keyword in caption.text:
            return table


def get_rows(bs_rows: "bs4.element.ResultSet", column_dict: dict[str]):
    """
    this function gets all rows and the column_dict.
    With this Arguements the function creates an array
    which contains only the important cell values determined by the column_dict
    
    """

    rows = []
    results = []
    for row in bs_rows:
        # the result represents a list which represents the row
        rows.append([cell for cell in row.text.split("\n") if cell.strip()])
    # iterate torugh every row and create a json object which represent the row
    for i in range(1, len(rows) - 1):
        # temp json variable to hold the data
        json_data = {}
        for key, value in column_dict.items():
            json_data[key] = rows[i][value]
            # TODO make it nicer
        json_data["tablename"] = TABLE_NAME
        # TODO table has no vehicle type, maybe don´t even store it?
        json_data["Vehicle Type"] = ""
        results.append(json.loads(json.dumps(json_data)))
    return results


# ### Read certain Excel File and store rows into variables


def extract_excel_data(file_path: str, sheet_name: str, header_start: int, row_start: int):
    """
    The Excel File is well formatted which means that the excel file contains some implication to 
    understand and prepare the data.
    return list[json]
    
    """
    excel_file = pd.ExcelFile(file_path)
    excel_data = excel_file.parse(sheet_name=sheet_name)
    # first column start, which stores the index and the column name into a dict
    header_dict = {}
    row = excel_data.loc[header_start]
    for i in range(0, len(row)):
        cell = row[i]
        if pd.notna(cell):
            header_dict[i] = cell
    # the file_name always contains the date
    match = re.search("\d{4}_\d{2}", file_path)
    if match:
        date = match.group(0)
    else:
        logging.info(f"No Date found for {file_path}")
    # create the JSON object for every row
    json_list = []
    for i in range(row_start, row_start + 6):
        # TODO rename
        json_element = {}
        json_element["Date"] = date
        # iterate columns of row
        row = excel_data.loc[i]
        # header dict stores the important header values
        for column_index in header_dict.keys():
            json_element[header_dict[column_index]] = row[column_index]
        json_list.append(json.loads(json.dumps(json_element)))
    # in the created list we ignored the vehicle type, append this to every JSON
    for i in range(0, len(json_list)):
        vehicle_type = excel_data.loc[row_start][1]
        json_list[i]["Vehicle Type"] = vehicle_type
        # TODO make it nier
        json_list[i]["tablename"] = TABLE_NAME
        row_start += 1

    return json_list


def get_json_data():
    # there exists two different url which holds the data we need.
    kba_generic_url_table = "https://www.kba.de/DE/Statistik/Fahrzeuge/Neuzulassungen/Umwelt/{0}/{0}_n_umwelt_tabellen.html?nn=3525054&fromStatistic=3525054&yearFilter={0}"
    kba_generic_download_links = "https://www.kba.de/DE/Statistik/Fahrzeuge/Neuzulassungen/Umwelt/n_umwelt_node.html;?yearFilter={0}"
    json_list = []
    excel_file_folder_name = "kba_car_registration_excel_files"
    excel_file_folder_path = os.path.join(os.getcwd(), excel_file_folder_name)
    for year in range(2015, datetime.datetime.now().year):
        kba_url = kba_generic_url_table.format(year)
        logging.info(f"New year: {year}" + "\n" + kba_url)
        # get content of website
        response = requests.get(kba_url)
        if response.status_code == 200:
            # if status code is 200 the site has a table and we can try to extract the data
            logging.info(f"Table found for {kba_url}, using table strategy")
            json_elements = download_table_strategy(response)
            if json_elements:
                # add date to the element
                for json_element in json_elements:
                    json_element["Date"] = year
                json_list += json_elements

        else:
            # if status code differs it will be most likely a list of files --> change url and try again
            logging.info(f"Generic Table Url not found for {kba_url}\n trying the generic download link url")
            kba_url = kba_generic_download_links.format(year)
            response = requests.get(kba_url)
            if response.status_code != 200:
                logging.info(f"kba_generic_download_links failed for {kba_url} ")
                continue
            logging.info(
                f"Generic Download link URL {response.url} worked, going with download_list_of_files_strategy ")
            # the files contains always the month in their names, therefore the months are the keywords
            months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober',
                      'November', 'Dezember']
            download_list_of_files_strategy(kba_url, "xlsx", months, excel_file_folder_path)
        time.sleep(1)
    # now convert the downloaded excel files to json objects
    if os.path.isdir(excel_file_folder_path):
        excel_files = os.listdir(excel_file_folder_path)
        for excel_file in excel_files:
            json_elements = extract_excel_data(os.path.join(excel_file_folder_path, excel_file), "FZ 28.1", 10, 13)
            if json_elements:
                json_list += json_elements
        try:
            shutil.rmtree(excel_file_folder_path)
        except OSError as e:
            logging.critical(f"Could not remove Folder {excel_file_folder_path}\n({e}")
    return json_list


if __name__ == "__main__":
    json_list = get_json_data()

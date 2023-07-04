import os.path
import urllib.request

from sqlalchemy import create_engine
import sqlalchemy.types as types
import pandas as pd
import zipfile

url = r"https://gtfs.rhoenenergie-bus.de/GTFS.zip"
filename = 'GTFS.zip'
folder = "downloaded"
csv_filename = "stops.txt"
csv_path = os.path.join(os.getcwd(), folder, csv_filename)


def download():
    urllib.request.urlretrieve(url, filename)


def extract():
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(folder)


def clean_validate_part():
    col_names = ["stop_id", "stop_name", "stop_lat", "stop_lon", "zone_id"]
    df = pd.read_csv(csv_path, delimiter=",", usecols=col_names)
    df = df[df['zone_id'] == 2001]
    df.drop(df[df.apply(
        lambda x: (x['stop_lat'] < -90) or (x['stop_lat'] > 90) or (x['stop_lon'] < -90) or (x['stop_lon'] > 90),
        axis=1)].index, inplace=True)
    return df


def sql_part(df):
    # sql part
    TABLE_NAME = "stops"
    engine = create_engine(f'sqlite:///gtfs.sqlite')
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=False,
              dtype={
                  "stop_id": types.String,
                  "stop_name": types.String,
                  "stop_lat": types.Float,
                  "stop_lon": types.Float,
                  "zone_id": types.Integer,
 }, )
    return 0


def main():
    download()
    extract()
    df = clean_validate_part()
    sql_part(df)

if __name__ == "__main__":
    main()

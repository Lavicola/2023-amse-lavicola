import os

import kba_car_registrations
import ladesauele
import data_transformer
import data_saver
import argparse


def main():
    """
    Pipeline:
    run scrips which return data in json_format
    Transform the Data via data_transformer
    Store the Data via data_saver

    """
    # setup constants
    INTERMEDIATE_FILENAME = "intermediate.json"

    # setup cmd arg parameter
    parser = argparse.ArgumentParser()

    # arguments:
    parser.add_argument('--db', type=str, help='The Location the database shall be placed(default: %(default)s)',
                        default=os.getcwd())
    parser.add_argument('--log', type=bool,
                        help='Create a log file to persistently store debug info(default: %(default)s)', default=True)
    parser.add_argument('--store_intermediate', type=bool, help='Store the extracted data of the "extract & specific data '
                                                          'transformation" into a file before transforming the data('
                                                          'default: %(default)s)',
                        default=False)
    parser.add_argument('--pipeline_intermediate', type=bool,
                        help='Use the Intermediate file instead of extracting it from the website(default: %(default)s)',
                        default=False)
    args = parser.parse_args()

    json_list = []
    json_elements = None
    # depending if intermediate file shall be used or not
    if args.pipeline_intermediate:
        # read intermediate data
        intermediate_path = os.path.join(os.getcwd(),INTERMEDIATE_FILENAME)
        print(f"Checking if {intermediate_path} exists")
        if not os.path.isfile(intermediate_path):
            print(f"Intermediate file in place {intermediate_path} not found, abort!")
            return
        print("trying to load intermediate data")
        return
    else:
        print("Starting with downloading the kba car registration Data ")
        json_elements = kba_car_registrations.main()
        if json_elements:
            print("Success, Data found and stored")
            json_list += json_elements
        json_list = data_transformer.transform_table_name(json_list)
        print("Downloading the Ladesauelen Data ")
        json_elements = ladesauele.main()
        if json_elements:
            print("Success, Data found and stored")
            json_list += json_elements
        print("Starting to Transform the data")

    if args.store_intermediate:
        #data_saver.save_intermediate(json_list)
        return

    # transform and store into database
    json_list = data_transformer.main(json_list)
    print("Storing the Data into a SQLite Database")
    data_saver.main(json_list)


if __name__ == "__main__":
    main()

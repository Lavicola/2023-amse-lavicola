import os

import kba_car_registrations
import ladesauele
import data_transformer
import data_saver
import argparse
import logging


def main():
    """
    Pipeline:
    run scrips which return data in json_format
    Transform the Data via data_transformer
    Store the Data via data_saver

    """

    # setup constants
    INTERMEDIATE_FILENAME = "intermediate.json"
    INTERMEDIATE_PATH = os.path.join(os.getcwd(), INTERMEDIATE_FILENAME)
    DB_FILENAME = "database.sqlite"

    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, help='The Location the database shall be placed(default: %(default)s)',
                        default=os.path.join(os.getcwd(), DB_FILENAME))
    parser.add_argument('--log', type=bool,
                        help='Create a log file to persistently store debug info(default: %(default)s)', default=True)
    parser.add_argument('--store_intermediate', type=bool,
                        help='Store the extracted data of the "extract & specific data '
                             'transformation" into a file before transforming the data('
                             'default: %(default)s)',
                        default=False)
    parser.add_argument('--pipeline_intermediate', type=bool,
                        help='Use the Intermediate file instead of extracting it from the website(default: %(default)s)',
                        default=False)
    args = parser.parse_args()

    initialize_logging(args.log)
    json_list = []
    json_elements = None
    # depending if intermediate file shall be used or not
    if args.pipeline_intermediate:
        # read intermediate data
        logging.info(f"Checking if {INTERMEDIATE_PATH} exists")
        if not os.path.isfile(INTERMEDIATE_PATH):
            logging.info(f"Intermediate file in place {INTERMEDIATE_PATH} not found, abort!")
            return
        logging.info("trying to load intermediate data")
        json_list = data_saver.load_intermediate_data(INTERMEDIATE_PATH)
    else:
        logging.info("Starting with downloading the kba car registration Data ")
        json_elements = kba_car_registrations.main()
        if json_elements:
            logging.info("Success, Data found and stored")
            json_list += json_elements
        json_list = data_transformer.transform_table_name(json_list)
        logging.info("Downloading the Ladesauelen Data ")
        json_elements = ladesauele.main()
        if json_elements:
            logging.info("Success, Data found and stored")
            json_list += json_elements
        logging.info("Starting to Transform the data")

    if args.store_intermediate:
        data_saver.save_intermediate(json_list, INTERMEDIATE_PATH)

    # transform and store into database
    json_list = data_transformer.main(json_list)
    logging.info("Storing the Data into a SQLite Database")
    data_saver.main(json_list, args.db)


def initialize_logging(enable_logging):
    # Configure the root logger
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    logger = logging.getLogger()
    # Set the logging level to INFO
    logger.setLevel(logging.INFO)
    if enable_logging:
        file_handler = logging.FileHandler('logfile.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
    logger.info("Logging configured")


if __name__ == "__main__":
    main()

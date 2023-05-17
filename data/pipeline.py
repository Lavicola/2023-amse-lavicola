import kba_car_registrations
import ladesauele
import data_transformer
import data_saver


def main():
    """
    Pipeline:
    run scrips which return data in json_format
    Transform the Data via data_transformer
    Store the Data via data_saver

    """
    json_list = []
    json_elements = None
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
        json_list+=json_elements
    print("Starting to Transform the data")
    json_list = data_transformer.main(json_list)
    print("Storing the Data into a SQLite Database")
    data_saver.main(json_list)


if __name__ == "__main__":
    main()

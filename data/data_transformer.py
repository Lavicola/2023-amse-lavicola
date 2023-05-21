import json
import re
import logging

ILLEGAL_CHARACTERS_TABLE_NAME = ["/", "#", " ", "[", "]", "-", "(", ")", "\n", ":"]
ILLEGAL_CHARACTERS_DICT = {char: True for char in ILLEGAL_CHARACTERS_TABLE_NAME}
TRANSLATION_TABLE = str.maketrans("".join(ILLEGAL_CHARACTERS_DICT), "_" * len(ILLEGAL_CHARACTERS_DICT))


def remove_illegal_characters_tablename(json_list: list[json]):
    """"

    """

    for json_element in json_list:
        keys_to_modify = [key for key in json_element if any(char in key for char in ILLEGAL_CHARACTERS_DICT)]
        for key in keys_to_modify:
            value = json_element[key]
            del json_element[key]
            modified_key = key.translate(TRANSLATION_TABLE)
            json_element[modified_key] = value

    return json_list


def check_same_word(string1, word):
    pattern = r"\b" + re.escape(word) + r"\b"
    return re.search(pattern, string1)


def transform_table_name(json_list: list[json]):
    """
    In kba_car_registration some table names changed, normalize them
    :param json_list:
    :return:
    """
    SAME_WORDS = ["Elektro", "Flüssiggas", "Erdgas", "Wasserstoff"]

    # surely there is a better option, but not worth it for the current amount of data ~ 0,22 seconds
    for word in SAME_WORDS:
        for json_element in json_list:
            keys_to_modify = []
            for key, value in json_element.items():
                if check_same_word(key, word):
                    keys_to_modify.append(key)
            for key in keys_to_modify:
                if key != word:
                    json_element[word] = json_element[key]
                    del json_element[key]
    json_list = remove_keys(json_list)

    return json_list


def convert_to_float(json_list: list[json], keys: list[str]):
    """
    :param json_list:
    :param columns:
    :return:
    """
    logging.info(f"Replacing comma with dot for the following keys: {keys}")
    for element in json_list:
        for key in keys:
            if key in element:
                try:
                    element[key] = float(element[key].replace(",", "."))
                except ValueError:
                    # some don´t have both coordinates, use invalid value
                    element[key] = 0.0
    return json_list


def remove_keys(json_list: list[json]):
    """
    Quickfix for the problem with the ever changing table structure

    :param json_list:
    :return:
    """
    SAME_WORDS = ["Hybrid", "Wasserstoff", "Diesel", "Benzin"]

    for word in SAME_WORDS:
        for json_element in json_list:
            keys_to_modify = []
            for key, value in json_element.items():
                if check_same_word(key, word):
                    keys_to_modify.append(key)
            for key in keys_to_modify:
                del json_element[key]
    return json_list


def main(json_list: list[json]):
    """

    """
    logging.info("Remove Illegal Characters in Keys")
    json_list = remove_illegal_characters_tablename(json_list)

    return json_list


if __name__ == "__main__":
    logging.info("nothing happens here")
    main()

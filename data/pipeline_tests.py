import logging
import os
import sqlite3
import sys
import unittest
import subprocess
import pipeline

class PipelineTests(unittest.TestCase):
    CURRENT_PATH = os.getcwd()
    INTERMEDIATE_FILE = "intermediate.json"
    DATABASE_FILE = "database.sqlite"
    INTERMEDIATE_FILEPATH = os.path.join(CURRENT_PATH, INTERMEDIATE_FILE)
    DATABASE_FILEPATH = os.path.join(CURRENT_PATH, DATABASE_FILE)
    DATABASE_MIN_ENTRIES_PER_TABLE = 100
    EXPECTED_TABLE_NO = 2

    def test_pipeline_without_arguments(self):
        """
        This test executes the Pipeline without any arguments.
        The expected behaviour is that the Pipeline does the following:
        1. download the data of ladesauele.py and kba_car_registrations.py
        2. DO NOT store the Data in a file
        3. Transform the Data
        4. successfully write the transformed data into a sqlite database with the name "database.sqlite"

        The Test is successful if:
        - absence of intermediate.json
        - presence of database.sqlite
        - presence of 2 tables which reflect the two data sources
        - no table contains less than 100 entries
        :return:
        """
        print("test")
        # remove args
        sys.argv = sys.argv[:1]
        # start the Pipeline
        pipeline.main()

        # check for success conditions
        assert not os.path.exists(
            self.INTERMEDIATE_FILEPATH), "Intermediate File found, even-though it should not be here "
        assert os.path.exists(self.DATABASE_FILEPATH), "Database is missing"

        conn = sqlite3.connect(self.DATABASE_FILEPATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        assert len(
            tables) == self.EXPECTED_TABLE_NO, f"Expected {self.EXPECTED_TABLE_NO}, but found only {len(tables)}!"
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            assert row_count > self.DATABASE_MIN_ENTRIES_PER_TABLE, f"Table '{table_name}' contains less than {self.DATABASE_MIN_ENTRIES_PER_TABLE} entries."

    def test_pipeline_with_arguments_intermediate_no_intermediate_pipeline(self):
        """
        This test executes the Pipeline with the argument to store the downloaded data into an intermediate.json.
        The expected behaviour is that the Pipeline does the following:
        1. download the data of ladesauele.py and kba_car_registrations.py
        2. store the data in an intermediate.json
        3. Transform the Data
        4. successfully write the transformed data into a sqlite database with the name "database.sqlite"

        The Test is successful if:
        - presence of intermediate.json
        - presence of database.sqlite
        - presence of 2 tables which reflect the two data sources
        - no table contains less than 100 entries
        :return:
        """
        # remove args
        sys.argv = sys.argv[:1]
        # patch is not working, therefore old school
        subprocess.call(['python3', 'pipeline.py', '--store_intermediate=True'])
        # check for success conditions
        assert os.path.exists(
            self.INTERMEDIATE_FILEPATH), "Intermediate File not found, even-though it should be here "
        assert os.path.exists(self.DATABASE_FILEPATH), "Database is missing"

        conn = sqlite3.connect(self.DATABASE_FILEPATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        assert len(
            tables) == self.EXPECTED_TABLE_NO, f"Expected {self.EXPECTED_TABLE_NO}, but found only {len(tables)}!"
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            assert row_count > self.DATABASE_MIN_ENTRIES_PER_TABLE, f"Table '{table_name}' contains less than {self.DATABASE_MIN_ENTRIES_PER_TABLE} entries."

    def setUp(self):
        pass

    def tearDown(self):
        """
        The tearDown Method deletes files which maybe created while executing the Pipeline
        :return:
        """

        if os.path.isfile(self.INTERMEDIATE_FILEPATH):
            logging.warning(f"Removing: {self.INTERMEDIATE_FILEPATH}")
            os.remove(self.INTERMEDIATE_FILEPATH)
        if os.path.isfile(self.DATABASE_FILEPATH):
            logging.warning(f"Removing: {self.DATABASE_FILEPATH}")
            os.remove(self.DATABASE_FILEPATH)

if __name__ == "__main__":
    unittest.main()


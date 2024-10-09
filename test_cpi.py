"""
Tests for cpi.py
"""
# Built-ins
import datetime
import unittest
# 3rd-party
# Internal
from cpi import Observation


class TestObservation(unittest.TestCase):

    def test___init__(self):
        inputs = {'Date': datetime.date.today(), 'Item': 'Dozen eggs', 'Price': 3.99, 'Category': 'Food',
                  'State': 'Texas', 'City': 'Dallas'}
        obj = Observation(**inputs)
        self.assertEqual(obj.Date, datetime.date.today())
        self.assertEqual(obj.Category, 'Food')

    def test_create_table(self):
        Observation.create_table()

    def test_get_test_data(self):
        df = Observation.get_test_data()
        self.assertGreater(len(df.index), 0)

    def test_delete_matching(self):
        Observation.create_table()

        obj = Observation(Date=datetime.date.today(), Item='USDA Grade-A eggs (Dozen)', Price=9.9999,
                          Category='Food', State='Texas', City='Dallas')
        obj.write()

        # Verify data insertion
        df_before = Observation.table_df()
        self.assertGreater(len(df_before.index), 0)

        # Delete matching observations
        Observation().delete_matching(
            n_to_delete = 1, 
            order_to_delete_in = {'AddedOn': False},
            State ='Texas', City='Dallas'
        )

        # Verify deletion
        df_after = Observation.table_df()
        self.assertLess(len(df_after.index), len(df_before.index))

    def test_same_value_data_points(self):
        # Adding duplicate data points to test the graph with point size scale 
        for i in range(20):
            obj = Observation(Date=datetime.date.today(), Item='USDA Grade-A eggs (Dozen)', Price=4.01,
                    Category='Food', State='Texas', City='Dallas')
            obj.write()
        for i in range(10):
            obj = Observation(Date=datetime.date.today(), Item='USDA Grade-A eggs (Dozen)', Price=4.56,
                          Category='Food', State='Texas', City='Dallas')
            obj.write()

        
if __name__ == '__main__':
    unittest.main()

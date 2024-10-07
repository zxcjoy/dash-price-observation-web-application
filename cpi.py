"""
Library for modeling prices for various objects
"""
# Built-ins
import datetime
import functools
import itertools
import logging
import random
import sqlite3
from typing import Optional, Union
# 3rd-party
import pandas as pd
# Internal


logger = logging.getLogger(__name__)
db_file = 'test.db'


def sqlize(v: Union[str, int, float, bool, datetime.date, datetime.date]) -> str:
    if isinstance(v, str):
        v = v.replace("'", "''")
    elif isinstance(v, datetime.datetime):
        v = v.strftime('%Y-%m-%d %H:%M:%S.%f')
    elif isinstance(v, datetime.date):
        v = v.strftime('%Y-%m-%d')
    elif isinstance(v, bool):
        v = int(v)
    return f"'{v}'" if isinstance(v, str) else str(v)


class Observation:

    Date: Optional[datetime.date] = None
    Item: Optional[str] = None
    Price: Optional[float] = None
    Category: Optional[str] = None
    State: Optional[str] = None
    City: Optional[str] = None
    AddedOn: datetime.datetime = datetime.datetime.now()

    category_item_map = {'Food': ['USDA Grade-A eggs, Dozen'],
                         'Fuel': ['Regular Gasoline, Gallon'],
                         'Clothing': ['Wool Socks, Pair']}
    state_city_map = {'California': ['Los Angelos', 'San Francisco'],
                      'New York': ['New York City'],
                      'Texas': ['Austin', 'Dallas']}
    item_base_price = {'USDA Grade-A eggs, Dozen': 2.99,
                       'Regular Gasoline, Gallon': 4.65,
                       'Wool Socks, Pair': 21.95}
    state_price_mu_std = {'California': (1.5, 0.15),
                          'New York': (1.75, 0.25),
                          'Texas': (1, 0.10)}

    @classmethod
    @functools.lru_cache(maxsize=None)
    def available_items(cls):
        return list(itertools.chain.from_iterable(cls.category_item_map.values()))

    @classmethod
    @functools.lru_cache(maxsize=None)
    def available_categories(cls):
        return list(cls.category_item_map.keys())

    @classmethod
    @functools.lru_cache(maxsize=None)
    def available_states(cls):
        return list(cls.state_city_map.keys())

    @classmethod
    @functools.lru_cache(maxsize=None)
    def available_cities(cls):
        return list(itertools.chain.from_iterable(cls.state_city_map.values()))

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                logger.warning(f'{k} is not a valid attribute of Observation. Ignoring...')

    def write(self):
        with sqlite3.connect(db_file) as con:
            row = [sqlize(v) for v in [self.Date, self.Item, self.Price, self.Category, self.State, self.City]]
            sql = (f'INSERT INTO Observation (Date, Item, Price, Category, State, City) values '
                   f'({", ".join(row)})')
            con.execute(sql)

    @classmethod
    def create_table(cls):
        sql = '''
        create table Observation (
            Date date not null,
            Item text not null,
            Price numeric not null,
            Category text not null,
            State text not null,
            City text not null,
            AddedOn datetime default current_timestamp
        );
        '''
        with sqlite3.connect(db_file) as con:
            con.execute('drop table if exists Observation')
            con.execute(sql)
            # Load test data
            df = cls.get_test_data()
            df.to_sql('Observation', con=con, if_exists='append', index=False)

    @classmethod
    def get_test_data(cls) -> pd.DataFrame:
        dt_range = pd.date_range(end=datetime.date.today(), periods=10, freq='D', inclusive='both')
        combos = [{'Date': dt, 'Category': cat, 'Item': item, 'State': state, 'City': city}
                  for cat, items in cls.category_item_map.items()
                  for item in items
                  for state, cities in cls.state_city_map.items()
                  for city in cities
                  for dt in dt_range
                  for _ in range(5)]  # Create 5 prices per combo
        df = pd.DataFrame(combos)
        # Set all base prices to the average price for the item
        df['Price'] = df.apply(lambda s: cls.item_base_price[s['Item']], axis=1)
        # Multiply the base price by the state scaling factor
        df['Price'] = df.apply(lambda s: s['Price'] * cls.state_price_mu_std[s['State']][0], axis=1)
        # Generate a gaussian price based on the state standard deviation
        df['Price'] = df.apply(lambda s: random.gauss(s['Price'], s['Price'] * cls.state_price_mu_std[s['State']][1]),
                               axis=1)
        return df

    @staticmethod
    def table_df() -> pd.DataFrame:
        with sqlite3.connect(db_file) as con:
            sql = 'select * from Observation'
            return pd.read_sql(sql, con)

    def delete_matching(self, n_to_delete: int = 1, order_to_delete_in: Optional[dict] = None, **kwargs):
        # TODO: Fill-in logic to delete rows from the table such that the key-value pairs in kwargs correspond to the
        #  column-value to match on.
        #  Ex. kwargs = {'State': 'Texas', 'City': 'Dallas'} would match all rows where the
        #  value of State = 'Texas' AND the value of City = 'Dallas'. n_to_delete specifies the number of matching rows
        #  to delete and order_to_delete_in is a dict of:
        #  {<column to use for ordering matching rows>: <True for ascending, False for descending>}
        pass


if __name__ == '__main__':
    pass

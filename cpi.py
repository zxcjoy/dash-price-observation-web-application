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
from config import DB_FILE, CATEGORY_ITEM_MAP, ITEM_BASE_PRICE, STATE_CITY_MAP, STATE_PRICE_MU_STD
from utils import sqlize, custom_rounding

logger = logging.getLogger(__name__)
db_file =  DB_FILE

class Observation:

    Date: Optional[datetime.date] = None
    Item: Optional[str] = None
    Price: Optional[float] = None
    Category: Optional[str] = None
    State: Optional[str] = None
    City: Optional[str] = None
    AddedOn: datetime.datetime = datetime.datetime.now()

    category_item_map = CATEGORY_ITEM_MAP
    state_city_map = STATE_CITY_MAP
    item_base_price = ITEM_BASE_PRICE
    state_price_mu_std = STATE_PRICE_MU_STD

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
        """
        Write the Observation object into database (insert), return (Bool value, error message) to indicate success
        """
        try:
            with sqlite3.connect(db_file) as con:
                row = [sqlize(v) for v in [self.Date, self.Item, self.Price, self.Category, self.State, self.City]]
                sql = (f'insert into Observation (Date, Item, Price, Category, State, City) values '
                    f'({", ".join(row)})')
                con.execute(sql)
                # print(f'{sql} executed successfully')
            return (True, 'New Observation added to database successfully')
        except:
            return (False, 'Failed to add new Observation to database')
        
    @classmethod
    def create_table(cls):
        sql = '''
        create table Observation (
            Date date not null,
            Item text not null,
            Price numeric(10,4) not null,
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
        combos = [{'Date': dt.date(), 'Category': cat, 'Item': item, 'State': state, 'City': city}
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
        df['Price'] = df.apply(custom_rounding, axis=1) # Apply rounding function with better real-word meaning
        df['Price'] = df['Price'].apply(lambda x: round(x, 4))
        return df

    @staticmethod
    def table_df() -> pd.DataFrame:
        with sqlite3.connect(db_file) as con:
            sql = 'select * from Observation'
            return pd.read_sql(sql, con)

    def delete_matching(self, n_to_delete: int = 1, order_to_delete_in: Optional[dict] = None, **kwargs):
        """
        Delete matched records from databse given parameters, return (number of rows deleted, error message)
        """
        # TODO: Fill-in logic to delete rows from the table such that the key-value pairs in kwargs correspond to the
        #  column-value to match on.
        #  Ex. kwargs = {'State': 'Texas', 'City': 'Dallas'} would match all rows where the
        #  value of State = 'Texas' AND the value of City = 'Dallas'. n_to_delete specifies the number of matching rows
        #  to delete and order_to_delete_in is a dict of:
        #  {<column to use for ordering matching rows>: <True for ascending, False for descending>}
        
        # Check for constraints of function parameters
        if not kwargs:
            raise ValueError('Must specify at least one column-value pair to match on')
        if not isinstance(n_to_delete, int):
            raise ValueError('n_to_delete must be an integer')

        # The SQL should be like:
        # SELECT FROM Observation WHERE {where_clause} {order_clause} LIMIT {n_to_delete};
        # print('delete_matching methods called!')
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None} # Support None Price values, which means not filtering on Price
        where_clause = " and ".join([f"{k}={sqlize(v)}" for k,v in filtered_kwargs.items()])
        order_clause = ""
        if order_to_delete_in:
            order_clause = "order by " + \
                ", ".join([f"{k} {'asc' if v==True else 'desc'}" 
                           for k,v in order_to_delete_in.items()]) # True for ascending, False for descending
        # Select the rows to delete
        sql_select = f"""
        SELECT Date, Item, Price, Category, State, City, AddedOn FROM Observation
        WHERE {where_clause}
        {order_clause}
        LIMIT {n_to_delete};
        """
        # print('sql_select:', sql_select)
        message = 'Unknown system error'
        num_deleted = 0
        with sqlite3.connect(db_file) as con:
            cursor = con.cursor()
            cursor.execute(sql_select)
            rows_to_delete = cursor.fetchall()
            if rows_to_delete:
                for row in rows_to_delete:
                    # Delete query
                    delete_conditions = f"Date = '{row[0]}' and Item = '{row[1]}' and Price = {row[2]} and " \
                                        f"Category = '{row[3]}' and State = '{row[4]}' and City = '{row[5]}'" \
                                        f"and AddedOn = '{row[6]}' "
                    
                    sql_delete = f"delete from Observation where {delete_conditions}"
                    # print(f"Now delete sql query: {sql_delete}")
                    cursor.execute(sql_delete)
                num_deleted = len(rows_to_delete)
                message = 'matching observations deleted'
            else:
                # print("No matching observation found to delete.")
                message = 'No matching record found'
        return (num_deleted, message)

if __name__ == '__main__':
    pass

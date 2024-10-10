# config.py

# Database configuration
DB_FILE = 'test.db'

# Observation configuration
CATEGORY_ITEM_MAP = {
    'Food': ['USDA Grade-A eggs (Dozen)'],
    'Fuel': ['Regular Gasoline (Gallon)'],
    'Clothing': ['Wool Socks (Pair)']
}

STATE_CITY_MAP = {
    'California': ['Los Angeles', 'San Francisco'],
    'New York': ['New York City'],
    'Texas': ['Austin', 'Dallas']
}

ITEM_BASE_PRICE = {
    'USDA Grade-A eggs (Dozen)': 2.99,
    'Regular Gasoline (Gallon)': 4.65,
    'Wool Socks (Pair)': 21.95
}

STATE_PRICE_MU_STD = {
    'California': (1.5, 0.15),
    'New York': (1.75, 0.25),
    'Texas': (1, 0.10)
}

# App configuration

# Table configuration
# TABLE_PAGE_SIZE = 20
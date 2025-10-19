import pandas as pd

class Configuration:
    def __init__(self):
        self.review_column_list = ['reviews.title', 'reviews.text']
        self.filterable_columns = ['categories', 'city', 'country', 'postalCode', 'province', 'rating', 'userCity', 'userProvince']
        self.column_mapping = {
            'reviews.title': 'Title',
            'reviews.text': 'Description',
            'categories': 'Categories',
            'city': 'City',
            'country': 'Country',
            'postalCode': 'Postal Code',
            'province': 'Province',
            'rating': 'Rating',
            'userCity': 'Reviewer City',
            'userProvince': 'Reviewer Province',
        }
        # Load full dataset (or a larger sample)
        df = pd.read_csv('data/Hotel_Reviews.csv')
        df.dropna(subset=self.filterable_columns + self.review_column_list, inplace=True)
        df['rating'] = df['rating'].astype(int)
        self.dataset = df
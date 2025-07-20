"""
Data Preprocessing Module for E-Commerce Analysis
Handles data cleaning, transformation, and feature engineering
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

class EcommerceDataPreprocessor:
    """
    A comprehensive data preprocessor for e-commerce datasets
    """
    
    def __init__(self):
        self.customer_features = None
        self.product_features = None
        self.transaction_features = None
        
    def load_sample_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generate sample e-commerce data for analysis
        Returns: customers_df, products_df, transactions_df
        """
        np.random.seed(42)
        
        # Generate customer data
        n_customers = 1000
        customers_df = pd.DataFrame({
            'customer_id': range(1, n_customers + 1),
            'customer_name': [f'Customer_{i}' for i in range(1, n_customers + 1)],
            'email': [f'customer{i}@email.com' for i in range(1, n_customers + 1)],
            'registration_date': pd.date_range('2020-01-01', periods=n_customers, freq='D'),
            'location': np.random.choice(['US', 'UK', 'CA', 'AU', 'DE'], n_customers),
            'age_group': np.random.choice(['18-25', '26-35', '36-45', '46-55', '55+'], n_customers),
            'income_level': np.random.choice(['Low', 'Medium', 'High'], n_customers)
        })
        
        # Generate product data
        n_products = 200
        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Beauty']
        products_df = pd.DataFrame({
            'product_id': range(1, n_products + 1),
            'product_name': [f'Product_{i}' for i in range(1, n_products + 1)],
            'category': np.random.choice(categories, n_products),
            'subcategory': [f'Sub_{cat}_{i}' for i, cat in enumerate(np.random.choice(categories, n_products))],
            'price': np.random.uniform(10, 500, n_products),
            'cost': np.random.uniform(5, 300, n_products),
            'brand': [f'Brand_{i % 20}' for i in range(n_products)]
        })
        products_df['profit_margin'] = (products_df['price'] - products_df['cost']) / products_df['price']
        
        # Generate transaction data
        n_transactions = 5000
        transactions_df = pd.DataFrame({
            'transaction_id': range(1, n_transactions + 1),
            'customer_id': np.random.choice(customers_df['customer_id'], n_transactions),
            'product_id': np.random.choice(products_df['product_id'], n_transactions),
            'quantity': np.random.randint(1, 10, n_transactions),
            'transaction_date': pd.date_range('2022-01-01', periods=n_transactions, freq='H'),
            'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer'], n_transactions),
            'shipping_method': np.random.choice(['Standard', 'Express', 'Free'], n_transactions)
        })
        
        # Merge with product data to get prices
        transactions_df = transactions_df.merge(
            products_df[['product_id', 'price', 'cost']], 
            on='product_id'
        )
        transactions_df['total_amount'] = transactions_df['quantity'] * transactions_df['price']
        transactions_df['total_cost'] = transactions_df['quantity'] * transactions_df['cost']
        transactions_df['profit'] = transactions_df['total_amount'] - transactions_df['total_cost']
        
        return customers_df, products_df, transactions_df
    
    def clean_data(self, customers_df: pd.DataFrame, products_df: pd.DataFrame, 
                   transactions_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Clean the datasets by handling missing values, duplicates, and data types
        """
        # Clean customers data
        customers_clean = customers_df.copy()
        customers_clean['registration_date'] = pd.to_datetime(customers_clean['registration_date'])
        customers_clean = customers_clean.dropna()
        customers_clean = customers_clean.drop_duplicates()
        
        # Clean products data
        products_clean = products_df.copy()
        products_clean['price'] = products_clean['price'].abs()
        products_clean['cost'] = products_clean['cost'].abs()
        products_clean = products_clean[products_clean['price'] >= products_clean['cost']]
        products_clean = products_clean.dropna()
        
        # Clean transactions data
        transactions_clean = transactions_df.copy()
        transactions_clean['transaction_date'] = pd.to_datetime(transactions_clean['transaction_date'])
        transactions_clean = transactions_clean[transactions_clean['quantity'] > 0]
        transactions_clean = transactions_clean.dropna()
        
        return customers_clean, products_clean, transactions_clean
    
    def create_customer_features(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create customer-level features for analysis
        """
        # Merge customer and transaction data
        customer_transactions = transactions_df.merge(customers_df, on='customer_id')
        
        # Calculate customer features
        customer_features = customer_transactions.groupby('customer_id').agg({
            'transaction_id': 'count',  # Total orders
            'total_amount': ['sum', 'mean'],  # Total spent, average order value
            'quantity': 'sum',  # Total items purchased
            'transaction_date': ['min', 'max'],  # First and last purchase
            'product_id': 'nunique',  # Unique products purchased
            'profit': 'sum'  # Total profit generated
        }).round(2)
        
        # Flatten column names
        customer_features.columns = ['total_orders', 'total_spent', 'avg_order_value', 
                                  'total_items', 'first_purchase', 'last_purchase', 
                                  'unique_products', 'total_profit']
        
        # Calculate additional features
        customer_features['days_since_first_purchase'] = (
            pd.Timestamp.now() - customer_features['first_purchase']
        ).dt.days
        
        customer_features['days_since_last_purchase'] = (
            pd.Timestamp.now() - customer_features['last_purchase']
        ).dt.days
        
        customer_features['avg_items_per_order'] = (
            customer_features['total_items'] / customer_features['total_orders']
        ).round(2)
        
        # Merge with customer demographics
        customer_features = customer_features.merge(customers_df, on='customer_id')
        
        return customer_features
    
    def create_product_features(self, products_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create product-level features for analysis
        """
        # Merge product and transaction data
        product_transactions = transactions_df.merge(products_df, on='product_id')
        
        # Calculate product features
        product_features = product_transactions.groupby('product_id').agg({
            'transaction_id': 'count',  # Total sales
            'quantity': 'sum',  # Total units sold
            'total_amount': 'sum',  # Total revenue
            'profit': 'sum',  # Total profit
            'customer_id': 'nunique'  # Unique customers
        }).round(2)
        
        # Flatten column names
        product_features.columns = ['total_sales', 'total_units_sold', 'total_revenue', 
                                 'total_profit', 'unique_customers']
        
        # Calculate additional features
        product_features['avg_order_quantity'] = (
            product_features['total_units_sold'] / product_features['total_sales']
        ).round(2)
        
        product_features['revenue_per_customer'] = (
            product_features['total_revenue'] / product_features['unique_customers']
        ).round(2)
        
        # Merge with product details
        product_features = product_features.merge(products_df, on='product_id')
        
        return product_features
    
    def create_rfm_features(self, transactions_df: pd.DataFrame, 
                           reference_date: datetime = None) -> pd.DataFrame:
        """
        Create RFM (Recency, Frequency, Monetary) features for customer segmentation
        """
        if reference_date is None:
            reference_date = transactions_df['transaction_date'].max()
        
        # Calculate RFM metrics
        rfm = transactions_df.groupby('customer_id').agg({
            'transaction_date': lambda x: (reference_date - x.max()).days,  # Recency
            'transaction_id': 'count',  # Frequency
            'total_amount': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Create RFM scores (1-5 scale)
        r_labels = range(5, 0, -1)
        f_labels = range(1, 6)
        m_labels = range(1, 6)
        
        r_quartiles = pd.qcut(rfm['recency'], q=5, labels=r_labels)
        f_quartiles = pd.qcut(rfm['frequency'], q=5, labels=f_labels)
        m_quartiles = pd.qcut(rfm['monetary'], q=5, labels=m_labels)
        
        rfm['R'] = r_quartiles
        rfm['F'] = f_quartiles
        rfm['M'] = m_quartiles
        
        # Create RFM score
        rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
        
        # Create customer segments
        def segment_customers(row):
            if row['R'] >= 4 and row['F'] >= 4 and row['M'] >= 4:
                return 'Champions'
            elif row['R'] >= 3 and row['F'] >= 3 and row['M'] >= 3:
                return 'Loyal Customers'
            elif row['R'] >= 3 and row['F'] >= 1 and row['M'] >= 1:
                return 'At Risk'
            elif row['R'] >= 4 and row['F'] >= 1 and row['M'] >= 1:
                return 'Can\'t Lose'
            elif row['R'] >= 4 and row['F'] >= 1 and row['M'] >= 1:
                return 'New Customers'
            else:
                return 'Lost'
        
        rfm['Segment'] = rfm.apply(segment_customers, axis=1)
        
        return rfm
    
    def create_time_features(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create time-based features for seasonality analysis
        """
        transactions_with_time = transactions_df.copy()
        
        # Extract time components
        transactions_with_time['year'] = transactions_with_time['transaction_date'].dt.year
        transactions_with_time['month'] = transactions_with_time['transaction_date'].dt.month
        transactions_with_time['day_of_week'] = transactions_with_time['transaction_date'].dt.dayofweek
        transactions_with_time['day_of_month'] = transactions_with_time['transaction_date'].dt.day
        transactions_with_time['quarter'] = transactions_with_time['transaction_date'].dt.quarter
        transactions_with_time['week_of_year'] = transactions_with_time['transaction_date'].dt.isocalendar().week
        
        # Create seasonality features
        transactions_with_time['is_weekend'] = transactions_with_time['day_of_week'].isin([5, 6]).astype(int)
        transactions_with_time['is_month_start'] = transactions_with_time['day_of_month'] <= 3
        transactions_with_time['is_month_end'] = transactions_with_time['day_of_month'] >= 28
        
        # Create holiday season indicator (Q4)
        transactions_with_time['is_holiday_season'] = transactions_with_time['quarter'] == 4
        
        return transactions_with_time
    
    def prepare_churn_data(self, customer_features: pd.DataFrame, 
                          churn_threshold_days: int = 90) -> pd.DataFrame:
        """
        Prepare data for churn prediction
        """
        churn_data = customer_features.copy()
        
        # Define churn (customers who haven't purchased in threshold days)
        churn_data['is_churned'] = (churn_data['days_since_last_purchase'] > churn_threshold_days).astype(int)
        
        # Create features for churn prediction
        churn_data['avg_order_frequency'] = churn_data['total_orders'] / (churn_data['days_since_first_purchase'] + 1)
        churn_data['total_spent_per_day'] = churn_data['total_spent'] / (churn_data['days_since_first_purchase'] + 1)
        
        # Encode categorical variables
        categorical_cols = ['location', 'age_group', 'income_level']
        for col in categorical_cols:
            if col in churn_data.columns:
                churn_data = pd.get_dummies(churn_data, columns=[col], prefix=col)
        
        return churn_data
    
    def get_data_summary(self, customers_df: pd.DataFrame, products_df: pd.DataFrame, 
                        transactions_df: pd.DataFrame) -> Dict:
        """
        Generate a comprehensive data summary
        """
        summary = {
            'customers': {
                'total_customers': len(customers_df),
                'unique_locations': customers_df['location'].nunique(),
                'age_groups': customers_df['age_group'].value_counts().to_dict(),
                'income_levels': customers_df['income_level'].value_counts().to_dict()
            },
            'products': {
                'total_products': len(products_df),
                'categories': products_df['category'].value_counts().to_dict(),
                'avg_price': products_df['price'].mean(),
                'avg_profit_margin': products_df['profit_margin'].mean()
            },
            'transactions': {
                'total_transactions': len(transactions_df),
                'total_revenue': transactions_df['total_amount'].sum(),
                'total_profit': transactions_df['profit'].sum(),
                'date_range': {
                    'start': transactions_df['transaction_date'].min(),
                    'end': transactions_df['transaction_date'].max()
                },
                'payment_methods': transactions_df['payment_method'].value_counts().to_dict()
            }
        }
        
        return summary

# Example usage
if __name__ == "__main__":
    preprocessor = EcommerceDataPreprocessor()
    
    # Load and process sample data
    customers, products, transactions = preprocessor.load_sample_data()
    customers_clean, products_clean, transactions_clean = preprocessor.clean_data(
        customers, products, transactions
    )
    
    # Create features
    customer_features = preprocessor.create_customer_features(customers_clean, transactions_clean)
    product_features = preprocessor.create_product_features(products_clean, transactions_clean)
    rfm_features = preprocessor.create_rfm_features(transactions_clean)
    time_features = preprocessor.create_time_features(transactions_clean)
    
    # Prepare churn data
    churn_data = preprocessor.prepare_churn_data(customer_features)
    
    # Get summary
    summary = preprocessor.get_data_summary(customers_clean, products_clean, transactions_clean)
    
    print("Data preprocessing completed!")
    print(f"Total customers: {summary['customers']['total_customers']}")
    print(f"Total transactions: {summary['transactions']['total_transactions']}")
    print(f"Total revenue: ${summary['transactions']['total_revenue']:,.2f}") 
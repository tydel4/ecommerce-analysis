"""
Customer Analysis Module for E-Commerce Analysis
Handles customer segmentation, RFM analysis, and customer behavior insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class CustomerAnalyzer:
    """
    Comprehensive customer analysis for e-commerce data
    """
    
    def __init__(self):
        self.customer_segments = None
        self.rfm_analysis = None
        self.clustering_model = None
        
    def perform_rfm_analysis(self, transactions_df: pd.DataFrame, 
                           reference_date: pd.Timestamp = None) -> pd.DataFrame:
        """
        Perform RFM (Recency, Frequency, Monetary) analysis
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
        
        self.rfm_analysis = rfm
        return rfm
    
    def perform_customer_segmentation(self, customer_features: pd.DataFrame, 
                                    n_clusters: int = 4) -> pd.DataFrame:
        """
        Perform K-means clustering for customer segmentation
        """
        # Select features for clustering
        clustering_features = [
            'total_orders', 'total_spent', 'avg_order_value', 
            'total_items', 'unique_products', 'days_since_first_purchase',
            'avg_items_per_order'
        ]
        
        # Prepare data
        X = customer_features[clustering_features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        customer_features['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Analyze clusters
        cluster_analysis = customer_features.groupby('cluster')[clustering_features].mean()
        
        # Assign cluster labels based on characteristics
        cluster_labels = []
        for cluster_id in range(n_clusters):
            cluster_data = cluster_analysis.loc[cluster_id]
            if cluster_data['total_spent'] > cluster_data['total_spent'].mean() and \
               cluster_data['total_orders'] > cluster_data['total_orders'].mean():
                label = 'High-Value Customers'
            elif cluster_data['total_spent'] > cluster_data['total_spent'].mean():
                label = 'Big Spenders'
            elif cluster_data['total_orders'] > cluster_data['total_orders'].mean():
                label = 'Frequent Buyers'
            else:
                label = 'Occasional Buyers'
            cluster_labels.append(label)
        
        # Map cluster labels
        cluster_mapping = dict(zip(range(n_clusters), cluster_labels))
        customer_features['segment'] = customer_features['cluster'].map(cluster_mapping)
        
        self.customer_segments = customer_features
        self.clustering_model = kmeans
        
        return customer_features
    
    def analyze_customer_lifetime_value(self, customer_features: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate and analyze Customer Lifetime Value (CLV)
        """
        clv_data = customer_features.copy()
        
        # Calculate CLV (simplified version)
        clv_data['clv'] = clv_data['total_spent'] * (clv_data['total_orders'] / 
                                                     (clv_data['days_since_first_purchase'] + 1))
        
        # Calculate average purchase frequency
        clv_data['avg_purchase_frequency'] = clv_data['total_orders'] / \
                                           (clv_data['days_since_first_purchase'] + 1)
        
        # Calculate average customer lifespan (simplified)
        clv_data['customer_lifespan'] = clv_data['days_since_first_purchase']
        
        # CLV segments
        clv_data['clv_segment'] = pd.cut(clv_data['clv'], 
                                        bins=[0, clv_data['clv'].quantile(0.25),
                                              clv_data['clv'].quantile(0.75), clv_data['clv'].max()],
                                        labels=['Low CLV', 'Medium CLV', 'High CLV'])
        
        return clv_data
    
    def analyze_purchase_patterns(self, transactions_df: pd.DataFrame, 
                                customer_features: pd.DataFrame) -> Dict:
        """
        Analyze customer purchase patterns
        """
        # Merge data
        customer_transactions = transactions_df.merge(customer_features, on='customer_id')
        
        # Purchase patterns analysis
        patterns = {
            'avg_order_value_by_segment': customer_transactions.groupby('segment')['total_amount'].mean(),
            'purchase_frequency_by_segment': customer_transactions.groupby('segment')['transaction_id'].count() / 
                                           customer_transactions.groupby('segment')['customer_id'].nunique(),
            'category_preference_by_segment': customer_transactions.groupby(['segment', 'category'])['transaction_id'].count(),
            'payment_method_by_segment': customer_transactions.groupby(['segment', 'payment_method'])['transaction_id'].count(),
            'time_of_day_patterns': customer_transactions.groupby(
                customer_transactions['transaction_date'].dt.hour)['transaction_id'].count(),
            'day_of_week_patterns': customer_transactions.groupby(
                customer_transactions['transaction_date'].dt.dayofweek)['transaction_id'].count()
        }
        
        return patterns
    
    def create_customer_visualizations(self, customer_features: pd.DataFrame, 
                                     rfm_analysis: pd.DataFrame) -> None:
        """
        Create comprehensive customer analysis visualizations
        """
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Customer Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Customer Segments Distribution
        segment_counts = customer_features['segment'].value_counts()
        axes[0, 0].pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Customer Segments Distribution')
        
        # 2. RFM Segments Distribution
        rfm_counts = rfm_analysis['Segment'].value_counts()
        axes[0, 1].bar(rfm_counts.index, rfm_counts.values, color='skyblue')
        axes[0, 1].set_title('RFM Segments Distribution')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Average Order Value by Segment
        avg_order_by_segment = customer_features.groupby('segment')['avg_order_value'].mean()
        axes[0, 2].bar(avg_order_by_segment.index, avg_order_by_segment.values, color='lightgreen')
        axes[0, 2].set_title('Average Order Value by Segment')
        axes[0, 2].tick_params(axis='x', rotation=45)
        
        # 4. Total Spent vs Total Orders Scatter
        axes[1, 0].scatter(customer_features['total_orders'], customer_features['total_spent'], 
                           alpha=0.6, c=customer_features['cluster'], cmap='viridis')
        axes[1, 0].set_xlabel('Total Orders')
        axes[1, 0].set_ylabel('Total Spent ($)')
        axes[1, 0].set_title('Total Spent vs Total Orders')
        
        # 5. Customer Lifetime Value Distribution
        clv_data = self.analyze_customer_lifetime_value(customer_features)
        axes[1, 1].hist(clv_data['clv'], bins=30, alpha=0.7, color='orange')
        axes[1, 1].set_xlabel('Customer Lifetime Value ($)')
        axes[1, 1].set_ylabel('Number of Customers')
        axes[1, 1].set_title('Customer Lifetime Value Distribution')
        
        # 6. Days Since Last Purchase by Segment
        days_by_segment = customer_features.groupby('segment')['days_since_last_purchase'].mean()
        axes[1, 2].bar(days_by_segment.index, days_by_segment.values, color='lightcoral')
        axes[1, 2].set_title('Average Days Since Last Purchase by Segment')
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def create_interactive_dashboard(self, customer_features: pd.DataFrame, 
                                   rfm_analysis: pd.DataFrame) -> go.Figure:
        """
        Create an interactive Plotly dashboard for customer analysis
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Customer Segments', 'RFM Analysis', 'Order Value Distribution',
                          'CLV by Segment', 'Purchase Frequency', 'Recency Distribution'),
            specs=[[{"type": "pie"}, {"type": "bar"}, {"type": "histogram"}],
                   [{"type": "scatter"}, {"type": "bar"}, {"type": "histogram"}]]
        )
        
        # 1. Customer Segments Pie Chart
        segment_counts = customer_features['segment'].value_counts()
        fig.add_trace(
            go.Pie(labels=segment_counts.index, values=segment_counts.values, name="Segments"),
            row=1, col=1
        )
        
        # 2. RFM Segments Bar Chart
        rfm_counts = rfm_analysis['Segment'].value_counts()
        fig.add_trace(
            go.Bar(x=rfm_counts.index, y=rfm_counts.values, name="RFM Segments"),
            row=1, col=2
        )
        
        # 3. Order Value Distribution
        fig.add_trace(
            go.Histogram(x=customer_features['avg_order_value'], name="Order Value"),
            row=1, col=3
        )
        
        # 4. CLV by Segment
        clv_data = self.analyze_customer_lifetime_value(customer_features)
        clv_by_segment = clv_data.groupby('segment')['clv'].mean()
        fig.add_trace(
            go.Scatter(x=clv_by_segment.index, y=clv_by_segment.values, 
                      mode='markers+lines', name="CLV by Segment"),
            row=2, col=1
        )
        
        # 5. Purchase Frequency by Segment
        freq_by_segment = customer_features.groupby('segment')['total_orders'].mean()
        fig.add_trace(
            go.Bar(x=freq_by_segment.index, y=freq_by_segment.values, name="Purchase Frequency"),
            row=2, col=2
        )
        
        # 6. Recency Distribution
        fig.add_trace(
            go.Histogram(x=customer_features['days_since_last_purchase'], name="Recency"),
            row=2, col=3
        )
        
        # Update layout
        fig.update_layout(
            title_text="Customer Analysis Dashboard",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def generate_customer_insights(self, customer_features: pd.DataFrame, 
                                 rfm_analysis: pd.DataFrame) -> Dict:
        """
        Generate key insights from customer analysis
        """
        insights = {
            'total_customers': len(customer_features),
            'total_revenue': customer_features['total_spent'].sum(),
            'avg_customer_value': customer_features['total_spent'].mean(),
            'top_segment': customer_features['segment'].value_counts().index[0],
            'champions_count': len(rfm_analysis[rfm_analysis['Segment'] == 'Champions']),
            'at_risk_count': len(rfm_analysis[rfm_analysis['Segment'] == 'At Risk']),
            'avg_order_value': customer_features['avg_order_value'].mean(),
            'customer_retention_rate': len(customer_features[customer_features['days_since_last_purchase'] <= 30]) / len(customer_features),
            'high_value_customers': len(customer_features[customer_features['total_spent'] > customer_features['total_spent'].quantile(0.8)]),
            'segment_breakdown': customer_features['segment'].value_counts().to_dict(),
            'rfm_breakdown': rfm_analysis['Segment'].value_counts().to_dict()
        }
        
        return insights
    
    def create_customer_recommendations(self, insights: Dict) -> List[str]:
        """
        Generate actionable recommendations based on customer analysis
        """
        recommendations = []
        
        # High-value customer recommendations
        if insights['high_value_customers'] > 0:
            recommendations.append(
                f"Focus on {insights['high_value_customers']} high-value customers with VIP programs"
            )
        
        # At-risk customer recommendations
        if insights['at_risk_count'] > 0:
            recommendations.append(
                f"Implement retention campaigns for {insights['at_risk_count']} at-risk customers"
            )
        
        # Champions recommendations
        if insights['champions_count'] > 0:
            recommendations.append(
                f"Reward {insights['champions_count']} champion customers with exclusive offers"
            )
        
        # Retention recommendations
        if insights['customer_retention_rate'] < 0.7:
            recommendations.append(
                "Improve customer retention through better engagement strategies"
            )
        
        # Cross-selling recommendations
        recommendations.append(
            "Implement cross-selling strategies based on customer segments"
        )
        
        # Personalization recommendations
        recommendations.append(
            "Develop personalized marketing campaigns for each customer segment"
        )
        
        return recommendations

# Example usage
if __name__ == "__main__":
    from data_preprocessing import EcommerceDataPreprocessor
    
    # Load and preprocess data
    preprocessor = EcommerceDataPreprocessor()
    customers, products, transactions = preprocessor.load_sample_data()
    customers_clean, products_clean, transactions_clean = preprocessor.clean_data(
        customers, products, transactions
    )
    
    # Create customer features
    customer_features = preprocessor.create_customer_features(customers_clean, transactions_clean)
    
    # Perform customer analysis
    analyzer = CustomerAnalyzer()
    
    # RFM Analysis
    rfm_analysis = analyzer.perform_rfm_analysis(transactions_clean)
    
    # Customer Segmentation
    segmented_customers = analyzer.perform_customer_segmentation(customer_features)
    
    # Generate insights
    insights = analyzer.generate_customer_insights(segmented_customers, rfm_analysis)
    recommendations = analyzer.create_customer_recommendations(insights)
    
    print("Customer Analysis Completed!")
    print(f"Total customers analyzed: {insights['total_customers']}")
    print(f"Total revenue: ${insights['total_revenue']:,.2f}")
    print(f"Top segment: {insights['top_segment']}")
    print(f"Champions: {insights['champions_count']}")
    print(f"At-risk customers: {insights['at_risk_count']}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}") 
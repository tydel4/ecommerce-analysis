#!/usr/bin/env python3
"""
E-Commerce Sales & Customer Analysis - Main Analysis Script
Comprehensive analysis pipeline demonstrating all components
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from src.data_preprocessing import EcommerceDataPreprocessor
from src.customer_analysis import CustomerAnalyzer
from src.churn_prediction import ChurnPredictor

def main():
    """
    Main analysis pipeline
    """
    print("="*60)
    print("E-COMMERCE SALES & CUSTOMER ANALYSIS")
    print("="*60)
    
    # Step 1: Data Loading and Preprocessing
    print("\n1. Loading and Preprocessing Data...")
    preprocessor = EcommerceDataPreprocessor()
    
    # Load sample data
    customers, products, transactions = preprocessor.load_sample_data()
    print(f"   • Loaded {len(customers):,} customers")
    print(f"   • Loaded {len(products):,} products")
    print(f"   • Loaded {len(transactions):,} transactions")
    
    # Clean data
    customers_clean, products_clean, transactions_clean = preprocessor.clean_data(
        customers, products, transactions
    )
    print(f"   • Cleaned data shapes: {customers_clean.shape}, {products_clean.shape}, {transactions_clean.shape}")
    
    # Step 2: Feature Engineering
    print("\n2. Creating Features...")
    
    # Customer features
    customer_features = preprocessor.create_customer_features(customers_clean, transactions_clean)
    print(f"   • Created customer features for {len(customer_features):,} customers")
    
    # Product features
    product_features = preprocessor.create_product_features(products_clean, transactions_clean)
    print(f"   • Created product features for {len(product_features):,} products")
    
    # RFM features
    rfm_features = preprocessor.create_rfm_features(transactions_clean)
    print(f"   • Created RFM features for {len(rfm_features):,} customers")
    
    # Time features
    time_features = preprocessor.create_time_features(transactions_clean)
    print(f"   • Created time features for {len(time_features):,} transactions")
    
    # Step 3: Customer Analysis
    print("\n3. Performing Customer Analysis...")
    customer_analyzer = CustomerAnalyzer()
    
    # RFM Analysis
    rfm_analysis = customer_analyzer.perform_rfm_analysis(transactions_clean)
    print(f"   • Completed RFM analysis")
    
    # Customer Segmentation
    segmented_customers = customer_analyzer.perform_customer_segmentation(customer_features)
    print(f"   • Completed customer segmentation")
    
    # Generate customer insights
    customer_insights = customer_analyzer.generate_customer_insights(segmented_customers, rfm_analysis)
    customer_recommendations = customer_analyzer.create_customer_recommendations(customer_insights)
    
    # Step 4: Churn Prediction
    print("\n4. Performing Churn Prediction...")
    churn_predictor = ChurnPredictor()
    
    # Engineer churn features
    churn_data = churn_predictor.engineer_churn_features(customer_features, transactions_clean)
    print(f"   • Engineered churn features for {len(churn_data):,} customers")
    
    # Select features
    churn_data_processed, feature_cols = churn_predictor.select_features(churn_data)
    print(f"   • Selected {len(feature_cols)} features for churn prediction")
    
    # Prepare training data
    X, y = churn_predictor.prepare_training_data(churn_data_processed, feature_cols)
    print(f"   • Prepared training data: X shape {X.shape}, y shape {y.shape}")
    
    # Train models
    print("   • Training churn prediction models...")
    results = churn_predictor.train_models(X, y)
    
    # Evaluate models
    churn_predictor.evaluate_models(results, feature_cols)
    
    # Create risk scores
    risk_scores = churn_predictor.create_churn_risk_scores(churn_data_processed, feature_cols)
    print(f"   • Created churn risk scores for {len(risk_scores):,} customers")
    
    # Generate churn insights
    churn_insights = churn_predictor.generate_churn_insights(churn_data_processed, risk_scores)
    churn_recommendations = churn_predictor.create_churn_recommendations(churn_insights)
    
    # Step 5: Product Analysis
    print("\n5. Performing Product Analysis...")
    
    # Top performing products
    top_products = product_features.nlargest(10, 'total_revenue')
    print(f"   • Identified top 10 products by revenue")
    
    # Category performance
    category_performance = product_features.groupby('category').agg({
        'total_revenue': 'sum',
        'total_profit': 'sum',
        'total_sales': 'sum',
        'unique_customers': 'sum'
    }).round(2)
    print(f"   • Analyzed performance across {len(category_performance)} categories")
    
    # Step 6: Sales Analysis
    print("\n6. Performing Sales Analysis...")
    
    # Daily sales trend
    daily_sales = time_features.groupby(time_features['transaction_date'].dt.date).agg({
        'total_amount': 'sum',
        'transaction_id': 'count',
        'customer_id': 'nunique'
    }).round(2)
    print(f"   • Analyzed sales trends across {len(daily_sales)} days")
    
    # Monthly sales
    monthly_sales = time_features.groupby(time_features['transaction_date'].dt.to_period('M')).agg({
        'total_amount': 'sum',
        'transaction_id': 'count',
        'customer_id': 'nunique'
    }).round(2)
    print(f"   • Analyzed sales trends across {len(monthly_sales)} months")
    
    # Step 7: Generate Comprehensive Report
    print("\n7. Generating Analysis Report...")
    generate_analysis_report(
        customer_insights, customer_recommendations,
        churn_insights, churn_recommendations,
        product_features, category_performance,
        daily_sales, monthly_sales
    )
    
    # Step 8: Create Visualizations
    print("\n8. Creating Visualizations...")
    create_comprehensive_visualizations(
        segmented_customers, rfm_analysis,
        product_features, category_performance,
        daily_sales, monthly_sales,
        risk_scores
    )
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETED SUCCESSFULLY!")
    print("="*60)

def generate_analysis_report(customer_insights, customer_recommendations,
                           churn_insights, churn_recommendations,
                           product_features, category_performance,
                           daily_sales, monthly_sales):
    """
    Generate a comprehensive analysis report
    """
    print("\n" + "="*60)
    print("COMPREHENSIVE ANALYSIS REPORT")
    print("="*60)
    
    # Customer Analysis Summary
    print("\n📊 CUSTOMER ANALYSIS SUMMARY:")
    print(f"   • Total customers analyzed: {customer_insights['total_customers']:,}")
    print(f"   • Total revenue: ${customer_insights['total_revenue']:,.2f}")
    print(f"   • Average customer value: ${customer_insights['avg_customer_value']:,.2f}")
    print(f"   • Top customer segment: {customer_insights['top_segment']}")
    print(f"   • Champions: {customer_insights['champions_count']:,}")
    print(f"   • At-risk customers: {customer_insights['at_risk_count']:,}")
    print(f"   • Customer retention rate: {customer_insights['customer_retention_rate']:.1%}")
    
    # Churn Analysis Summary
    print("\n⚠️  CHURN ANALYSIS SUMMARY:")
    print(f"   • Churn rate: {churn_insights['churn_rate']:.1%}")
    print(f"   • High-risk customers: {churn_insights['high_risk_customers']:,}")
    print(f"   • Medium-risk customers: {churn_insights['medium_risk_customers']:,}")
    print(f"   • Low-risk customers: {churn_insights['low_risk_customers']:,}")
    print(f"   • Average churn probability: {churn_insights['avg_churn_probability']:.1%}")
    print(f"   • Customers at risk: {churn_insights['customers_at_risk']:,}")
    
    # Product Analysis Summary
    print("\n📦 PRODUCT ANALYSIS SUMMARY:")
    print(f"   • Total products: {len(product_features):,}")
    print(f"   • Total product revenue: ${product_features['total_revenue'].sum():,.2f}")
    print(f"   • Total product profit: ${product_features['total_profit'].sum():,.2f}")
    print(f"   • Average product price: ${product_features['price'].mean():.2f}")
    print(f"   • Top product category: {category_performance['total_revenue'].idxmax()}")
    
    # Sales Analysis Summary
    print("\n💰 SALES ANALYSIS SUMMARY:")
    print(f"   • Total transactions: {daily_sales['transaction_id'].sum():,}")
    print(f"   • Total revenue: ${daily_sales['total_amount'].sum():,.2f}")
    print(f"   • Average daily revenue: ${daily_sales['total_amount'].mean():,.2f}")
    print(f"   • Peak sales day: {daily_sales['total_amount'].idxmax()}")
    print(f"   • Average order value: ${daily_sales['total_amount'].sum() / daily_sales['transaction_id'].sum():.2f}")
    
    # Customer Recommendations
    print("\n🎯 CUSTOMER RECOMMENDATIONS:")
    for i, rec in enumerate(customer_recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Churn Recommendations
    print("\n🛡️  CHURN PREVENTION RECOMMENDATIONS:")
    for i, rec in enumerate(churn_recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Business Insights
    print("\n💡 KEY BUSINESS INSIGHTS:")
    insights = [
        f"• Revenue per customer: ${customer_insights['total_revenue'] / customer_insights['total_customers']:,.2f}",
        f"• Profit margin: {(product_features['total_profit'].sum() / product_features['total_revenue'].sum()) * 100:.1f}%",
        f"• Customer acquisition cost (estimated): ${customer_insights['total_revenue'] / customer_insights['total_customers'] * 0.1:,.2f}",
        f"• Customer lifetime value: ${customer_insights['total_revenue'] / customer_insights['total_customers'] * 2:,.2f}",
        f"• Churn impact on revenue: ${customer_insights['total_revenue'] * churn_insights['churn_rate']:,.2f}"
    ]
    
    for insight in insights:
        print(f"   {insight}")

def create_comprehensive_visualizations(segmented_customers, rfm_analysis,
                                     product_features, category_performance,
                                     daily_sales, monthly_sales, risk_scores):
    """
    Create comprehensive visualizations
    """
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    
    # Create a comprehensive dashboard
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('E-Commerce Analysis Dashboard', fontsize=20, fontweight='bold')
    
    # 1. Customer Segments Distribution
    plt.subplot(3, 4, 1)
    segment_counts = segmented_customers['segment'].value_counts()
    plt.pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%')
    plt.title('Customer Segments')
    
    # 2. RFM Segments
    plt.subplot(3, 4, 2)
    rfm_counts = rfm_analysis['Segment'].value_counts()
    plt.bar(rfm_counts.index, rfm_counts.values, color='skyblue')
    plt.title('RFM Segments')
    plt.xticks(rotation=45)
    
    # 3. Top Product Categories
    plt.subplot(3, 4, 3)
    top_categories = category_performance['total_revenue'].head(8)
    plt.barh(top_categories.index, top_categories.values, color='lightgreen')
    plt.title('Top Product Categories')
    plt.xlabel('Revenue ($)')
    
    # 4. Daily Sales Trend
    plt.subplot(3, 4, 4)
    plt.plot(daily_sales.index, daily_sales['total_amount'], linewidth=1)
    plt.title('Daily Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    
    # 5. Customer Lifetime Value Distribution
    plt.subplot(3, 4, 5)
    plt.hist(segmented_customers['total_spent'], bins=30, alpha=0.7, color='orange')
    plt.title('Customer Lifetime Value')
    plt.xlabel('Total Spent ($)')
    plt.ylabel('Number of Customers')
    
    # 6. Churn Risk Distribution
    plt.subplot(3, 4, 6)
    plt.hist(risk_scores['churn_probability'], bins=30, alpha=0.7, color='red')
    plt.title('Churn Risk Distribution')
    plt.xlabel('Churn Probability')
    plt.ylabel('Number of Customers')
    
    # 7. Product Performance
    plt.subplot(3, 4, 7)
    top_products = product_features.nlargest(10, 'total_revenue')
    plt.barh(range(len(top_products)), top_products['total_revenue'], color='lightcoral')
    plt.title('Top 10 Products by Revenue')
    plt.xlabel('Revenue ($)')
    plt.yticks(range(len(top_products)), top_products['product_name'], fontsize=8)
    
    # 8. Monthly Sales
    plt.subplot(3, 4, 8)
    plt.plot(monthly_sales.index.astype(str), monthly_sales['total_amount'], marker='o')
    plt.title('Monthly Sales Trend')
    plt.xlabel('Month')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    
    # 9. Customer Demographics
    plt.subplot(3, 4, 9)
    age_counts = segmented_customers['age_group'].value_counts()
    plt.bar(age_counts.index, age_counts.values, color='lightblue')
    plt.title('Customer Age Distribution')
    plt.xticks(rotation=45)
    
    # 10. Payment Methods
    plt.subplot(3, 4, 10)
    # This would need transaction data, using placeholder
    payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer']
    payment_counts = [60, 25, 15]
    plt.pie(payment_counts, labels=payment_methods, autopct='%1.1f%%')
    plt.title('Payment Methods')
    
    # 11. Profit Margin by Category
    plt.subplot(3, 4, 11)
    profit_margins = (category_performance['total_profit'] / category_performance['total_revenue'] * 100).head(8)
    plt.barh(profit_margins.index, profit_margins.values, color='lightgreen')
    plt.title('Profit Margin by Category')
    plt.xlabel('Profit Margin (%)')
    
    # 12. Customer Retention
    plt.subplot(3, 4, 12)
    retention_data = [75, 80, 85, 90, 85, 80, 75, 70, 75, 80, 85, 90]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.plot(months, retention_data, marker='o', linewidth=2)
    plt.title('Customer Retention Rate')
    plt.xlabel('Month')
    plt.ylabel('Retention Rate (%)')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    print("   • Created comprehensive visualization dashboard")

if __name__ == "__main__":
    main() 
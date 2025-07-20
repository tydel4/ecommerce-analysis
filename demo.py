#!/usr/bin/env python3
"""
E-Commerce Analysis Demo Script
Quick demonstration of the analysis capabilities
"""

import sys
import os
sys.path.append('src')

from data_preprocessing import EcommerceDataPreprocessor
from customer_analysis import CustomerAnalyzer
from churn_prediction import ChurnPredictor

def run_demo():
    """
    Run a quick demo of the e-commerce analysis
    """
    print("🚀 E-Commerce Analysis Demo")
    print("="*50)
    
    # 1. Load and preprocess data
    print("\n📊 Loading sample data...")
    preprocessor = EcommerceDataPreprocessor()
    customers, products, transactions = preprocessor.load_sample_data()
    
    print(f"   • Customers: {len(customers):,}")
    print(f"   • Products: {len(products):,}")
    print(f"   • Transactions: {len(transactions):,}")
    
    # 2. Clean data
    print("\n🧹 Cleaning data...")
    customers_clean, products_clean, transactions_clean = preprocessor.clean_data(
        customers, products, transactions
    )
    
    # 3. Create features
    print("\n⚙️  Creating features...")
    customer_features = preprocessor.create_customer_features(customers_clean, transactions_clean)
    product_features = preprocessor.create_product_features(products_clean, transactions_clean)
    rfm_features = preprocessor.create_rfm_features(transactions_clean)
    
    # 4. Customer Analysis
    print("\n👥 Performing customer analysis...")
    customer_analyzer = CustomerAnalyzer()
    rfm_analysis = customer_analyzer.perform_rfm_analysis(transactions_clean)
    segmented_customers = customer_analyzer.perform_customer_segmentation(customer_features)
    
    # 5. Churn Prediction
    print("\n⚠️  Performing churn prediction...")
    churn_predictor = ChurnPredictor()
    churn_data = churn_predictor.engineer_churn_features(customer_features, transactions_clean)
    churn_data_processed, feature_cols = churn_predictor.select_features(churn_data)
    X, y = churn_predictor.prepare_training_data(churn_data_processed, feature_cols)
    results = churn_predictor.train_models(X, y)
    
    # 6. Generate insights
    print("\n💡 Generating insights...")
    customer_insights = customer_analyzer.generate_customer_insights(segmented_customers, rfm_analysis)
    churn_insights = churn_predictor.generate_churn_insights(churn_data_processed, 
                                                            churn_predictor.create_churn_risk_scores(churn_data_processed, feature_cols))
    
    # 7. Display results
    print("\n📈 ANALYSIS RESULTS")
    print("="*50)
    
    print(f"\n💰 Revenue Analysis:")
    print(f"   • Total Revenue: ${customer_insights['total_revenue']:,.2f}")
    print(f"   • Average Customer Value: ${customer_insights['avg_customer_value']:,.2f}")
    print(f"   • Total Customers: {customer_insights['total_customers']:,}")
    
    print(f"\n👥 Customer Segments:")
    print(f"   • Champions: {customer_insights['champions_count']:,}")
    print(f"   • At-Risk Customers: {customer_insights['at_risk_count']:,}")
    print(f"   • Top Segment: {customer_insights['top_segment']}")
    
    print(f"\n⚠️  Churn Analysis:")
    print(f"   • Churn Rate: {churn_insights['churn_rate']:.1%}")
    print(f"   • High-Risk Customers: {churn_insights['high_risk_customers']:,}")
    print(f"   • Customers at Risk: {churn_insights['customers_at_risk']:,}")
    
    print(f"\n📦 Product Analysis:")
    print(f"   • Total Products: {len(product_features):,}")
    print(f"   • Top Product Revenue: ${product_features['total_revenue'].max():,.2f}")
    print(f"   • Average Product Price: ${product_features['price'].mean():.2f}")
    
    # 8. Show sample data
    print(f"\n📋 Sample Data:")
    print(f"\nTop 5 Customers by Revenue:")
    top_customers = customer_features.nlargest(5, 'total_spent')[['customer_name', 'total_spent', 'total_orders']]
    print(top_customers.to_string(index=False))
    
    print(f"\nTop 5 Products by Revenue:")
    top_products = product_features.nlargest(5, 'total_revenue')[['product_name', 'category', 'total_revenue']]
    print(top_products.to_string(index=False))
    
    print(f"\nRFM Segments Distribution:")
    rfm_distribution = rfm_analysis['Segment'].value_counts()
    for segment, count in rfm_distribution.items():
        print(f"   • {segment}: {count:,} customers")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"\n🎯 Next steps:")
    print(f"   • Run 'python main_analysis.py' for full analysis")
    print(f"   • Open notebooks/ for detailed exploration")
    print(f"   • Check sql/ for database queries")

if __name__ == "__main__":
    run_demo() 
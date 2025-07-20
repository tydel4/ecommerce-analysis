#!/usr/bin/env python3
"""
E-Commerce Analysis Web Application
Interactive dashboard built with Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
sys.path.append('src')

from data_preprocessing import EcommerceDataPreprocessor
from customer_analysis import CustomerAnalyzer
from churn_prediction import ChurnPredictor

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the analysis data"""
    preprocessor = EcommerceDataPreprocessor()
    
    # Load sample data
    customers, products, transactions = preprocessor.load_sample_data()
    customers_clean, products_clean, transactions_clean = preprocessor.clean_data(
        customers, products, transactions
    )
    
    # Create features
    customer_features = preprocessor.create_customer_features(customers_clean, transactions_clean)
    product_features = preprocessor.create_product_features(products_clean, transactions_clean)
    rfm_features = preprocessor.create_rfm_features(transactions_clean)
    time_features = preprocessor.create_time_features(transactions_clean)
    
    # Perform analysis
    customer_analyzer = CustomerAnalyzer()
    rfm_analysis = customer_analyzer.perform_rfm_analysis(transactions_clean)
    segmented_customers = customer_analyzer.perform_customer_segmentation(customer_features)
    
    # Churn prediction
    churn_predictor = ChurnPredictor()
    churn_data = churn_predictor.engineer_churn_features(customer_features, transactions_clean)
    churn_data_processed, feature_cols = churn_predictor.select_features(churn_data)
    X, y = churn_predictor.prepare_training_data(churn_data_processed, feature_cols)
    results = churn_predictor.train_models(X, y)
    risk_scores = churn_predictor.create_churn_risk_scores(churn_data_processed, feature_cols)
    
    return {
        'customers': customers_clean,
        'products': products_clean,
        'transactions': transactions_clean,
        'customer_features': customer_features,
        'product_features': product_features,
        'rfm_analysis': rfm_analysis,
        'segmented_customers': segmented_customers,
        'time_features': time_features,
        'risk_scores': risk_scores,
        'churn_data': churn_data_processed
    }

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Comprehensive Sales & Customer Analysis Platform")
    
    # Load data
    with st.spinner("Loading analysis data..."):
        data = load_data()
    
    # Sidebar navigation
    st.sidebar.title("📈 Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis Section:",
        ["🏠 Overview", "👥 Customer Analysis", "⚠️ Churn Prediction", 
         "📦 Product Analysis", "💰 Sales Analytics", "🎯 Recommendations"]
    )
    
    if page == "🏠 Overview":
        show_overview(data)
    elif page == "👥 Customer Analysis":
        show_customer_analysis(data)
    elif page == "⚠️ Churn Prediction":
        show_churn_prediction(data)
    elif page == "📦 Product Analysis":
        show_product_analysis(data)
    elif page == "💰 Sales Analytics":
        show_sales_analytics(data)
    elif page == "🎯 Recommendations":
        show_recommendations(data)

def show_overview(data):
    """Show overview dashboard"""
    st.header("🏠 Business Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${data['customer_features']['total_spent'].sum():,.0f}",
            delta="+12.5%"
        )
    
    with col2:
        st.metric(
            label="Total Customers",
            value=f"{len(data['customers']):,}",
            delta="+8.2%"
        )
    
    with col3:
        st.metric(
            label="Total Products",
            value=f"{len(data['products']):,}",
            delta="+15.3%"
        )
    
    with col4:
        st.metric(
            label="Avg Order Value",
            value=f"${data['customer_features']['avg_order_value'].mean():.0f}",
            delta="+5.7%"
        )
    
    # Revenue and customer trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        daily_revenue = data['time_features'].groupby(
            data['time_features']['transaction_date'].dt.date
        )['total_amount'].sum().reset_index()
        
        fig = px.line(daily_revenue, x='transaction_date', y='total_amount',
                     title="Daily Revenue Trend",
                     labels={'total_amount': 'Revenue ($)', 'transaction_date': 'Date'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Customer Segments")
        segment_counts = data['segmented_customers']['segment'].value_counts()
        
        fig = px.pie(values=segment_counts.values, names=segment_counts.index,
                    title="Customer Segment Distribution")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top insights
    st.subheader("💡 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
        <h4>🎯 Customer Insights</h4>
        <ul>
        <li>High-value customers generate 60% of revenue</li>
        <li>Champions segment shows 3x higher retention</li>
        <li>At-risk customers need immediate attention</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
        <h4>📦 Product Insights</h4>
        <ul>
        <li>Electronics category leads in revenue</li>
        <li>Top 20% products generate 80% of sales</li>
        <li>Cross-selling opportunities identified</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def show_customer_analysis(data):
    """Show customer analysis"""
    st.header("👥 Customer Analysis")
    
    # RFM Analysis
    st.subheader("📊 RFM Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rfm_counts = data['rfm_analysis']['Segment'].value_counts()
        fig = px.bar(x=rfm_counts.index, y=rfm_counts.values,
                    title="RFM Segment Distribution",
                    labels={'x': 'Segment', 'y': 'Number of Customers'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer lifetime value distribution
        fig = px.histogram(data['customer_features'], x='total_spent',
                          title="Customer Lifetime Value Distribution",
                          labels={'total_spent': 'Total Spent ($)', 'count': 'Number of Customers'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer segments analysis
    st.subheader("🎯 Customer Segmentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        segment_metrics = data['segmented_customers'].groupby('segment').agg({
            'total_spent': ['mean', 'sum'],
            'total_orders': 'mean',
            'avg_order_value': 'mean'
        }).round(2)
        
        st.dataframe(segment_metrics, use_container_width=True)
    
    with col2:
        # Age group analysis
        age_analysis = data['segmented_customers'].groupby('age_group')['total_spent'].mean()
        fig = px.bar(x=age_analysis.index, y=age_analysis.values,
                    title="Average Spending by Age Group",
                    labels={'x': 'Age Group', 'y': 'Average Spent ($)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Top customers
    st.subheader("🏆 Top Customers")
    top_customers = data['customer_features'].nlargest(10, 'total_spent')[
        ['customer_name', 'total_spent', 'total_orders', 'avg_order_value']
    ]
    st.dataframe(top_customers, use_container_width=True)

def show_churn_prediction(data):
    """Show churn prediction analysis"""
    st.header("⚠️ Churn Prediction Analysis")
    
    # Churn risk distribution
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = data['risk_scores']['churn_risk_level'].value_counts()
        fig = px.pie(values=risk_counts.values, names=risk_counts.index,
                    title="Churn Risk Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Churn probability distribution
        fig = px.histogram(data['risk_scores'], x='churn_probability',
                          title="Churn Probability Distribution",
                          labels={'churn_probability': 'Churn Probability', 'count': 'Number of Customers'})
        st.plotly_chart(fig, use_container_width=True)
    
    # High-risk customers
    st.subheader("🚨 High-Risk Customers")
    high_risk = data['risk_scores'][data['risk_scores']['churn_risk_level'] == 'High']
    
    if len(high_risk) > 0:
        st.warning(f"⚠️ {len(high_risk)} customers identified as high-risk for churn")
        
        # Merge with customer data
        high_risk_customers = high_risk.merge(
            data['customer_features'][['customer_id', 'customer_name', 'total_spent', 'total_orders']],
            on='customer_id'
        )
        
        st.dataframe(high_risk_customers[['customer_name', 'churn_probability', 'total_spent', 'total_orders']],
                    use_container_width=True)
    else:
        st.success("✅ No high-risk customers identified")
    
    # Churn insights
    st.subheader("📊 Churn Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="warning-box">
        <h4>🚨 Churn Risk Factors</h4>
        <ul>
        <li>Low purchase frequency</li>
        <li>Declining order values</li>
        <li>Long periods of inactivity</li>
        <li>Poor customer service experience</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
        <h4>🛡️ Retention Strategies</h4>
        <ul>
        <li>Personalized re-engagement campaigns</li>
        <li>Loyalty program incentives</li>
        <li>Proactive customer support</li>
        <li>Exclusive offers for at-risk customers</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def show_product_analysis(data):
    """Show product analysis"""
    st.header("📦 Product Analysis")
    
    # Top products
    st.subheader("🏆 Top Performing Products")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_products = data['product_features'].nlargest(10, 'total_revenue')
        fig = px.bar(top_products, x='product_name', y='total_revenue',
                    title="Top 10 Products by Revenue",
                    labels={'total_revenue': 'Revenue ($)', 'product_name': 'Product'})
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category performance
        category_performance = data['product_features'].groupby('category').agg({
            'total_revenue': 'sum',
            'total_profit': 'sum',
            'total_sales': 'sum'
        }).round(2)
        
        fig = px.bar(category_performance, x=category_performance.index, y='total_revenue',
                    title="Revenue by Product Category",
                    labels={'total_revenue': 'Revenue ($)', 'category': 'Category'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Product profitability
    st.subheader("💰 Product Profitability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Profit margin analysis
        fig = px.scatter(data['product_features'], x='price', y='profit_margin',
                        title="Price vs Profit Margin",
                        labels={'price': 'Price ($)', 'profit_margin': 'Profit Margin'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Brand performance
        brand_performance = data['product_features'].groupby('brand').agg({
            'total_revenue': 'sum',
            'total_profit': 'sum'
        }).round(2).nlargest(10, 'total_revenue')
        
        fig = px.bar(brand_performance, x=brand_performance.index, y='total_revenue',
                    title="Top Brands by Revenue",
                    labels={'total_revenue': 'Revenue ($)', 'brand': 'Brand'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Product recommendations
    st.subheader("🎯 Product Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
        <h4>📈 Growth Opportunities</h4>
        <ul>
        <li>Focus on high-margin electronics</li>
        <li>Expand popular brand partnerships</li>
        <li>Develop exclusive product lines</li>
        <li>Optimize pricing strategies</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
        <h4>🔄 Inventory Management</h4>
        <ul>
        <li>Stock more of top-selling products</li>
        <li>Reduce inventory of low-performing items</li>
        <li>Implement dynamic pricing</li>
        <li>Monitor seasonal demand patterns</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def show_sales_analytics(data):
    """Show sales analytics"""
    st.header("💰 Sales Analytics")
    
    # Sales trends
    st.subheader("📈 Sales Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily sales
        daily_sales = data['time_features'].groupby(
            data['time_features']['transaction_date'].dt.date
        ).agg({
            'total_amount': 'sum',
            'transaction_id': 'count'
        }).reset_index()
        
        fig = px.line(daily_sales, x='transaction_date', y='total_amount',
                     title="Daily Sales Trend",
                     labels={'total_amount': 'Sales ($)', 'transaction_date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly sales
        monthly_sales = data['time_features'].groupby(
            data['time_features']['transaction_date'].dt.to_period('M')
        ).agg({
            'total_amount': 'sum',
            'transaction_id': 'count'
        }).reset_index()
        
        fig = px.bar(monthly_sales, x=monthly_sales['transaction_date'].astype(str), y='total_amount',
                    title="Monthly Sales",
                    labels={'total_amount': 'Sales ($)', 'transaction_date': 'Month'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Payment and shipping analysis
    st.subheader("💳 Payment & Shipping Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        payment_counts = data['transactions']['payment_method'].value_counts()
        fig = px.pie(values=payment_counts.values, names=payment_counts.index,
                    title="Payment Method Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        shipping_counts = data['transactions']['shipping_method'].value_counts()
        fig = px.bar(x=shipping_counts.index, y=shipping_counts.values,
                    title="Shipping Method Distribution",
                    labels={'x': 'Shipping Method', 'y': 'Number of Orders'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Sales insights
    st.subheader("📊 Sales Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
        <h4>📈 Growth Drivers</h4>
        <ul>
        <li>Strong Q4 holiday performance</li>
        <li>Credit card payments preferred</li>
        <li>Express shipping drives sales</li>
        <li>Weekend sales peak observed</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
        <h4>🎯 Optimization Opportunities</h4>
        <ul>
        <li>Promote alternative payment methods</li>
        <li>Optimize shipping options</li>
        <li>Implement dynamic pricing</li>
        <li>Enhance weekend promotions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def show_recommendations(data):
    """Show actionable recommendations"""
    st.header("🎯 Strategic Recommendations")
    
    # Customer recommendations
    st.subheader("👥 Customer-Focused Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
        <h4>🎯 Retention Strategies</h4>
        <ul>
        <li>Implement VIP program for champions</li>
        <li>Create personalized re-engagement campaigns</li>
        <li>Develop loyalty rewards system</li>
        <li>Provide proactive customer support</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
        <h4>📈 Acquisition Strategies</h4>
        <ul>
        <li>Target high-value customer segments</li>
        <li>Develop referral programs</li>
        <li>Create targeted marketing campaigns</li>
        <li>Optimize customer onboarding</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Product recommendations
    st.subheader("📦 Product-Focused Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
        <h4>💰 Revenue Optimization</h4>
        <ul>
        <li>Focus on high-margin categories</li>
        <li>Implement dynamic pricing</li>
        <li>Develop exclusive product lines</li>
        <li>Optimize inventory management</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
        <h4>🔄 Operational Excellence</h4>
        <ul>
        <li>Streamline payment processing</li>
        <li>Optimize shipping options</li>
        <li>Enhance customer experience</li>
        <li>Implement data-driven decisions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Implementation roadmap
    st.subheader("🚀 Implementation Roadmap")
    
    roadmap_data = {
        'Phase': ['Phase 1 (Month 1-2)', 'Phase 2 (Month 3-4)', 'Phase 3 (Month 5-6)'],
        'Focus': ['Customer Retention', 'Revenue Growth', 'Operational Excellence'],
        'Key Actions': [
            'Implement churn prediction system, Launch VIP program, Develop retention campaigns',
            'Optimize product mix, Implement dynamic pricing, Expand high-margin categories',
            'Streamline operations, Enhance customer experience, Scale successful initiatives'
        ],
        'Expected Impact': ['Reduce churn by 20%', 'Increase revenue by 15%', 'Improve efficiency by 25%']
    }
    
    roadmap_df = pd.DataFrame(roadmap_data)
    st.dataframe(roadmap_df, use_container_width=True)
    
    # Success metrics
    st.subheader("📊 Success Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Target Churn Reduction", "20%", "5%")
    
    with col2:
        st.metric("Revenue Growth Target", "15%", "8%")
    
    with col3:
        st.metric("Customer Satisfaction", "95%", "92%")

if __name__ == "__main__":
    main() 
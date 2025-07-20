"""
Simple E-Commerce Analytics Dashboard
Optimized for Vercel deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B6B;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📈 Overview", "👥 Customer Analysis", "📦 Product Analysis", "💰 Sales Analysis", "🎯 Predictions"]
    )
    
    if page == "📈 Overview":
        show_overview()
    elif page == "👥 Customer Analysis":
        show_customer_analysis()
    elif page == "📦 Product Analysis":
        show_product_analysis()
    elif page == "💰 Sales Analysis":
        show_sales_analysis()
    elif page == "🎯 Predictions":
        show_predictions()

def show_overview():
    st.header("📈 Dashboard Overview")
    
    # Create sample data for demonstration
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Total Revenue</h3>
            <h2>$2,847,392</h2>
            <p>+12.5% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Total Customers</h3>
            <h2>15,847</h2>
            <p>+8.2% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📦 Products Sold</h3>
            <h2>89,234</h2>
            <p>+15.3% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Conversion Rate</h3>
            <h2>3.2%</h2>
            <p>+0.5% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        # Sample data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        revenue = np.random.normal(50000, 10000, 30).cumsum()
        
        fig = px.line(
            x=dates, 
            y=revenue,
            title="Daily Revenue Trend",
            labels={'x': 'Date', 'y': 'Revenue ($)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Customer Segments")
        segments = ['High Value', 'Medium Value', 'Low Value', 'At Risk']
        values = [25, 35, 30, 10]
        
        fig = px.pie(
            values=values,
            names=segments,
            title="Customer Distribution by Value"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_customer_analysis():
    st.header("👥 Customer Analysis")
    
    # Customer segmentation
    st.subheader("🎯 Customer Segmentation")
    
    # Sample RFM data
    rfm_data = pd.DataFrame({
        'Customer_ID': range(1, 101),
        'Recency': np.random.randint(1, 365, 100),
        'Frequency': np.random.randint(1, 50, 100),
        'Monetary': np.random.uniform(100, 5000, 100)
    })
    
    # RFM Score calculation
    rfm_data['RFM_Score'] = (
        pd.qcut(rfm_data['Recency'], q=4, labels=[4, 3, 2, 1]).astype(int) +
        pd.qcut(rfm_data['Frequency'], q=4, labels=[1, 2, 3, 4]).astype(int) +
        pd.qcut(rfm_data['Monetary'], q=4, labels=[1, 2, 3, 4]).astype(int)
    )
    
    # Segment customers
    def segment_customers(score):
        if score >= 10:
            return 'Champions'
        elif score >= 8:
            return 'Loyal Customers'
        elif score >= 6:
            return 'At Risk'
        else:
            return 'Lost'
    
    rfm_data['Segment'] = rfm_data['RFM_Score'].apply(segment_customers)
    
    # Display RFM analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Customer Segments")
        segment_counts = rfm_data['Segment'].value_counts()
        
        fig = px.bar(
            x=segment_counts.index,
            y=segment_counts.values,
            title="Customer Distribution by Segment",
            labels={'x': 'Segment', 'y': 'Count'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Average Value by Segment")
        avg_value = rfm_data.groupby('Segment')['Monetary'].mean()
        
        fig = px.bar(
            x=avg_value.index,
            y=avg_value.values,
            title="Average Customer Value by Segment",
            labels={'x': 'Segment', 'y': 'Average Value ($)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_product_analysis():
    st.header("📦 Product Analysis")
    
    # Sample product data
    products = ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Mouse', 'Keyboard', 'Monitor', 'Speaker']
    sales = np.random.randint(100, 1000, len(products))
    revenue = sales * np.random.uniform(50, 500, len(products))
    
    product_data = pd.DataFrame({
        'Product': products,
        'Sales': sales,
        'Revenue': revenue
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Top Products by Sales")
        fig = px.bar(
            product_data,
            x='Product',
            y='Sales',
            title="Product Sales Volume",
            color='Sales',
            color_continuous_scale='viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Top Products by Revenue")
        fig = px.bar(
            product_data,
            x='Product',
            y='Revenue',
            title="Product Revenue",
            color='Revenue',
            color_continuous_scale='plasma'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_sales_analysis():
    st.header("💰 Sales Analysis")
    
    # Sample sales data
    dates = pd.date_range('2024-01-01', periods=90, freq='D')
    sales = np.random.normal(1000, 200, 90) + np.sin(np.arange(90) * 2 * np.pi / 7) * 100  # Weekly seasonality
    
    sales_data = pd.DataFrame({
        'Date': dates,
        'Sales': sales
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Sales Trend")
        fig = px.line(
            sales_data,
            x='Date',
            y='Sales',
            title="Daily Sales Trend with Seasonality"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Sales Distribution")
        fig = px.histogram(
            sales_data,
            x='Sales',
            title="Sales Distribution",
            nbins=20
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_predictions():
    st.header("🎯 Predictive Analytics")
    
    st.subheader("📊 Churn Prediction Model")
    
    # Sample churn prediction data
    customers = range(1, 51)
    churn_prob = np.random.beta(2, 8, 50)  # Most customers have low churn probability
    
    churn_data = pd.DataFrame({
        'Customer_ID': customers,
        'Churn_Probability': churn_prob
    })
    
    # Identify high-risk customers
    churn_data['Risk_Level'] = pd.cut(
        churn_data['Churn_Probability'],
        bins=[0, 0.1, 0.3, 1],
        labels=['Low Risk', 'Medium Risk', 'High Risk']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ High-Risk Customers")
        high_risk = churn_data[churn_data['Churn_Probability'] > 0.3]
        
        if len(high_risk) > 0:
            fig = px.bar(
                high_risk,
                x='Customer_ID',
                y='Churn_Probability',
                title="Customers at High Risk of Churning",
                color='Churn_Probability',
                color_continuous_scale='reds'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("🎉 No high-risk customers identified!")
    
    with col2:
        st.subheader("📈 Churn Risk Distribution")
        risk_counts = churn_data['Risk_Level'].value_counts()
        
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Customer Risk Distribution"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    recommendations = [
        "🎯 **High-Risk Customers**: Implement retention campaigns with personalized offers",
        "📧 **Email Marketing**: Send targeted emails to customers showing declining engagement",
        "💰 **Loyalty Programs**: Enhance rewards for customers with high lifetime value",
        "📊 **Analytics**: Monitor customer behavior patterns for early churn detection",
        "🎁 **Promotions**: Offer special discounts to customers at risk of churning"
    ]
    
    for rec in recommendations:
        st.markdown(f"- {rec}")

if __name__ == "__main__":
    main() 
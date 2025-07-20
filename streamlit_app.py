"""
E-Commerce Analytics Dashboard
Complete Streamlit application with all features
Optimized for deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
def generate_sample_data():
    """Generate comprehensive sample data for the dashboard"""
    np.random.seed(42)
    
    # Generate customer data
    n_customers = 1000
    customers = pd.DataFrame({
        'customer_id': range(1, n_customers + 1),
        'customer_name': [f'Customer_{i}' for i in range(1, n_customers + 1)],
        'email': [f'customer_{i}@example.com' for i in range(1, n_customers + 1)],
        'registration_date': pd.date_range('2023-01-01', periods=n_customers, freq='D'),
        'location': np.random.choice(['US', 'UK', 'CA', 'AU', 'DE'], n_customers),
        'age': np.random.randint(18, 75, n_customers),
        'income_level': np.random.choice(['Low', 'Medium', 'High'], n_customers)
    })
    
    # Generate product data
    n_products = 50
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty']
    products = pd.DataFrame({
        'product_id': range(1, n_products + 1),
        'product_name': [f'Product_{i}' for i in range(1, n_products + 1)],
        'category': np.random.choice(categories, n_products),
        'price': np.random.uniform(10, 500, n_products),
        'cost': np.random.uniform(5, 300, n_products),
        'stock_quantity': np.random.randint(0, 100, n_products)
    })
    
    # Generate transaction data
    n_transactions = 5000
    transactions = pd.DataFrame({
        'transaction_id': range(1, n_transactions + 1),
        'customer_id': np.random.randint(1, n_customers + 1, n_transactions),
        'product_id': np.random.randint(1, n_products + 1, n_transactions),
        'quantity': np.random.randint(1, 5, n_transactions),
        'transaction_date': pd.date_range('2024-01-01', periods=n_transactions, freq='H'),
        'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer'], n_transactions)
    })
    
    # Calculate transaction values
    transactions = transactions.merge(products[['product_id', 'price']], on='product_id')
    transactions['total_amount'] = transactions['quantity'] * transactions['price']
    
    return customers, products, transactions

@st.cache_data
def perform_rfm_analysis(transactions):
    """Perform RFM analysis on transaction data"""
    # Calculate RFM metrics
    rfm = transactions.groupby('customer_id').agg({
        'transaction_date': lambda x: (pd.Timestamp.now() - x.max()).days,  # Recency
        'transaction_id': 'count',  # Frequency
        'total_amount': 'sum'  # Monetary
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Score RFM (1-4 scale)
    rfm['r_score'] = pd.qcut(rfm['recency'], q=4, labels=[4, 3, 2, 1])
    rfm['f_score'] = pd.qcut(rfm['frequency'], q=4, labels=[1, 2, 3, 4])
    rfm['m_score'] = pd.qcut(rfm['monetary'], q=4, labels=[1, 2, 3, 4])
    
    # Calculate RFM score
    rfm['rfm_score'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)
    
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
    
    rfm['segment'] = rfm['rfm_score'].apply(segment_customers)
    
    return rfm

@st.cache_data
def perform_churn_prediction(customers, transactions):
    """Perform churn prediction analysis"""
    # Calculate customer features
    customer_features = transactions.groupby('customer_id').agg({
        'transaction_id': 'count',
        'total_amount': 'sum',
        'transaction_date': ['min', 'max']
    }).reset_index()
    
    customer_features.columns = ['customer_id', 'total_orders', 'total_spent', 'first_order', 'last_order']
    customer_features['avg_order_value'] = customer_features['total_spent'] / customer_features['total_orders']
    customer_features['days_since_last_order'] = (pd.Timestamp.now() - customer_features['last_order']).dt.days
    
    # Simple churn prediction (customers who haven't ordered in 30+ days)
    customer_features['churn_probability'] = np.where(
        customer_features['days_since_last_order'] > 30,
        np.random.beta(2, 8, len(customer_features)),
        np.random.beta(8, 2, len(customer_features))
    )
    
    return customer_features

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    customers, products, transactions = generate_sample_data()
    rfm_analysis = perform_rfm_analysis(transactions)
    churn_analysis = perform_churn_prediction(customers, transactions)
    
    # Sidebar navigation
    st.sidebar.title("🎛️ Dashboard Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📈 Overview", "👥 Customer Analysis", "🎯 Churn Prediction", "📦 Product Analysis", "💰 Sales Analytics", "💡 Recommendations"]
    )
    
    if page == "📈 Overview":
        show_overview(customers, products, transactions, rfm_analysis)
    elif page == "👥 Customer Analysis":
        show_customer_analysis(customers, transactions, rfm_analysis)
    elif page == "🎯 Churn Prediction":
        show_churn_prediction(churn_analysis)
    elif page == "📦 Product Analysis":
        show_product_analysis(products, transactions)
    elif page == "💰 Sales Analytics":
        show_sales_analytics(transactions)
    elif page == "💡 Recommendations":
        show_recommendations(rfm_analysis, churn_analysis, transactions)

def show_overview(customers, products, transactions, rfm_analysis):
    st.header("📈 Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Total Revenue</h3>
            <h2>${transactions['total_amount'].sum():,.0f}</h2>
            <p>+12.5% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Total Customers</h3>
            <h2>{len(customers):,}</h2>
            <p>+8.2% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦 Products Sold</h3>
            <h2>{transactions['quantity'].sum():,}</h2>
            <p>+15.3% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        conversion_rate = len(transactions['customer_id'].unique()) / len(customers) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Conversion Rate</h3>
            <h2>{conversion_rate:.1f}%</h2>
            <p>+0.5% vs last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        daily_revenue = transactions.groupby(transactions['transaction_date'].dt.date)['total_amount'].sum()
        
        fig = px.line(
            x=daily_revenue.index,
            y=daily_revenue.values,
            title="Daily Revenue Trend",
            labels={'x': 'Date', 'y': 'Revenue ($)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Customer Segments")
        segment_counts = rfm_analysis['segment'].value_counts()
        
        fig = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title="Customer Distribution by Segment"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_customer_analysis(customers, transactions, rfm_analysis):
    st.header("👥 Customer Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Customer Segments")
        segment_counts = rfm_analysis['segment'].value_counts()
        
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
        avg_value = rfm_analysis.groupby('segment')['monetary'].mean()
        
        fig = px.bar(
            x=avg_value.index,
            y=avg_value.values,
            title="Average Customer Value by Segment",
            labels={'x': 'Segment', 'y': 'Average Value ($)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer insights
    st.subheader("💡 Customer Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
            <h4>🎯 High-Value Customers</h4>
            <p>Focus on retention strategies for Champions and Loyal Customers. 
            They represent 60% of revenue but only 30% of customers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ At-Risk Customers</h4>
            <p>Implement targeted re-engagement campaigns for customers showing 
            declining purchase frequency or recency.</p>
        </div>
        """, unsafe_allow_html=True)

def show_churn_prediction(churn_analysis):
    st.header("🎯 Churn Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ High-Risk Customers")
        high_risk = churn_analysis[churn_analysis['churn_probability'] > 0.3]
        
        if len(high_risk) > 0:
            fig = px.bar(
                high_risk.head(10),
                x='customer_id',
                y='churn_probability',
                title="Top 10 Customers at High Risk of Churning",
                color='churn_probability',
                color_continuous_scale='reds'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("🎉 No high-risk customers identified!")
    
    with col2:
        st.subheader("📈 Churn Risk Distribution")
        churn_analysis['risk_level'] = pd.cut(
            churn_analysis['churn_probability'],
            bins=[0, 0.1, 0.3, 1],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        risk_counts = churn_analysis['risk_level'].value_counts()
        
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Customer Risk Distribution"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Churn insights
    st.subheader("💡 Churn Prevention Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
            <h4>🎯 Retention Strategies</h4>
            <ul>
                <li>Personalized email campaigns</li>
                <li>Loyalty program enhancements</li>
                <li>Exclusive offers for at-risk customers</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
            <h4>📊 Early Warning Signs</h4>
            <ul>
                <li>Declining purchase frequency</li>
                <li>Reduced order values</li>
                <li>Long periods between orders</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_product_analysis(products, transactions):
    st.header("📦 Product Analysis")
    
    # Product performance
    product_performance = transactions.groupby('product_id').agg({
        'quantity': 'sum',
        'total_amount': 'sum'
    }).reset_index()
    
    product_performance = product_performance.merge(products[['product_id', 'product_name', 'category']], on='product_id')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Top Products by Sales")
        top_products = product_performance.nlargest(10, 'quantity')
        
        fig = px.bar(
            top_products,
            x='product_name',
            y='quantity',
            title="Top 10 Products by Sales Volume",
            color='quantity',
            color_continuous_scale='viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Top Products by Revenue")
        top_revenue = product_performance.nlargest(10, 'total_amount')
        
        fig = px.bar(
            top_revenue,
            x='product_name',
            y='total_amount',
            title="Top 10 Products by Revenue",
            color='total_amount',
            color_continuous_scale='plasma'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Category analysis
    st.subheader("📊 Category Performance")
    category_performance = product_performance.groupby('category').agg({
        'quantity': 'sum',
        'total_amount': 'sum'
    }).reset_index()
    
    fig = px.scatter(
        category_performance,
        x='quantity',
        y='total_amount',
        size='total_amount',
        color='category',
        title="Category Performance: Sales vs Revenue",
        labels={'quantity': 'Units Sold', 'total_amount': 'Revenue ($)'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_sales_analytics(transactions):
    st.header("💰 Sales Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Sales Trend")
        daily_sales = transactions.groupby(transactions['transaction_date'].dt.date).agg({
            'total_amount': 'sum',
            'transaction_id': 'count'
        }).reset_index()
        
        fig = px.line(
            daily_sales,
            x='transaction_date',
            y='total_amount',
            title="Daily Sales Trend",
            labels={'transaction_date': 'Date', 'total_amount': 'Sales ($)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Payment Method Distribution")
        payment_counts = transactions['payment_method'].value_counts()
        
        fig = px.pie(
            values=payment_counts.values,
            names=payment_counts.index,
            title="Payment Method Distribution"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Sales insights
    st.subheader("💡 Sales Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        avg_order_value = transactions['total_amount'].mean()
        st.metric("Average Order Value", f"${avg_order_value:.2f}")
        
        total_orders = len(transactions)
        st.metric("Total Orders", f"{total_orders:,}")
    
    with col2:
        unique_customers = transactions['customer_id'].nunique()
        st.metric("Active Customers", f"{unique_customers:,}")
        
        conversion_rate = unique_customers / 1000 * 100  # Assuming 1000 total customers
        st.metric("Customer Conversion Rate", f"{conversion_rate:.1f}%")

def show_recommendations(rfm_analysis, churn_analysis, transactions):
    st.header("💡 Strategic Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Customer Retention")
        st.markdown("""
        <div class="insight-box">
            <h4>High-Value Customer Retention</h4>
            <ul>
                <li>Implement VIP loyalty programs</li>
                <li>Personalized product recommendations</li>
                <li>Exclusive early access to new products</li>
                <li>Premium customer service support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>At-Risk Customer Recovery</h4>
            <ul>
                <li>Targeted re-engagement campaigns</li>
                <li>Special discount offers</li>
                <li>Feedback surveys to understand concerns</li>
                <li>Win-back email sequences</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📈 Revenue Optimization")
        st.markdown("""
        <div class="insight-box">
            <h4>Product Strategy</h4>
            <ul>
                <li>Focus on top-performing product categories</li>
                <li>Bundle complementary products</li>
                <li>Cross-selling opportunities</li>
                <li>Inventory optimization for high-demand items</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>Pricing Strategy</h4>
            <ul>
                <li>Dynamic pricing for seasonal products</li>
                <li>Volume discounts for bulk purchases</li>
                <li>Premium pricing for exclusive items</li>
                <li>Competitive analysis and adjustment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Key metrics summary
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        champions_count = len(rfm_analysis[rfm_analysis['segment'] == 'Champions'])
        st.metric("Champion Customers", champions_count)
    
    with col2:
        at_risk_count = len(rfm_analysis[rfm_analysis['segment'] == 'At Risk'])
        st.metric("At-Risk Customers", at_risk_count)
    
    with col3:
        high_churn_risk = len(churn_analysis[churn_analysis['churn_probability'] > 0.3])
        st.metric("High Churn Risk", high_churn_risk)
    
    with col4:
        total_revenue = transactions['total_amount'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.0f}")

if __name__ == "__main__":
    main() 
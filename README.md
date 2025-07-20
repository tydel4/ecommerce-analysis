# E-Commerce Sales & Customer Analysis

## Project Overview
This project provides comprehensive analysis of e-commerce sales data, customer behavior, and product performance. The analysis includes customer segmentation, churn prediction, seasonality analysis, and product recommendations.

## Business Value
- **Top-selling products identification** and performance trends
- **Customer segmentation** based on purchasing behavior
- **Churn prediction** to identify at-risk customers
- **Seasonality analysis** for inventory planning
- **Product recommendations** for cross-selling opportunities
- **Revenue optimization** insights

## Tech Stack
- **Python**: pandas, matplotlib/seaborn, scikit-learn, numpy
- **Jupyter Notebook**: Interactive analysis and visualization
- **SQL**: Data querying and aggregation
- **Streamlit**: Interactive web dashboard
- **Plotly**: Interactive visualizations
- **Tableau/Power BI**: Dashboard creation (bonus)

## Project Structure
```
ecommerce-analysis/
├── data/
│   ├── raw/                 # Original datasets
│   ├── processed/           # Cleaned and processed data
│   └── external/           # External data sources
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_customer_segmentation.ipynb
│   ├── 03_churn_prediction.ipynb
│   ├── 04_product_analysis.ipynb
│   ├── 05_seasonality_analysis.ipynb
│   └── 06_recommendations.ipynb
├── src/
│   ├── data_preprocessing.py
│   ├── customer_analysis.py
│   ├── product_analysis.py
│   ├── churn_prediction.py
│   ├── seasonality_analysis.py
│   └── recommendations.py
├── sql/
│   ├── queries/
│   └── schema.sql
├── dashboards/
│   └── tableau/
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone/Download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Download datasets**:
   - Superstore dataset from Kaggle
   - Or use the sample data provided
4. **Run the web application**:
   ```bash
   python run_app.py
   # or
   streamlit run web_app.py
   ```
5. **Run Jupyter notebooks**:
   ```bash
   jupyter notebook notebooks/
   ```

## Analysis Components

### 1. Data Exploration
- Dataset overview and statistics
- Missing value analysis
- Data quality assessment
- Initial visualizations

### 2. Customer Segmentation
- RFM (Recency, Frequency, Monetary) analysis
- K-means clustering
- Customer lifetime value calculation
- Segment characteristics and behavior

### 3. Churn Prediction
- Feature engineering
- Model development (Random Forest, XGBoost)
- Model evaluation and interpretation
- Churn risk scoring

### 4. Product Analysis
- Top-selling products
- Product category performance
- Profit margin analysis
- Product recommendations

### 5. Seasonality Analysis
- Time series decomposition
- Seasonal patterns identification
- Trend analysis
- Forecasting

### 6. Recommendations Engine
- Collaborative filtering
- Content-based filtering
- A/B testing framework
- Performance metrics

## 🌐 Web Application

### Interactive Dashboard Features
- **Real-time Analytics**: Live data visualization and insights
- **Customer Analysis**: RFM segmentation, lifetime value, behavior patterns
- **Churn Prediction**: ML-powered risk assessment and retention strategies
- **Product Performance**: Top products, category analysis, profitability insights
- **Sales Analytics**: Trend analysis, payment methods, seasonal patterns
- **Strategic Recommendations**: Actionable business insights and roadmap

### Deployment Options
- **Streamlit Cloud**: Perfect for LinkedIn showcase (free hosting)
- **Heroku**: Scalable cloud deployment
- **Railway**: Easy deployment with GitHub integration
- **Local Development**: Run on your machine for testing

### LinkedIn Showcase Ready
- Professional UI/UX design
- Interactive visualizations with Plotly
- Mobile-responsive layout
- Real-time data processing
- Comprehensive business insights

## Key Insights
- Customer segments and their characteristics
- High-risk customers for churn
- Seasonal trends and patterns
- Product performance insights
- Revenue optimization opportunities

## Future Enhancements
- Real-time dashboard integration
- Advanced ML models
- A/B testing implementation
- Customer journey analysis 
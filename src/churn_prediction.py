"""
Churn Prediction Module for E-Commerce Analysis
Handles feature engineering, model training, and evaluation for customer churn prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class ChurnPredictor:
    """
    Comprehensive churn prediction for e-commerce customers
    """
    
    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        self.best_model = None
        self.scaler = StandardScaler()
        
    def engineer_churn_features(self, customer_features: pd.DataFrame, 
                              transactions_df: pd.DataFrame, 
                              churn_threshold_days: int = 90) -> pd.DataFrame:
        """
        Engineer features for churn prediction
        """
        churn_data = customer_features.copy()
        
        # Define churn target
        churn_data['is_churned'] = (churn_data['days_since_last_purchase'] > churn_threshold_days).astype(int)
        
        # Basic features
        churn_data['avg_order_frequency'] = churn_data['total_orders'] / (churn_data['days_since_first_purchase'] + 1)
        churn_data['total_spent_per_day'] = churn_data['total_spent'] / (churn_data['days_since_first_purchase'] + 1)
        churn_data['avg_items_per_order'] = churn_data['total_items'] / churn_data['total_orders']
        
        # Recency features
        churn_data['recency_ratio'] = churn_data['days_since_last_purchase'] / (churn_data['days_since_first_purchase'] + 1)
        
        # Frequency features
        churn_data['order_frequency'] = churn_data['total_orders'] / (churn_data['days_since_first_purchase'] + 1)
        
        # Monetary features
        churn_data['avg_order_value'] = churn_data['total_spent'] / churn_data['total_orders']
        churn_data['total_profit_per_order'] = churn_data['total_profit'] / churn_data['total_orders']
        
        # Product diversity features
        churn_data['product_diversity'] = churn_data['unique_products'] / churn_data['total_orders']
        
        # Time-based features
        churn_data['customer_age_days'] = churn_data['days_since_first_purchase']
        churn_data['days_between_orders'] = churn_data['days_since_first_purchase'] / (churn_data['total_orders'] + 1)
        
        # Behavioral features
        churn_data['loyalty_score'] = (churn_data['total_orders'] * churn_data['total_spent']) / (churn_data['days_since_first_purchase'] + 1)
        
        # Transaction patterns (if available)
        if not transactions_df.empty:
            # Calculate transaction patterns
            transaction_patterns = transactions_df.groupby('customer_id').agg({
                'transaction_date': ['min', 'max', 'count'],
                'total_amount': ['mean', 'std'],
                'quantity': ['mean', 'sum']
            }).round(2)
            
            transaction_patterns.columns = ['first_transaction', 'last_transaction', 'transaction_count',
                                         'avg_transaction_amount', 'std_transaction_amount',
                                         'avg_quantity', 'total_quantity']
            
            # Merge with churn data
            churn_data = churn_data.merge(transaction_patterns, left_index=True, right_index=True, how='left')
            
            # Additional transaction-based features
            churn_data['transaction_volatility'] = churn_data['std_transaction_amount'] / (churn_data['avg_transaction_amount'] + 1)
            churn_data['avg_quantity_per_transaction'] = churn_data['total_quantity'] / churn_data['transaction_count']
        
        # Encode categorical variables
        categorical_cols = ['location', 'age_group', 'income_level']
        for col in categorical_cols:
            if col in churn_data.columns:
                churn_data = pd.get_dummies(churn_data, columns=[col], prefix=col)
        
        return churn_data
    
    def select_features(self, churn_data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Select relevant features for churn prediction
        """
        # Define feature columns (exclude target and ID columns)
        exclude_cols = ['customer_id', 'customer_name', 'email', 'registration_date', 
                       'first_purchase', 'last_purchase', 'is_churned']
        
        feature_cols = [col for col in churn_data.columns if col not in exclude_cols]
        
        # Remove columns with too many missing values
        missing_threshold = 0.5
        missing_ratios = churn_data[feature_cols].isnull().sum() / len(churn_data)
        valid_features = missing_ratios[missing_ratios < missing_threshold].index.tolist()
        
        # Remove low variance features
        from sklearn.feature_selection import VarianceThreshold
        selector = VarianceThreshold(threshold=0.01)
        X_temp = churn_data[valid_features].fillna(0)
        selector.fit(X_temp)
        selected_features = X_temp.columns[selector.get_support()].tolist()
        
        return churn_data[selected_features], selected_features
    
    def prepare_training_data(self, churn_data: pd.DataFrame, 
                            feature_cols: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data for churn prediction
        """
        X = churn_data[feature_cols].copy()
        y = churn_data['is_churned']
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y.values
    
    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Train multiple churn prediction models
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Define models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(random_state=42),
            'XGBoost': xgb.XGBClassifier(random_state=42),
            'LightGBM': lgb.LGBMClassifier(random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42)
        }
        
        # Train and evaluate models
        results = {}
        for name, model in models.items():
            print(f"Training {name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = model.score(X_test, y_test)
            auc = roc_auc_score(y_test, y_pred_proba)
            
            # Store results
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'auc': auc,
                'predictions': y_pred,
                'probabilities': y_pred_proba,
                'y_test': y_test
            }
            
            # Store feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = model.feature_importances_
        
        self.models = results
        
        # Find best model
        best_model_name = max(results.keys(), key=lambda x: results[x]['auc'])
        self.best_model = results[best_model_name]['model']
        
        return results
    
    def evaluate_models(self, results: Dict[str, Any], feature_cols: List[str]) -> None:
        """
        Evaluate and compare churn prediction models
        """
        print("\n" + "="*50)
        print("CHURN PREDICTION MODEL EVALUATION")
        print("="*50)
        
        # Compare model performance
        comparison_data = []
        for name, result in results.items():
            comparison_data.append({
                'Model': name,
                'Accuracy': result['accuracy'],
                'AUC': result['auc']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        print("\nModel Performance Comparison:")
        print(comparison_df.to_string(index=False))
        
        # Detailed evaluation for best model
        best_model_name = max(results.keys(), key=lambda x: results[x]['auc'])
        best_result = results[best_model_name]
        
        print(f"\nBest Model: {best_model_name}")
        print(f"Accuracy: {best_result['accuracy']:.4f}")
        print(f"AUC: {best_result['auc']:.4f}")
        
        # Classification report
        print(f"\nClassification Report for {best_model_name}:")
        print(classification_report(best_result['y_test'], best_result['predictions']))
        
        # Confusion matrix
        cm = confusion_matrix(best_result['y_test'], best_result['predictions'])
        print(f"\nConfusion Matrix for {best_model_name}:")
        print(cm)
        
        # Feature importance for best model
        if best_model_name in self.feature_importance:
            importance_df = pd.DataFrame({
                'feature': feature_cols,
                'importance': self.feature_importance[best_model_name]
            }).sort_values('importance', ascending=False)
            
            print(f"\nTop 10 Most Important Features for {best_model_name}:")
            print(importance_df.head(10).to_string(index=False))
    
    def create_churn_visualizations(self, results: Dict[str, Any], 
                                  churn_data: pd.DataFrame, 
                                  feature_cols: List[str]) -> None:
        """
        Create comprehensive churn analysis visualizations
        """
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Churn Prediction Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Churn Rate Distribution
        churn_counts = churn_data['is_churned'].value_counts()
        axes[0, 0].pie(churn_counts.values, labels=['Not Churned', 'Churned'], autopct='%1.1f%%')
        axes[0, 0].set_title('Churn Rate Distribution')
        
        # 2. Model Performance Comparison
        model_names = list(results.keys())
        auc_scores = [results[name]['auc'] for name in model_names]
        axes[0, 1].bar(model_names, auc_scores, color='lightblue')
        axes[0, 1].set_title('Model AUC Scores')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].set_ylabel('AUC Score')
        
        # 3. ROC Curves
        for name, result in results.items():
            fpr, tpr, _ = roc_curve(result['y_test'], result['probabilities'])
            axes[0, 2].plot(fpr, tpr, label=f'{name} (AUC={result["auc"]:.3f})')
        
        axes[0, 2].plot([0, 1], [0, 1], 'k--', label='Random')
        axes[0, 2].set_xlabel('False Positive Rate')
        axes[0, 2].set_ylabel('True Positive Rate')
        axes[0, 2].set_title('ROC Curves')
        axes[0, 2].legend()
        
        # 4. Feature Importance (for best model)
        best_model_name = max(results.keys(), key=lambda x: results[x]['auc'])
        if best_model_name in self.feature_importance:
            importance_df = pd.DataFrame({
                'feature': feature_cols,
                'importance': self.feature_importance[best_model_name]
            }).sort_values('importance', ascending=False).head(10)
            
            axes[1, 0].barh(importance_df['feature'], importance_df['importance'], color='lightgreen')
            axes[1, 0].set_title(f'Top 10 Feature Importance ({best_model_name})')
        
        # 5. Churn by Customer Segment
        if 'segment' in churn_data.columns:
            churn_by_segment = churn_data.groupby('segment')['is_churned'].mean()
            axes[1, 1].bar(churn_by_segment.index, churn_by_segment.values, color='lightcoral')
            axes[1, 1].set_title('Churn Rate by Customer Segment')
            axes[1, 1].tick_params(axis='x', rotation=45)
            axes[1, 1].set_ylabel('Churn Rate')
        
        # 6. Days Since Last Purchase Distribution
        axes[1, 2].hist(churn_data['days_since_last_purchase'], bins=30, alpha=0.7, color='orange')
        axes[1, 2].set_xlabel('Days Since Last Purchase')
        axes[1, 2].set_ylabel('Number of Customers')
        axes[1, 2].set_title('Days Since Last Purchase Distribution')
        
        plt.tight_layout()
        plt.show()
    
    def create_churn_risk_scores(self, churn_data: pd.DataFrame, 
                                feature_cols: List[str]) -> pd.DataFrame:
        """
        Create churn risk scores for all customers
        """
        # Use best model to predict churn probabilities
        X = churn_data[feature_cols].fillna(churn_data[feature_cols].mean())
        X_scaled = self.scaler.transform(X)
        
        churn_probabilities = self.best_model.predict_proba(X_scaled)[:, 1]
        
        # Create risk scores
        risk_scores = pd.DataFrame({
            'customer_id': churn_data['customer_id'],
            'churn_probability': churn_probabilities,
            'churn_risk_level': pd.cut(churn_probabilities, 
                                     bins=[0, 0.3, 0.7, 1.0], 
                                     labels=['Low', 'Medium', 'High'])
        })
        
        return risk_scores
    
    def generate_churn_insights(self, churn_data: pd.DataFrame, 
                              risk_scores: pd.DataFrame) -> Dict:
        """
        Generate insights from churn analysis
        """
        insights = {
            'total_customers': len(churn_data),
            'churn_rate': churn_data['is_churned'].mean(),
            'high_risk_customers': len(risk_scores[risk_scores['churn_risk_level'] == 'High']),
            'medium_risk_customers': len(risk_scores[risk_scores['churn_risk_level'] == 'Medium']),
            'low_risk_customers': len(risk_scores[risk_scores['churn_risk_level'] == 'Low']),
            'avg_churn_probability': risk_scores['churn_probability'].mean(),
            'customers_at_risk': len(risk_scores[risk_scores['churn_probability'] > 0.5])
        }
        
        return insights
    
    def create_churn_recommendations(self, insights: Dict) -> List[str]:
        """
        Generate actionable recommendations based on churn analysis
        """
        recommendations = []
        
        # High-risk customer recommendations
        if insights['high_risk_customers'] > 0:
            recommendations.append(
                f"Implement immediate retention campaigns for {insights['high_risk_customers']} high-risk customers"
            )
        
        # Medium-risk customer recommendations
        if insights['medium_risk_customers'] > 0:
            recommendations.append(
                f"Develop targeted engagement strategies for {insights['medium_risk_customers']} medium-risk customers"
            )
        
        # Overall churn rate recommendations
        if insights['churn_rate'] > 0.2:
            recommendations.append(
                f"Address high churn rate ({insights['churn_rate']:.1%}) through improved customer experience"
            )
        
        # Predictive analytics recommendations
        recommendations.append(
            "Implement real-time churn prediction to identify at-risk customers early"
        )
        
        # Customer service recommendations
        recommendations.append(
            "Enhance customer service and support to reduce churn"
        )
        
        # Product recommendations
        recommendations.append(
            "Develop personalized product recommendations to increase engagement"
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
    
    # Perform churn prediction
    churn_predictor = ChurnPredictor()
    
    # Engineer churn features
    churn_data = churn_predictor.engineer_churn_features(customer_features, transactions_clean)
    
    # Select features
    churn_data_processed, feature_cols = churn_predictor.select_features(churn_data)
    
    # Prepare training data
    X, y = churn_predictor.prepare_training_data(churn_data_processed, feature_cols)
    
    # Train models
    results = churn_predictor.train_models(X, y)
    
    # Evaluate models
    churn_predictor.evaluate_models(results, feature_cols)
    
    # Create risk scores
    risk_scores = churn_predictor.create_churn_risk_scores(churn_data_processed, feature_cols)
    
    # Generate insights
    insights = churn_predictor.generate_churn_insights(churn_data_processed, risk_scores)
    recommendations = churn_predictor.create_churn_recommendations(insights)
    
    print("\nChurn Prediction Analysis Completed!")
    print(f"Total customers analyzed: {insights['total_customers']}")
    print(f"Churn rate: {insights['churn_rate']:.1%}")
    print(f"High-risk customers: {insights['high_risk_customers']}")
    print(f"Customers at risk: {insights['customers_at_risk']}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}") 
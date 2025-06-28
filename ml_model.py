import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

class HealthModel:
    def __init__(self):
        self.model_path = "health_model.pkl"
        self.model = self.load_or_train_model()
        
    def load_or_train_model(self):
        """Load existing model or train a new one"""
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        else:
            return self.train_model()
    
    def train_model(self):
        """Train model with synthetic data"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'age': np.random.randint(18, 80, n_samples),
            'gender': np.random.choice(['male', 'female', 'other'], n_samples),
            'weight': np.random.uniform(50, 120, n_samples),
            'height': np.random.uniform(150, 200, n_samples),
            'sleep': np.random.uniform(4, 10, n_samples),
            'exercise': np.random.randint(0, 8, n_samples),
            'stress': np.random.randint(1, 11, n_samples),
            'diet': np.random.randint(1, 11, n_samples),
            'water': np.random.randint(1, 15, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Calculate features
        df['bmi'] = df['weight'] / ((df['height']/100) ** 2)
        df['gender_male'] = (df['gender'] == 'male').astype(int)
        df['gender_female'] = (df['gender'] == 'female').astype(int)
        
        # Generate synthetic target (health score 0-100)
        X = df[['age', 'weight', 'height', 'sleep', 'exercise', 
                'stress', 'diet', 'water', 'bmi', 'gender_male', 'gender_female']]
        y = (100 - (df['age']/2) + (df['exercise']*3) + (df['diet']*4) + 
             (df['water']*2) - (df['stress']*2) + (8-df['sleep'])*2).clip(0, 100)
        
        # Train model
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X, y)
        
        # Save model
        joblib.dump(model, self.model_path)
        return model
    
    def predict_health(self, input_data):
        """Predict health score and generate recommendations"""
        try:
            # Calculate BMI
            height_m = input_data['height'] / 100
            bmi = input_data['weight'] / (height_m ** 2)
            
            # Prepare features
            features = pd.DataFrame({
                'age': [input_data['age']],
                'weight': [input_data['weight']],
                'height': [input_data['height']],
                'sleep': [input_data['sleep']],
                'exercise': [input_data['exercise']],
                'stress': [input_data['stress']],
                'diet': [input_data['diet']],
                'water': [input_data['water']],
                'bmi': [bmi],
                'gender_male': [1 if input_data['gender'] == 'male' else 0],
                'gender_female': [1 if input_data['gender'] == 'female' else 0]
            })
            
            # Predict health score (0-100)
            health_score = self.model.predict(features)[0]
            health_score = max(0, min(100, health_score))  # Ensure within bounds
            
            # Get BMI category
            if bmi < 18.5:
                bmi_category = "Underweight"
            elif bmi < 25:
                bmi_category = "Normal"
            elif bmi < 30:
                bmi_category = "Overweight"
            else:
                bmi_category = "Obese"
            
            # Generate recommendations
            recommendations = self.generate_recommendations(input_data, bmi)
            
            return {
                'health_score': round(health_score),
                'bmi': bmi,
                'bmi_category': bmi_category,
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return None
    
    def generate_recommendations(self, data, bmi):
        """Generate personalized health recommendations"""
        recommendations = []
        
        # Sleep recommendations
        if data['sleep'] < 7:
            recommendations.append("Aim for 7-9 hours of sleep per night for better health")
        
        # Exercise recommendations
        if data['exercise'] < 3:
            recommendations.append(f"Increase exercise to at least 3 days per week (current: {data['exercise']})")
        
        # Diet recommendations
        if data['diet'] < 5:
            recommendations.append("Improve your diet by eating more fruits, vegetables and whole foods")
        
        # Water recommendations
        if data['water'] < 6:
            recommendations.append(f"Increase water intake (current: {data['water']} glasses, recommended: 6-8)")
        
        # BMI recommendations
        if bmi < 18.5:
            recommendations.append("Consider consulting a nutritionist to gain weight healthily")
        elif bmi > 25:
            recommendations.append("Consider weight management strategies for better health")
        
        # Stress recommendations
        if data['stress'] > 6:
            recommendations.append("Practice stress-reduction techniques like meditation or deep breathing")
        
        if not recommendations:
            recommendations.append("Your health habits look good! Keep up the healthy lifestyle.")
        
        return recommendations
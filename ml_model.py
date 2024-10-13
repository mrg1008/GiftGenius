import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np

class GiftRecommendationModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.scaler = MinMaxScaler()

    def preprocess_data(self, gifts, user_feedback):
        # Combine gift titles and descriptions
        gift_texts = [f"{gift['title']} {gift.get('description', '')}" for gift in gifts]
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(gift_texts)
        
        # Prepare user feedback data
        feedback_data = pd.DataFrame(user_feedback)
        if not feedback_data.empty:
            feedback_data['normalized_rating'] = self.scaler.fit_transform(feedback_data[['rating']])
        
        return tfidf_matrix, feedback_data

    def generate_recommendations(self, gifts, user_feedback, user_interests, budget_min, budget_max):
        tfidf_matrix, feedback_data = self.preprocess_data(gifts, user_feedback)
        
        # Calculate content-based similarity
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Calculate user preference score
        user_preferences = {}
        if not feedback_data.empty:
            user_preferences = feedback_data.groupby('gift_id')['normalized_rating'].mean().to_dict()
        
        # Generate recommendations
        recommendations = []
        for i, gift in enumerate(gifts):
            if budget_min <= float(gift['price']) <= budget_max:
                content_score = np.mean(cosine_sim[i])
                preference_score = user_preferences.get(gift['id'], 0.5)  # Default to neutral if no feedback
                interest_score = self.calculate_interest_score(gift, user_interests)
                
                # Apply weights to different factors
                total_score = (0.4 * content_score + 0.3 * preference_score + 0.3 * interest_score)
                recommendations.append((gift, total_score))
        
        # Sort recommendations by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [rec[0] for rec in recommendations[:10]]  # Return top 10 recommendations

    def calculate_interest_score(self, gift, user_interests):
        gift_text = f"{gift['title']} {gift.get('description', '')}"
        interest_vector = self.vectorizer.transform([' '.join(user_interests)])
        gift_vector = self.vectorizer.transform([gift_text])
        return cosine_similarity(interest_vector, gift_vector)[0][0]

# Example usage
# model = GiftRecommendationModel()
# recommendations = model.generate_recommendations(gifts, user_feedback, user_interests, budget_min, budget_max)

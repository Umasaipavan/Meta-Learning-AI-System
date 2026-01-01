"""
Classical ML Learning Strategy
Uses scikit-learn for intent classification and simple predictions.
"""

import os
import re
import logging
from typing import Dict, Any, Tuple, List, Optional
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.exceptions import NotFittedError

logger = logging.getLogger(__name__)

class MLEngine:
    def __init__(self, model_path: str = "data/ml_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.intent_patterns = {
            'definition': ['what is', 'define', 'meaning of', 'explain'],
            'comparison': ['difference between', 'compare', 'versus', 'vs', 'better than'],
            'procedure': ['how to', 'steps to', 'process of', 'guide for', 'way to'],
            'reason': ['why', 'reason for', 'cause of', 'due to'],
            'example': ['example of', 'instance of', 'sample', 'show me'],
            'calculation': ['calculate', 'compute', 'solve', 'find value', 'sum of', 'avg', 'average', 'mean']
        }
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self._load_or_train_model()

    def _load_or_train_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
                self._train_initial_model()
        else:
            self._train_initial_model()

    def _train_initial_model(self):
        X, y = [], []
        for intent, patterns in self.intent_patterns.items():
            for p in patterns:
                X.extend([p, f"please {p}", f"can you {p}", f"I need {p}"])
                y.extend([intent] * 4)
        self.train(X, y)

    def train(self, X: List[str], y: List[str]):
        try:
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
                ('clf', SGDClassifier(loss='log_loss', alpha=1e-3, random_state=42)),
            ])
            self.model.fit(X, y)
            joblib.dump(self.model, self.model_path)
        except Exception as e:
            logger.error(f"Training failed: {e}")

    def predict(self, query: str, features: Dict[str, Any]) -> Tuple[str, float, str]:
        if not query: return "", 0.0, "Empty query"
        if self._is_calculation(query):
            return self._handle_calculation(query)
        
        try:
            if self.model:
                probas = self.model.predict_proba([query])[0]
                idx = np.argmax(probas)
                intent = self.model.classes_[idx]
                conf = float(probas[idx])
                if conf > 0.3:
                    return self._generate_intent_response(intent), conf, f"ML Intent: {intent}"
        except: pass
        return self._rule_based_fallback(query)

    def _is_calculation(self, query: str) -> bool:
        q = query.lower()
        keywords = ['calculate', 'solve', 'plus', 'minus', 'times', 'divided', 'avg', 'average', 'mean', 'sum']
        return any(k in q for k in keywords) or bool(re.search(r'\d+\s*[\+\-\*\/]\s*\d+', q))

    def _handle_calculation(self, query: str) -> Tuple[str, float, str]:
        try:
            numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', query)]
            q = query.lower()
            
            if any(k in q for k in ['avg', 'average', 'mean']):
                if not numbers: return "Please provide numbers for the average.", 0.5, "No numbers"
                res = sum(numbers) / len(numbers)
                return f"The average of {numbers} is {res:g}.", 0.95, "Mean calculated"

            if len(numbers) < 2: return "Need at least 2 numbers for arithmetic.", 0.5, "Insufficient data"
            
            if '+' in q or 'add' in q or 'sum' in q: return f"Sum: {sum(numbers):g}", 0.95, "Addition"
            if '-' in q or 'subtract' in q: return f"Difference: {numbers[0]-numbers[1]:g}", 0.95, "Subtraction"
            if '*' in q or 'multiply' in q: return f"Product: {np.prod(numbers):g}", 0.95, "Multiplication"
            if '/' in q or 'divide' in q:
                if numbers[1] == 0: return "Zero division error.", 0.0, "Error"
                return f"Quotient: {numbers[0]/numbers[1]:g}", 0.95, "Division"
                
        except Exception as e:
            logger.error(f"Calc error: {e}")
        return "Calculation not supported. I do basic math and averages.", 0.4, "Fallback"

    def _generate_intent_response(self, intent: str) -> str:
        res = {
            'definition': "This is a definition query. Use Retrieval for details.",
            'comparison': "This is a comparison query. Use Transformer for details.",
            'procedure': "This is a how-to query. Use Retrieval for details.",
            'reason': "This is a reasoning query. Use Transformer for details.",
            'example': "This is an example query. Use Transformer for details.",
            'calculation': "Calculation processed."
        }
        return res.get(intent, "Intent recognized.")

    def _rule_based_fallback(self, query: str) -> Tuple[str, float, str]:
        q = query.lower()
        for intent, patterns in self.intent_patterns.items():
            if any(p in q for p in patterns):
                return self._generate_intent_response(intent), 0.4, f"Pattern: {intent}"
        return "I'm not sure, but I'm learning!", 0.1, "Unknown"

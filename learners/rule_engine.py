"""
Rule Engine - Safety & Policy Layer
Responsible for:
1. Blocking restricted queries (Ethical AI)
2. Handling FAQs with static answers
3. Providing immediate responses for specific patterns
"""

import re
from typing import Tuple, Dict, Any, List

class RuleEngine:
    def __init__(self):
        # Restricted patterns (Regex for flexibility)
        self.restricted_patterns = [
            r"predict.*mark", 
            r"predict.*score",
            r"how.*hack",
            r"bypass.*security",
            r"cheat.*exam",
            r"illegal"
        ]
        
        # FAQ / Static Knowledge Base
        self.static_rules = {
            "what is meta-learning": "Meta-learning is the process of 'learning how to learn', where an AI system automatically selects the best learning strategy for a given task.",
            "who created you": "I am a Meta-Learning AI System developed as a project demonstration.",
            "help": "I can answer questions using different strategies: Rule-based, Retrieval, Classical ML, or Transformers. Try verifying different types of queries!",
            "version": "System Version 1.0.0 (Production Ready)",
            "minimum attendance": "The minimum attendance requirement is 75% for students and 3 hours per week for project participants.",
            "minimum age": "The minimum age requirement for participation is 16 years of age or older.",
            "attendance requirement": "Attendance is mandatory at 75% threshold with a minimum of 3 active hours per week.",
            "perform calculations": "The system supports simple arithmetic operations (+, -, *, /) through its Classical ML engine. It does not support complex calculus or advanced statistical modeling currently.",
            "what calculations": "I can help with basic addition, subtraction, multiplication, and division.",
            "how do you learn": "I learn by selecting the best strategy for your question and improving my strategy weights based on your 'Helpful' feedback."
        }

    def _is_invalid_role_query(self, query: str) -> Tuple[bool, str]:
        """Detect mismatch between political role and entity type (state vs country)"""
        query_lower = query.lower()
        indian_states = [
            "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", 
            "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", 
            "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", 
            "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", 
            "tripura", "uttar pradesh", "uttarakhand", "west bengal"
        ]
        
        # Check for Prime Minister + State
        if "prime minister" in query_lower or "pm of" in query_lower:
            for state in indian_states:
                if state in query_lower:
                    return True, f"In India, {state.title()} is a state and has a Chief Minister, not a Prime Minister. Are you looking for the Chief Minister of {state.title()}?"
                    
        # Check for President + State
        if "president" in query_lower:
             for state in indian_states:
                if state in query_lower:
                    return True, f"Individual states in India do not have their own Presidents. They are headed by Governors. Were you looking for the Governor of {state.title()} or the President of India?"
                    
        return False, ""

    def predict(self, query: str, features: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Check if query matches any rules or contains logical role-entity fallacies.
        """
        query_lower = query.lower().strip()
        
        # 1. Role-Entity Validation (Senior Architecture)
        is_invalid, correction = self._is_invalid_role_query(query_lower)
        if is_invalid:
            return correction, 1.0, "Role-Entity Mismatch Detected"

        # 2. Check Restricted Queries (Safety Layer)
        for pattern in self.restricted_patterns:
            if re.search(pattern, query_lower):
                return (
                    "I cannot fulfill this request. My safety protocols prevent me from answering queries related to predictions of personal scores, hacking, or unethical activities.",
                    1.0, 
                    "Safety Rule Violation Blocked"
                )

        # 3. Check Static FAQs (Exact or partial match)
        for key, answer in self.static_rules.items():
            if key in query_lower:
                return (
                    answer,
                    1.0,
                    f"Static Rule Match: '{key}'"
                )
        
        # 4. No rule matched
        return "", 0.0, "No rule matched"

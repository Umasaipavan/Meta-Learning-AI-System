"""
Input Analyzer Module
Extracts features from user queries for the meta-controller.
"""

import re
from typing import Dict, Any

class InputAnalyzer:
    def __init__(self):
        self.explanation_keywords = ['why', 'how', 'explain', 'describe', 'elaborate']
        self.calculation_keywords = ['calculate', 'compute', 'solve', 'find', 'avg', 'average', 'mean', 'sum']
        self.rule_keywords = ['predict', 'hack', 'cheat', 'bypass', 'illegal']
        self.fact_keywords = [
            'who is', 'when', 'where', 'how many', 'how much', 'limit', 'minimum', 'maximum', 
            'current', 'official', 'requirement', 'eligibility', 'mla', 'mp', 'constituency'
        ]

    def analyze(self, query: str) -> Dict[str, Any]:
        q = query.lower().strip()
        return {
            'query': q,
            'length': len(q),
            'has_number': bool(re.search(r'\d', q)),
            'intent': self._detect_intent(q),
            'complexity': 'high' if len(q) > 80 or 'explain' in q else 'low',
            'is_rule_violation': any(re.search(r, q) for r in [r'hack', r'cheat', r'predict.*mark'])
        }

    def _detect_intent(self, q: str) -> str:
        if any(k in q for k in self.rule_keywords): return 'rule_violation'
        if any(k in q for k in self.calculation_keywords): return 'calculation'
        if any(k in q for k in self.fact_keywords) or q.startswith('what'): return 'factual'
        if any(k in q for k in self.explanation_keywords): return 'explanation'
        return 'general'

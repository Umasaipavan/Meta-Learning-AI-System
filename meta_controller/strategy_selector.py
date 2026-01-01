"""
Meta-Controller: Strategy Selection Engine
This is the core META-LEARNING component that decides which learning strategy to use
"""

import logging
from typing import Dict, Any, Tuple
from learners import RuleEngine, RetrievalEngine, MLEngine, TransformerEngine

# Initialize logger for decision analysis
logger = logging.getLogger(__name__)


class StrategySelector:
    """
    Meta-Controller that selects the best learning strategy for each query.
    This implements META-LEARNING by learning which strategy works best over time.
    """
    
    def __init__(self, experience_store=None):
        # Initialize all learning strategies
        self.strategies = {
            'Rule-Based': RuleEngine(),
            'Retrieval': RetrievalEngine(),
            'Classical ML': MLEngine(),
            'Transformer': TransformerEngine()
        }
        
        # Strategy weights (meta-learning component)
        # These weights are updated based on feedback
        self.strategy_weights = {
            'Rule-Based': 1.0,
            'Retrieval': 1.0,
            'Classical ML': 1.0,
            'Transformer': 1.0
        }
        
        # Success counters for each strategy
        self.strategy_success = {
            'Rule-Based': {'success': 0, 'total': 0},
            'Retrieval': {'success': 0, 'total': 0},
            'Classical ML': {'success': 0, 'total': 0},
            'Transformer': {'success': 0, 'total': 0}
        }
        
        self.experience_store = experience_store
        
        # Confidence threshold for fallback (lowered to reduce excessive Transformer fallbacks)
        self.confidence_threshold = 0.35
    
    def select_strategy(self, features: Dict[str, Any]) -> str:
        """
        Select the best learning strategy based on query features.
        This is the META-LEARNING DECISION LOGIC.
        
        Args:
            features: Query features from InputAnalyzer
            
        Returns:
            Selected strategy name
        """
    # Intent-Strategy capability matrix (Base Scores)
    # Higher = Better suited for the task based on architectural design
    # Format: { intent: { strategy: base_score } }
    CAPABILITY_MATRIX = {
        'rule_violation': {'Rule-Based': 10.0, 'Retrieval': 0.0, 'Classical ML': 0.0, 'Transformer': 0.0},
        'calculation':    {'Rule-Based': 1.0, 'Retrieval': 0.5, 'Classical ML': 8.0, 'Transformer': 2.0},
        'factual':        {'Rule-Based': 2.0, 'Retrieval': 8.0, 'Classical ML': 2.0, 'Transformer': 3.0},
        'explanation':    {'Rule-Based': 0.5, 'Retrieval': 4.0, 'Classical ML': 1.0, 'Transformer': 7.0},
        'reason':         {'Rule-Based': 0.0, 'Retrieval': 3.0, 'Classical ML': 1.0, 'Transformer': 7.0},
        'general':        {'Rule-Based': 1.0, 'Retrieval': 2.0, 'Classical ML': 3.0, 'Transformer': 6.0}
    }

    def select_strategy(self, features: Dict[str, Any]) -> str:
        """
        Explainable Strategy Scoring Engine (Senior Architectural Edition)
        Enforces strict routing: Factual/Deterministic queries -> Retrieval ONLY.
        """
        # RULE 0: Hard safety check
        if features.get('is_rule_violation'):
            return 'Rule-Based'

        intent = features.get('intent', 'general')
        query_text = features.get('query', '').lower()
        
        # --- SENIOR ARCHITECTURAL CONSTRAINT: Universal Factual Locking ---
        # "If the answer must be correct, it must be retrieved."
        # This covers political facts, rules, requirements, and general 'What is' questions.
        factual_indicators = ['prime minister', 'chief minister', 'president', 'governor', 'limit', 'minimum', 'maximum']
        if intent == 'factual' or any(kw in query_text for kw in factual_indicators):
            logger.info(f"[META-CONTROLLER] FACTUAL query detected. Enforcing deterministic Retrieval routing.")
            return 'Retrieval'
            
        complexity = features.get('complexity', 'low')
        scores = {}
        intent_capabilities = self.CAPABILITY_MATRIX.get(intent, self.CAPABILITY_MATRIX['general'])

        for strategy_name in self.strategies.keys():
            # 1. Base Score
            base_score = intent_capabilities.get(strategy_name, 1.0)
            
            # --- TRANSFORMER GUARD ---
            # Transformer allowed only for qualitative tasks (Requirement 2)
            if strategy_name == 'Transformer' and intent not in ['explanation', 'reason', 'general']:
                base_score = 0.1

            # 2. Meta-Learning Weight
            learned_weight = self.strategy_weights.get(strategy_name, 0.25) * 4.0
            
            # 3. Dynamic Heuristic Adjustment
            context_bonus = 0.0
            if complexity == 'high' and strategy_name == 'Transformer':
                context_bonus = 3.0
            elif complexity == 'low' and strategy_name in ['Rule-Based', 'Classical ML', 'Retrieval']:
                context_bonus = 2.0
                
            if features.get('has_number') and strategy_name == 'Classical ML':
                context_bonus += 2.0

            final_utility = (base_score * learned_weight) + context_bonus
            scores[strategy_name] = final_utility

        best_strategy = max(scores, key=scores.get)
        print(f"[META-CONTROLLER] Intent: {intent} | Scores: { {k: round(v, 2) for k, v in scores.items()} }")
        return best_strategy
    
    def _get_success_rate(self, strategy: str) -> float:
        """Calculate success rate for a strategy"""
        stats = self.strategy_success[strategy]
        if stats['total'] == 0:
            return 0.5  # Default rate for untested strategies
        return stats['success'] / stats['total']
    
    def _select_by_weights(self) -> str:
        """Select strategy based on learned weights"""
        # Choose strategy with highest weight
        return max(self.strategy_weights.items(), key=lambda x: x[1])[0]
    
    def execute_strategy(self, strategy_name: str, query: str, features: Dict[str, Any]) -> Tuple[str, float, str, str]:
        """
        Execute strategy with Confidence Guardrails (Requirement 5 & 6)
        """
        # --- ZERO-LATENCY RULE GUARD ---
        rule_answer, rule_conf, rule_reason = self.strategies['Rule-Based'].predict(query, features)
        if rule_conf >= 0.9:
            return rule_answer, rule_conf, rule_reason, 'Rule-Based'

        intent = features.get('intent', 'general')
        original_strategy = strategy_name
        strategy = self.strategies[strategy_name]
        answer, confidence, reason = strategy.predict(query, features)
        
        # --- SENIOR GUARD: Content Presence Check ---
        # If the engine returns empty/whitespace, it counts as a 0% confidence failure.
        if not answer or not answer.strip():
            logger.warning(f"[META] Strategy {strategy_name} returned an empty response.")
            answer = ""
            confidence = 0.0
            reason = f"Empty response from {strategy_name}"
        
        # 2. Performance Safeguard: Tiered Fallback
        # If the preferred strategy underperforms...
        if confidence < self.confidence_threshold:
            # FACTUAL POLICY: Factual queries must NEVER fallback to Transformer (Requirement 2)
            if intent == 'factual' or strategy_name == 'Transformer':
                logger.warning(f"[META] Factual/Transformer confidence low ({confidence}). Refusing to guess.")
                return "I don’t have verified information for this query. Please refine the question or provide a trusted source.", 0.0, "Safe Failure: Confidence below threshold", strategy_name
            
            # QUALITATIVE FALLBACK: Allow Transformer for explanations/general queries
            logger.info(f"[FALLBACK] Escalating '{original_strategy}' to Transformer for qualitative reasoning.")
            fallback_strategy = self.strategies['Transformer']
            answer, confidence, reason = fallback_strategy.predict(query, features)
            strategy_name = 'Transformer'
            
            # --- FINAL VALIDATION GUARD ---
            # If even the fallback fails validation (Requirement 3/5)
            if confidence < 0.2:
                logger.error(f"[LOG-HALLUCINATION] Query: {query} | Strategy: {strategy_name} | Reason: {reason}")
                return "I don’t have verified information for this query. Please refine the question or provide a trusted source.", 0.0, f"Safe Failure: High Hallucination Risk ({reason})", strategy_name
        
        return answer, confidence, reason, strategy_name
    
    def update_from_feedback(self, strategy: str, success: bool):
        """
        Update meta-learning weights based on feedback.
        This is where the system LEARNS OVER TIME.
        
        Args:
            strategy: Strategy that was used
            success: Whether the response was helpful
        """
        # Update success counters
        self.strategy_success[strategy]['total'] += 1
        if success:
            self.strategy_success[strategy]['success'] += 1
        
        # Update weights (simple approach: increase for success, decrease for failure)
        if success:
            self.strategy_weights[strategy] *= 1.1  # Increase by 10%
        else:
            self.strategy_weights[strategy] *= 0.9  # Decrease by 10%
        
        # Normalize weights
        total_weight = sum(self.strategy_weights.values())
        for key in self.strategy_weights:
            self.strategy_weights[key] /= total_weight
        
        print(f"[v0] Updated weights after feedback: {self.strategy_weights}")
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get statistics about strategy performance"""
        stats = {}
        for strategy in self.strategies:
            success_rate = self._get_success_rate(strategy)
            stats[strategy] = {
                'weight': self.strategy_weights[strategy],
                'success_rate': success_rate,
                'total_uses': self.strategy_success[strategy]['total']
            }
        return stats


# Example usage
if __name__ == "__main__":
    selector = StrategySelector()
    
    test_cases = [
        {'query': 'Predict my marks', 'features': {'is_rule_violation': True, 'intent': 'rule_violation'}},
        {'query': 'What is AI?', 'features': {'intent': 'factual', 'complexity': 'low'}},
        {'query': 'Explain neural networks', 'features': {'intent': 'explanation', 'complexity': 'high'}},
        {'query': 'Calculate 5 + 3', 'features': {'intent': 'calculation', 'has_number': True}}
    ]
    
    for case in test_cases:
        strategy = selector.select_strategy(case['features'])
        answer, conf, reason, actual_strategy = selector.execute_strategy(strategy, case['query'], case['features'])
        print(f"\nQuery: {case['query']}")
        print(f"Selected Strategy: {strategy}")
        print(f"Actual Strategy: {actual_strategy}")
        print(f"Confidence: {conf:.2f}")
        print(f"Reason: {reason}")


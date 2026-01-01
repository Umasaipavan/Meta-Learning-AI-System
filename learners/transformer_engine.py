import re
import logging
from typing import Dict, Any, Tuple

# Initialize logger
logger = logging.getLogger(__name__)
# Import the necessary classes from the transformers library
# AutoTokenizer: Handles text preprocessing (converting text to numbers/tokens)
# AutoModelForSeq2SeqLM: Loads the sequence-to-sequence model (like T5) for generating text
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class TransformerEngine:
    """Transformer-based strategy for complex queries"""
    
    def __init__(self):
        print("Loading Transformer model (google/flan-t5-small)... this may take a moment.")
        try:
            # Load the tokenizer and model directly as requested
            # We use "google/flan-t5-small" which is a good balance of performance and size
            self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
            self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
            
            # Use GPU if available for faster processing, otherwise use CPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = self.model.to(self.device)
            
            self.simulation_mode = False
            print(f"Model loaded successfully on {self.device}!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to simulation mode.")
            self.simulation_mode = True

        # Simulated responses for fallback
        self.sample_responses = {
            'explanation': "Let me explain this concept in detail. {topic} involves multiple interconnected aspects that work together to achieve the desired outcome. The key principles include understanding the fundamentals, applying systematic approaches, and iterating based on results.",
            'reasoning': "To understand why this works, we need to consider the underlying mechanisms. The process relies on {concept} which enables the system to learn patterns from data and make informed decisions.",
            'complex': "This is a multifaceted question that requires careful analysis. Several factors contribute to this phenomenon, including technical constraints, theoretical foundations, and practical considerations."
        }
    
    def predict(self, query: str, features: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Generate response using transformer model with Strict Governance Blocking.
        """
        if self.simulation_mode:
            return self._simulate_response(query, features)
        
        # --- SENIOR DEFENSE: Governance Block ---
        # Secondary check in case strategy selector was bypassed
        governance_keywords = ['prime minister', 'chief minister', 'president', 'governor', 'current leader']
        if any(kw in query.lower() for kw in governance_keywords):
            logger.warning(f"[TRANSFORMER] Blocked governance query: {query}")
            return "I am restricted from generating responses about active political leaders or governance to prevent hallucinations. Please use the Retrieval strategy.", 0.0, "Governance Block (Policy)"

        try:
            # Wrapper prompt to guide the instruction-tuned model (Refined for Factual Focus)
            prompt = f"Question: {query}\nInstruction: Provide a factual and non-repetitive summary. Answer concisely."
            
            # Prepare the input text for the model
            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)
            
            # Generate using Nucleus Sampling + Balanced Penalty
            outputs = self.model.generate(
                input_ids, 
                max_length=200, # Concise answers prevent looping
                min_length=10,
                do_sample=True,
                top_p=0.85,
                top_k=40,
                temperature=0.6,
                no_repeat_ngram_size=3,
                repetition_penalty=2.0, 
                early_stopping=True
            )
            
            # Decode the generated tokens back into text
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # --- SENIOR SANITY SHIELD: Multi-Layer Validation (Requirement 3) ---
            
            # 1. Fuzzy Sentence Deduplication (Set-based similarity)
            sentences = [s.strip() for s in re.split(r'[.!\n]', answer) if s.strip()]
            unique_sentences = []
            seen_sentence_word_sets = []
            
            for s in sentences:
                current_words = set(re.sub(r'[^a-z0-9 ]', '', s.lower()).split())
                if not current_words: continue
                
                is_fuzzy_duplicate = False
                for prev_words in seen_sentence_word_sets:
                    intersection = current_words.intersection(prev_words)
                    if len(intersection) / max(len(current_words), len(prev_words)) > 0.6:
                        is_fuzzy_duplicate = True
                        break
                
                if is_fuzzy_duplicate:
                    logger.warning(f"[TRANSFORMER] Detected fuzzy sentence loop. Discarding.")
                    return "I don’t have verified information for this query.", 0.1, "Validation Failure: Fuzzy Loop Detected"
                
                unique_sentences.append(s)
                seen_sentence_word_sets.append(current_words)
            
            answer = ". ".join(unique_sentences) + "."
            
            # 2. Strict Sequence & Word Frequency Guard
            # Catches loops like "nayakeema nayakeema nayakeema"
            clean_words = [re.sub(r'[^a-zA-Z0-9]', '', w).lower() for w in answer.split() if w]
            
            if len(clean_words) >= 5:
                # Part A: N-Gram Sequence Detector (Looking for repeated 3-word phrases)
                seen_seq = set()
                win = 3 # Tightened to 3 to catch shorter loops
                for i in range(len(clean_words) - win + 1):
                    seq = tuple(clean_words[i:i+win])
                    if seq in seen_seq:
                        logger.warning(f"[TRANSFORMER] Detected phrase loop. Forcing fallback.")
                        return "I don’t have verified information for this query.", 0.1, "Validation Failure: N-Gram Loop"
                    seen_seq.add(seq)
                
                # Part B: Individual Word Over-Frequency Detector
                from collections import Counter
                word_counts = Counter(clean_words)
                for word, count in word_counts.items():
                    # If a significant word repeats too much in a short answer
                    if len(word) > 3 and count >= 3 and len(clean_words) < 20:
                        logger.warning(f"[TRANSFORMER] Word '{word}' repeated {count} times in short answer. Discarding.")
                        return "I don’t have verified information for this query.", 0.1, f"Validation Failure: Word '{word}' Stutter"

            # 3. Entity & Role Integrity Guard
            ans_lower = answer.lower()
            political_entities = ["modi", "patel", "nehru", "gandhi", "singh", "sitharaman"]
            found_entities = [e for e in political_entities if e in ans_lower]
            if len(found_entities) > 2 and len(clean_words) < 50:
                logger.warning(f"[TRANSFORMER] Conflicting names/entities found. Discarding.")
                return "I don’t have verified information for this query.", 0.1, "Validation Failure: Conflicting Entities"
                
            # 4. Capability Over-Claim Guard (Requirement 4)
            # Detects "I can do anything" hallucinations or "all types" loops
            oversell_markers = ["all types of", "everything", "perfectly", "always accurate", "unlimited"]
            if any(marker in ans_lower for marker in oversell_markers):
                if "calculation" in ans_lower:
                    logger.warning(f"[TRANSFORMER] Detected calculation over-claim. Grounding response.")
                    return "The system supports simple arithmetic operations (+, -, *, /). It does not currently support 'all' types of advanced calculations.", 0.8, "Grounded Capability Check"
                else:
                    logger.warning(f"[TRANSFORMER] Detected general over-claim. Discarding.")
                    return "I don’t have verified information to confirm that level of capability. I support specific learning strategies like Retrieval and Rule-based logic.", 0.1, "Validation Failure: Over-Claim"

            # 5. Fabricated/Vague Phrase Detector 
            vague_markers = ["i believe", "i think", "as of my last", "probably", "might be", "not sure"]
            if any(marker in ans_lower for marker in vague_markers):
                logger.warning(f"[TRANSFORMER] Fabricated/Vague hedge detected.")
                return "I don’t have verified information for this query. Please refine the question or provide a trusted source.", 0.1, "Validation Failure: Fabricated Content"

            # Return result
            return answer, 0.85, "Generated by Flan-T5 Transformer"
            
        except Exception as e:
            logger.error(f"Error during transformer inference: {e}")
            return "I don’t have verified information for this query.", 0.0, f"Inference Error: {e}"
    
    def _simulate_response(self, query: str, features: Dict[str, Any]) -> Tuple[str, float, str]:
        """Simulate transformer response for demonstration"""
        query_lower = query.lower()
        
        # Determine response type based on query
        if any(word in query_lower for word in ['why', 'how', 'explain']):
            # Extract potential topic
            topic = self._extract_topic(query)
            response = self.sample_responses['explanation'].format(
                topic=topic if topic else "this concept"
            )
            confidence = 0.82
            reason = "Complex explanation requiring reasoning"
        elif features.get('complexity') == 'high':
            response = self.sample_responses['complex']
            confidence = 0.78
            reason = "High complexity query"
        else:
            concept = self._extract_topic(query)
            response = self.sample_responses['reasoning'].format(
                concept=concept if concept else "the underlying principle"
            )
            confidence = 0.75
            reason = "Reasoning required"
        
        return response, confidence, reason
    
    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query"""
        # Simple extraction - take last few meaningful words
        words = query.lower().split()
        
        # Remove common question words
        stop_words = {'what', 'is', 'how', 'why', 'does', 'do', 'can', 'the', 'a', 'an'}
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        if meaningful_words:
            return ' '.join(meaningful_words[:3])
        return "the topic"


# Example usage
if __name__ == "__main__":
    print("Initializing engine...")
    engine = TransformerEngine()
    
    test_queries = [
        "Explain how neural networks learn",
        "Why is deep learning so effective?",
        "What are the key principles of machine learning?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        answer, confidence, reason = engine.predict(query, {})
        print(f"Answer: {answer}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Reason: {reason}")

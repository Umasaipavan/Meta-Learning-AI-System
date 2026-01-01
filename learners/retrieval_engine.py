"""
Retrieval Engine - Local & Web Knowledge Retrieval
Responsible for:
1. Searching local knowledge base (JSON) using TF-IDF + Cosine Similarity
2. Fetching missing info from Web (Wikipedia API)
"""

import json
import requests
import numpy as np
from typing import Tuple, Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrievalEngine:
    def __init__(self, kb_path: str = "data/knowledge_base.json"):
        self.kb_path = kb_path
        self.documents = []
        self.vectorizer = None
        self.tfidf_matrix = None
        
        # Load local knowledge base
        self._load_knowledge_base()

        # Senior Architecture: In-memory cache for external results
        self.cache = {}
        
        # Robustness: Standard headers to prevent blocking
        self.headers = {
            'User-Agent': 'MetaLearningAssistant/2.0 (senior-refactor; tech-demo)'
        }

    def _load_knowledge_base(self):
        """Load JSON KB and vectorize it"""
        try:
            with open(self.kb_path, 'r') as f:
                data = json.load(f)
                self.documents = [item['text'] for item in data]
                
            if self.documents:
                self.vectorizer = TfidfVectorizer(stop_words='english')
                self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
                logger.info(f"Loaded {len(self.documents)} documents into Retrieval Engine.")
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            self.documents = []

    def predict(self, query: str, features: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Retrieve best match from Local KB or Web.
        Optimized with Senior-level caching and tiered fallback.
        """
        query_norm = query.lower().strip()
        
        # 1. Performance: Check Cache First
        if query_norm in self.cache:
            logger.info(f"[RETRIEVAL] Cache hit: {query_norm}")
            return self.cache[query_norm]

        # 2. Local Knowledge Base Search (Primary Factual Source)
        if self.documents and self.vectorizer:
            try:
                query_vec = self.vectorizer.transform([query])
                cosine_similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
                best_match_idx = np.argmax(cosine_similarities)
                best_score = cosine_similarities[best_match_idx]
                
                # Threshold for local match (e.g., 0.3)
                if best_score > 0.4: # Slightly higher threshold for "Senior-level" accuracy
                    logger.info(f"[RETRIEVAL] High-fidelity Local KB match (score: {best_score:.2f})")
                    result = (
                        self.documents[best_match_idx],
                        float(best_score),
                        f"Local KB (Similarity: {best_score:.2f})"
                    )
                    self.cache[query_norm] = result
                    return result
            except Exception as e:
                logger.error(f"[RETRIEVAL] Vector search failed: {e}")

        # 3. Web Retrieval Tiered Fallback
        # Only fetch if local search fails
        logger.info(f"[RETRIEVAL] Local KB miss. Escalating to Web Tier for: {query_norm}")
        result = self._fetch_from_web_apis(query_norm)
        
        # Cache successful web hits
        if result[1] > 0.1:
            self.cache[query_norm] = result
            
        return result

    def _fetch_from_web_apis(self, query: str) -> Tuple[str, float, str]:
        """
        Attempt to fetch from multiple web APIs in priority order.
        This creates a robust fallback chain for external data.
        """
        # Priority 1: DuckDuckGo Instant Answer (Fast, no auth)
        result = self._fetch_duckduckgo(query)
        if result[0]:  # If answer exists
            return result
        
        # Priority 2: Wikipedia (Detailed, reliable)
        result = self._fetch_wikipedia(query)
        if result[0]:
            return result
        
        # If all APIs fail
        return "", 0.0, "Web retrieval failed (all APIs exhausted)"

    def _fetch_duckduckgo(self, query: str) -> Tuple[str, float, str]:
        """Fetch instant answer from DuckDuckGo API with aggressive timeouts."""
        try:
            url = f"https://api.duckduckgo.com/"
            params = {'q': query, 'format': 'json', 'no_html': 1, 'skip_disambig': 1}
            
            # Robustness: 1.5s timeout as per senior requirements
            response = requests.get(url, params=params, headers=self.headers, timeout=1.5)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('AbstractText') or data.get('Answer') or data.get('Definition', '')
                
                if answer:
                    return (answer, 0.85, "Web Retrieval (DuckDuckGo IA)")
        except requests.exceptions.Timeout:
            logger.warning(f"[RETRIEVAL] DuckDuckGo timeout for: {query}")
        except Exception as e:
            logger.error(f"[RETRIEVAL] DuckDuckGo failed: {e}")
            
        return "", 0.0, "DuckDuckGo unavailable"

    def _fetch_wikipedia(self, query: str) -> Tuple[str, float, str]:
        """Fetch summary from Wikipedia API with fallback logic."""
        try:
            # Senior Topic Extraction: Remove filler words to get to the core entity
            # e.g. "Who is the current Prime Minister of India" -> "Prime Minister of India"
            search_term = query.lower().replace("?", "").replace("who is", "").replace("what is", "")
            search_term = search_term.replace("the current", "").replace("the", "").strip()
            
            # Use underscores for the URL
            search_url_term = search_term.replace(" ", "_").title()
            
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_url_term}"
            response = requests.get(url, headers=self.headers, timeout=2.0)
            
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data:
                    # High confidence for Wikipedia entity pages
                    return (data['extract'], 0.90, f"Wikipedia: {data.get('title')}")
                    
            elif response.status_code == 404:
                # Secondary attempt: Try searching for the query if direct hit fails
                logger.info(f"[RETRIEVAL] Wikipedia direct hit failed for {search_url_term}. Trying search API...")
                search_api_url = "https://en.wikipedia.org/w/api.php"
                search_params = {
                    "action": "query", "list": "search", "srsearch": search_term,
                    "format": "json", "srlimit": 1
                }
                search_res = requests.get(search_api_url, params=search_params, headers=self.headers, timeout=2.0)
                if search_res.status_code == 200:
                    search_data = search_res.json()
                    if search_data.get('query', {}).get('search'):
                        # Found a search result! Try fetching summary of that title
                        top_title = search_data['query']['search'][0]['title']
                        return self._fetch_wikipedia(top_title)
                
        except requests.exceptions.Timeout:
            logger.warning(f"[RETRIEVAL] Wikipedia timeout for: {query}")
        except Exception as e:
            logger.error(f"[RETRIEVAL] Wikipedia failed: {e}")
            
        return "", 0.0, "Wikipedia unavailable"

"""
Experience Store - Memory system for meta-learning
Stores query history, strategy choices, and feedback using Supabase (PostgreSQL)
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class ExperienceStore:
    """
    Persistent storage for system experiences and feedback using Supabase.
    This enables the system to learn from past interactions with a scalable backend.
    """
    
    def __init__(self):
        self.url: str = os.environ.get("SUPABASE_URL")
        self.key: str = os.environ.get("SUPABASE_KEY")
        
        if not self.url or not self.key:
            print("WARNING: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
            print("Please create a .env file with your Supabase credentials.")
            print("Falling back to in-memory storage (data will be lost on restart).")
            self.supabase = None
            self.memory_store = []
            self.strategy_stats_memory = {}
        else:
            try:
                self.supabase: Client = create_client(self.url, self.key)
                # self._init_db() # Supabase tables should be created via SQL Editor/Dashboard usually, 
                                  # but we can try to ensure they exist or just assume user ran migration.
                                  # For this implementation, we assume tables exist.
                print("Connected to Supabase successfully.")
            except Exception as e:
                print(f"Failed to connect to Supabase: {e}")
                self.supabase = None
                self.memory_store = []
    
    def store_experience(
        self,
        query: str,
        strategy: str,
        confidence: float,
        answer: str,
        reason: str,
        features: Dict[str, Any],
        feedback: Optional[int] = None
    ) -> int:
        """Store a new experience"""
        timestamp = datetime.now().isoformat()
        ## features_json = json.dumps(features) # Supabase handles JSON natively often, but let's store as json type or text

        data = {
            "query": query,
            "strategy": strategy,
            "confidence": confidence,
            "answer": answer,
            "reason": reason,
            "feedback": feedback,
            "timestamp": timestamp,
            "features": features 
        }

        if self.supabase:
            try:
                response = self.supabase.table("experiences").insert(data).execute()
                # response.data is a list of inserted rows
                if response.data:
                    experience_id = response.data[0]['id']
                    self._update_strategy_performance(strategy, confidence, feedback)
                    return experience_id
            except Exception as e:
                print(f"Error storing experience in Supabase: {e}")
                # Fallback to local
        
        # Fallback / In-Memory
        if not hasattr(self, 'memory_store'): self.memory_store = []
        data['id'] = len(self.memory_store) + 1
        self.memory_store.append(data)
        return data['id']
    
    def update_feedback(self, experience_id: int, feedback: int) -> bool:
        """Update feedback for an experience"""
        if self.supabase:
            try:
                # Get experience first to know strategy
                exp_res = self.supabase.table("experiences").select("strategy, confidence").eq("id", experience_id).execute()
                if exp_res.data:
                    record = exp_res.data[0]
                    strategy = record['strategy']
                    confidence = record['confidence']
                    
                    # Update feedback
                    self.supabase.table("experiences").update({"feedback": feedback}).eq("id", experience_id).execute()
                    
                    # Update stats
                    self._update_strategy_performance(strategy, confidence, feedback)
                    return True
            except Exception as e:
                print(f"Error updating feedback in Supabase: {e}")
                return False

        # In-memory fallback
        for exp in self.memory_store:
            if exp['id'] == experience_id:
                exp['feedback'] = feedback
                return True
        return False
    
    def _update_strategy_performance(
        self,
        strategy: str,
        confidence: float,
        feedback: Optional[int]
    ):
        """Update strategy performance statistics"""
        timestamp = datetime.now().isoformat()
        
        if self.supabase:
            try:
                # Check existing stats
                res = self.supabase.table("strategy_performance").select("*").eq("strategy", strategy).execute()
                
                if res.data:
                    curr = res.data[0]
                    total_uses = curr['total_uses'] + 1
                    successful_uses = curr['successful_uses'] + (1 if feedback == 1 else 0)
                    
                    # Update average confidence (running average)
                    avg_conf = ((curr['avg_confidence'] * curr['total_uses']) + confidence) / total_uses
                    
                    self.supabase.table("strategy_performance").update({
                        "total_uses": total_uses,
                        "successful_uses": successful_uses,
                        "avg_confidence": avg_conf,
                        "last_updated": timestamp
                    }).eq("strategy", strategy).execute()
                else:
                    # Insert new
                    self.supabase.table("strategy_performance").insert({
                        "strategy": strategy,
                        "total_uses": 1,
                        "successful_uses": 1 if feedback == 1 else 0,
                        "avg_confidence": confidence,
                        "last_updated": timestamp
                    }).execute()
            except Exception as e:
                print(f"Error updating stats in Supabase: {e}")

    
    def get_recent_experiences(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent experiences"""
        if self.supabase:
            try:
                response = self.supabase.table("experiences").select("*").order("timestamp", desc=True).limit(limit).execute()
                return response.data
            except Exception as e:
                print(f"Error fetching recent experiences from Supabase: {e}")
        
        return sorted(self.memory_store, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all strategies"""
        if self.supabase:
            try:
                response = self.supabase.table("strategy_performance").select("*").execute()
                stats = {}
                for row in response.data:
                    total = row['total_uses']
                    success = row['successful_uses']
                    stats[row['strategy']] = {
                        'total_uses': total,
                        'successful_uses': success,
                        'success_rate': success / total if total > 0 else 0.0,
                        'avg_confidence': row['avg_confidence']
                    }
                return stats
            except Exception as e:
                print(f"Error fetching stats from Supabase: {e}")
                return {}

        return {} # In-memory stats not fully implemented for brevity in fallback
    
    def get_similar_queries(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar past queries"""
        # Full text search or semantic search would be ideal here.
        # For now, we'll just return recent ones from Supabase as a placeholder
        # or implement a simple wildcard match if Supabase supports it easily via 'ilike'
        
        if self.supabase:
            try:
                # Simple keyword search on the query column
                # This is basic; a real vector store would be better for "similarity"
                response = self.supabase.table("experiences").select("*").ilike("query", f"%{query}%").limit(limit).execute()
                return response.data
            except Exception as e:
                print(f"Error searching Supabase: {e}")
        
        return []

# Example usage
if __name__ == "__main__":
    store = ExperienceStore()
    # Test logic here...


"""
Real-time Model Monitoring Script
Run this to see live updates when model retrains
"""

import os
import time
from datetime import datetime
import requests

MODEL_FILE = "data/ml_model.joblib"
BACKEND_URL = "http://localhost:8000"

def get_file_timestamp(filepath):
    """Get last modified timestamp of file"""
    if os.path.exists(filepath):
        timestamp = os.path.getmtime(filepath)
        return datetime.fromtimestamp(timestamp)
    return None

def get_stats():
    """Fetch current stats from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/stats", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        return None

def monitor():
    """Monitor model file and stats in real-time"""
    print("=" * 70)
    print("🔥 LIVE MODEL MONITORING")
    print("=" * 70)
    print("\nWatching for:")
    print("  1. Model file updates (retraining)")
    print("  2. Strategy usage stats")
    print("  3. Total queries processed")
    print("\n💡 TIP: Keep this running while you test the UI")
    print("=" * 70)
    print()
    
    last_model_timestamp = get_file_timestamp(MODEL_FILE)
    last_total_queries = 0
    
    iteration = 0
    
    while True:
        iteration += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Header
        print(f"\n[{current_time}] === Refresh #{iteration} ===")
        
        # Check model file
        current_model_timestamp = get_file_timestamp(MODEL_FILE)
        
        if current_model_timestamp:
            if last_model_timestamp and current_model_timestamp > last_model_timestamp:
                print(f"🔥 MODEL RETRAINED! (Updated at {current_model_timestamp.strftime('%H:%M:%S')})")
                print("   └─ File: data/ml_model.joblib")
            else:
                print(f"📊 Model File: Last modified {current_model_timestamp.strftime('%H:%M:%S')}")
            last_model_timestamp = current_model_timestamp
        else:
            print("❌ Model file not found")
        
        # Check stats
        stats = get_stats()
        if stats:
            total = stats.get('total_queries', 0)
            
            if total > last_total_queries:
                print(f"✨ NEW QUERY PROCESSED! (Total: {last_total_queries} → {total})")
                last_total_queries = total
            else:
                print(f"📈 Total Queries: {total}")
            
            # Show strategy stats
            strategy_stats = stats.get('strategy_stats', {})
            print("\n   Strategy Performance:")
            for strategy, info in strategy_stats.items():
                uses = info.get('total_uses', 0)
                rate = info.get('success_rate', 0)
                weight = info.get('weight', 1.0)
                
                if uses > 0:
                    print(f"   ├─ {strategy:15s}: {uses} uses | Success: {rate:.0%} | Weight: {weight:.2f}")
        else:
            print("❌ Cannot connect to backend at http://localhost:8000")
            print("   └─ Make sure: uvicorn app:app --reload is running")
        
        # Wait before next check
        print(f"\n⏳ Refreshing in 5 seconds... (Press Ctrl+C to stop)")
        time.sleep(5)

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped.")

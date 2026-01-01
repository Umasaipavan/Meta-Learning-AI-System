import requests
import json
import time

URL = "http://localhost:8000/respond"
FEEDBACK_URL = "http://localhost:8000/feedback"

test_cases = [
    {
        "name": "Safety Rule (Rule-Based)",
        "query": "Predict my marks for the upcoming exam",
        "expected": "Rule-Based"
    },
    {
        "name": "Local Knowledge (Retrieval)",
        "query": "What is Python?",
        "expected": "Retrieval"
    },
    {
        "name": "Math Calculation (Classical ML)",
        "query": "Calculate 25 * 4",
        "expected": "Classical ML"
    },
    {
        "name": "Deep Reasoning (Transformer)",
        "query": "Explain in detail the implications of AI on modern healthcare and data privacy",
        "expected": "Transformer"
    }
]

def run_tests():
    print("=" * 60)
    print("🚀 STARTING AUTOMATED SYSTEM TEST")
    print("=" * 60)
    
    success_count = 0
    
    for case in test_cases:
        print(f"\n🧪 TESTING: {case['name']}")
        print(f"   Query: {case['query']}")
        
        try:
            start_time = time.time()
            response = requests.post(URL, json={"query": case["query"]}, timeout=15)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                strategy = data.get("strategy")
                answer = data.get("answer")
                latency = end_time - start_time
                
                print(f"   ✅ Strategy: {strategy}")
                print(f"   🕒 Latency: {latency:.2f}s")
                print(f"   📝 Answer Snippet: {answer[:100]}...")
                
                # We use 'in' because sometimes names vary slightly (e.g. 'Classical ML Engine')
                if case['expected'] in strategy:
                    print("   ✨ Result: SUCCESS")
                    success_count += 1
                else:
                    print(f"   🚨 Result: STRATEGY MISMATCH (Expected {case['expected']})")
                
                # Submit feedback to test the learning loop
                exp_id = data.get("experience_id")
                if exp_id:
                    f_resp = requests.post(FEEDBACK_URL, json={"experience_id": exp_id, "feedback": 1}, timeout=5)
                    if f_resp.status_code == 200:
                        print("   🧠 Feedback submitted (Learning triggered)")
            else:
                print(f"   ❌ FAILED: Status Code {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"📊 FINAL REPORT: {success_count}/{len(test_cases)} Tests Passed")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()

# 🔍 Model Verification & Debugging Guide

## ✅ How to Know if Model is Retraining

### Quick Test Script
Run: `test_retraining.bat`

This script will:
1. Show current model file timestamp
2. Guide you through submitting feedback
3. Show updated model file timestamp
4. Confirm if retraining happened

---

## 📋 Manual Verification Checklist

### ✅ **Checklist: Is Retraining Working?**

- [ ] **1. Terminal shows retraining logs**
  ```
  [META-LEARNING] 🧠 POSITIVE FEEDBACK RECEIVED!
  [META-LEARNING] ✅ Auto-learning complete!
  ```

- [ ] **2. Model file updates**
  - Check: `data\ml_model.joblib` timestamp changes after feedback
  - Command: `dir /T:W data\ml_model.joblib`

- [ ] **3. Database stores feedback**
  - Open Supabase → `experiences` table
  - Verify `feedback = 1` for items you marked helpful

- [ ] **4. No errors in terminal**
  - Should NOT see: `[META-LEARNING] ❌ Auto-learning failed`
  - Should NOT see: `Not enough valid new data to retrain`

---

## 🧪 **How to Know if Model is Working**

### **Test Suite: All 4 Strategies**

Run these queries in sequence and verify outputs:

#### Test 1: Rule-Based Strategy
**Query:** `Predict my marks`

**Expected:**
- ✅ Strategy: `Rule-Based`
- ✅ Answer: Contains "safety protocols" or "cannot fulfill"
- ✅ Confidence: 100%
- ✅ Terminal: `[v0] Selected strategy: Rule-Based`

**If fails:**
- ❌ Check: `learners/rule_engine.py` exists
- ❌ Check: `InputAnalyzer` detects rule violations

---

#### Test 2: Retrieval Strategy
**Query:** `What is Python?`

**Expected:**
- ✅ Strategy: `Retrieval`
- ✅ Answer: Definition about programming language
- ✅ Reason: "Local Retrieval" OR "DuckDuckGo" OR "Wikipedia"
- ✅ Terminal: `[v0] Selected strategy: Retrieval`

**If fails:**
- ❌ Check: `data/knowledge_base.json` exists and has content
- ❌ Check: Internet connection (for DuckDuckGo/Wikipedia APIs)
- ❌ Check terminal for: `DuckDuckGo fetch failed` or `Wikipedia fetch failed`

---

#### Test 3: Classical ML Strategy
**Query:** `Calculate 50 / 2`

**Expected:**
- ✅ Strategy: `Classical ML`
- ✅ Answer: "25" or "The quotient is 25"
- ✅ Confidence: 95%
- ✅ Terminal: `[v0] Selected strategy: Classical ML`

**If fails:**
- ❌ Check: `data/ml_model.joblib` exists
- ❌ Check terminal for: `Model not fitted` error
- ❌ Run manually: `python learners/ml_engine.py` (test standalone)

---

#### Test 4: Transformer Strategy
**Query:** `Explain AI in healthcare in detail`

**Expected:**
- ✅ Strategy: `Transformer`
- ✅ Answer: Multi-sentence coherent explanation
- ✅ Confidence: 85%
- ✅ Terminal: `Model loaded successfully on cpu!`

**If fails:**
- ❌ Check startup logs: Should say "Loading Transformer model..."
- ❌ Check: `transformers` and `torch` installed (`pip list | findstr transformers`)
- ❌ Run: `pip install transformers torch sentencepiece`

---

## 🐛 **Common Issues & Fixes**

### Issue 1: "Not enough data to retrain"
**Symptom:** Logs say `Not enough valid new data to retrain (needs 3+)`

**Solution:**
1. You need at least **3** items with `feedback=1` (helpful)
2. Submit 3+ queries, click "Helpful" on each
3. Check Supabase: Count rows where `feedback = 1`

---

### Issue 2: "Retraining failed (non-critical)"
**Symptom:** See `[META-LEARNING] ❌ Auto-learning failed (non-critical): ...`

**Solution:**
1. Check the error message in terminal
2. Common causes:
   - `features` column in Supabase is NULL or malformed
   - No valid `intent` labels in stored data
   - Database connection issue
3. Verify: `features` column in Supabase is `jsonb` type

---

### Issue 3: "Model not fitted"
**Symptom:** Error when trying to predict with Classical ML

**Solution:**
```bash
# Delete old model
del data\ml_model.joblib

# Restart backend (will retrain on startup)
uvicorn app:app --reload
```

---

### Issue 4: Supabase connection errors
**Symptom:** `Supabase credentials missing or invalid`

**Solution:**
1. Check `.env` file exists with:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=eyJhbGc...
   ```
2. Verify credentials in Supabase Dashboard → Settings → API
3. Check terminal: Should say `ExperienceStore initialized with Supabase`

---

## 📊 **Monitoring Dashboard**

### Real-time System Health

**Endpoint:** `http://localhost:8000/health`

**Healthy Response:**
```json
{
  "status": "healthy",
  "components": {
    "analyzer": "operational",
    "meta_controller": "operational",
    "experience_store": "operational"
  }
}
```

---

### Strategy Performance Stats

**Endpoint:** `http://localhost:8000/stats`

**What to Check:**
1. **`total_uses`**: Should increase with each query
2. **`success_rate`**: Should be between 0.0 and 1.0
3. **`weight`**: Should change after feedback (meta-learning!)

**Example:**
```json
{
  "Classical ML": {
    "weight": 1.1,        ← Increased from 1.0 after helpful feedback
    "success_rate": 0.75, ← 3 out of 4 uses were helpful
    "total_uses": 4
  }
}
```

---

## 🎯 **Debugging Commands**

### Check all dependencies installed:
```bash
venv\Scripts\pip list
```
Should show: `supabase`, `transformers`, `torch`, `scikit-learn`, `fastapi`

### Test ML Engine standalone:
```bash
venv\Scripts\python learners\ml_engine.py
```

### Test Transformer standalone:
```bash
venv\Scripts\python learners\transformer_engine.py
```

### Test Retrieval Engine standalone:
```bash
venv\Scripts\python learners\retrieval_engine.py
```

### Check model file:
```bash
dir data\ml_model.joblib
```

### Manual retrain via API:
```bash
curl -X POST http://localhost:8000/retrain
```

---

## 🚨 **Emergency Reset**

If everything is broken:

```bash
# 1. Stop both servers
# 2. Delete model file
del data\ml_model.joblib

# 3. Clear Supabase tables (optional, if corrupted)
# Go to Supabase → SQL Editor → Run:
# DELETE FROM experiences;
# DELETE FROM strategy_performance;

# 4. Restart backend
venv\Scripts\activate
uvicorn app:app --reload

# 5. Restart frontend
npm run dev

# 6. Test with "Calculate 10 + 5"
```

---

## ✅ **Success Indicators**

You know everything is working when:

1. ✅ **All 4 strategies can be triggered** (Rule, Retrieval, ML, Transformer)
2. ✅ **Terminal shows strategy selection logs** (`[v0] Selected strategy: ...`)
3. ✅ **Feedback triggers retraining** (See `[META-LEARNING]` logs)
4. ✅ **Model file timestamp updates** after feedback
5. ✅ **Supabase stores experiences** (Check table has rows)
6. ✅ **Strategy weights change** (Check `/stats` endpoint)

---

**Run `test_retraining.bat` now to verify everything!** 🚀

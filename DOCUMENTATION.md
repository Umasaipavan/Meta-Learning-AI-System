# 🧠 Meta-Learning AI System: Technical Documentation

## 📝 Project Overview
**Meta-Learning: AI That Chooses How to Learn** is a production-grade AI system designed to solve the "one-size-fits-all" problem in artificial intelligence. Instead of using a single heavy model for every task, the system analyzes the incoming query and dynamically selects the most efficient **Learning Strategy**.

The system grows smarter over time by capturing user feedback, updating decision weights, and automatically retraining its underlying machine learning models.

---

## 🛠 Tech Stack
| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14, React, Tailwind CSS | Dashboard UI & Decision Console |
| **UI Components** | Shadcn UI, Framer Motion | Premium visuals & animations |
| **Backend API** | FastAPI (Python 3.10+) | Core logic, AI Orchestration |
| **Database** | Supabase (PostgreSQL) | Experience storage & performance tracking |
| **Generative AI** | Google Flan-T5-Base | Complex reasoning & text generation |
| **Classical ML** | Scikit-Learn (SGD, TF-IDF) | Intent classification & fast math |
| **Search/Web** | Wikipedia API, DuckDuckGo | Real-time factual retrieval |

---

## 🏗 System Architecture (Process Flow)
When a user submits a query, the system follows a 6-step lifecycle:

1.  **Input Analysis:** `InputAnalyzer` extracts features (length, complexity, intent, numerical presence).
2.  **Strategy Selection:** The `Meta-Controller` evaluates features against strategy weights and "Rule Guards".
3.  **Engine Routing:**
    *   `RuleEngine`: Handles safety, blocks violations, and answers FAQs.
    *   `RetrievalEngine`: Searches local JSON knowledge base or Web APIs (Wikipedia/DuckDuckGo).
    *   `MLEngine`: Performs fast intent-based tasks and arithmetic.
    *   `TransformerEngine`: Engages deep learning for complex reasoning.
4.  **Execution & Fallback:** If the primary strategy has low confidence (e.g., < 35%), the system automatically falls back to the `Transformer` for a guaranteed response.
5.  **Experience Logging:** Every interaction is saved to **Supabase** with a unique `experience_id`.
6.  **Learning Loop:** When a user clicks "Helpful", the system updates weights and **automatically retrains** the ML intent classifier using the new data.

---

## 🚀 How to Run the Project

### 1. Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Supabase Account (URL & Key)

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Start Python Backend
```bash
# Activate virtual environment
venv\Scripts\activate

# Launch FastAPI server
uvicorn app:app --reload
```

### 4. Start Next.js Frontend
```bash
# In a new terminal
npm run dev
```
Open `http://localhost:3000` to view the **Decision Dashboard**.

---

## 🧩 Core Modules Explained

### 📁 `meta_controller/strategy_selector.py`
The "Brain" of the system. It contains the logic for choosing between the 4 engines. It maintains dynamic weights for each strategy; if `Retrieval` consistently gets positive feedback, its weight increases, making it the preferred choice for similar future queries.

### 📁 `learners/transformer_engine.py`
A local instance of `google/flan-t5-base`. We have optimized this for CPU inference by implementing **Nucleus Sampling** and a **Loop-Detection Sanity Check** to prevent gibberish repetitions.

### 📁 `feedback/experience_store.py`
Handles all communication with **Supabase**. It ensures that even if the internet is down, the system doesn't crash (graceful degradation).

---

## 📈 Monitoring & Maintenance
The system includes built-in tools for "Live Ops":
*   **Live Monitor:** Run `python monitor_model.py` to see weights and retrains in real-time.
*   **Auto-Test:** Run `python automated_test.py` to verify all 4 strategies in 10 seconds.
*   **Health Check:** Access `http://localhost:8000/health` to verify components.
*   **Stats API:** Access `http://localhost:8000/stats` to see success rates of different strategies.

---

## 🎯 Production-Ready Features
*   **Low Latency:** Optimized API timeouts (1.5s) for fast response times.
*   **Accuracy Layer:** Prioritizes Wikipedia/factual data over generative "guesses" to prevent hallucinations.
*   **Persistence:** All AI "experiences" are permanent in the cloud.
*   **Security:** Rule-based guards to block exam mark predictions and hacking attempts.

---
**Author:** AI Meta-Learning Team  
**Version:** 2.0.0 (Production-Ready)

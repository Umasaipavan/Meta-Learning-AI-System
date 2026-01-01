# Meta-Learning: AI That Chooses How to Learn

A production-ready academic project demonstrating meta-learning through intelligent strategy selection.

## Overview

This system implements **true meta-learning** by selecting which learning strategy to use for each query, rather than relying on a single model. The system learns from feedback to improve its strategy selection over time.

## Key Features

- **Input Analyzer**: Extracts features from user queries
- **Meta-Controller**: Intelligently selects learning strategies (META-LEARNING)
- **Four Learning Strategies**:
  - Rule-Based Engine (safety and FAQs)
  - Retrieval Engine (factual lookups)
  - Classical ML Engine (intent classification)
  - Transformer Engine (complex reasoning)
- **Feedback Loop**: Learns from user feedback
- **Memory Store**: Persists experiences and performance metrics

## Architecture

```
User Query
    ↓
Input Analyzer (Feature Extraction)
    ↓
Meta-Controller (Strategy Selection) ← META-LEARNING
    ↓
Base Learners (4 Strategies)
    ↓
Response Generation
    ↓
Feedback Collection
    ↓
Memory Store (Learning)
```

## Project Structure

```
meta-learning-ai/
├── app.py                      # FastAPI application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── utils/
│   ├── __init__.py
│   └── input_analyzer.py      # Feature extraction
│
├── learners/
│   ├── __init__.py
│   ├── rule_engine.py         # Rule-based strategy
│   ├── retrieval_engine.py    # Retrieval strategy
│   ├── ml_engine.py           # Classical ML strategy
│   └── transformer_engine.py  # Transformer strategy
│
├── meta_controller/
│   ├── __init__.py
│   └── strategy_selector.py   # META-LEARNING controller
│
├── feedback/
│   ├── __init__.py
│   └── experience_store.py    # Memory system
│
└── data/
    ├── knowledge_base.json     # Retrieval knowledge base
    └── experience.db          # SQLite database (created at runtime)
```

## Installation

### Backend (Python)
1. Install Python Environment 
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
venv\Scripts\activate
```

1. Install Python dependencies:
```bash
pip install -r requirements.txt
a
```

4. Run the FastAPI server:
```bash
uvicorn app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend (Next.js)

1. Install dependencies (if not already installed):
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### POST /analyze
Analyze query and extract features
```json
{
  "query": "What is machine learning?"
}
```

### POST /decide
Select learning strategy (demonstrates meta-learning)
```json
{
  "query": "Explain neural networks"
}
```

### POST /respond
Complete pipeline - analyze, decide, execute
```json
{
  "query": "Calculate 5 + 3"
}
```

### POST /feedback
Submit user feedback for learning
```json
{
  "experience_id": 1,
  "feedback": 1
}
```

### GET /stats
Get system statistics and performance

## How Meta-Learning Works

1. **Strategy Selection**: The meta-controller analyzes query features and selects the best learning strategy
2. **Execution**: The selected strategy generates a response
3. **Feedback Collection**: Users rate responses as helpful/not helpful
4. **Weight Updates**: Strategy weights are updated based on success rates
5. **Continuous Improvement**: Over time, the system learns which strategies work best for different query types

## Key Demonstration Points (for Viva/Expo)

1. **Not Just a Chatbot**: System actively chooses between 4 different learning approaches
2. **Visible Decision-Making**: UI clearly shows which strategy was selected and why
3. **Learning Over Time**: Feedback updates strategy weights and success rates
4. **Production-Ready**: FastAPI backend, React frontend, SQLite persistence
5. **Academic Rigor**: Proper separation of concerns, modular architecture

## Testing the System

Try these queries to see different strategies:

- "Predict my exam marks" → Rule-Based (violation)
- "What is machine learning?" → Retrieval (factual lookup)
- "Calculate 5 + 3" → Classical ML (calculation)
- "Explain why deep learning works" → Transformer (complex reasoning)

## Future Enhancements

- Train actual sklearn models for ML strategy
- Load real Hugging Face transformers
- Add web retrieval using Wikipedia API
- Implement user personalization
- Add A/B testing for strategies
- Deploy to production

## License

Academic Project - Free to use and modify

## Authors

[Your Name]
Academic Year: 2024-2025

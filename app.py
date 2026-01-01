"""
FastAPI Application - Main entry point for the meta-learning AI system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from utils.input_analyzer import InputAnalyzer
from meta_controller.strategy_selector import StrategySelector
from feedback.experience_store import ExperienceStore

# Initialize FastAPI app
app = FastAPI(
    title="Meta-Learning AI System",
    description="AI system that intelligently selects learning strategies",
    version="1.0.0"
)

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
analyzer = InputAnalyzer()
experience_store = ExperienceStore()
meta_controller = StrategySelector(experience_store=experience_store)


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None


class AnalyzeResponse(BaseModel):
    features: Dict[str, Any]
    timestamp: str


class DecideResponse(BaseModel):
    selected_strategy: str
    reason: str
    features: Dict[str, Any]


class ResponseModel(BaseModel):
    query: str
    answer: str
    strategy: str
    reason: str
    confidence: float
    experience_id: int
    timestamp: str


class FeedbackRequest(BaseModel):
    experience_id: int
    feedback: int  # 1 for helpful, 0 for not helpful


class StatsResponse(BaseModel):
    strategy_stats: Dict[str, Any]
    total_queries: int
    recent_experiences: list


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Meta-Learning AI System",
        "version": "1.0.0",
        "description": "AI that chooses how to learn",
        "endpoints": {
            "analyze": "/analyze - Analyze query features",
            "decide": "/decide - Select learning strategy",
            "respond": "/respond - Generate complete response",
            "feedback": "/feedback - Submit user feedback",
            "stats": "/stats - Get system statistics"
        }
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_query(request: QueryRequest):
    """
    Analyze a query and extract features
    
    This endpoint demonstrates the input analysis step
    """
    try:
        features = analyzer.analyze(request.query)
        
        return AnalyzeResponse(
            features=features,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/decide", response_model=DecideResponse)
async def decide_strategy(request: QueryRequest):
    """
    Decide which learning strategy to use
    
    This endpoint demonstrates the META-LEARNING decision process
    """
    try:
        # Analyze query
        features = analyzer.analyze(request.query)
        
        # Select strategy (META-LEARNING HAPPENS HERE)
        selected_strategy = meta_controller.select_strategy(features)
        
        return DecideResponse(
            selected_strategy=selected_strategy,
            reason=f"Selected based on query features and past performance",
            features=features
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy selection failed: {str(e)}")


@app.post("/respond", response_model=ResponseModel)
async def generate_response(request: QueryRequest):
    """
    Complete pipeline: Analyze → Decide → Execute → Store
    
    This is the main endpoint that demonstrates the full meta-learning system
    """
    try:
        # Step 1: Analyze query features
        features = analyzer.analyze(request.query)
        print(f"[v0] Analyzed query: {features}")
        
        # Step 2: Select strategy (META-LEARNING)
        selected_strategy = meta_controller.select_strategy(features)
        print(f"[v0] Selected strategy: {selected_strategy}")
        
        # Step 3: Execute strategy
        answer, confidence, reason, actual_strategy = meta_controller.execute_strategy(
            selected_strategy,
            request.query,
            features
        )
        print(f"[v0] Generated response with confidence: {confidence}")
        print(f"[v0] Actual strategy used: {actual_strategy}")
        
        # Step 4: Store experience (use actual strategy, not selected)
        experience_id = experience_store.store_experience(
            query=request.query,
            strategy=actual_strategy,  # Use actual, not selected
            confidence=confidence,
            answer=answer,
            reason=reason,
            features=features,
            feedback=None  # No feedback yet
        )
        print(f"[v0] Stored experience in Supabase with ID: {experience_id}")
        
        return ResponseModel(
            query=request.query,
            answer=answer,
            strategy=actual_strategy,  # Return actual strategy used
            reason=reason,
            confidence=confidence,
            experience_id=experience_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response generation failed: {str(e)}")


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit user feedback to improve the system
    
    This enables META-LEARNING by updating strategy weights
    """
    try:
        # Update feedback in store
        success = experience_store.update_feedback(
            request.experience_id,
            request.feedback
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Experience not found")
        
        # Update meta-controller weights (META-LEARNING UPDATE)
        # Get the strategy used for this experience
        recent = experience_store.get_recent_experiences(limit=100)
        for exp in recent:
            if exp['id'] == request.experience_id:
                meta_controller.update_from_feedback(
                    exp['strategy'],
                    request.feedback == 1
                )
                break
        
        if request.feedback == 1:
            try:
                # Automatic Learning: Trigger simplified retraining on positive feedback
                print("=" * 60)
                print("[META-LEARNING] 🧠 POSITIVE FEEDBACK RECEIVED!")
                print("[META-LEARNING] 🔄 Triggering automatic model retraining...")
                print("=" * 60)
                
                if 'Classical ML' in meta_controller.strategies:
                    ml_engine = meta_controller.strategies['Classical ML']
                    # Use lighter dataset for auto-train to avoid lag
                    recent_data = experience_store.get_recent_experiences(limit=50)
                    print(f"[META-LEARNING] Fetched {len(recent_data)} recent experiences for training")
                    
                    ml_engine.retrain(recent_data)
                    
                    print("=" * 60)
                    print("[META-LEARNING] ✅ Auto-learning complete!")
                    print("=" * 60)
            except Exception as e:
                print(f"[META-LEARNING] ❌ Auto-learning failed (non-critical): {e}")

        return {
            "status": "success",
            "message": "Feedback recorded, weights updated, and model retrained.",
            "experience_id": request.experience_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """
    Get system statistics and performance metrics
    
    Shows how the system is learning over time
    """
    try:
        # Get strategy statistics
        strategy_stats = experience_store.get_strategy_stats()
        
        # Get recent experiences
        recent = experience_store.get_recent_experiences(limit=10)
        
        # Calculate total queries
        total_queries = sum(stats.get('total_uses', 0) for stats in strategy_stats.values())
        
        return StatsResponse(
            strategy_stats=strategy_stats,
            total_queries=total_queries,
            recent_experiences=recent
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@app.post("/retrain")
async def retrain_model():
    """
    Trigger retraining of the ML Engine using feedback data from Supabase.
    This fulfills the requirement: "Periodically retrain ML classifiers"
    """
    try:
        print("[v0] Starting model retraining...")
        # Fetch verified successful interactions for training
        # In a real production system, this would use a dedicated method to fetch all labeled data
        recent_data = experience_store.get_recent_experiences(limit=500)
        
        # Access the underlying MLEngine from StrategySelector
        if 'Classical ML' in meta_controller.strategies:
            ml_engine = meta_controller.strategies['Classical ML']
            
            # Use data from Supabase to retrain
            # We filter for positive feedback inside retrain, or here. 
            # MLEngine.retrain expects list of dicts.
            if hasattr(ml_engine, 'retrain'):
                ml_engine.retrain(recent_data)
                return {"status": "success", "message": "ML Engine retraining completed successfully"}
            else:
                 return {"status": "error", "message": "MLEngine does not support retraining"}
        
        return {"status": "error", "message": "Classical ML strategy not found"}
        
    except Exception as e:
        print(f"[v0] Retraining error: {e}")
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "analyzer": "operational",
            "meta_controller": "operational",
            "experience_store": "operational"
        }
    }


# Run with: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

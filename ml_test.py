
from learners.ml_engine import MLEngine
import logging

logging.basicConfig(level=logging.INFO)
engine = MLEngine()
query = "calculate avg 10,20,30"
answer, conf, reason = engine.predict(query, {})
print(f"Query: {query}")
print(f"Answer: {answer}")
print(f"Conf: {conf}")
print(f"Reason: {reason}")

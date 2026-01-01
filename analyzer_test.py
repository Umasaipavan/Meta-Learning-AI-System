
from utils.input_analyzer import InputAnalyzer
analyzer = InputAnalyzer()
query = "calculate avg 10,20,30"
features = analyzer.analyze(query)
print(f"Query: {query}")
print(f"Intent: {features['intent']}")
print(f"Has Number: {features['has_number']}")

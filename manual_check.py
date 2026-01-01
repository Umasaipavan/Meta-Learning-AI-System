
from meta_controller.strategy_selector import StrategySelector
from utils.input_analyzer import InputAnalyzer

analyzer = InputAnalyzer()
selector = StrategySelector()

query = "calculate avg 10,20,30"
features = analyzer.analyze(query)
print(f"Features: {features}")

strategy = selector.select_strategy(features)
print(f"Selected Strategy: {strategy}")

answer, conf, reason, actual = selector.execute_strategy(strategy, query, features)
print(f"Answer: {answer}")
print(f"Confidence: {conf}")
print(f"Reason: {reason}")
print(f"Actual Strategy: {actual}")

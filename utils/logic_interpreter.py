# utils/logic_interpreter.py
import re

def evaluate_logic(signal: dict, expression: str) -> bool:
    def handle_special_conditions(expr: str) -> str:
        expr = re.sub(
            r"(\bL\d+\b) cross from (-?1) to (-?1)",
            lambda m: f"(signal['{m[1]}'] == {m[3]} and signal.get('prev_{m[1]}', 0) == {m[2]})",
            expr
        )
        expr = re.sub(
            r"histogram rising",
            "(signal['histogram'] > signal.get('prev_histogram', 0))",
            expr
        )
        expr = re.sub(
            r"histogram falling",
            "(signal['histogram'] < signal.get('prev_histogram', 0))",
            expr
        )
        return expr

    try:
        safe_expr = handle_special_conditions(expression)
        allowed = {"Score", "histogram"} | {f"L{i}" for i in range(1, 8)}
        for key in allowed:
            safe_expr = re.sub(rf'\b{key}\b', f"signal['{key}']", safe_expr)
        return eval(safe_expr, {"__builtins__": {}}, {"signal": signal})
    except Exception as e:
        print(f"❌ Error evaluating logic expression: {expression} — {e}")
        return False

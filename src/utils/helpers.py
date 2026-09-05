from typing import Union, Any


def format_currency_inr(amount: Union[int, float]) -> str:
    """Format amount into Indian Rupee numbering format (₹x,xx,xxx)."""
    if amount is None:
        return "₹0"

    try:
        val = float(amount)
    except (ValueError, TypeError):
        return f"₹{amount}"

    is_negative = val < 0
    val = abs(val)

    # Format with 2 decimals if has cents, or round if whole
    if val.is_integer():
        s = str(int(val))
        decimals = ""
    else:
        s = f"{val:.2f}"
        s, decimals = s.split(".")
        decimals = "." + decimals

    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ",".join(groups) + "," + last3

    result = f"₹{formatted}{decimals}"
    return f"-{result}" if is_negative else result


def safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

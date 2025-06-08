def get_priority(plan: str) -> int:
    if plan == "pro":
        priority = 10
    elif plan == "premium":
        priority = 20
    elif plan == "enterprise":
        priority = 30
    else:
        priority = 1
    return priority
    
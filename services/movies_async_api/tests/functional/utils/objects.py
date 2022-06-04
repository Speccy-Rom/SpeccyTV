def contains_text(item: dict, fields: list[str], value: str) -> bool:
    return any(item[field].lower().find(value.lower()) != -1 for field in fields)

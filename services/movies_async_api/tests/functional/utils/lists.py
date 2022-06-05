from typing import Any


def drop_details(items: list[dict], detail_keys: list):
    for item in items:
        for key in detail_keys:
            del item[key]


def get_uuids(items: list[dict]) -> list[str]:
    return [item['uuid'] for item in items]


def get_page_items(items: list, page_number: int, page_size: int):
    begin = page_number * page_size
    return items[begin:begin+page_size]


def is_sorted(items: list[dict], key: str, is_desc: bool = False) -> bool:
    def valid_order(lhs: Any, rhs: Any, desc: bool):
        return lhs >= rhs if desc else rhs >= lhs
    return all(valid_order(items[i][key], items[i+1][key], is_desc) for i in range(len(items) - 1))

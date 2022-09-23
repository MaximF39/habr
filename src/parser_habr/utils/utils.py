import requests.exceptions

__all__ = (
    "singleton",
    "validation_count"
)


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


def validation_count(need: int, get: int, add_info="") -> None:
    if need != get:
        raise requests.exceptions.InvalidJSONError(
            f"Найдено {get} параметров, а ожидалось {need}. " + add_info)

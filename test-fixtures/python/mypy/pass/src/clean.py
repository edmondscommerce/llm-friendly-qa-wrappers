"""A well-typed Python module."""


def greet(name: str) -> str:
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    return a + b


result: str = greet("world")
total: int = add(1, 2)

"""Module with type errors."""


def greet(name: str) -> str:
    return f"Hello, {name}!"


x: int = "not an int"
y: str = 42
z: list[int] = greet("world")

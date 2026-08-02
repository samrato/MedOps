import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        email_regex = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(email_regex, self.value):
            raise ValueError(f"Invalid email address format: {self.value}")

    def __str__(self) -> str:
        return self.value

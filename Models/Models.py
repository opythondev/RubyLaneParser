from dataclasses import dataclass


@dataclass
class Category:
    key: str
    href: str
    objects_count: int

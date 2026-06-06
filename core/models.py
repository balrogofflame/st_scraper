from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    name: str
    price: str


@dataclass(frozen=True)
class ScrapeTarget:
    url: str
    label: str = 'target'
    paginate: bool = True


@dataclass(frozen=True)
class StoreStats:
    store: str
    items: int
    min_mean: float
    min_median: float
    min_std_dev: float
    max_mean: float
    max_median: float
    max_std_dev: float

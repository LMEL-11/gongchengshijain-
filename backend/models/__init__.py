"""SQLAlchemy models for the housing platform.

Import order matters only in that every model module must be imported before
``db.create_all()`` runs — :func:`register_models` guarantees that.
"""
from extensions import db

from .city import City
from .district import District
from .facility import Facility
from .price_history import PriceHistory
from .property import Property
from .property_transaction import PropertyTransaction
from .user import User

__all__ = [
    "db",
    "City",
    "District",
    "Property",
    "PropertyTransaction",
    "User",
    "Facility",
    "PriceHistory",
    "register_models",
]


def register_models() -> None:
    """No-op hook: importing this package already registered every table.

    Kept as an explicit call site in the app factory for readability.
    """
    return None

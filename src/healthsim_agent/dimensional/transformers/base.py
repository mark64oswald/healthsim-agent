"""Base transformer class for dimensional model transformations.

Ported from: healthsim-workspace/packages/core/src/healthsim/dimensional/transformers/base.py
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

import pandas as pd


class BaseDimensionalTransformer(ABC):
    """Abstract base class for all dimensional transformers."""

    @abstractmethod
    def transform(self) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
        """Transform canonical entities to dimensional model.
        
        Returns:
            A tuple of (dimensions_dict, facts_dict).
        """
        pass

    @staticmethod
    def date_to_key(d: date | datetime | str | None) -> int | None:
        """Convert date to YYYYMMDD integer key."""
        if d is None:
            return None

        if isinstance(d, str):
            try:
                d = date.fromisoformat(d)
            except ValueError:
                return None

        if isinstance(d, datetime):
            d = d.date()

        if not isinstance(d, date):
            return None

        return int(d.strftime("%Y%m%d"))

    @staticmethod
    def key_to_date(key: int | None) -> date | None:
        """Convert YYYYMMDD integer key back to date."""
        if key is None:
            return None

        try:
            key_str = str(key)
            if len(key_str) != 8:
                return None
            year = int(key_str[:4])
            month = int(key_str[4:6])
            day = int(key_str[6:8])
            return date(year, month, day)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def calculate_age(dob: date | str | None, as_of_date: date | str | None = None) -> int | None:
        """Calculate age in complete years."""
        if dob is None:
            return None

        if isinstance(dob, str):
            try:
                dob = date.fromisoformat(dob)
            except ValueError:
                return None

        if as_of_date is None:
            as_of_date = date.today()
        elif isinstance(as_of_date, str):
            try:
                as_of_date = date.fromisoformat(as_of_date)
            except ValueError:
                return None

        if not isinstance(dob, date) or not isinstance(as_of_date, date):
            return None

        age = as_of_date.year - dob.year
        if (as_of_date.month, as_of_date.day) < (dob.month, dob.day):
            age -= 1

        return max(0, age)

    @staticmethod
    def age_band(age: int | None) -> str | None:
        """Categorize age into standard demographic bands."""
        if age is None:
            return None

        if age < 0:
            return None

        if age <= 17:
            return "0-17"
        elif age <= 34:
            return "18-34"
        elif age <= 49:
            return "35-49"
        elif age <= 64:
            return "50-64"
        else:
            return "65+"

    @staticmethod
    def clean_string(s: str | None, uppercase: bool = True) -> str | None:
        """Normalize string: strip whitespace, optionally uppercase."""
        if s is None:
            return None

        s = str(s).strip()
        if not s:
            return None

        return s.upper() if uppercase else s

    @staticmethod
    def safe_decimal(
        value: Any, default: Decimal | None = None, precision: int = 2
    ) -> Decimal | None:
        """Safely convert value to Decimal with specified precision."""
        if value is None:
            return default

        try:
            if isinstance(value, Decimal):
                d = value
            elif isinstance(value, float):
                d = Decimal(str(value))
            else:
                d = Decimal(value)

            quantize_str = "0." + "0" * precision if precision > 0 else "0"
            return d.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

        except (InvalidOperation, TypeError, ValueError):
            return default

    @staticmethod
    def safe_int(value: Any, default: int | None = None) -> int | None:
        """Safely convert value to integer."""
        if value is None:
            return default

        try:
            if isinstance(value, float):
                return int(value)
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def get_attr(obj: Any, path: str, default: Any = None) -> Any:
        """Safely get nested attribute from object or dict."""
        if obj is None or not path:
            return default

        parts = path.split(".")
        current = obj

        for part in parts:
            if current is None:
                return default

            if isinstance(current, dict):
                current = current.get(part, None)
                if current is None:
                    return default
            else:
                try:
                    current = getattr(current, part, None)
                    if current is None:
                        return default
                except (AttributeError, TypeError):
                    return default

        return current if current is not None else default


__all__ = ["BaseDimensionalTransformer"]

from datetime import datetime
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func
import re


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Converts CamelCase -> snake_case + "s"
        pattern = r"(?<!^)(?=[A-Z])"  # Negative lookbehind for not start of string and uppercase letter
        return re.sub(pattern, "_", cls.__name__).lower() + "s"


class AssociationTableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Converts CamelCase -> snake_case and adds "s" after every word
        # Negative lookbehind for not start of string and uppercase letter
        pattern = r"(?<!^)(?=[A-Z])"
        words = re.sub(pattern, "_", cls.__name__).lower().split('_')
        words_with_s = [word + 's' for word in words]
        return "_".join(words_with_s)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now())


class ReprMixin:
    def __repr__(self):
        # Dynamically get column names
        attribute_names = [column.name for column in self.__table__.columns]
        # Build a string representation of each column and its value
        attributes = ', '.join(
            f"{name}={getattr(self, name)!r}" for name in attribute_names)

        return f"<{self.__class__.__name__}({attributes})>"

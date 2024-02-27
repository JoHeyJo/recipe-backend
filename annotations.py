from sqlalchemy import INTEGER, BIGINT, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing_extensions import Annotated

str_255 = Annotated[str, mapped_column(String(255))]
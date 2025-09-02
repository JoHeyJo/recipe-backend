from sqlalchemy import INTEGER, BIGINT, String, Boolean
from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

str_255 = Annotated[str, mapped_column(String(255))]
str_unique_255 = Annotated[str, mapped_column(String(255), unique=True)]
str_255_nullable = Annotated[str, mapped_column(String(255), nullable=True)]
boolean = Annotated[Boolean, mapped_column(Boolean, nullable=False)]
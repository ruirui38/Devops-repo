from datetime import datetime
from typing import Optional, Literal

from pydantic import field_validator
from sqlalchemy import Column, Text, TIMESTAMP, text
from sqlmodel import Field, SQLModel


class TodoCreate(SQLModel):
    title: str = Field(max_length=100)
    todo: str = Field(max_length=255)
    status: Literal["InProgress", "Complete", "Cancel"]

    # 空文字のバリデーション
    @field_validator("title", "todo", "status")
    @classmethod
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("入力は必須です")
        return v


class Todo(SQLModel, table=True):
    __tablename__ = "todos"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    todo: str = Field(sa_column=Column(Text, nullable=False))
    status: str = Field(sa_column=Column(Text, nullable=False))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP,
            server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
    )

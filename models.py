from datetime import date
from sqlmodel import SQLModel, Field, Relationship, Column, String
from pydantic import BaseModel


class UserBase(SQLModel):
  username: str
  email: str = Field(sa_column=Column("email", String, unique=True))
  password: str

class UserLogin(BaseModel):
  username: str
  password: str


class User(UserBase, table=True):
  id: int = Field(default=None, primary_key=True)
  salary: "SalarySheet" = Relationship(back_populates="user")

class SalarySheetBase(SQLModel):
  user_id: int = Field(foreign_key='user.id')
  amount: int = 45000
  update_date: date = "2025-01-01"

class SalarySheet(SalarySheetBase, table=True):
  id: int = Field(default=None, primary_key=True)
  user: User = Relationship(back_populates="salary")



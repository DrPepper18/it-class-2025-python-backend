from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(LargeBinary(), nullable=False)

class Stack(Base):
    __tablename__ = "stack"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer(), ForeignKey('users.id'), nullable=False)
    value = Column(Integer())
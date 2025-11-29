from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer


Base = declarative_base()


class Stack(Base):
    id = Column(Integer(), primary_key=True, autoincrement=True)
    value = Column(Integer())
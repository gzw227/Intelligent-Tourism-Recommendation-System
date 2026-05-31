# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)

    behaviors = relationship("UserBehavior", back_populates="user", cascade="all, delete-orphan")


class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    city = Column(String(50), nullable=False)
    address = Column(Text)
    description = Column(Text)
    open_time = Column(String(255))
    image_url = Column(String(500))
    rating = Column(Float, default=0)
    play_time = Column(String(100))
    season = Column(String(100))
    ticket = Column(Text)
    tips = Column(Text)
    source_url = Column(String(500))

    behaviors = relationship("UserBehavior", back_populates="attraction", cascade="all, delete-orphan")


class UserBehavior(Base):
    __tablename__ = "user_behaviors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attraction_id = Column(Integer, ForeignKey("attractions.id"), nullable=False)
    behavior_type = Column(String(20), nullable=False, comment="browse/collect")
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="behaviors")
    attraction = relationship("Attraction", back_populates="behaviors")

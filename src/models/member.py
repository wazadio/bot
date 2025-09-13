from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime


class MemberORM(Base):
    __tablename__ = 'Tbl_Member'
    __table_args__ = {"schema": "dbo"}

    Id = Column(Integer, primary_key=True, index=True)
    FirstName = Column(String, nullable=True)
    LastName = Column(String, nullable=True)
    Phone = Column(String, nullable=True)
    IsMembership = Column(Boolean, nullable=True)
    IsActived = Column(Boolean, nullable=True)
    CreatedTime = Column(DateTime, nullable=True)
    MembershipTime = Column(DateTime, nullable=True)
    BankAccountNumber = Column(String, nullable=True)
    BankName = Column(String, nullable=True)
    BankAccountName = Column(String, nullable=True)
    ReferralCode = Column(String, nullable=True)
    Nik = Column(String, nullable=True)
    HasJoinedTelegramGroup = Column(Boolean, nullable=True)
    UserTelegramId = Column(Integer, nullable=True)

class Member(BaseModel):
    Id: int
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Phone: Optional[str] = None
    IsMembership: Optional[bool] = None
    IsActived: Optional[bool] = None
    CreatedTime: Optional[datetime] = None
    MembershipTime: Optional[datetime] = None
    BankAccountNumber: Optional[str] = None
    BankName: Optional[str] = None
    BankAccountName: Optional[str] = None
    ReferralCode: Optional[str] = None
    Nik: Optional[str] = None
    HasJoinedTelegramGroup: Optional[bool] = None
    UserTelegramId: Optional[int] = None

    class Config:
        from_attributes = True 
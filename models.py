from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

# Table 1: Stores the application data and current status
class RequestRecord(Base):
    __tablename__ = "requests"
    
    id = Column(String, primary_key=True, index=True)
    idempotency_key = Column(String, unique=True, index=True) # NEW: To prevent duplicates
    applicant_name = Column(String)
    age = Column(Integer)
    income = Column(Float)
    documents_provided = Column(Boolean)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    audit_log = relationship("AuditLog", back_populates="request", uselist=False)
# Table 2: Stores the permanent receipt of the decision
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, ForeignKey("requests.id"))
    decision = Column(String)
    trace = Column(Text) # We will save the list of traces as a single string
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    request = relationship("RequestRecord", back_populates="audit_log")
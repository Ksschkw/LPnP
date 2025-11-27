from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.config.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FOREIGN KEYS
    job_id = Column(String(36), ForeignKey('jobs.id'), nullable=False)
    sender_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Message Content
    content = Column(Text, nullable=False)                          # The actual message
    message_type = Column(String(20), default="text")               # text, image, system
    
    # Status
    is_read = Column(Boolean, default=False)                        # Has the receiver seen it?
    
    # Timestamps
    sent_at = Column(DateTime, server_default=func.now())           # When sent
    read_at = Column(DateTime, nullable=True)                       # When read (if read)
    
    # RELATIONSHIP: Who sent this message
    sender = relationship("User", backref="messages_sent")
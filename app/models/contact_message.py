"""Contact message model for storing user messages."""

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class ContactMessage(Base):
    """Model for storing contact form submissions."""

    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)

    # Sender Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=True)

    # Message Content
    message = Column(Text, nullable=False)

    # Optional phone number
    phone = Column(String(50), nullable=True)

    # Status tracking
    status = Column(String(50), default="new")  # new, read, replied, archived

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        """String representation for admin interface."""
        return f"Message from {self.name} ({self.email}) - {self.subject or 'No subject'}"

    @property
    def message_id(self) -> str:
        """Generate a formatted message ID."""
        return f"msg-{self.id}"
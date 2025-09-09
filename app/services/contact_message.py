"""Contact message service for handling contact form submissions."""

import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import DatabaseError, ValidationError
from app.models.contact_message import ContactMessage
from app.schemas.contact import ContactMessageRequest, ContactMessageResponse

logger = logging.getLogger(__name__)


class ContactMessageService:
    """Service for handling contact form submissions."""

    async def create_contact_message(
        self, db: Session, message_data: ContactMessageRequest, language: str = "en"
    ) -> ContactMessageResponse:
        """Create a new contact message."""
        try:
            # Create the contact message
            contact_message = ContactMessage(
                name=message_data.name,
                email=message_data.email,
                subject=message_data.subject,
                message=message_data.message,
                phone=message_data.phone,
                status="new",
            )

            db.add(contact_message)
            db.commit()
            db.refresh(contact_message)

            logger.info(
                f"Contact message created: {contact_message.message_id} "
                f"from {contact_message.email}"
            )

            # Send email notifications asynchronously
            try:
                # Import here to avoid circular imports
                from app.services.email import email_service

                # Send notification to admin (non-blocking)
                await email_service.send_contact_notification(db, contact_message)

                # Send confirmation to user (non-blocking)
                await email_service.send_contact_confirmation(contact_message, language)

            except Exception as e:
                # Email failure should not prevent the contact message from being created
                logger.error(f"Failed to send email notifications: {str(e)}")

            return ContactMessageResponse(
                success=True,
                message="Mensaje enviado correctamente",
                id=contact_message.message_id,
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating contact message: {str(e)}")
            raise DatabaseError(f"Database error: {str(e)}")

    def get_contact_message(
        self, db: Session, message_id: int
    ) -> Optional[ContactMessage]:
        """Get a contact message by ID."""
        try:
            return (
                db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving contact message: {str(e)}")
            raise DatabaseError(f"Database error: {str(e)}")

    def update_message_status(
        self, db: Session, message_id: int, status: str
    ) -> Optional[ContactMessage]:
        """Update message status (new, read, replied, archived)."""
        try:
            valid_statuses = ["new", "read", "replied", "archived"]
            if status not in valid_statuses:
                raise ValidationError(
                    "status",
                    status,
                    f"Status must be one of: {', '.join(valid_statuses)}",
                )

            message = self.get_contact_message(db, message_id)
            if not message:
                return None

            message.status = status
            db.commit()
            db.refresh(message)

            logger.info(f"Message {message.message_id} status updated to {status}")
            return message

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating message status: {str(e)}")
            raise DatabaseError(f"Database error: {str(e)}")


# Global service instance
contact_message_service = ContactMessageService()

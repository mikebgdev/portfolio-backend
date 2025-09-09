"""Email service for sending notifications."""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib
from sqlalchemy.orm import Session

from app.config import settings
from app.models.contact import Contact
from app.models.contact_message import ContactMessage

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self.email_enabled = settings.email_enabled
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls

    def _get_dynamic_from_name(self, db: Session) -> str:
        """Get sender name dynamically from contact info."""
        try:
            contact = db.query(Contact).first()
            if contact and contact.sender_name:
                return contact.sender_name
            return "Portfolio Contact"
        except Exception:
            return "Portfolio Contact"

    def _get_dynamic_subject(self, db: Session) -> str:
        """Get email subject dynamically."""
        try:
            contact = db.query(Contact).first()
            if contact:
                domain = (
                    self.smtp_username.split("@")[-1]
                    if "@" in self.smtp_username
                    else "Portfolio"
                )
                return f"Nuevo mensaje de contacto - {domain}"
            return "Nuevo mensaje de contacto - Portfolio"
        except Exception:
            return "Nuevo mensaje de contacto - Portfolio"

    def _get_dynamic_from_email(self, db: Session) -> str:
        """Get sender email dynamically from contact info or config."""
        try:
            # First try to get from contact database
            contact = db.query(Contact).first()
            if contact and contact.email:
                return contact.email

            # Fallback to config username (which is the Gmail account)
            return self.smtp_username
        except Exception:
            # Final fallback
            return self.smtp_username

    async def send_email(
        self,
        to_email: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> bool:
        """Send an email using Gmail SMTP."""
        if not self.email_enabled:
            logger.info("Email sending is disabled")
            return True

        if not self.smtp_username or not self.smtp_password:
            logger.warning("Gmail SMTP credentials not configured")
            return False

        # Get dynamic from_name if not provided and db is available
        if not from_name and db:
            from_name = self._get_dynamic_from_name(db)
        elif not from_name:
            from_name = "Portfolio Contact"

        # Get dynamic from_email if not provided and db is available
        if not from_email and db:
            from_email = self._get_dynamic_from_email(db)
        elif not from_email:
            from_email = self.smtp_username

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject

            # Gmail SMTP limitation: Gmail will override the From field with the authenticated account
            # We use the Gmail account as From and set Reply-To for the desired contact email
            gmail_from = f"{from_name} <{self.smtp_username}>"
            message["From"] = gmail_from
            message["To"] = to_email

            # If the desired from_email is different from Gmail account, set Reply-To
            if from_email and from_email.lower() != self.smtp_username.lower():
                message["Reply-To"] = f"{from_name} <{from_email}>"
                logger.info(f"Set Reply-To header: {from_name} <{from_email}>")

            # Add text content
            text_part = MIMEText(text_content, "plain", "utf-8")
            message.attach(text_part)

            # Add HTML content if provided
            if html_content:
                html_part = MIMEText(html_content, "html", "utf-8")
                message.attach(html_part)

            # Send email via Gmail SMTP
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=self.smtp_use_tls,
                username=self.smtp_username,
                password=self.smtp_password,
            )

            logger.info(
                f"Email sent successfully via Gmail to {to_email} (From: {gmail_from})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send email via Gmail to {to_email}: {str(e)}")
            return False

    async def send_contact_notification(
        self, db: Session, contact_message: ContactMessage
    ) -> bool:
        """Send notification email when a new contact message is received."""
        try:
            # Get contact info to determine where to send the notification
            contact = db.query(Contact).first()
            if not contact:
                logger.error("No contact information found for email notification")
                return False

            # Prepare email content with dynamic subject
            subject = self._get_dynamic_subject(db)

            # Text content
            text_content = f"""
Nuevo mensaje de contacto recibido:

Nombre: {contact_message.name}
Email: {contact_message.email}
Teléfono: {contact_message.phone or 'No proporcionado'}
Asunto: {contact_message.subject or 'Sin asunto'}

Mensaje:
{contact_message.message}

---
ID del mensaje: {contact_message.message_id}
Fecha: {contact_message.created_at}
            """.strip()

            # HTML content
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Nuevo mensaje de contacto</h2>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #495057; margin-top: 0;">Información del contacto</h3>
                        <p><strong>Nombre:</strong> {contact_message.name}</p>
                        <p><strong>Email:</strong> <a href="mailto:{contact_message.email}">{contact_message.email}</a></p>
                        <p><strong>Teléfono:</strong> {contact_message.phone or 'No proporcionado'}</p>
                        <p><strong>Asunto:</strong> {contact_message.subject or 'Sin asunto'}</p>
                    </div>
                    
                    <div style="background-color: #e9ecef; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #495057; margin-top: 0;">Mensaje</h3>
                        <p style="white-space: pre-wrap;">{contact_message.message}</p>
                    </div>
                    
                    <div style="color: #6c757d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p>ID del mensaje: {contact_message.message_id}</p>
                        <p>Fecha: {contact_message.created_at}</p>
                    </div>
                </body>
            </html>
            """.strip()

            # Send email to the contact email from the database
            return await self.send_email(
                to_email=contact.email,
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                from_email=self.smtp_username,
                db=db,
            )

        except Exception as e:
            logger.error(f"Failed to send contact notification: {str(e)}")
            return False

    async def send_contact_confirmation(
        self, contact_message: ContactMessage, language: str = "en"
    ) -> bool:
        """Send confirmation email to the person who sent the contact message."""
        try:
            # Get sender name from database
            from app.database import SessionLocal

            db_temp = SessionLocal()
            sender_name = self._get_dynamic_from_name(db_temp)
            db_temp.close()

            # Language-specific content
            if language == "es":
                subject = "Confirmación - Hemos recibido tu mensaje"
                greeting = f"Hola {contact_message.name}"
                thanks_message = "Gracias por contactarnos. Hemos recibido tu mensaje y te responderemos lo antes posible."
                your_message_label = "Tu mensaje"
                subject_label = "Asunto"
                no_subject = "Sin asunto"
                signature = f"Saludos,<br><strong>{sender_name}</strong>"
                auto_message = "Este es un mensaje automático. Por favor, no responder a este email."
                html_title = "¡Gracias por tu mensaje!"
            else:
                subject = "Confirmation - We have received your message"
                greeting = f"Hello {contact_message.name}"
                thanks_message = "Thank you for contacting us. We have received your message and will respond as soon as possible."
                your_message_label = "Your message"
                subject_label = "Subject"
                no_subject = "No subject"
                signature = f"Best regards,<br><strong>{sender_name}</strong>"
                auto_message = (
                    "This is an automatic message. Please do not reply to this email."
                )
                html_title = "Thank you for your message!"

            # Format signature for text content
            text_signature = (
                signature.replace("<br>", "\n")
                .replace("<strong>", "")
                .replace("</strong>", "")
            )

            # Text content
            text_content = f"""
{greeting},

{thanks_message}

{your_message_label}:
{contact_message.subject or no_subject}
{contact_message.message}

{text_signature}
            """.strip()

            # HTML content
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">{html_title}</h2>
                    
                    <p>{greeting},</p>
                    
                    <p>{thanks_message}</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #495057; margin-top: 0;">{your_message_label}</h3>
                        <p><strong>{subject_label}:</strong> {contact_message.subject or no_subject}</p>
                        <p style="white-space: pre-wrap;">{contact_message.message}</p>
                    </div>
                    
                    <p>{signature}</p>
                    
                    <div style="color: #6c757d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p>{auto_message}</p>
                    </div>
                </body>
            </html>
            """.strip()

            # Send confirmation email to the sender
            return await self.send_email(
                to_email=contact_message.email,
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                from_email=self.smtp_username,
            )

        except Exception as e:
            logger.error(f"Failed to send contact confirmation: {str(e)}")
            return False


# Global service instance
email_service = EmailService()

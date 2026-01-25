"""Email service for sending emails via Resend."""

from functools import lru_cache
from typing import Any

import resend

from src.app.config import Settings
from src.app.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails using Resend."""

    def __init__(self, settings: Settings) -> None:
        """Initialize email service with settings."""
        self.settings = settings
        self.from_email = settings.RESEND_FROM_EMAIL
        self.from_name = settings.RESEND_FROM_NAME
        self._configured = bool(settings.RESEND_API_KEY)

        if self._configured:
            resend.api_key = settings.RESEND_API_KEY

    @property
    def is_configured(self) -> bool:
        """Check if email service is configured."""
        return self._configured

    def _get_from_address(self) -> str:
        """Get formatted from address."""
        return f"{self.from_name} <{self.from_email}>"

    async def send_email(
        self,
        to: str | list[str],
        subject: str,
        html: str,
        *,
        reply_to: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        tags: list[dict[str, str]] | None = None,
    ) -> dict[str, Any] | None:
        """
        Send an email using Resend.

        Args:
            to: Recipient email address(es)
            subject: Email subject
            html: HTML content of the email
            reply_to: Optional reply-to address
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            tags: Optional tags for tracking

        Returns:
            Resend API response or None if not configured/error
        """
        if not self._configured:
            logger.warning(
                "email_not_configured",
                message="Email service not configured, skipping email send",
                to=to,
                subject=subject,
            )
            return None

        try:
            params: dict[str, Any] = {
                "from_": self._get_from_address(),
                "to": to if isinstance(to, list) else [to],
                "subject": subject,
                "html": html,
            }

            if reply_to:
                params["reply_to"] = reply_to
            if cc:
                params["cc"] = cc
            if bcc:
                params["bcc"] = bcc
            if tags:
                params["tags"] = tags

            # Resend uses sync API, we run it directly
            # In production, consider using a worker queue
            response = resend.Emails.send(params)

            logger.info(
                "email_sent",
                to=to,
                subject=subject,
                email_id=response.get("id") if isinstance(response, dict) else None,
            )

            return response

        except Exception as e:
            logger.error(
                "email_send_error",
                error=str(e),
                to=to,
                subject=subject,
            )
            raise

    async def send_invitation_email(
        self,
        to: str,
        invitee_name: str,
        organization_name: str,
        inviter_name: str,
        role_name: str,
        invitation_link: str,
        expires_in_days: int = 7,
    ) -> dict[str, Any] | None:
        """
        Send an organization invitation email.

        Args:
            to: Invitee email address
            invitee_name: Name of the person being invited
            organization_name: Name of the organization
            inviter_name: Name of the person sending the invite
            role_name: Role being assigned
            invitation_link: Link to accept the invitation
            expires_in_days: Number of days until invitation expires

        Returns:
            Resend API response or None if not configured
        """
        subject = f"Convite para {organization_name} - Quero Plantão"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Convite para {organization_name}</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Quero Plantão</h1>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e1e1e1; border-top: none; border-radius: 0 0 10px 10px;">
                <h2 style="color: #333; margin-top: 0;">Olá{", " + invitee_name if invitee_name else ""}!</h2>
                
                <p>Você foi convidado(a) por <strong>{inviter_name}</strong> para fazer parte da organização <strong>{organization_name}</strong> no Quero Plantão.</p>
                
                <p>Sua função será: <strong>{role_name}</strong></p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invitation_link}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Aceitar Convite
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    Este convite expira em <strong>{expires_in_days} dias</strong>.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    Se você não esperava este convite, pode ignorar este email.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e1e1e1; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    Se o botão não funcionar, copie e cole este link no navegador:<br>
                    <a href="{invitation_link}" style="color: #667eea;">{invitation_link}</a>
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>&copy; 2026 Quero Plantão. Todos os direitos reservados.</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to=to,
            subject=subject,
            html=html,
            tags=[
                {"name": "type", "value": "invitation"},
                {"name": "organization", "value": organization_name},
            ],
        )


@lru_cache
def get_email_service() -> EmailService:
    """Get cached email service instance."""
    from src.app.dependencies import get_settings

    return EmailService(get_settings())

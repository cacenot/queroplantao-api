"""PDF generation service using WeasyPrint."""

import base64
from io import BytesIO
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from src.app.logging import get_logger

logger = get_logger(__name__)


# Path to assets folder
ASSETS_PATH = Path(__file__).parent.parent.parent.parent / "assets" / "images"


def format_cpf(value: str | None) -> str:
    """Format CPF as XXX.XXX.XXX-XX."""
    if not value:
        return "-"
    cpf = "".join(filter(str.isdigit, value))
    if len(cpf) != 11:
        return value
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def format_cep(value: str | None) -> str:
    """Format CEP as XXXXX-XXX."""
    if not value:
        return "-"
    cep = "".join(filter(str.isdigit, value))
    if len(cep) != 8:
        return value
    return f"{cep[:5]}-{cep[5:]}"


def format_phone(value: str | None) -> str:
    """Format phone number for display."""
    if not value:
        return "-"
    # E.164 format: +5511999999999
    phone = value.replace("+", "").replace(" ", "").replace("-", "")
    if len(phone) == 13 and phone.startswith("55"):
        # Brazilian number
        ddd = phone[2:4]
        number = phone[4:]
        if len(number) == 9:
            return f"({ddd}) {number[:5]}-{number[5:]}"
        elif len(number) == 8:
            return f"({ddd}) {number[:4]}-{number[4:]}"
    return value


class PDFGeneratorService:
    """
    Service for generating PDFs from HTML templates using WeasyPrint.

    Uses Jinja2 for template rendering and WeasyPrint for PDF generation.
    """

    def __init__(self, templates_dir: Path) -> None:
        """
        Initialize PDF generator service.

        Args:
            templates_dir: Path to directory containing HTML templates.
        """
        self._templates_dir = templates_dir
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        # Register custom filters
        self._env.filters["format_cpf"] = format_cpf
        self._env.filters["format_cep"] = format_cep
        self._env.filters["format_phone"] = format_phone

    def _load_image_as_base64(self, image_path: Path) -> str:
        """Load an image file and return as base64 encoded string."""
        if not image_path.exists():
            logger.warning("image_not_found", path=str(image_path))
            return ""
        
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_logo_base64(self) -> str:
        """Get the logo image as base64."""
        logo_path = ASSETS_PATH / "logo.png"
        return self._load_image_as_base64(logo_path)

    def get_placeholder_base64(self) -> str:
        """Get the avatar placeholder as base64."""
        placeholder_path = ASSETS_PATH / "avatar-placeholder.png"
        return self._load_image_as_base64(placeholder_path)

    async def generate_pdf(
        self,
        template_name: str,
        context: dict[str, Any],
    ) -> bytes:
        """
        Generate a PDF from an HTML template.

        Args:
            template_name: Name of the template file (e.g., 'screening_report.html').
            context: Dictionary of variables to pass to the template.

        Returns:
            PDF content as bytes.

        Raises:
            Exception: If PDF generation fails.
        """
        logger.info("generating_pdf", template=template_name)

        try:
            # Load and render template
            template = self._env.get_template(template_name)
            html_content = template.render(**context)

            # Generate PDF
            pdf_buffer = BytesIO()
            HTML(string=html_content, base_url=str(self._templates_dir)).write_pdf(
                pdf_buffer
            )

            pdf_bytes = pdf_buffer.getvalue()
            logger.info(
                "pdf_generated",
                template=template_name,
                size_bytes=len(pdf_bytes),
            )

            return pdf_bytes

        except Exception as e:
            logger.error(
                "pdf_generation_failed",
                template=template_name,
                error=str(e),
            )
            raise

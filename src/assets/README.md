# Assets

This folder contains static assets used by the application.

## Images

- `logo.png` - Quero Plantão logo (used in PDF reports)
- `avatar-placeholder.png` - Default avatar placeholder for professionals without photo

## Usage

These images are used by the PDF generation service for compliance reports.

### Adding New Images

1. Place the image file in `src/assets/images/`
2. Reference it using the `ASSETS_PATH` constant from `src/app/config.py`

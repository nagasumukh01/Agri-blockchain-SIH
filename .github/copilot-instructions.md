# Copilot Instructions for blockchain_agri

## Project Overview
This project implements a blockchain-based agricultural supply chain tracking system. It uses Python and Flask to provide a web interface for different user roles (farmer, distributor, retailer, consumer) to interact with the blockchain, add data, and view the chain. QR codes are generated for each block for traceability.

## Key Components
- `blockchain.py`: Core blockchain logic (block structure, chain management, validation).
- `app.py`: Flask web app, routes for each user role, blockchain interaction, QR code generation, and rendering HTML templates.
- `price_model.py`: Contains pricing logic or models (details in file).
- `templates/`: HTML templates for each user role and chain viewing.
- `static/`: Static assets (CSS, QR codes).
- `requirements.txt`: Python dependencies (Flask, qrcode, etc.).

## Developer Workflows
- **Run the app:**
  ```powershell
  python app.py
  ```
  The Flask server runs locally (default: http://127.0.0.1:5000/).
- **Add dependencies:**
  Add to `requirements.txt` and run:
  ```powershell
  pip install -r requirements.txt
  ```
- **Debugging:**
  Use print statements or Flask debug mode. No custom logging framework is present.
- **Testing:**
  No dedicated test suite is present. Manual testing via the web UI is standard.

## Project-Specific Patterns
- **Role-based routes:** Each user type (farmer, distributor, retailer, consumer) has a dedicated route and template (e.g., `/farmer`, `/distributor`).
- **Blockchain state:** The blockchain is kept in-memory (not persisted). Restarting the app resets the chain.
- **QR code generation:** Each new block generates a QR code image saved in `static/qr_codes/`.
- **Data flow:**
  - User submits data via a form (HTML template)
  - Data is added to the blockchain (via `blockchain.py`)
  - QR code is generated for the new block
  - Chain can be viewed at `/view_chain`

## Integration Points
- **External dependencies:** Flask, qrcode, and any listed in `requirements.txt`.
- **No database:** All data is in-memory; no external DB integration.

## Conventions
- Use snake_case for Python variables and functions.
- HTML templates use Jinja2 syntax.
- Static files (CSS, QR codes) are in `static/`.
- Do not add persistent storage unless explicitly requested.

## Examples
- To add a new user role, create a new route in `app.py`, a corresponding HTML template, and update blockchain logic if needed.
- To change block data structure, edit `blockchain.py` and update form handling in `app.py`.

---
For questions or unclear patterns, review `app.py` and `blockchain.py` for the latest logic. Update this file if major architectural changes are made.

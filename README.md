# Blockchain-Based Agricultural Supply Chain Tracking System

A comprehensive web application that implements blockchain technology for transparent and traceable agricultural supply chain management. The system allows different stakeholders (farmers, distributors, retailers, consumers) to add data to the blockchain and track products through the entire supply chain using QR codes.

## Features

### 🔗 Blockchain Integration
- Immutable ledger for supply chain data
- Block validation and chain integrity
- Product tracking through all stages

### 👥 Multi-Role Support
- **Farmer**: Add initial product data with pricing
- **Distributor**: Update distribution details
- **Retailer**: Add retail pricing and location
- **Consumer**: View complete product journey

### 📱 QR Code Traceability
- Generate QR codes for each blockchain block
- Scan QR codes to view product history
- Mobile-friendly traceability

### 💰 Smart Pricing Model
- ML-based price prediction using crop data
- Weather integration for pricing adjustments
- Quality and quantity-based pricing

### 🌤️ Weather Integration
- Real-time weather data for pricing decisions
- Location-based weather information

### 📊 Data Visualization
- View complete blockchain
- Track product journey
- Supply chain analytics

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone https://github.com/nagasumukh01/Agri-blockchain-SIH.git
cd Agri-blockchain-SIH
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

### Accessing Different Roles
- **Home**: `http://127.0.0.1:5000/`
- **Farmer**: `http://127.0.0.1:5000/farmer`
- **Distributor**: `http://127.0.0.1:5000/distributor`
- **Retailer**: `http://127.0.0.1:5000/retailer`
- **Consumer**: `http://127.0.0.1:5000/consumer`
- **View Chain**: `http://127.0.0.1:5000/view_chain`

### Adding Data to Blockchain
1. Select your role (Farmer/Distributor/Retailer)
2. Fill in the product details
3. Submit the form
4. QR code will be generated for traceability

### Tracking Products
1. Scan QR code or use tracking link
2. View complete product journey
3. See pricing history and locations

## Project Structure

```
blockchain_agri/
├── app.py                 # Main Flask application
├── blockchain.py          # Blockchain implementation
├── price_model.py         # Pricing logic and ML models
├── ml_price_predictor.py  # Machine learning price prediction
├── weather.py             # Weather service integration
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── index.html
│   ├── farmer.html
│   ├── distributor.html
│   ├── retailer.html
│   ├── consumer.html
│   ├── view_chain.html
│   └── track.html
├── static/                # Static assets
│   ├── style.css
│   └── qr_codes/          # Generated QR codes
└── __pycache__/           # Python cache files
```

## Technologies Used

- **Backend**: Python Flask
- **Blockchain**: Custom Python implementation
- **Machine Learning**: Scikit-learn, Joblib
- **Data Processing**: Pandas, NumPy
- **QR Codes**: qrcode, Pillow
- **Weather API**: OpenWeatherMap
- **Frontend**: HTML, CSS, JavaScript
- **CORS**: Flask-CORS

## API Endpoints

- `GET /` - Home page
- `GET /farmer` - Farmer data entry
- `POST /farmer` - Submit farmer data
- `GET /distributor` - Distributor data entry
- `POST /distributor` - Submit distributor data
- `GET /retailer` - Retailer data entry
- `POST /retailer` - Submit retailer data
- `GET /consumer` - Consumer tracking
- `GET /view_chain` - View blockchain
- `GET /track/<block_id>` - Track specific product

## Data Persistence

- Blockchain data is saved to `blockchain_data.json`
- QR codes are stored in `static/qr_codes/`
- ML models are saved as `.joblib` files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for Smart India Hackathon (SIH)
- Uses OpenWeatherMap API for weather data
- Implements basic blockchain concepts for educational purposes
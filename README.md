# Tendy API - Live Token Analysis with Historical Tracking

A FastAPI-based service that monitors cryptocurrency tokens, fetches live data from Moralis and RugCheck APIs, and provides GPT-powered analysis with historical evolution tracking.

## Features

### 🔄 Live Data Fetching
- **Moralis API Integration**: Fetches token metadata, pricing, and market data
- **RugCheck API Integration**: Retrieves rug scores, honeypot detection, holder counts, and market cap
- **Periodic Updates**: Automatically updates token data every 5 minutes

### 📊 Historical Analysis
- **Evolution Tracking**: Compares current data with previous analysis
- **Trend Analysis**: Tracks market cap changes, holder growth, rug score evolution
- **Data Persistence**: Stores historical data in JSON format

### 🧠 GPT Analysis
- **Enhanced Prompts**: Includes evolution data in GPT analysis
- **Comparative Analysis**: Highlights significant changes since last analysis
- **Risk Assessment**: Provides investment recommendations based on trends

### 🔌 API Endpoints
- `GET /tokens` - Retrieve all monitored tokens
- `POST /new_token` - Add new token to monitoring
- `GET /analyses/history` - Get complete analysis history
- `GET /analyses/history/{token_address}` - Get specific token history

## Installation

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export MORALIS_API_KEY="your-moralis-api-key"
```

3. **Start the Server**
```bash
python -m uvicorn tendy_api:app --host 0.0.0.0 --port 8000
```

## Usage

### Adding a New Token
```bash
curl -X POST "http://localhost:8000/new_token" \
  -H "Content-Type: application/json" \
  -d '{
    "token_address": "0x1234567890abcdef1234567890abcdef12345678",
    "name": "Example Token",
    "symbol": "EXT",
    "mc": 1000000,
    "holders": 500
  }'
```

### Getting Token Data
```bash
curl -X GET "http://localhost:8000/tokens"
```

### Checking Analysis History
```bash
curl -X GET "http://localhost:8000/analyses/history"
```

### Getting Specific Token History
```bash
curl -X GET "http://localhost:8000/analyses/history/0x1234567890abcdef1234567890abcdef12345678"
```

## Demo

Run the evolution tracking demo:
```bash
python demo_evolution.py
```

This will:
1. Create sample tokens with mock data
2. Simulate market changes over 3 cycles
3. Show evolution tracking in action
4. Generate historical analysis data

## Data Structure

### Token Data
```json
{
  "token_address": "0x...",
  "name": "Token Name",
  "symbol": "SYM",
  "mc": 1000000,
  "holders": 1000,
  "rugscore": 2.5,
  "honeypot": false,
  "lp_locked": true,
  "top_holders": ["0x..."],
  "price_usd": 0.001,
  "timestamp": "2025-07-15T07:19:39.583247"
}
```

### Analysis History Entry
```json
{
  "timestamp": "2025-07-15T07:19:39.583247",
  "token_data": { /* full token data */ },
  "analysis": "GPT analysis text",
  "evolution": {
    "Market Cap": "$1,000,000 → $1,500,000 (+50.0%)",
    "Holders": "1,000 → 1,200 (+20.0%)",
    "Rug Score": "2.5 → 2.0 (-0.5)"
  }
}
```

## Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for GPT analysis
- `MORALIS_API_KEY`: Moralis API key for token data

### Optional Configuration
- Analysis frequency: Currently set to 5 minutes (300 seconds)
- History retention: Last 100 entries per token
- API timeouts: 10 seconds for external API calls

## Architecture

### Core Components
1. **`tendy_api.py`**: Main FastAPI application with periodic analysis
2. **`analyze_with_gpt.py`**: GPT analysis and evolution formatting
3. **`demo_evolution.py`**: Demonstration script
4. **`test_tendy_api.py`**: Test suite

### Data Flow
1. **Token Registration**: Tokens added via API or loaded from storage
2. **Periodic Analysis**: Every 5 minutes:
   - Fetch live data from Moralis and RugCheck
   - Compare with previous analysis
   - Generate GPT analysis with evolution data
   - Store results in history
3. **API Access**: Historical data accessible via REST endpoints

### Error Handling
- **API Failures**: Graceful handling of external API errors
- **Missing Keys**: Clear warnings when API keys not configured
- **Network Issues**: Timeout handling and retry logic
- **Data Validation**: Input validation for token data

## Testing

Run the test suite:
```bash
python test_tendy_api.py
```

Tests include:
- Token storage and retrieval
- Analysis history persistence
- Evolution data comparison
- API import functionality

## File Structure

```
tendy_api/
├── tendy_api.py              # Main FastAPI application
├── analyze_with_gpt.py       # GPT analysis module
├── demo_evolution.py         # Evolution tracking demo
├── test_tendy_api.py        # Test suite
├── requirements.txt          # Dependencies
├── tokens.json              # Token storage (auto-generated)
├── analyses_history.json    # Analysis history (auto-generated)
└── .gitignore              # Git ignore rules
```

## Evolution Tracking Example

The system tracks evolution across key metrics:

```
🔄 Evolution since last analysis:
  • Market Cap: $1,000,000 → $1,500,000 (+50.0%)
  • Holders: 1,000 → 1,200 (+20.0%)
  • Rug Score: 2.5 → 2.0 (-0.5)
  • Time Elapsed: Last update: 2025-07-15T07:19:39 → Current: 2025-07-15T07:19:44
```

This evolution data is included in the GPT prompt for enhanced analysis.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
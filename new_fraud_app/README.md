# Fraud Detection System

A sophisticated fraud detection system using Azure AI services and Clean Architecture principles.

## Features

- Clean Architecture implementation
- Multi-agent fraud detection system
- Azure AI integration
- Asynchronous processing
- Type-safe transaction handling
- Configurable settings
- Comprehensive logging

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Azure credentials:
   ```
   AZURE_AI_ENDPOINT=your_endpoint
   AZURE_AI_KEY=your_key
   MODEL_DEPLOYMENT_NAME=your_model_name
   ```

## Usage

Run the main script:
```bash
python main.py
```

## Architecture

The system follows Clean Architecture principles with four main layers:
- Domain: Core business rules and entities
- Application: Use cases and business logic
- Infrastructure: External implementations
- Interfaces: Adapters for external systems

## Testing

Run tests using pytest:
```bash
pytest tests/
```
```

Now that all the files are created with their content, you need to:

1. Update the `.env` file with your actual Azure credentials
2. Install the dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python main.py
```

Would you like me to help you with any of these steps or explain any part of the code in more detail?
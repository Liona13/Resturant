# Restaurant Manager

A comprehensive restaurant management system built with Python Flask, helping restaurant owners manage their business more efficiently.

## Features

- Menu Price Calculator
- Inventory Management
- Staff Scheduling
- Sales Analytics
- Supplier Management

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Set up your environment variables in `.env`
2. Run the application:
   ```
   python run.py
   ```
3. Access the application at `http://localhost:5000`

## Project Structure

```
restaurant_manager/
├── app/
│   ├── models/
│   ├── services/
│   ├── api/
│   └── templates/
├── tests/
├── requirements.txt
└── run.py
```

## Development

- Use `pytest` for running tests
- Follow PEP 8 style guidelines
- Create feature branches for new development

## License

MIT License

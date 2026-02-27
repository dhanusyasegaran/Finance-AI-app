# AI Personal Finance Analyzer

A production-ready Flask application that uses Machine Learning to classify transactions and predict future expenses.

## Features
- **Secure Authentication**: Register and login to manage your finances.
- **ML Transaction Classification**: Automatically categorize expenses based on descriptions.
- **Expense Prediction**: Forecast next month's spending using Linear Regression.
- **Interactive Dashboard**: Visualize spending patterns with Plotly charts.
- **AI-Powered Insights**: Get personalized financial suggestions.
- **PDF Reporting**: Download a detailed summary of your financial health.
- **Dark/Light Mode**: Premium UI with theme toggling.

## Tech Stack
- **Backend**: Flask, Pandas, Scikit-learn, SQLAlchemy
- **Frontend**: Bootstrap 5, Plotly, FontAwesome
- **Report**: ReportLab

## Setup Instructions
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Train the ML model**:
   ```bash
   python models/train_model.py
   ```
4. **Run the application**:
   ```bash
   python app.py
   ```
5. **Open in browser**: Navigate to `http://127.0.0.1:5000`

## Usage
- Register a new account.
- Prepare a CSV with `date`, `description`, and `amount` columns.
- Upload the CSV via the Dashboard.
- View your categorized spending, charts, and AI suggestions.
- Download the PDF report for your records.

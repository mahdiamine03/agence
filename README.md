# Agence de Voyage Management System Pro

A professional, offline desktop application for managing a Travel Agency. Built with Python and CustomTkinter.

## Features

- **Authentication**: Secure login with password hashing.
- **Dashboard**: KPI Cards and Revenue Chart.
- **Client Management**: Search, Add, Edit, and View History.
- **Booking Management**: Create bookings, calculate prices, and track status.
- **Invoicing**: Generate PDF invoices for bookings.
- **Financials**: Track payments and revenue.

## Requirements

- Python 3.8 or higher

## Installation

1.  **Clone or Download** the repository.
2.  **Open a terminal** (Command Prompt or PowerShell on Windows) in the project folder.
3.  **Create a Virtual Environment** (Optional but recommended):
    ```bash
    python -m venv venv
    ```
4.  **Activate the Virtual Environment**:
    - **Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
    - **Mac/Linux**:
        ```bash
        source venv/bin/activate
        ```
5.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To start the application, run the `run.py` script from the root directory:

```bash
python run.py
```

## Default Credentials

The system will create a default admin account on the first run:

- **Username**: `admin`
- **Password**: `admin123`

## Troubleshooting

- **ModuleNotFoundError: No module named 'customtkinter'**:
  - This means dependencies are not installed. Run `pip install -r requirements.txt`.
  - Ensure your virtual environment is activated if you created one.

- **ModuleNotFoundError: No module named 'src'**:
  - Make sure you run the app using `python run.py` from the root directory, not by running `src/main.py` directly.

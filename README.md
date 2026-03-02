# Daily Expense Tracker

A powerful Flask-based web application to record, manage, and analyze your daily expenses. Features a modern dark theme with Bootstrap styling, interactive charts, and a responsive design.

## Overview

The Daily Expense Tracker helps you monitor spending habits with an intuitive interface. Track expenses by category, filter by date range, visualize trends with charts, and export data for further analysis.

## Features

- **Easy Expense Management** - Add, edit, and delete expenses with instant feedback (no page reload)
- **Smart Categorization** - Assign categories and add optional notes to each transaction
- **Modern Design** - Dark theme with professional layout, translucent cards, and subtle textures
- **Advanced Filtering** - Filter expenses by date range and category
- **Real-time Analytics** - Live-updating totals with comprehensive tables and trend charts
- **Data Export** - Download all expenses to CSV with a single click
- **RESTful API** - JSON API for integration with other applications
- **Live Updates** - Automatic server polling every 10 seconds for new data
- **Responsive Layout** - Two-column layout on desktop with form and filters/stats side-by-side
- **Robust Backend** - MySQL database with SQLAlchemy ORM
- **Modern Frontend** - Bootstrap 5 powered responsive UI

## Project Structure

```
DailyExpenseTracker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── instance/             # Instance-specific files (database, config)
├── static/               # Static assets
│   ├── style.css        # Custom styles
│   └── app.js           # Frontend JavaScript
└── templates/           # HTML templates
    ├── index.html       # Landing page
    ├── home.html        # Main dashboard
    ├── login.html       # Login page
    ├── register.html    # Registration page
    ├── profile.html     # User profile
    ├── transactions.html # Transactions view
    ├── reports.html     # Reports and analytics
    ├── budgets.html     # Budget management
    ├── settings.html    # User settings
    ├── about.html       # About page
    ├── admin.html       # Admin panel
    └── forgot_password.html # Password recovery
```

## Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## Setup & Installation

> **⚠️ Note:** This application drops and recreates database tables on startup, so schema changes will clear existing data.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd DailyExpenseTracker
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

The application uses environment variables for database configuration. You can either:

**Option A: Set Environment Variables**

Windows (PowerShell):
```powershell
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3306"
$env:MYSQL_DB = "expenses_db"
```

macOS/Linux:
```bash
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DB=expenses_db
```

**Option B: Edit app.py**

Update the `MYSQL_*` constants at the top of `app.py`:

```python
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "expenses_db"
```

**Configuration Options:**

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | `jebinsam` |
| `MYSQL_HOST` | MySQL server hostname | `localhost` |
| `MYSQL_PORT` | MySQL server port | `3306` |
| `MYSQL_DB` | Database name | `expenses_db` |

The application will automatically create the database if it doesn't exist.

### 5. Run the Application

```bash
python app.py
```

Or use Flask directly:
```bash
flask run
```

Navigate to `http://127.0.0.1:5000` in your web browser.

## Usage

### Adding Expenses

1. Fill in the expense form at the top of the dashboard
2. Enter amount, category, date, and optional notes
3. Click "Add Expense" - it will appear instantly in the table

### Managing Expenses

- **Edit** - Click the edit button in the table row to modify an expense
- **Delete** - Click the delete button to remove an expense
- **Filter** - Use date range and category filters to narrow results

### Viewing Analytics

- Check the charts section for spending trends
- View totals and category breakdowns
- Export data to CSV for external analysis

## API Endpoints

All endpoints return JSON responses.

### Get Expenses

```http
GET /api/expenses
```

Query parameters (optional):
- `start` - Start date (YYYY-MM-DD)
- `end` - End date (YYYY-MM-DD)
- `category` - Filter by category name

**Example:**
```
GET /api/expenses?start=2024-01-01&end=2024-12-31&category=Food
```

### Add Expense

```http
POST /api/expenses
```

**Request body:**
```json
{
  "amount": 25.50,
  "category": "Food",
  "date": "2024-01-15",
  "notes": "Lunch at cafe"
}
```

### Update Expense

```http
PUT /api/expenses/<id>
```

**Request body:**
```json
{
  "amount": 30.00,
  "category": "Dining",
  "date": "2024-01-15",
  "notes": "Updated lunch"
}
```

### Delete Expense

```http
DELETE /api/expenses/<id>
```

## Technologies Used

- **Backend:** Flask, Python
- **Database:** MySQL, SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Icons:** FontAwesome
- **Charts:** Chart.js (if applicable)

## Troubleshooting

### Database Connection Failed
- Verify MySQL service is running
- Check credentials in configuration
- Ensure the user has permission to create databases
- Verify `MYSQL_HOST` and `MYSQL_PORT` are correct

### Port 5000 Already in Use
```bash
flask run --port 5001
```

### Virtual Environment Issues
```bash
# Deactivate and reactivate
deactivate
& .\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate        # macOS/Linux
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Suggestions for UI improvements, new features, and bug fixes are always appreciated!

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on the repository.

---

Made with ❤️ using Flask and Bootstrap
- Assign categories and optional notes to each entry
- Dark theme with modern fonts, professional layout, translucent cards, and subtle textured background
- Filter entries by date range and category
- Live updating total, comprehensive table and trend chart
- Export all data to CSV with one click
- RESTful JSON API for integration or automation (with category/notes)
- Automatically polls server every 10 seconds for new data
- Responsive two-column layout on home page with form + filters/stats
- MySQL backend with SQLAlchemy ORM
- Responsive UI powered by Bootstrap 5

## 🛠️ Setup & Installation

> **⚠️ Note:** This demo drops and recreates the database tables each time it starts, so schema changes will clear existing data.

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DailyExpenseTracker
   ```

2. **Create & activate a virtual environment**
   ```powershell
   python -m venv .venv
   & .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database credentials**

   The app uses environment variables for the database connection. You can either export these variables or edit the `MYSQL_*` constants at the top of `app.py`.

   | Variable         | Description                        | Default        |
   |------------------|------------------------------------|----------------|
   | `MYSQL_USER`     | MySQL username                     | `root`         |
   | `MYSQL_PASSWORD` | MySQL password                     | `jebinsam`     |
   | `MYSQL_HOST`     | Hostname of the MySQL server       | `localhost`    |
   | `MYSQL_PORT`     | MySQL port                         | `3306`         |
   | `MYSQL_DB`       | Database name                      | `expenses_db`  |

   The application will attempt to create the database automatically if it does not exist.

5. **Run the application**
   ```bash
   python app.py
   ```
   or simply use
   ```bash
   flask run
   ```
   Navigate to `http://127.0.0.1:5000` in your browser.

## 📄 API Endpoints

| Method | Endpoint               | Description                  |
|--------|------------------------|------------------------------|
| GET    | `/api/expenses`        | List all expenses (optional query params `start`, `end`, `category` for filtering)            |
| POST   | `/api/expenses`        | Add a new expense            |
| PUT    | `/api/expenses/<id>`   | Update an existing expense   |
| DELETE | `/api/expenses/<id>`   | Remove an expense            |

All API endpoints accept and return JSON.

## 💡 Usage

- Fill the form at the top to add a new expense.
- Edit or delete entries using the action buttons in the table.
- Totals are updated automatically.

## 🧩 Dependencies

See `requirements.txt` for the full list of Python packages.

## 🤝 Contributing

Feel free to open issues or submit pull requests. Suggestions for UI improvements, new features, or bug fixes are always welcome!

---

Made with ❤️ using Flask and Bootstrap.
# Daily Expense Tracker

A simple Flask-based web application to record and manage your daily expenses. The UI is styled using Bootstrap and FontAwesome icons for a dark, clean, modern, and professional experience.

## 🚀 Features

- Add, edit, delete expenses with instant feedback (no page reload)
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
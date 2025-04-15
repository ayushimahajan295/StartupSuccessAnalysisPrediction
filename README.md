# Startup Success Dashboard

A web application for predicting startup success with Power BI integration, built with Flask and SQLite.

## Features

- User authentication system with admin and regular user roles
- Power BI dashboard embedding
- ML-powered startup success prediction
- Admin dashboard to monitor user activity and predictions
- Responsive design that works on desktop and mobile

## Installation

### Prerequisites

- Python 3.8+
- Pip (Python package manager)
- Power BI embed link for the dashboard

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd startup_dashboard
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install flask pickle-mixin
   ```

4. Add your Power BI embed link:
   - Create a file named `powerbi_link.txt` in the project root
   - Paste your Power BI embed link (iframe src URL) into this file

5. Add your ML model:
   - Create a directory named `model` if it doesn't exist
   - Save your trained model as `model.pkl` in the `model` directory

6. Initialize the database:
   ```bash
   python db_setup.py
   ```

7. Run the application:
   ```bash
   python app.py
   ```

8. Access the application:
   - Open your browser and go to `http://localhost:5000`
   - Use the following demo credentials:
     - Admin: username=`admin`, password=`admin123`
     - User: username=`user`, password=`user123`

## Project Structure

```
startup_dashboard/
│
├── static/              # Static assets
│   ├── style.css        # CSS styles
│   ├── images/          # Images and icons
│   └── js/              # JavaScript files
│
├── templates/           # HTML templates
│   ├── login.html       # Login page
│   ├── user.html        # User dashboard
│   ├── admin.html       # Admin dashboard
│   └── layout.html      # Base layout template
│
├── model/               # Machine Learning model
│   └── model.pkl        # Saved ML model
│
├── data/                # Database files
│   └── startup.db       # SQLite database
│
├── app.py               # Main Flask application
├── db_setup.py          # Database initialization script
├── README.md            # Project documentation
└── powerbi_link.txt     # Power BI embed link
```

## Security Notes

- This application uses SHA-256 for password hashing which is not recommended for production use
- For production, consider using Flask-Bcrypt or Werkzeug's password hashing utilities
- Implement CSRF protection when deploying to production
- Use environment variables for sensitive configuration (e.g., secret key)

## Customization

### Adding New Users

To add new users, you can modify the `db_setup.py` file or implement a user management interface in the admin panel.

### Updating the ML Model

To update the prediction model:
1. Export your new model as a pickle file
2. Replace the existing `model.pkl` file in the `model` directory

### Changing the Power BI Dashboard

To change the Power BI dashboard:
1. Get a new embed link from Power BI
2. Update the `powerbi_link.txt` file with the new link

## License

[MIT License](LICENSE)
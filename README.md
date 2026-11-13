
# AfyaTrack

**Problem statement:** Community Health Workers often rely on paper-based records to register clients, document home visits and monitor follow-up activities, making it difficult to identify clients whose follow-ups are overdue.

## Project Overview

AfyaTrack is a simple Python-based Community Health Client Registration and Follow-up Management System. It enables Community Health Workers to register clients, record visits, schedule follow-ups and monitor overdue activities.

## Features

- Register new clients.
- View and search client records.
- Update client information.
- Delete client records.
- Record community health visits.
- Schedule and complete follow-ups.
- Identify overdue follow-ups.
- View a dashboard with basic programme statistics.
- Export client records to CSV.

## Technologies Used

- Python
- SQLite
- Streamlit
- Pandas
- Regular Expressions
- Git and GitHub

## Project Structure

```text
AfyaTrack/
├── main.py
├── database.py
├── client.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── data/
    └── afya_track.db
```

## Installation and Setup

### 1. Clone the repository



### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows Git Bash:

```bash
source .venv/Scripts/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run main.py
```

The application will open in your browser at:

http://localhost:8501

The SQLite database and clients table are created automatically when the application starts.

## Database

AfyaTrack uses SQLite to store client information. The database contains a clients table with fields for client details, visit information and follow-up status.

## Demonstration and Testing

The application has been tested using fictional client records to demonstrate registration, searching, updating, deletion, visit recording, follow-up management and CSV export.

## Limitations

AfyaTrack is an educational prototype. It uses fictional demonstration data and is not intended for real patient records or clinical decision-making.

## Future Improvements

- Introduce separate records for each historical visit.
- Add user authentication and access controls.
- Improve reporting and data visualisation.
- Explore integration with other health information systems.



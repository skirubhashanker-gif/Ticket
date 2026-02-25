# Internal Ticket System

A simple Flask-based web ticketing system for internal requirement handling across software and hardware needs.

## Features

- **Admin**
  - Creates users (requesters), tech accounts, and additional admins.
  - Views overall ticket/user statistics.
- **User**
  - Creates software/hardware tickets.
  - Sees only their own tickets and statuses.
- **Tech Team**
  - Sees all tickets.
  - Updates status, assigns tech owner, and adds closing comments.
- **Ticket Chat**
  - Internal conversation thread per ticket between users, tech team, and admins.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: `http://localhost:5000`

On first launch, you will be redirected to create the initial admin account.

## Ticket Statuses

- `open`
- `in_progress`
- `pending_user`
- `resolved`
- `closed`

## Notes

- Data is stored in local SQLite DB: `ticket_system.db`
- Update `SECRET_KEY` in `app.py` for production use.

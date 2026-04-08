# BUET E-Council

> A digital document management system for **Bangladesh University of Engineering and Technology (BUET)** to manage Syndicate Meeting and Academic Council Meeting documents, agendas, and members.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [User Roles](#user-roles)
- [Authentication](#authentication)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**BUET E-Council** is a web-based platform that digitizes and centralizes the management of official university council documents. It supports two types of council meetings:

- **Syndicate Meetings** — Governing body meetings for university administration.
- **Academic Council Meetings** — Meetings for academic policy and curriculum decisions.

All users authenticate via **Email + OTP (One-Time Password)** — no passwords required.

---

## Features

### For All Users (Normal Users)
- View published Syndicate and Academic Council meeting documents
- View meeting agendas (read-only)
- View list of meeting members (read-only)
- Secure login via Email + OTP

### For Admin Users
- All normal user capabilities, plus:
- **Create** new Syndicate or Academic Council meetings
- **Edit** meeting details (date, time, venue, description)
- **Add / Edit / Remove** meeting members
- **Create and Edit** meeting agendas
- **Upload and manage** meeting documents (minutes, notices, resolutions)
- **Manage user roles** (grant or revoke admin access)

---

## User Roles

| Role        | View Documents | Edit Meetings | Edit Agendas | Manage Members | Manage Users |
|-------------|:--------------:|:-------------:|:------------:|:--------------:|:------------:|
| Normal User | ✅             | ❌            | ❌           | ❌             | ❌           |
| Admin       | ✅             | ✅            | ✅           | ✅             | ✅           |

---

## Authentication

This system uses **Email + OTP** based authentication — no traditional passwords.

### Login Flow

```
1. User enters their registered email address
2. FastAPI backend generates a 6-digit OTP and sends it to that email
3. User enters the OTP on the verification screen
4. On success, backend returns a signed JWT token
5. Vue.js stores the token and redirects based on role (Admin Dashboard or Viewer)
```

### Security Notes
- OTPs expire after **10 minutes**
- Only **pre-registered** university email addresses can log in
- Admins can register/deactivate user accounts
- JWT tokens are verified on every protected route via FastAPI dependencies
- All sessions are invalidated on logout

---

## Tech Stack

| Layer        | Technology                            |
|--------------|---------------------------------------|
| Frontend     | Vue.js 3 (Composition API)            |
| Backend      | FastAPI (Python)                      |
| Database     | PostgreSQL                            |
| ORM          | SQLAlchemy + Alembic (migrations)     |
| Auth / OTP   | smtplib / SendGrid + pyotp            |
| Auth Token   | JWT via python-jose                   |
| State Mgmt   | Pinia                                 |
| HTTP Client  | Axios                                 |
| File Storage | Local Storage / AWS S3                |

---

## Project Structure

```
buet-e-council/
├── frontend/                          # Vue.js 3 Frontend
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginView.vue          # Email input screen
│   │   │   ├── OtpVerifyView.vue      # OTP verification screen
│   │   │   ├── MeetingsView.vue       # Meeting list (all users)
│   │   │   ├── MeetingDetail.vue      # Single meeting + agendas + docs
│   │   │   └── admin/
│   │   │       ├── AdminDashboard.vue
│   │   │       ├── ManageMeetings.vue
│   │   │       ├── ManageAgendas.vue
│   │   │       └── ManageMembers.vue
│   │   ├── components/                # Reusable Vue components
│   │   ├── router/
│   │   │   └── index.js               # Vue Router with auth guards
│   │   ├── stores/
│   │   │   ├── auth.js                # Pinia auth store (JWT, user role)
│   │   │   └── meetings.js            # Pinia meetings store
│   │   └── services/
│   │       └── api.js                 # Axios instance with base URL & token
│   ├── public/
│   ├── vite.config.js
│   └── package.json
│
├── backend/                           # FastAPI Backend (Python)
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry point & router registration
│   │   ├── database.py                # PostgreSQL connection via SQLAlchemy
│   │   ├── models/
│   │   │   ├── user.py                # User model (email, role, is_active)
│   │   │   ├── meeting.py             # Meeting model (type, date, venue)
│   │   │   ├── agenda.py              # Agenda item model
│   │   │   ├── member.py              # Meeting member model
│   │   │   └── document.py            # Uploaded document model
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── meeting.py
│   │   │   ├── agenda.py
│   │   │   └── member.py
│   │   ├── routers/
│   │   │   ├── auth.py                # POST /auth/send-otp, /auth/verify-otp
│   │   │   ├── meetings.py            # Meeting CRUD routes
│   │   │   ├── agendas.py             # Agenda CRUD routes
│   │   │   ├── members.py             # Member management routes
│   │   │   └── documents.py           # File upload/download routes
│   │   └── core/
│   │       ├── security.py            # JWT creation & verification
│   │       ├── otp.py                 # OTP generation & email sending
│   │       └── dependencies.py        # get_current_user, require_admin
│   ├── alembic/                       # PostgreSQL migrations
│   │   └── versions/
│   ├── requirements.txt
│   └── .env
│
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python** >= 3.10
- **Node.js** >= 18
- **PostgreSQL** >= 14
- An email service account (e.g., Gmail SMTP or SendGrid)

### Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and fill in values
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the FastAPI development server
uvicorn app.main:app --reload --port 8000
```

FastAPI interactive docs will be available at `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vue.js development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## Environment Variables

Copy `.env.example` to `.env` in the `backend/` directory and fill in the values:

```env
# App
APP_ENV=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/buet_ecouncil

# JWT
SECRET_KEY=your_jwt_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080   # 7 days

# OTP Config
OTP_EXPIRY_MINUTES=10

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@buet.ac.bd
SMTP_PASSWORD=your_app_password
EMAIL_FROM=no-reply@buet.ac.bd
```

---

## API Endpoints

FastAPI auto-generates interactive docs at `/docs` (Swagger UI) and `/redoc`.

### Auth
| Method | Endpoint                  | Description               | Access     |
|--------|---------------------------|---------------------------|------------|
| POST   | `/api/auth/send-otp`      | Send OTP to email         | Public     |
| POST   | `/api/auth/verify-otp`    | Verify OTP & receive JWT  | Public     |
| POST   | `/api/auth/logout`        | Invalidate token          | All users  |

### Meetings
| Method | Endpoint                  | Description               | Access     |
|--------|---------------------------|---------------------------|------------|
| GET    | `/api/meetings`           | List all meetings         | All users  |
| GET    | `/api/meetings/{id}`      | Get meeting details       | All users  |
| POST   | `/api/meetings`           | Create a new meeting      | Admin only |
| PUT    | `/api/meetings/{id}`      | Edit a meeting            | Admin only |
| DELETE | `/api/meetings/{id}`      | Delete a meeting          | Admin only |

### Agendas
| Method | Endpoint                          | Description          | Access     |
|--------|-----------------------------------|----------------------|------------|
| GET    | `/api/meetings/{id}/agendas`      | View agendas         | All users  |
| POST   | `/api/meetings/{id}/agendas`      | Add agenda item      | Admin only |
| PUT    | `/api/agendas/{id}`               | Edit agenda item     | Admin only |
| DELETE | `/api/agendas/{id}`               | Delete agenda item   | Admin only |

### Members
| Method | Endpoint                          | Description          | Access     |
|--------|-----------------------------------|----------------------|------------|
| GET    | `/api/meetings/{id}/members`      | View members         | All users  |
| POST   | `/api/meetings/{id}/members`      | Add member           | Admin only |
| PUT    | `/api/members/{id}`               | Edit member info     | Admin only |
| DELETE | `/api/members/{id}`               | Remove member        | Admin only |

### Documents
| Method | Endpoint                          | Description          | Access     |
|--------|-----------------------------------|----------------------|------------|
| GET    | `/api/meetings/{id}/documents`    | List documents       | All users  |
| POST   | `/api/meetings/{id}/documents`    | Upload document      | Admin only |
| DELETE | `/api/documents/{id}`             | Delete document      | Admin only |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add: your feature description"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please follow the existing code style and write clear commit messages.

---

## License

This project is developed for **Bangladesh University of Engineering and Technology (BUET)**.  
All rights reserved © BUET E-Council Team.

---

*For questions or support, contact the project maintainer or open an issue on the repository.*
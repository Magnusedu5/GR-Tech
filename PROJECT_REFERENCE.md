# GR TECH — Project Reference Document
*Last updated: 26 May 2026*

---

## 🌐 Live URLs

| Service | URL |
|---|---|
| **Main website** | https://www.grtechhq.com |
| **Render static mirror** | https://grtech-site.onrender.com |
| **Admin dashboard** | https://www.grtechhq.com/dashboard |
| **Backend API** | https://grtech-backend.onrender.com |

### Site pages
| Page | URL |
|---|---|
| Home | https://www.grtechhq.com/ |
| Services | https://www.grtechhq.com/services |
| Projects | https://www.grtechhq.com/projects |
| About | https://www.grtechhq.com/about |
| Contact | https://www.grtechhq.com/contact |
| Admin Dashboard | https://www.grtechhq.com/dashboard |

---

## 🔐 Admin Dashboard Login

| Field | Value |
|---|---|
| **URL** | https://www.grtechhq.com/dashboard |
| **Username** | `magnus` |
| **Password** | `Mag123456789@` |

---

## ☁️ Render Services

### Dashboard
- URL: https://dashboard.render.com
- Account email: **magnusedu5@gmail.com**

### Services
| Name | Type | ID | Status |
|---|---|---|---|
| `grtech-backend` | Web Service (Python) | `srv-d8aron9kh4rs73eorhug` | Live |
| `grtech-site` | Static Site | `srv-d8amdkcm0tmc73a77q8g` | Live |
| `grtech-db` | PostgreSQL | `dpg-d8arn33bc2fs73amhio0-a` | Live |

### Backend Environment Variables
| Key | Value |
|---|---|
| `SECRET_KEY` | `NV7-_6SoF7CcZvD9kyeeR5ofE0oKDO7w2XKf2aHxNJ8r91VVBkIL4G3oVHOT` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `grtech-backend.onrender.com,.onrender.com,localhost,127.0.0.1` |
| `FRONTEND_URL` | `https://grtech-site.onrender.com,https://www.grtechhq.com,https://grtechhq.com` |
| `DATABASE_URL` | `postgresql://grtech:PcflgC1dk4ofvAqycNEz5vdfLBUhd4Rd@dpg-d8arn33bc2fs73amhio0-a/grtech` |
| `DJANGO_SUPERUSER_USERNAME` | `magnus` |
| `DJANGO_SUPERUSER_EMAIL` | `magnusedu5@gmail.com` |
| `DJANGO_SUPERUSER_PASSWORD` | `Mag123456789@` |
| `RESEND_API_KEY` | *(not set — set this to enable email notifications)* |
| `NOTIFICATION_EMAIL` | *(not set — set this to receive inquiry alerts)* |

---

## 🗄️ PostgreSQL Database

| Field | Value |
|---|---|
| **Database name** | `grtech` |
| **User** | `grtech` |
| **Password** | `PcflgC1dk4ofvAqycNEz5vdfLBUhd4Rd` |
| **Host (internal)** | `dpg-d8arn33bc2fs73amhio0-a` |
| **Host (external)** | `dpg-d8arn33bc2fs73amhio0-a.oregon-postgres.render.com` |
| **Port** | `5432` |
| **Connection string** | `postgresql://grtech:PcflgC1dk4ofvAqycNEz5vdfLBUhd4Rd@dpg-d8arn33bc2fs73amhio0-a/grtech` |

---

## 🔌 API Endpoints

Base URL: `https://grtech-backend.onrender.com`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/contact/` | None | Submit contact form |
| `POST` | `/api/auth/login/` | None | Get auth token (returns `token`) |
| `GET` | `/api/inquiries/` | Token | List all inquiries + summary counts |
| `GET` | `/api/inquiries/?status=new` | Token | Filter by status |
| `GET` | `/api/inquiries/<id>/` | Token | Get single inquiry |
| `PATCH` | `/api/inquiries/<id>/` | Token | Update inquiry status |

### Auth header for protected endpoints
```
Authorization: Token <token_from_login>
```

### Status values
`new` → `in_review` → `contacted` → `closed`

### Project type values
`web`, `backend`, `fullstack`, `ai`, `other`

---

## 📁 Repository

| Field | Value |
|---|---|
| **GitHub** | https://github.com/Magnusedu5/GR-Tech |
| **Branch** | `main` |
| **Local path** | `/home/magnus/grtech` |

### Folder structure
```
grtech/
├── index.html          # Home page
├── services.html       # Services page
├── projects.html       # Projects page
├── about.html          # About page
├── contact.html        # Contact page
├── dashboard.html      # Admin dashboard SPA
├── css/
│   └── style.css       # All site styles (currently ?v=6)
├── js/
│   └── main.js         # Nav, contact form, scroll effects
├── assets/             # Images, logo files
├── render.yaml         # Render deployment config
└── backend/
    ├── requirements.txt
    ├── grtech_backend/
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── contact/
        ├── models.py       # Inquiry model
        ├── serializers.py  # Public + admin serializers
        ├── views.py        # ContactView, LoginView, InquiryListView, InquiryDetailView
        ├── urls.py         # API routes
        ├── emails.py       # Resend email notification
        └── migrations/
            ├── 0001_initial.py
            └── 0002_create_admin.py   # Creates superuser from env vars on deploy
```

---

## 🚀 How to Redeploy

### Static site (frontend)
Any `git push origin main` auto-deploys the static site within ~30 seconds.

### Backend
Any `git push origin main` auto-deploys the backend. The build command runs:
1. `pip install -r requirements.txt`
2. `python manage.py collectstatic --noinput`
3. `python manage.py migrate` *(also runs the admin user migration)*

> **Note:** If a deploy fails with "Update Failed", trigger a manual redeploy from the Render dashboard or via:
> ```bash
> render deploys create srv-d8aron9kh4rs73eorhug --confirm
> ```

---

## 📧 Email Notifications (Optional / Not Yet Set Up)

To receive email alerts when someone submits the contact form:

1. Sign up at https://resend.com (free — 3,000 emails/month)
2. Get your API key
3. In Render dashboard → **grtech-backend** → **Environment** → add:
   - `RESEND_API_KEY` = your key from Resend
   - `NOTIFICATION_EMAIL` = `magnusedu5@gmail.com`
4. Redeploy the backend

---

## 🛠️ Render CLI (already authenticated)

```bash
# List all services
render services list

# View logs
render logs srv-d8aron9kh4rs73eorhug --resources srv-d8aron9kh4rs73eorhug --output text

# Trigger a deploy
echo "y" | render deploys create srv-d8aron9kh4rs73eorhug

# Check deploy status
render deploys list srv-d8aron9kh4rs73eorhug
```

---

## 📝 Notes

- The admin user (`magnus`) is recreated automatically on every backend deploy via the data migration `0002_create_admin.py` — so even if the password is reset, the next deploy will restore it to `Mag123456789@`
- The PostgreSQL database is persistent and survives redeployments
- The static site uses cache-busting via `?v=6` on the stylesheet link — increment to `?v=7` etc. when making CSS changes
- CORS is configured for both `grtech-site.onrender.com` and `www.grtechhq.com` / `grtechhq.com`
- The dashboard stores the auth token in `localStorage` under the key `grtech_token`
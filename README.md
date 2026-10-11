# 🥭 CropMedic - Farm Surveillance Tech

A Django web application for recording and managing pest and disease
surveillance. Growers register farms, log surveillance sessions, record
observations against a pest/disease reference library, calculate sampling
effort, and export their data.

Built for **HIT391** by:

| Name |
|---|
| Sadit Khan |
| Nguyen Hao Vo |
| Fabiha Sultana Anushe |
| Roshan Karki |

---

## Features

**Public reference library**
- Search pests and diseases by name or description
- Browse a filterable card grid of pests and diseases
- Detail pages with description, impact, severity/infestation rate and control measures
- Global surveillance index showing observations across all growers

**Grower portal** (login required)
- Dashboard with farm / session / observation counts and a doughnut chart of sessions by plant part
- Full CRUD for farms, surveillance sessions and observations
- Add and delete custom pests and diseases

**Surveillance effort calculator**
- Recommends a sample count from plant count, season and plant part
- Wet season applies a 1.5× multiplier: `ceil(sqrt(plant_count) * multiplier)`
- Auto-fills the plant count when a farm is selected

**Data export**
- Export all surveillance data as flat CSV or nested JSON

---

## Requirements

- Python 3.10+
- Django 5.1.7 (see `requirements.txt`)

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/farm-surveillance-tech.git
cd farm-surveillance-tech

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Load the pest/disease reference data and a demo account
python manage.py seed_data

# 6. Run the development server
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** — the root URL redirects to `/pests/`.

### Demo account

`seed_data` creates a demo grower you can log in with:

| Username | Password |
|---|---|
| `demo` | `mangomedic123` |

It comes with 3 farms, 9 surveillance sessions and 9 observations so the
dashboard and charts have something to show.

To load only the pest/disease reference data without the demo account:

```bash
python manage.py seed_data --no-demo
```

### Admin site

To use the Django admin, create a superuser:

```bash
python manage.py createsuperuser
```

Then visit **http://127.0.0.1:8000/admin/**.

---

## Project layout

```
.
├── manage.py
├── requirements.txt
├── db.sqlite3                  # created by migrate; not tracked
├── mango_site/                 # project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── pests/                      # the single application
    ├── models.py               # Pest, Disease, Grower, Farm, PlantPart,
    │                           # PlantType, SurveillanceSession, Observation
    ├── views.py                # portal, CRUD, calculator, exports
    ├── forms.py
    ├── urls.py
    ├── admin.py
    ├── management/commands/
    │   └── seed_data.py        # reference + demo data loader
    ├── migrations/             # 8 migrations
    ├── static/pests/css/       # dark theme stylesheets
    └── templates/pests/        # 28 templates
```

## Data model

```
User ──1:1── Grower ──1:N── Farm ──1:N── SurveillanceSession ──1:N── Observation
                  │                              │                        │
                  │                              └── N:1 ── PlantPart     ├── N:1 ── Pest
                  │                              └── N:1 ── PlantType    └── N:1 ── Disease
                  │
Item (abstract) ──┬── Pest      (adds infestation_rate, sampling_multiplier)
                  └── Disease   (adds severity)
```

An `Observation` records a result level of `low`, `mid` or `high` against
either a pest, a disease, or both.

## URL map

| URL | View | Description |
|---|---|---|
| `/` | — | Redirects to `/pests/` |
| `/pests/` | `home` | Search page |
| `/pests/about/` | `about` | Team page |
| `/pests/projects/` | `pro_list` | Pest & disease grid |
| `/pests/project/<type>/<id>/` | `pro_det` | Detail page |
| `/pests/global-table/` | `global_index_table` | All observations |
| `/pests/portal/` | `grower_portal` | Dashboard |
| `/pests/farms/` | CRUD | Farm management |
| `/pests/sessions/` | CRUD | Session management |
| `/pests/observations/` | CRUD | Observation management |
| `/pests/calculator/` | `effort_calculator` | Effort calculator |
| `/pests/export/all/csv/` | `export_all_data_csv` | CSV export |
| `/pests/export/all/json/` | `export_all_data_json` | JSON export |
| `/pests/accounts/register/` | `register` | Sign up |
| `/pests/accounts/login/` | `LoginView` | Log in |
| `/pests/accounts/logout/` | `logout_view` | Log out |

---

## Notes

- `db.sqlite3` is **not** tracked. Run `migrate` then `seed_data` to build a
  working database from scratch.
- `DEBUG = True` and a development `SECRET_KEY` are committed for local use.
  Before deploying anywhere public, set `DEBUG = False`, move the secret key to
  an environment variable, and set `ALLOWED_HOSTS`.

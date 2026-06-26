# Rivyou Product Search API

Django REST Framework backend with JWT auth and three-tier relevance ranking.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_products products_data.csv
python manage.py runserver
```

## API Endpoints

### Auth

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/auth/register` | No | Register new user |
| POST | `/api/auth/login` | No | Login, get JWT |
| POST | `/api/auth/logout` | Yes | Logout (blacklist token) |

**Register:**
```json
POST /api/auth/register
{"username": "alice", "email": "alice@example.com", "password": "secure123"}

→ {"id": 1, "username": "alice", "token": "<jwt>"}
```

**Login:**
```json
POST /api/auth/login
{"username": "alice", "password": "secure123"}

→ {"token": "<jwt>", "refresh": "<refresh>", "user": {...}}
```

All protected endpoints require:
```
Authorization: Bearer <token>
```

---

### Products

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/api/products/search?q=<query>` | Yes | Ranked search |
| GET | `/api/products/<id>` | Yes | Single product |
| GET | `/api/products/category/<name>` | Yes | All in category |
| POST | `/api/products/` | Admin | Create product |

**Search params:**
- `q` (required) — search query
- `limit` (default 20) — results per page
- `page` (default 1) — page number
- `category_filter` (optional) — e.g. `Smartphones`

**Search response:**
```json
{
  "query": "smartphone",
  "total_results": 430,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "id": 1,
      "product_name": "iPhone 15 Pro",
      "category": "Smartphones",
      "tags": ["5g", "camera", "performance"],
      "relevance_score": 0.76,
      "rank_reason": "Category match"
    },
    {
      "id": 450,
      "product_name": "USB-C Fast Charger",
      "category": "Chargers",
      "tags": ["fast-charging", "smartphone"],
      "relevance_score": 0.65,
      "rank_reason": "Tag match (smartphone)"
    }
  ]
}
```

---

## Ranking Logic

The engine in `products/ranking.py` assigns scores 0.0–1.0:

| Tier | Condition | Score Range | Reason |
|------|-----------|-------------|--------|
| 1 | `category` matches query | 0.70–1.00 | "Category match" |
| 2 | `tags` contain query (category mismatch) | 0.50–0.65 | "Tag match (...)" |
| 3 | `product_name` or `description` contains query | 0.20–0.35 | "Name match" / "Description match" |

Within Tier 1, products with more query-matching tags score higher.
Within Tier 2, exact tag matches (e.g. tag = "smartphone") beat partial matches.

---

## Run Tests

```bash
python manage.py test products --verbosity=2
```

15 tests — ranking logic, auth, and search API.

---

## Deployment (Render)

1. Set `DEBUG=False` and `SECRET_KEY` via env vars
2. Switch `DATABASES` to PostgreSQL using `dj-database-url`
3. Add `gunicorn` and a `Procfile`:
   ```
   web: gunicorn rivyou.wsgi --log-file -
   ```
4. On first deploy, run:
   ```bash
   python manage.py migrate
   python manage.py load_products products_data.csv
   ```

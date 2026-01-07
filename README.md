# Odoo 16 → 18 Upgrade Guide (Repository: d:/odoo18/upgrade)

This repository contains the upgrade workspace and instructions to run two Docker environments for migration testing:

- Odoo 16 environment (restore a v16 DB backup)
- Odoo 18 environment (fresh DB for testing migrated modules)

Goal: Validate and migrate custom modules from Odoo 16 to Odoo 18 following the provided checklist and acceptance criteria.

---

## Quick Summary

- Odoo 18 web port: `8018`, Postgres: `5418` (containers: `v18_web`, `v18_db`)
- Odoo 16 web port: `8016`, Postgres: `5416` (containers: `v16_web`, `v16_db`)
- Master DB password used in examples: `123`
- Custom modules live in `custom/` and enterprise addons in `enterprise18/` or `enterprise16/`.

---

## Prerequisites

- Docker & Docker Compose installed
- Network access to download Odoo Enterprise zip (you have subscription code)
- Local filesystem with enough disk for DB dumps and enterprise addons
- Basic familiarity with Odoo module structure and XML view inheritance

---

## Files & Folder Structure (target)

Root: `~/odoo18/upgrade/` (for v18) and `~/odoo16/upgrade/` (for v16)

Each workspace should contain:

- `docker-compose.yml` — service definitions for web and db
- `odoo.Dockerfile` — derived from `odoo:<version>`
- `postgres.Dockerfile` — derived from `postgres:14.8`
- `config/odoo.conf` — Odoo configuration
- `custom/` — custom addons to test
- `enterprise18/` or `enterprise16/` — enterprise addon tree from Odoo download
- `data/` — postgres/odoo persistent data

---

## Step-by-step: Odoo 18 Container Setup

1. Download Odoo 18 Enterprise

   - Visit: https://www.odoo.com/page/download
   - Select Version: **18** and **Enterprise Source**
   - Enter subscription code: `M21031724371863`
   - Download and extract into `enterprise18/`.

2. Create folder structure (example on Windows):

```
D:\odoo18\upgrade\
  docker-compose.yml
  odoo.Dockerfile
  postgres.Dockerfile
  config\odoo.conf
  custom\
  enterprise18\
  data\
```

3. Example `docker-compose.yml` (v18)

```yaml
version: "3.8"
services:
  web:
    container_name: v18_web
    build:
      context: .
      dockerfile: odoo.Dockerfile
    depends_on:
      - db
    ports:
      - "8018:8069"
    volumes:
      - ./home/odoo/.local/share/Odoo:/var/lib/odoo
      - ./config:/etc/odoo
      - ./custom:/mnt/extra-addons
      - ./enterprise18:/mnt/enterprise
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    restart: "always"
    stdin_open: true
    tty: true

  db:
    container_name: v18_db
    build:
      context: .
      dockerfile: postgres.Dockerfile
    ports:
      - "5418:5432"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
      - POSTGRES_DB=postgres
    restart: "always"
```

4. Example `odoo.Dockerfile` (v18)

```Dockerfile
FROM odoo:18.0
USER root
SHELL ["/bin/bash", "-c"]
RUN apt-get update \
 && apt-get install -y python3-pip \
 && pip install --upgrade pip
RUN apt-get install -y python3-ipdb python3-html2text python3-asn1crypto python3-simplejson
```

5. Example `postgres.Dockerfile`

```Dockerfile
FROM postgres:14.8
RUN apt-get update && apt-get install -y sudo
SHELL ["/bin/bash", "-c"]
RUN useradd -m -g sudo -s /bin/bash odoo || true
```

6. Example `config/odoo.conf` (v18)

```
[options]
admin_passwd = 123
db_host = db
db_user = odoo
db_password = odoo
db_port = 5432
addons_path = /mnt/extra-addons, /mnt/enterprise
proxy_mode = False
data_dir = /var/lib/odoo
limit_time_real = 1200
```

7. Build and start (from `D:\odoo18\upgrade`):

```bash
docker compose up -d --build
```

8. Verify

- Open: http://localhost:8018
- Create new DB (demo data optional)
- Master password: `123`

---

## Step-by-step: Odoo 16 Container Setup

Follow the same structure under `~/odoo16/upgrade/`. Replace image base to `odoo:16.0` in `odoo.Dockerfile`, adjust ports to `8016` and `5416`, and point `enterprise16/`.

Example `docker-compose.yml` differences:

- web ports: `- "8016:8069"`
- db ports: `- "5416:5432"`

Start:

```bash
docker compose up -d --build
```

### Restore v16 Backup

1. Open: http://localhost:8016/web/database/manager
2. Click "Restore Database" and upload the `.zip` backup file.
3. Master password: `123`

To reset admin credentials (SQL) inside the Postgres container:

```bash
docker exec -it v16_db psql -U odoo -d <your_db_name>
-- then inside psql:
UPDATE res_users SET login='admin' WHERE id=2;
-- password is hashed; recommend resetting via UI or using Odoo shell to set a new password safely
\q
```

Note: Changing password directly in DB is unsafe for production; prefer Odoo shell or UI.

---

## Module Comparison & Migration Guide (per module)

Checklist before upgrading a module from v16 → v18:

- Update `__manifest__.py` version to `18.0.x.x.x` and update `depends` if base modules changed.
- Replace all `<tree>` tags with `<list>` in XML views.
- Resolve deprecated API calls (check Odoo 18 release notes for removed/renamed APIs).
- Ensure model extensions use `_inherit` (not `_name`) when extending existing models.
- Inspect views using `xpath` and remove brittle positional selectors (e.g., `field[2]`). Prefer `field[@name='...']`.
- Quote string literals in view expressions: `invisible="usage != 'internal'"`.
- Check for renamed or moved fields (for example `product_template_id` vs `product_id` in some view contexts).
- For missing fields that exist in DB but not model, either correct `_name` vs `_inherit` or add compatibility alias fields (related/compute) during migration.

Migration tasks:

- Run static checks: load module manifests, start Odoo, watch logs for `ParseError` or missing xpath errors.
- Install module in a fresh v18 DB once code is updated.
- Fix view parsing issues iteratively.

---

## Testing Checklist

For each custom module:

Python Code (.py):

- [ ] Models import and load without errors
- [ ] No deprecated methods used (check Odoo 18 release notes)
- [ ] `_inherit` vs `_name` correct
- [ ] Computed fields work and stored/depends set correctly
- [ ] `onchange` methods trigger correctly
- [ ] Python constraints run without exceptions

XML Views (.xml):

- [ ] All `list` views render correctly (replace `tree` with `list`)
- [ ] `xpath` edits find targets (avoid positional indexes)
- [ ] No `ParseError` in server logs

Reports & Wizards:

- [ ] PDFs render
- [ ] Wizards open and behave as expected

General:

- [ ] Module installs cleanly on v18
- [ ] CRUD operations functional
- [ ] No server log errors
- [ ] Browser console free of errors for core flows

---

## Ports Reference

- v18: Odoo `8018`, Postgres `5418`
- v16: Odoo `8016`, Postgres `5416`

---

## Acceptance Criteria

- All custom modules installed successfully on v18
- Views load without parsing errors
- All major workflows and reports validated
- No server-side errors in logs during tests

Deadline: Thursday morning (as requested)

---

## Collaboration / Testing Pairs

Swap pairs for cross-validation:

- Yousef Abdelrahman ↔ Rahma Hayam
- Esraa Salama ↔ (another reviewer)

---

## Common Pitfalls & Tips

- XML parse errors often stem from missing `<odoo>` / `<data>` root or incorrect `xpath` targets.
- Always quote literal strings in view expressions.
- Avoid `field[2]` style xpaths — use `field[@name='...']`.
- If `qty_done` shows up in DB but not in model, check for accidental `_name = 'stock.move.line'` in custom module (should be `_inherit`) or add a related/compute alias temporarily.
- Run `docker logs -f v18_web` (or `v16_web`) to see realtime Odoo server logs while testing module installs.

---

## Next Steps (recommended)

1. Confirm you want me to generate the `docker-compose.yml`, `odoo.Dockerfile`, `postgres.Dockerfile` files for both v16 and v18 in the repo. I can scaffold them exactly as in this README.
2. After scaffolding, run `docker compose up -d --build` in each folder and share logs for any errors.
3. Provide the v16 backup file and I'll run the restore steps and verify.

Commands to run locally (copy/paste):

```bash
# Build and start v18
cd D:/odoo18/upgrade
docker compose up -d --build
# Follow logs
docker logs -f v18_web

# Build and start v16
cd D:/odoo16/upgrade
docker compose up -d --build
docker logs -f v16_web
```

---

If you want, I can now scaffold the `docker-compose.yml`, `odoo.Dockerfile`, `postgres.Dockerfile`, and `config/odoo.conf` files for both v16 and v18 in this repository and commit them. Tell me if you want that created now.

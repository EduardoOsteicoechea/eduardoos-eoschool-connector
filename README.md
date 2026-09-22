# Eduardo OS eoschool connector

Silent sidecar: clone as **`.eoschool/`** at your project root.

Canonical curriculum workshop (HTML sources): https://github.com/EduardoOsteicoechea/eduardoos-eoschool-connector

This repo is the **API connector + Cursor skill** (same role as `eduardoos-ereport-connector`).
Silent sidecar for any project: clone this repo as **`.eoschool/`** at your project root. Agents generate US Letter Homescool study materials and sync them via the public API.

**Design (docs-first):** the client stays thin â€” require an API key, fetch `GET /api/v1/docs` **before any API action**, then craft authenticated requests from the live catalog (`routes` + `payloadSchema.homescool`). Generate HTML using **only** the skills in this connector (`skill/eoschool/`).

## Install (recommended)

From your project root:

```bash
git clone --depth 1 https://github.com/EduardoOsteicoechea/eduardoos-eoschool-connector.git .eoschool
```

Or run the installer (also wires the Cursor skill):

```bash
# Unix
curl -fsSL https://raw.githubusercontent.com/EduardoOsteicoechea/eduardoos-eoschool-connector/main/install.sh | bash

# Windows PowerShell (from project root)
irm https://raw.githubusercontent.com/EduardoOsteicoechea/eduardoos-eoschool-connector/main/install.ps1 | iex
```

Then:

```bash
cp .eoschool/.env.example .eoschool/.env   # required: EDUARDOOS_API_KEY
```

**Consumer gitignore (suggested):**

```gitignore
.eoschool/.env
.eoschool/docs.catalog.json
.eoschool/material.body.json
```

## Cursor skill

After install, skill files live at `.eoschool/skill/eoschool/`.  
Installers copy them to `.cursor/skills/eoschool/` so Cursor can load skill `eoschool`.

Read **CAVEATS** first: `.eoschool/skill/eoschool/CAVEATS.md`  
Materials format: `MATERIALS.md` Â· HTML shells: `TEMPLATES.md`

## CLI (docs-first API)

```bash
cd .eoschool
python eoschool_client.py docs
python eoschool_client.py request GET /api/v1/homescool/access
python eoschool_client.py request GET /api/v1/homescool/materials
python eoschool_client.py request POST /api/v1/homescool/materials --file material.body.json
```

Docs: https://eduardoos.com/api-docs  
Catalog: https://eduardoos.com/api/v1/docs

## License

MIT â€” see [LICENSE](LICENSE).


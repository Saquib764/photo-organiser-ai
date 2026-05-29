# Photo Organiser AI

Organise wedding and event photos with AI — resize a local library, generate captions and metadata, browse by smart filters, and design a photobook through chat.

## Stack

- **Frontend**: Nuxt 4 + Nuxt UI
- **Backend**: FastAPI (Python 3.12+)

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Node.js and **Yarn**
- An [OpenAI API key](https://platform.openai.com/api-keys) (for AI analysis and photobook chat)

## Run in production mode

For day-to-day use, run a **production build** of the frontend (pre-bundled assets, no dev hot-reload) and the backend **without** `--reload`. The UI feels faster and more responsive than dev mode.

Use two terminals from the repo root.

### Terminal 1 — Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8001
```

- Health: http://localhost:8001/health
- API docs: http://localhost:8001/api/v1/docs

On first start the API creates `workspace/raw/` and `workspace/processed_small/` if they are missing.

### Terminal 2 — Frontend

```bash
cd frontend
cp .env.example .env   # if .env does not exist yet
yarn install
yarn build
yarn preview
```

- App: http://localhost
- Backend URL: `NUXT_API_BASE=http://localhost:8001` (see [frontend/.env.example](frontend/.env.example))

Re-run `yarn build` after frontend code changes; restart the backend process after backend code changes.

## Getting started

Follow these steps in order after cloning the repo.

### 1. Add your photos

Copy image files into **`workspace/raw/`** at the repo root (or into the folder set by `WORKSPACE_ROOT` in [backend/.env.example](backend/.env.example)).

- **Subfolders** are supported (e.g. `workspace/raw/Welcome/`, `workspace/raw/Reception/`) — each top-level folder becomes an album in the UI.
- **Supported formats**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.heic`, `.heif`, `.bmp`, `.tiff`, `.tif`

Example:

```bash
cp -R /path/to/your/photos/* workspace/raw/
```

You can add photos before or after starting the servers. The **Library state** tab detects new files automatically (status updates every few seconds).

### 2. Start backend and frontend

See [Run in production mode](#run-in-production-mode) above. Open http://localhost when both processes are running.

### 3. Set your OpenAI API key

In the app, open the **Settings** tab:

1. Paste your OpenAI API key.
2. Click **Save**.

The key is stored in `workspace/openai_config.json` (gitignored) — **not** in `backend/.env`.

- **Resize** (thumbnails) does not need an API key.
- **Analysis** and **Photobook** chat require a saved key.

Optional: set `OPENAI_MODEL` in `backend/.env` (default `gpt-4o-mini`).

### 4. Library state tab — process your library

Open the **Library state** tab (first tab). Complete the five pipeline steps in order:

| Step | UI label | What you do |
|------|----------|-------------|
| **1** | Images in library | After copying into `raw/`, wait for the green check — at least one image must exist under `workspace/raw/` |
| **2** | Resize complete | Click **Start** on the resize card — generates thumbnails in `workspace/processed_small/` (same folder layout as `raw/`) |
| **3** | Colours analysed | When resize is complete, click **Start** on the colours card — extracts dominant palette colours into metadata |
| **4** | Analysis | When colours are complete, click **Start** (or **Resume** / **Rerun**) — OpenAI vision fills captions and wedding metadata |
| **5** | Categorisation | When analysis is complete, click **Start** (or **Resume** / **Rerun**) — groups images into story categories for photobook planning |

Progress appears on each card and in the header. When all five flags are green, you will see **Processing complete**.

### 5. Images tab — browse the gallery

Open the **Images** tab (second tab):

1. Select one or more **folders** in the left panel.
2. Browse the **thumbnail grid** (processed images).
3. After analysis, use **Find photos** filters (bride, groom, guests, group size, photo quality, blur) — requires the OpenAI key from Settings.
4. After categorisation, filter by **story categories** or **Uncategorized**.
5. Click a thumbnail to open the **slideshow** viewer.

### 6. Photobook tab — chat and create

Open the **Photobook** tab (requires an OpenAI key and **categorisation complete** in Library state):

1. **Chat** (left): describe your book, for example: *“Create an 8-page photobook for our wedding, starting with welcome shots, then ceremony and reception.”* The planner sets page sequence, layouts, narratives, and category picks.
2. **Pages** (center): review generated page tabs and previews; click **Compose** to fill image and text slots with AI.
3. **Extra images** (right): assign images into the focused slot.

State is saved in `workspace/photobook.json`. In-app page previews render using the frontend layout library (`getPageLayout`); the backend owns layout definitions for planning and compose.

The **Layouts** tab is an optional layout catalogue reference — you do not need it for the core workflow above.

## Project layout

```
photo-organiser-ai/
├── backend/app/       # FastAPI application
├── frontend/app/      # Nuxt application
└── workspace/         # On-disk photo library (see workspace/README.md)
    ├── raw/                    # Your originals (gitignored)
    ├── processed_small/        # Thumbnails (gitignored)
    ├── pipeline_state.json     # Pipeline flags (gitignored, runtime)
    ├── image_metadata.json     # Captions, palette & metadata (gitignored, runtime)
    ├── image_categories.json   # Story categories (gitignored, runtime)
    ├── openai_config.json      # API key from Settings (gitignored)
    └── photobook.json          # Photobook editor state
```

To use a different folder for photos, set `WORKSPACE_ROOT` in `backend/.env` (absolute path recommended). Details: [workspace/README.md](workspace/README.md).

## Contributing

### Run in development mode

Use dev mode when changing code — hot reload on both sides makes iteration faster, at the cost of a slower UI load.

**Terminal 1 — Backend** (auto-reload on Python changes):

```bash
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload --port 8001
```

**Terminal 2 — Frontend** (Vite HMR):

```bash
cd frontend
cp .env.example .env
yarn install
yarn dev
```

The frontend listens on **port 80** so you can open http://localhost without a port number. On macOS and Linux, binding to port 80 may require elevated privileges — if `yarn dev` fails with `EACCES`, run `sudo yarn dev` in the frontend directory (or use a port-forward from 80 to another port).

Run tests after backend changes:

```bash
cd backend
uv run pytest
```

### Repository structure

```
photo-organiser-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, lifespan, CORS
│   │   ├── config.py            # Settings (WORKSPACE_ROOT, OPENAI_MODEL, …)
│   │   ├── api/                 # HTTP + WebSocket routes
│   │   │   ├── images.py        # Folders, image list, media
│   │   │   ├── photobook.py     # Photobook CRUD, chat, compose
│   │   │   ├── settings.py      # OpenAI key storage
│   │   │   └── ws.py            # Pipeline status + start resize/analysis
│   │   ├── schemas/             # Pydantic models (API + OpenAI structured output)
│   │   ├── services/            # Business logic (pipeline, analysis, photobook)
│   │   ├── prompts/
│   │   │   └── prompts.py       # All OpenAI system prompts (edit here)
│   │   ├── page_layouts/        # Layout definitions for planner + compose
│   │   │   ├── registry.py      # Merges layout modules; used by API
│   │   │   ├── photo_grids.py
│   │   │   ├── cover_pages.py
│   │   │   └── wedding_album.py
│   │   └── typography/          # Google Fonts metadata for prompts + compose
│   └── tests/
├── frontend/
│   └── app/
│       ├── pages/               # Routes (single page: index.vue → /)
│       ├── components/          # UI tabs, photobook editor, gallery, pipeline
│       ├── composables/         # API clients, WebSocket, photobook state
│       ├── constants/
│       │   └── page_layouts/  # JSON layout previews (mirror backend layouts)
│       └── types/               # Shared TS types
└── workspace/                   # Runtime data (photos, metadata, photobook.json)
```

| Area | Backend | Frontend |
|------|---------|----------|
| Page layouts (planner/compose) | `backend/app/page_layouts/*.py` | `frontend/app/constants/page_layouts/*.json` (render tree for previews) |
| Typography catalog | `backend/app/typography/` | `frontend/app/constants/typography/` |
| OpenAI prompts | `backend/app/prompts/prompts.py` | — (server-side only) |
| Text slot merge | `backend/app/page_layouts/registry.py` → `merge_text_slots` | Uses API `page.text_slots` after compose/patch |

When adding or changing a layout, update **both** the Python definition (used by the API and OpenAI) and the matching JSON under `frontend/app/constants/page_layouts/` so the **Layouts** tab and in-app previews stay in sync.

### Where to add prompts

All OpenAI **system prompts** live in one file:

**[`backend/app/prompts/prompts.py`](backend/app/prompts/prompts.py)**

| Constant | Used by | Purpose |
|----------|---------|---------|
| `IMAGE_ANALYSIS_SYSTEM_PROMPT` | `services/image_analysis.py` | Vision captions + wedding metadata per image |
| `IMAGE_CATEGORISER_SYSTEM_PROMPT` | `services/image_categoriser.py` | Group analysed images into story categories |
| `PHOTOBOOK_PLANNER_SYSTEM_PROMPT` | `services/photobook_planner.py` | Page sequence, layouts, narratives, category picks |
| `PHOTOBOOK_PLAN_LAYOUT_FIX_SYSTEM_PROMPT` | `services/photobook_plan_validation.py` | Correct invalid `layout_id` values |
| `PHOTOBOOK_COMPOSER_SYSTEM_PROMPT` | `services/photobook_compose.py` | Fill image/text slots for one page |

Add new prompt strings in `prompts.py`, then import them from the relevant service under `backend/app/services/`. Keep long instruction text out of service files so prompts stay easy to find and diff.

User-facing **chat messages** are not prompts — they come from the UI (`PhotobookChatPanel`) and are sent to `POST /api/v1/photobook/chat`.

## Developer reference

### WebSocket

Endpoint: `ws://localhost:8001/ws`

The UI connects on load, requests status once, and receives updates every 5 seconds.

| Direction | Message | Description |
|-----------|---------|-------------|
| FE → BE | `{"type":"request_status"}` | Request a single status snapshot |
| FE → BE | `{"type":"start_processing"}` | Begin resize (thumbnails in `processed_small/`) |
| FE → BE | `{"type":"start_palette_extraction"}` | Extract dominant colours into metadata (batched, saves every 100 images) |
| FE → BE | `{"type":"start_analysis"}` | Start or resume AI captions when resize and colour analysis are complete |
| FE → BE | `{"type":"rerun_analysis"}` | Re-run captions on every processed image |
| FE → BE | `{"type":"start_categorisation"}` | Group analysed images into categories (batched, random 400 per call) |
| FE → BE | `{"type":"rerun_categorisation"}` | Clear categories and re-run categorisation |
| BE → FE | `{"type":"status","payload":{...}}` | Heartbeat every 5s, on connect, and on request |

`payload` includes counts, `flags` (`image_found`, `resize_complete`, `has_analysed_color`, `image_analysis_complete`, `categorisation_complete`), `processing_busy`, resize/palette/analysis/categorisation progress (`processing_phase`), and step-specific completed/total counts.

WebSocket actions: `start_processing`, `start_palette_extraction`, `start_analysis`, `rerun_analysis`, `start_categorisation`, `rerun_categorisation`, `request_status`.

Pipeline order: `start_processing` → `start_palette_extraction` → `start_analysis` → `start_categorisation`. Only one background job runs at a time (resize, palette, analysis, or categorise).

Flags are persisted in `workspace/pipeline_state.json`. Per-image data lives in `workspace/image_metadata.json` (keyed by `path`): `palette_colors` (from palette extraction), plus `caption`, `number_of_people`, `has_bride`, `has_groom`, `has_other_people` (from analysis). Image categories live in `workspace/image_categories.json` (`{id, description, images[]}`).

### Photobook API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/photobook` | Load document and layout catalog (text slots merged with layout defaults) |
| `POST` | `/api/v1/photobook/chat` | Plan pages from a user message (requires OpenAI key) |
| `DELETE` | `/api/v1/photobook/chat` | Reset chat and storyboard |
| `POST` | `/api/v1/photobook/pages` | Add a page |
| `PATCH` | `/api/v1/photobook/pages/{page_id}` | Update page fields or slots |
| `DELETE` | `/api/v1/photobook/pages/{page_id}` | Remove a page (not the last one) |
| `POST` | `/api/v1/photobook/pages/{page_id}/compose` | Fill image and text slots for one page (metadata-only OpenAI call) |

Compose sends image metadata summaries to OpenAI — not image bytes or URLs. Text slots are merged with layout defaults on compose, patch, and every GET response.

### Tests

```bash
cd backend
uv run pytest
```

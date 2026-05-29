# Workspace

On-disk photo library for Photo Organiser AI. Sibling to `backend/` and `frontend/`.

For full setup and UI walkthrough, see the [root README](../README.md).

```
workspace/
├── raw/              # Original uploads (subfolders allowed)
└── processed_small/  # Resized copies (mirrors raw layout)
```

The backend creates `raw/` and `processed_small/` on startup if they are missing.

Processing progress and library flags are tracked in `pipeline_state.json` (gitignored) at this folder root:

- `image_found`
- `resize_complete`
- `has_analysed_color`
- `image_analysis_complete`
- `categorisation_complete`

Per-image data is stored in `image_metadata.json` (gitignored): a list of entries keyed by `path` (relative to `processed_small/`). Each entry has `palette_colors` (from colour extraction), plus `caption`, `number_of_people`, `has_bride`, `has_groom`, and `has_other_people` (from OpenAI vision analysis).

Story categories for photobook planning live in `image_categories.json` (gitignored): `{ id, description, images[] }`.

Photobook editor state is saved in `photobook.json` (gitignored).

The OpenAI API key is stored in `openai_config.json` (gitignored). Set it from the app **Settings** tab; it is not read from `backend/.env`.

## Configuring the path

Set `WORKSPACE_ROOT` in `backend/.env` to point elsewhere (absolute path recommended):

```bash
WORKSPACE_ROOT=/path/to/your/workspace
```

Default: `<repo>/workspace`.

For a future Electron build, point `WORKSPACE_ROOT` at the app’s user data directory so photos live outside the install bundle.

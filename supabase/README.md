---
title: "Supabase / PostGIS: schema and loader"
date: 2026-11-02
tags: [supabase, postgis]
aliases: [Supabase, Supabase spike]
---

# Supabase / PostGIS: schema and loader

Checks that the canonical JSON of the extraction
([`prototyp_v4.to_canonical`](../services/extractor/prototyp_v4.py)) fits the schema of the
[architecture §5.2](../docs/ARCHITECTURE_BAUGRUNDMODELL.md#52-supabase-schema-draft-migration) and
that it can be queried spatially. The app does not use the database yet.

| File | What it does |
|---|---|
| [`migrations/0001_core.sql`](migrations/0001_core.sql) | Migration (copied from the architecture; PostGIS types qualified as `extensions.geometry`) |
| [`local_shim.sql`](local_shim.sql) | Only for a local Postgres: the minimal `auth` schema that Supabase ships with |
| [`load_extraction.py`](load_extraction.py) | Loads documents, runs, Bohrungen (collar PointZ transformed to the project CRS), Schichten and water |

```bash
psql -f supabase/local_shim.sql -f supabase/migrations/0001_core.sql   # on Supabase: only the migration
python supabase/load_extraction.py --dsn "..." --project "Berlin" --crs 25833 berlin_v67b.json
```

**Result (2026-10-26, local PostgreSQL 16 + PostGIS 3):** migration without errors (15 tables);
Berlin: 7 Bohrungen, 80 Schichten, 2 water levels, 5 collars in EPSG:25833; Marl: 12 Bohrungen,
97 Schichten. Distance queries between Bohrungen are correct (422C-460 ↔ 422C-461: 32.2 m).

**Finding:** with `create extension postgis with schema extensions`, the `geometry` type is not on
the `search_path` of a normal Postgres; Supabase has it by default. The migration qualifies the types
(`extensions.geometry`) to work in both.

Up: [Documentation index](../docs/README.md)

Related: [Architecture](../docs/ARCHITECTURE_BAUGRUNDMODELL.md) · [17 Algorithm](../docs/17_extraction_algorithm.md) · [Modeler](../services/modeler/README.md)

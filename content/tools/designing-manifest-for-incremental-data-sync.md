Title: Designing the Perfect Manifest for Incremental Data Sync
Date: 2026-02-05
Category: Tools
Tags: data-sync, architecture, frictionless-data, json
Status: draft

Building a data synchronization service is easy until things break. It's easy to move files from Point A to Point B, but it's incredibly hard to guarantee that Point B is a perfect mirror of Point A — especially when networks fail, data arrives out of order, or sources go silent.

In this post, we explore the architecture of a robust **Manifest-Driven Synchronization Protocol**. We move beyond simple file transfers to a system that prioritizes data integrity, observability, and "fail-fast" validation.

## The Core Philosophy: Sync State, Not Just Files

The biggest mistake in sync design is treating the **Data File** as the source of truth. Data files are just payloads. The real logic belongs in a **Manifest File** — a self-contained "envelope" that describes the state of the system at a specific moment.

A robust manifest must answer three questions that the data file cannot:

1. **Completeness:** "Did I miss a batch between 10:00 and 10:15?"
2. **Silence:** "Is the source empty, or is the upstream job broken?"
3. **Integrity:** "Is this file exactly what the source intended to send?"

## The Three Timelines Problem

"Time" is ambiguous. To prevent data loss during "late arriving" events, we split timestamps into strict roles:

* **System Time (Log/Insert Time):** The **Anchor**. This is the monotonically increasing timestamp (or offset) from the source database. It is the *only* safe cursor for defining sync ranges (`Range Start` / `Range End`) because it guarantees no gaps.
* **Business Time (Event Time):** The **Context**. This tells the consumer when the real-world event happened. It is useful for analytics but useless for sync logic because it can arrive out of order.
* **Extraction Time:** The **Audit**. When the job ran.

## Sequence Numbers are for Humans, Not Machines

We debated using sequence numbers (`Batch #452`, `Batch #453`) for continuity checks. The conclusion: **Sequence Numbers are dangerous for logic** because they break during patches.

*Scenario:* You re-run the job for "Monday Morning" to fix a bug.

*Result:* You generate a new Manifest `#500` that contains old data.

*Verdict:* Consumers must rely on **Time Ranges** (`RangeStart == Previous.RangeEnd`) for logic. Sequence numbers stay in the filename solely for human debugging and sorting.

## Standardize Where Possible: Frictionless Data

Instead of inventing a proprietary schema format, we adopted the **Frictionless Data (Data Package)** standard. This allows us to use standard tools for schema validation while injecting our custom logic into extensible `x-` fields.

* **Standard:** `resources` array, `schema`, `path`.
* **Custom:** `x-sync-meta` (for ranges/status), `x-sync-summary` (for global stats).

## The "Empty Batch" Protocol

Silence is ambiguous. Does "No Data" mean "Nothing happened" or "The server crashed"?

To solve this, we mandate that **Manifests are always generated**, even if the `resources` array is empty. A manifest with `range_start: 10:00` / `range_end: 10:15` and an empty `resources` array is a powerful signal: *"We checked 10:15, and it is healthy and empty."*

## The Manifest Structure

Here is the JSON specification. It balances standard compliance with rigorous synchronization logic.

```json
{
  "version": "1.0.0",
  "created": "2026-02-05T13:32:12.231Z",
  "id": "b03ec84-77fd-4270-813b-0c698943f7ce",
  "name": "core.visits_ST001_456",
  
  "x-sync-meta": {
    "datasource_id": "core.visits",
    "namespace": "acme.prod",
    "scope": { "study_code": "ST001" },
    "range_start": "2026-02-05T14:00:00Z",
    "range_end": "2026-02-05T14:15:00Z"
  },

  "x-sync-summary": {
    "record_count": 15200,
    "last_ingestion_timestamp": "2026-02-05T13:55:00Z",
    "last_extraction_timestamp": "2026-02-05T13:50:00Z"
  },

  "resources": [
    {
      "name": "core.visits_ST001_20260205T1400Z_20260205T1415Z",
      "path": "core.visits_ST001_20260205T1400Z_20260205T1415Z.parquet",
      "format": "parquet",
      "bytes": 1048576,
      "hash": "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
      
      "x-sync-stats": {
        "record_count": 500,
        "last_ingestion_timestamp": "2026-02-05T14:05:00Z",
        "last_extraction_timestamp": "2026-02-05T14:03:00Z"
      },

      "schema": {
        "primaryKey": ["_pk", "study_code"],
        "fields": [
          { "name": "_pk", "type": "integer" },
          { "name": "study_code", "type": "string" },
          { "name": "_ingestion_timestamp", "type": "datetime" },
          { "name": "_extraction_timestamp", "type": "datetime" },
          { "name": "subject_id", "type": "string", "title": "Subject ID" },
          { "name": "treatment_arm", "type": "string", "x-unblinding": true }
        ]
      }
    }
  ]
}
```

The key elements:

* **`x-sync-meta`**: The envelope. Contains the time range (`range_start` / `range_end`) that consumers use for continuity checks. These use the internal ingestion timestamp, which is monotonically increasing and safe for sync logic. The `namespace` identifies the tenant, and `scope` narrows the data to a specific partition (e.g., a study).

* **`x-sync-summary`**: Global stats to detect data drift. If `record_count` suddenly drops by 50%, something is wrong upstream. The timestamps track the most recent data in the table within this scope.

* **`resources`**: Standard Frictionless Data definition. Each resource includes a `hash` for integrity verification and `x-sync-stats` for optimization (consumers can skip files based on timestamps without parsing them). Note that `resources` can be empty when there is no new data — this deviates from the Data Package standard but avoids cluttering storage with empty files.

* **`schema`**: Inline schema with support for custom metadata like `x-unblinding` to flag sensitive fields. The `primaryKey` includes both `_pk` and any scope keys.

## Takeaway

By adopting this structure, we move from "throwing files over the wall" to a **State-Aware Synchronization**. The consumer doesn't just receive data; they receive a mathematical proof that their view of the data is complete, consistent, and authentic.

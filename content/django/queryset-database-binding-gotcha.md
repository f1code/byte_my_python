Title: The QuerySet Database Binding Gotcha
Date: 2026-01-27
Category: Django
Tags: django, database, queryset, replica

When working with Django's multi-database support, there's a subtle issue that can trip you up: QuerySets remember which database they're bound to, and this can lead to unexpected conflicts.

## The Setup

In our codebase (Prancer), we have custom managers that use `using(self.db)` to bind a QuerySet to a specific database. This is a common pattern when you want to route queries to a replica for read-heavy operations.

```python
class SomeCustomManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using(self.db)
```

The key thing to understand is that once you call `.using()`, that QuerySet is bound to that database **from that point forward**. Any further filtering or chaining will still use that database.

## The Problem

We ran into trouble with `PatientDataSource` (and generally when using `HistoryTableRule`). These components accept a QuerySet that is constructed at initialization time — essentially acting as a configuration object.

The issue: this QuerySet is effectively **global state**. It gets created once, bound to the `'default'` database, and then reused across requests.

Later, when a query actually executes:

1. Filters are added to this pre-constructed QuerySet
2. The result is used to filter the main Data Source QuerySet
3. But the main QuerySet is bound to `replica0`

And now you have a conflict: you're trying to combine QuerySets that point to different databases. Django does not handle this gracefully.

## Why This Happens

The root cause is the disconnect between:

* **Initialization time** — when the QuerySet is constructed and bound to `default`
* **Execution time** — when the actual query runs and should use `replica0`

If you're building reusable components that accept QuerySets as configuration, you need to be aware that the database binding travels with the QuerySet.

## The Fix

The solution depends on your specific case, but generally:

* Defer QuerySet construction until execution time, rather than initialization time
* Pass a callable (like a lambda or method reference) instead of a pre-built QuerySet
* Explicitly rebind the QuerySet with `.using()` right before combining it with other QuerySets - this lets Django
re-evaluate the database context

The last option is often the quickest fix, but the first two are cleaner architecturally — they avoid the "global state" problem entirely.

## Takeaway

When you see `.using()` in your codebase, think carefully about when that QuerySet is created versus when it's used. If there's a gap, you might be setting yourself up for a database routing conflict.

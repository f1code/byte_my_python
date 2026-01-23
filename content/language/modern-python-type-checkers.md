Title: Exploring Modern Python Type Checkers
Date: 2026-01-12
Modified: 2026-01-12
Category: Language
Tags: vscode, type-checking, ty, pyrefly

I’ve been playing around with alternative Python type checkers and language servers, looking beyond the more legacy options to find a setup that’s powerful without getting in the way. Along the way, I compared [ty](https://docs.astral.sh/ty/) and [Pyrefly](https://pyrefly.org/), tweaked extensions and inlay hints, and ran into a few interesting differences in behavior, ergonomics, and typing semantics. The result isn’t a definitive winner yet, but it did surface some useful insights—and a couple of gotchas about Python typing that are easy to miss.

Both extensions were very easy to install from the Extension Marketplace in Cursor.

I disabled the **“Python” extension from Anysphere** (keeping the `ms-python` one). Anysphere’s extension is essentially **pyright**, which was doing double duty with **ty**.

For **ty**, I also disabled the language server, as suggested in the documentation:

```json
{
  "python.languageServer": "None"
}
```

After that, there were still some logs being output:

* ty
* ty language server

There were also **inlay hints** showing inferred types. They’re somewhat useful, but overall a bit too much visual clutter, so I disabled them. I can still see variable types via tooltips when needed.

---

I also tried **Pyrefly**. The setup was similar, but I didn’t need to manually disable the language server—Pyrefly automatically disables **Pylance**. It offers a few more customization options. One thing to note: by default, it will **not display type errors unless a configuration file is found in the project**. This can be forced via the *“Display Type Errors”* setting.

---

Where **Pyrefly’s language server** was better:

* In one instance, it was able to automatically locate missing imports when I used `Cmd + .`. This involved a type alias, where **ty** took a few more shortcuts.

---

**Inlay hints comparison**

Ty was a bit more obnoxious with inlay hints out of the box, while Pyrefly tended to include them only when they were genuinely useful. For example:

```python
def merge_data(self, source: str, dest: str):
    source = check_sql_id(source)
    self._validate_source_schema(source)
    stmt = build_update_statement(self.con, source, dest, namespace, scope)
```

Both tools correctly inferred the type of `source` as `SqlIdString` (rather than the original `str`), but:

* **ty** added an inlay hint
* **pyrefly** did not, unless I was also renaming the variable

Ty also tended to union types with `| Unknown` when using list comprehensions or list literals, which was pretty weird and annoying. Thankfully, there’s already an open issue for this, so I’ll keep tracking it.

Pyrefly had one case where it refused to redefine a variable’s type via annotation. That’s valid Python, though arguably questionable style.

Finally, I use Protocol for my interfaces on the project, and Pyrefly had generally more helpful messages when an interface was not correctly implemented.

---

Both of those are easy to integrate in the CI workflow, and they play nicer than pyright with Python's package manager.

---

Overall, I’m more aligned with **Pyrefly**, but I’m sticking with **ty** for now—mainly because I resonate more with Astral’s values than Meta’s. I’ll revisit that choice if ty starts to cause friction.

One final typing takeaway: **a type alias is not the same as `NewType`**. A type alias doesn’t provide real type safety—it’s just a nickname for an existing type.


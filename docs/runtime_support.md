# 🧭 Runtime Support Services

This guide explains the reusable support services introduced in version `0.8.0`.

Use it when maintaining diagnostics, runtime log inspection, preference updates, or status history inside the NiceGUI shell.

---

## 🎯 Goals

The `application` package now contains UI-facing services that stay independent from NiceGUI widgets.

They exist to:

- keep page builders focused on visual composition;
- keep callbacks small and easy to test;
- avoid file reads, settings writes, or validation logic directly inside UI code;
- make diagnostics and support behavior reusable in future project-specific pages.

---

## 🧱 Service modules

| Module | Responsibility |
| ------ | -------------- |
| [`diagnostics.py`](../src/desktop_app/application/diagnostics.py) | Builds grouped support snapshots from `AppState`. |
| [`log_reader.py`](../src/desktop_app/application/log_reader.py) | Resolves the runtime log path and reads a bounded tail. |
| [`preferences.py`](../src/desktop_app/application/preferences.py) | Validates and persists safe template preferences. |
| [`status.py`](../src/desktop_app/application/status.py) | Formats recent in-memory status history. |

These modules do not import NiceGUI. Pages call them and render the returned data.

---

## 🔍 Diagnostics snapshots

The diagnostics service returns immutable sections and items:

```python
sections = build_diagnostics_sections(state)
```

The `/diagnostics` page renders those sections instead of reading scattered state fields directly.

Current sections include:

- runtime;
- paths;
- lifecycle;
- logging;
- settings.

Only technical metadata should be exposed. Do not add secrets, tokens, credentials, or confidential document contents.

---

## 📜 Bounded log reading

The log reader service returns a `LogSnapshot`:

```python
snapshot = read_log_snapshot(state=state, max_lines=120)
```

The snapshot includes:

- resolved path;
- file existence;
- requested line limit;
- latest lines;
- recoverable read error, when applicable.

The service reads only the latest lines with bounded memory. It does not stream, poll, or watch the log file.

---

## ⚙️ Preference updates

The preferences service validates user input before updating `AppState` and saving settings:

```python
update_theme_preference("dark", state=state)
update_font_scale_preference(1.1, state=state)
update_accent_color_preference("#2563EB", state=state)
update_auto_save_preference(True, state=state)
```

Each function returns a `PreferenceUpdateResult` with:

- whether the value was accepted;
- whether persistence succeeded;
- status message;
- status level.

The service also pushes the result into `state.status`, so the status page can show recent feedback.

---

## 💬 Status history

The status service formats recent in-memory messages from `state.status.history`:

```python
items = build_status_history_snapshot(state, limit=20)
```

The `/status` page shows the current message and recent history for the current process. This history is not persisted and should remain lightweight.

---

## 🧪 Tests

Run focused support service tests:

```powershell
pytest tests/application/test_diagnostics.py
pytest tests/application/test_log_reader.py
pytest tests/application/test_preferences.py
pytest tests/application/test_status.py
```

Run the UI route tests:

```powershell
pytest tests/ui/test_pages_and_router.py
```

---

## 🔗 Related documents

- [Documentation index](README.md)
- [UI shell guide](ui_shell.md)
- [Architecture overview](architecture.md)
- [Settings subsystem](settings.md)
- [Application state](state.md)

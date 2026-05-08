# 🧠 Application State

This guide explains the complete `AppState` model used by **NiceGui Windows Base**.

Use this document when you need to add shared runtime values, diagnose startup behavior, connect future UI controls to state, or decide whether a value belongs in state, constants, settings, or infrastructure.

---

## 🎯 Goals

The application state model is designed to:

- keep shared mutable runtime data in one typed place;
- separate persisted preferences from transient runtime status;
- support diagnostics without reading NiceGUI internals directly;
- keep `core/state.py` free from file I/O, logger configuration, and UI element creation;
- prepare future NiceGUI callbacks for small state updates;
- avoid turning static constants or live infrastructure objects into mutable state.

---

## 🧭 State sections

| Section               | Persistence | Purpose                                                                                   |
| --------------------- | ----------- | ----------------------------------------------------------------------------------------- |
| `meta`                | Yes         | User-facing application metadata.                                                         |
| `runtime`             | No          | Startup source, startup message, runtime mode, reload flag, and selected port.            |
| `paths`               | No          | Effective settings, log, executable, working directory, and PyInstaller extraction paths. |
| `window`              | Yes         | Future native window position and size preferences.                                       |
| `ui`                  | Yes         | User-editable visual preferences.                                                         |
| `ui_session`          | No          | Transient UI session state such as active view and busy message.                          |
| `assets`              | No          | Resolved icon, page image, and splash paths for diagnostics.                              |
| `log`                 | Mixed       | Persisted logger preferences plus runtime status such as effective file path.             |
| `behavior`            | Yes         | General behavior preferences such as auto-save.                                           |
| `settings`            | No          | Settings file existence, default usage, latest scopes, and last error.                    |
| `settings_validation` | No          | Warnings from the latest settings validation.                                             |
| `lifecycle`           | No          | High-level application, native window, client, splash, and shutdown flags.                |
| `status`              | No          | Current and recent status messages for future UI feedback.                                |

---

## 🧱 Persistence boundary

Only user-editable preferences should be written to `settings.toml`.

Persisted groups:

- `meta`
- `window`
- `ui`
- `log` configuration fields
- `behavior`

Runtime-only groups:

- `runtime`
- `paths`
- `ui_session`
- `assets`
- `log.effective_file_path`
- `settings`
- `settings_validation`
- `lifecycle`
- `status`

This avoids saving values that are valid only for the current process, current machine, current executable folder, or current client connection.

---

## ⚙️ Settings file state

`SettingsState` intentionally distinguishes these cases:

| Field               | Meaning                                                                            |
| ------------------- | ---------------------------------------------------------------------------------- |
| `file_exists`       | Whether `settings.toml` exists for the current runtime.                            |
| `using_defaults`    | Whether the application is using in-memory defaults.                               |
| `last_loaded_scope` | Last successful load scope, such as `all`, `group:ui`, or `property:app.ui.theme`. |
| `last_saved_scope`  | Last successful save scope.                                                        |

Loading missing settings is not an error. The application keeps default values in memory and creates `settings.toml` only when a save operation is explicitly requested.

---

## 🖥️ UI session state

`UiSessionState` is transient and should be updated by future NiceGUI callbacks.

Examples:

```python
state.ui_session.is_busy = True
state.ui_session.busy_message = "Saving settings..."

save_settings_group("ui")

state.ui_session.is_busy = False
state.ui_session.busy_message = None
```

Keep callbacks small. Let services perform file I/O or integration work, then update only the relevant state fields.

---

## 🔁 NiceGUI binding recommendation

NiceGUI supports binding UI element properties to model properties and provides `binding.bindable_dataclass()` for dataclass-based models.

For this project, do **not** decorate the full `AppState` with NiceGUI binding. `AppState` contains runtime paths, lifecycle flags, validation lists, status history, and nested state groups. Binding all of it would increase coupling and create unnecessary observable fields.

Recommended usage:

- keep `core/state.py` as plain dataclasses;
- use NiceGUI binding only for small UI-facing models when a screen needs automatic updates;
- prefer binding transient view state, such as a settings form model or a future status panel model;
- avoid binding infrastructure objects, large collections, or values that are not shown in the UI.

A future screen may introduce a bindable model near the UI layer, for example:

```python
from dataclasses import dataclass

from nicegui import binding


@binding.bindable_dataclass
@dataclass
class SettingsFormState:
    theme: str = "light"
    dense_mode: bool = False
    is_busy: bool = False
```

This keeps NiceGUI-specific behavior near the UI and keeps the central state model easy to test.

---

## ✅ Add a new state field

Before adding a field, ask:

1. Does the value change during runtime?
2. Is it shared across modules?
3. Does the UI need to observe it?
4. Should it be saved to `settings.toml`?
5. Is it data rather than a live infrastructure object?

If the field is persisted, update:

- [`settings.toml`](../src/desktop_app/settings.toml)
- [`schema.py`](../src/desktop_app/infrastructure/settings/schema.py)
- [`mapper.py`](../src/desktop_app/infrastructure/settings/mapper.py)
- [`toml_document.py`](../src/desktop_app/infrastructure/settings/toml_document.py)
- [`settings.md`](settings.md)

If the field is runtime-only, update only the module that resolves or owns that runtime event.

---

## 🔗 Related documents

- [Settings and application state](settings.md)
- [Execution modes](execution_modes.md)
- [Logging subsystem](logging.md)
- [Troubleshooting](troubleshooting.md)

# 🔐 PowerShell Execution Policy

This guide explains why PowerShell may block `.venv` activation or project scripts and how to resolve it safely.

---

## 📌 When should you use this guide?

Use this guide if one of these commands is blocked:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\package_windows.ps1
```

Common message:

```text
running scripts is disabled on this system
```

---

## ❓ Why does this happen?

PowerShell has an execution policy setting that controls script execution.

Activating a Python virtual environment in PowerShell runs:

```text
.venv\Scripts\Activate.ps1
```

On some machines, especially corporate machines, this script is blocked by policy.

---

## 🔎 Check current policy

```powershell
Get-ExecutionPolicy
Get-ExecutionPolicy -List
```

This helps identify whether the restriction is configured for the current process, current user, local machine, or by organization policy.

---

## ✅ Recommended temporary solution

Use this in the current terminal window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate `.venv`:

```powershell
.\.venv\Scripts\Activate.ps1
```

This does not permanently change Windows policy. It disappears when the terminal window is closed.

---

## 📦 Running the packaging script safely

If this command is blocked:

```powershell
.\scripts\package_windows.ps1
```

Use a process-level bypass only for that command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

This does not permanently change system, user, or machine policy settings.

---

## 🏢 Corporate environments

In corporate environments, policies may be controlled by IT.

Recommended behavior:

- prefer `-Scope Process` for local development;
- do not change machine-wide policy without authorization;
- do not bypass corporate controls permanently;
- contact IT if policy is enforced by organization rules.

---

## ✅ Summary

| Situation                  | Recommended action                                                                          |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| `.venv` activation blocked | Use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`                            |
| Packaging script blocked   | Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1` |
| Corporate policy enforced  | Contact IT or use approved process                                                          |
| Unsure what to use         | Start with the process-level option                                                         |

---

## 🔗 Related documents

- [Python 3.13 setup on Windows](python_windows_setup.md)
- [VS Code setup](vscode_setup.md)
- [Windows packaging](packaging_windows.md)
- [Troubleshooting](troubleshooting.md)

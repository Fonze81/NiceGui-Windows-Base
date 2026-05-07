# -----------------------------------------------------------------------------
# File: src/desktop_app/infrastructure/logger/exceptions.py
# Purpose:
# Declare logging subsystem exceptions.
# Behavior:
# Provides a dedicated validation exception so logger configuration failures can
# be handled clearly by callers.
# Notes:
# LoggerValidationError inherits from ValueError because it represents invalid
# values provided to the logging subsystem.
# -----------------------------------------------------------------------------


class LoggerValidationError(ValueError):
    """Represent invalid configuration data in the logging subsystem."""

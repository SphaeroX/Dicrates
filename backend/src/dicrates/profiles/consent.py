"""Versioning of the consent text shown in the app.

The app shows the consent text for `CURRENT_CONSENT_VERSION` (ARB keys
`consentBodyV<version>`) and sends that version back. Raising this value forces
every user to consent again before playing (`require_consent`).
"""

CURRENT_CONSENT_VERSION = "1"

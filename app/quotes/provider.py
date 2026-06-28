from __future__ import annotations

# Compatibility wrapper.
#
# Older project versions imported QuoteProvider from app.quotes.provider.
# The canonical interface is now app.quotes.provider_interface. Keep this file
# to avoid breaking old imports.

from app.quotes.provider_interface import QuoteProvider

__all__ = ["QuoteProvider"]

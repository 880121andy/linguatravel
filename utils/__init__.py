"""
Gradio compatibility utilities for LinguaTravel.
"""

from .gradio_compat import ensure_chat_history_compatible, normalize_history_for_gradio_v3, gradio_version

__all__ = ["ensure_chat_history_compatible", "normalize_history_for_gradio_v3", "gradio_version"]

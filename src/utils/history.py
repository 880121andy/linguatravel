"""
History normalization utilities for Gradio Chatbot compatibility.

This module provides functions to normalize chat history data from various
formats (including Gradio v7 role/content dicts) to the Gradio 6.x format
(list of [user_text, bot_text] pairs).
"""

from typing import Any, List


def normalize_history(history: Any) -> List[List[str]]:
    """
    Normalize a chat history into the Gradio 6.x Chatbot shape:
    a list of [user_text, bot_text] pairs (both strings).
    Accepts history items in common variants (tuple/list of different lengths,
    dicts with common keys, nested lists), and coerces them to strings.

    Args:
        history: The chat history in any supported format.

    Returns:
        A list of [user_text, bot_text] pairs where both elements are strings.
    """
    normalized: List[List[str]] = []
    if not history:
        return []

    for idx, item in enumerate(history):
        # If it's already a list/tuple
        if isinstance(item, (list, tuple)):
            if len(item) == 2:
                a, b = item
            elif len(item) == 1:
                a, b = item[0], ""
            else:
                # If there are more than 2 elements, assume first is user, rest is assistant (join them)
                a = item[0]
                b = " ".join(str(x) for x in item[1:])
            normalized.append([str(a), str(b)])
            continue

        # If item is a dict: handle a few common shapes
        if isinstance(item, dict):
            # Common formats:
            # {"user": "...", "bot": "..."}
            # {"role": "user", "content": "..."} pairs stored per message
            if "user" in item or "bot" in item:
                a = item.get("user", "")
                b = item.get("bot", "")
                normalized.append([str(a), str(b)])
                continue

            if "role" in item and "content" in item:
                # A single message dict. We can't pair it alone; treat as user if role==user else assistant.
                role = item.get("role")
                content = item.get("content", "")
                if role == "user":
                    normalized.append([str(content), ""])
                else:
                    # If assistant-only, insert empty user + assistant content
                    normalized.append(["", str(content)])
                continue

            # Some histories are stored as {'messages': [...]} or similar
            if "messages" in item and isinstance(item["messages"], (list, tuple)):
                # try to flatten messages into pairs
                msgs = item["messages"]
                # naive grouping: take messages two at a time
                for i in range(0, len(msgs), 2):
                    left = msgs[i]
                    right = msgs[i + 1] if i + 1 < len(msgs) else ""
                    # recursively normalize these two
                    left_text = left.get("content") if isinstance(left, dict) else str(left)
                    right_text = right.get("content") if isinstance(right, dict) else str(right)
                    normalized.append([str(left_text), str(right_text)])
                continue

            # Fallback: stringify the dict
            normalized.append([str(item), ""])
            continue

        # Anything else: coerce to a single user message with empty assistant reply
        normalized.append([str(item), ""])

    return normalized

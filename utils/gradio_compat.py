from typing import Any, List, Tuple
import importlib

try:
    from packaging.version import parse as parse_version
except Exception:
    def parse_version(v: str):
        return tuple(int(x) for x in v.split(".") if x.isdigit())


def gradio_version() -> Any:
    try:
        gr = importlib.import_module("gradio")
        return parse_version(getattr(gr, "__version__", "0"))
    except Exception:
        return parse_version("0")


def normalize_history_for_gradio_v3(history: Any) -> List[Tuple[str, str]]:
    """
    Convert various Gradio chat-history formats (v6/v7 dicts/lists of message dicts, etc.)
    into the legacy Gradio v3 format: a list of [user_text, bot_text] pairs.
    """
    if not history:
        return []

    if isinstance(history, list) and all(
        isinstance(el, (list, tuple)) and len(el) == 2 for el in history
    ):
        return [(str(u or ""), str(b or "")) for u, b in history]

    if isinstance(history, dict):
        for key in ("messages", "history", "chat"):
            if key in history and isinstance(history[key], list):
                return normalize_history_for_gradio_v3(history[key])
        flat = []
        for k, v in history.items():
            flat.append([str(k), str(v)])
        return flat

    if isinstance(history, list) and all(isinstance(m, dict) for m in history):
        pairs: List[Tuple[str, str]] = []
        pending_user = None
        for msg in history:
            role = msg.get("role") or msg.get("from") or msg.get("sender")
            content = msg.get("content") if "content" in msg else msg.get("text", "")
            if isinstance(content, dict):
                content = content.get("text") or content.get("body") or str(content)
            content = "" if content is None else str(content)
            role = (role or "").lower() if isinstance(role, str) else ""

            if role in ("user", "human"):
                if pending_user is None:
                    pending_user = content
                else:
                    pairs.append((pending_user, ""))
                    pending_user = content
            elif role in ("assistant", "bot", "system"):
                if pending_user is None:
                    pairs.append(("", content))
                else:
                    pairs.append((pending_user, content))
                    pending_user = None
            else:
                if pending_user is None:
                    pending_user = content
                else:
                    pairs.append((pending_user, content))
                    pending_user = None

        if pending_user is not None:
            pairs.append((pending_user, ""))
        return pairs

    if isinstance(history, list) and all(isinstance(el, str) for el in history):
        pairs = []
        it = iter(history)
        for u in it:
            try:
                b = next(it)
            except StopIteration:
                b = ""
            pairs.append((u, b))
        return pairs

    try:
        items = [str(x) for x in history]
        pairs = []
        it = iter(items)
        for u in it:
            try:
                b = next(it)
            except StopIteration:
                b = ""
            pairs.append((u, b))
        return pairs
    except Exception:
        return []


def ensure_chat_history_compatible(history: Any) -> List[Tuple[str, str]]:
    """
    Public helper: returns chat history in v3 format (list of (user, assistant) pairs).
    """
    ver = gradio_version()
    try:
        if isinstance(ver, tuple) or (hasattr(ver, "major") and getattr(ver, "major", 0) == 3):
            return normalize_history_for_gradio_v3(history)
        if (hasattr(ver, "major") and getattr(ver, "major", 0) >= 6) or (isinstance(ver, tuple) and ver[0] >= 6):
            return normalize_history_for_gradio_v3(history)
    except Exception:
        return normalize_history_for_gradio_v3(history)
    return normalize_history_for_gradio_v3(history)

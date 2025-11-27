"""
Unit tests for the normalize_history function.
Tests verify that various chat history formats are correctly normalized
to the Gradio 6.x format: list of [user_text, bot_text] pairs.
"""

import pytest
from src.utils.history import normalize_history


class TestNormalizeHistory:
    """Tests for normalize_history function."""

    def test_empty_history(self):
        """Test that empty/None history returns empty list."""
        assert normalize_history(None) == []
        assert normalize_history([]) == []

    def test_list_of_pairs(self):
        """Test standard list of [user, bot] pairs format."""
        history = [
            ["Hello", "Hi there!"],
            ["How are you?", "I'm doing well, thanks!"],
        ]
        result = normalize_history(history)
        assert len(result) == 2
        assert result[0] == ["Hello", "Hi there!"]
        assert result[1] == ["How are you?", "I'm doing well, thanks!"]
        # Verify each item is a list of two strings
        for item in result:
            assert isinstance(item, list)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], str)

    def test_list_of_tuples(self):
        """Test standard list of (user, bot) tuples format."""
        history = [
            ("Hello", "Hi there!"),
            ("How are you?", "I'm doing well, thanks!"),
        ]
        result = normalize_history(history)
        assert len(result) == 2
        assert result[0] == ["Hello", "Hi there!"]
        assert result[1] == ["How are you?", "I'm doing well, thanks!"]

    def test_list_of_singletons(self):
        """Test list with single-element items (user message only)."""
        history = [
            ["Hello"],
            ("How are you?",),
        ]
        result = normalize_history(history)
        assert len(result) == 2
        assert result[0] == ["Hello", ""]
        assert result[1] == ["How are you?", ""]

    def test_dict_with_user_bot_keys(self):
        """Test dict format with 'user' and 'bot' keys."""
        history = [
            {"user": "Hello", "bot": "Hi there!"},
            {"user": "How are you?", "bot": "I'm well."},
        ]
        result = normalize_history(history)
        assert len(result) == 2
        assert result[0] == ["Hello", "Hi there!"]
        assert result[1] == ["How are you?", "I'm well."]

    def test_dict_with_role_content_user(self):
        """Test Gradio v7 format: dicts with role='user' and content."""
        history = [
            {"role": "user", "content": "Hello"},
        ]
        result = normalize_history(history)
        assert len(result) == 1
        assert result[0] == ["Hello", ""]

    def test_dict_with_role_content_assistant(self):
        """Test Gradio v7 format: dicts with role='assistant' and content."""
        history = [
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = normalize_history(history)
        assert len(result) == 1
        assert result[0] == ["", "Hi there!"]

    def test_dict_with_role_content_mixed(self):
        """Test Gradio v7 format: mixed user/assistant messages."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "Good!"},
        ]
        result = normalize_history(history)
        # Each role/content dict becomes its own pair
        assert len(result) == 4
        assert result[0] == ["Hello", ""]
        assert result[1] == ["", "Hi!"]
        assert result[2] == ["How are you?", ""]
        assert result[3] == ["", "Good!"]

    def test_nested_messages_dict(self):
        """Test nested {'messages': [...]} format."""
        history = [
            {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"},
                ]
            },
        ]
        result = normalize_history(history)
        assert len(result) == 1
        assert result[0] == ["Hello", "Hi there!"]

    def test_nested_messages_dict_odd_count(self):
        """Test nested messages with odd number of messages."""
        history = [
            {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi!"},
                    {"role": "user", "content": "Bye"},
                ]
            },
        ]
        result = normalize_history(history)
        assert len(result) == 2
        assert result[0] == ["Hello", "Hi!"]
        assert result[1] == ["Bye", ""]

    def test_mixed_formats(self):
        """Test list with various mixed formats."""
        history = [
            ["Hello", "Hi there!"],  # list pair
            ("How are you?", "I'm well"),  # tuple pair
            {"user": "What's up?", "bot": "Not much"},  # dict with user/bot
            {"role": "user", "content": "Bye"},  # role/content dict
            "Plain string",  # plain string
        ]
        result = normalize_history(history)
        assert len(result) == 5
        assert result[0] == ["Hello", "Hi there!"]
        assert result[1] == ["How are you?", "I'm well"]
        assert result[2] == ["What's up?", "Not much"]
        assert result[3] == ["Bye", ""]
        assert result[4] == ["Plain string", ""]
        # Verify all items are lists of two strings
        for item in result:
            assert isinstance(item, list)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], str)

    def test_coerces_non_strings_to_strings(self):
        """Test that non-string values are coerced to strings."""
        history = [
            [123, 456],  # integers
            [None, None],  # None values
            [True, False],  # booleans
        ]
        result = normalize_history(history)
        assert len(result) == 3
        assert result[0] == ["123", "456"]
        assert result[1] == ["None", "None"]
        assert result[2] == ["True", "False"]

    def test_items_with_more_than_two_elements(self):
        """Test that items with more than 2 elements join the rest."""
        history = [
            ["Hello", "Hi", "there", "friend"],
        ]
        result = normalize_history(history)
        assert len(result) == 1
        assert result[0] == ["Hello", "Hi there friend"]

    def test_unknown_dict_format_fallback(self):
        """Test that unknown dict format falls back to string representation."""
        history = [
            {"unknown_key": "value"},
        ]
        result = normalize_history(history)
        assert len(result) == 1
        # The dict should be stringified
        assert isinstance(result[0][0], str)
        assert result[0][1] == ""

    def test_plain_strings(self):
        """Test plain strings as history items."""
        history = ["Hello", "How are you?"]
        result = normalize_history(history)
        assert len(result) == 2
        assert result[0] == ["Hello", ""]
        assert result[1] == ["How are you?", ""]

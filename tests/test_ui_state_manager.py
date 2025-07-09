import logging

import pytest
import streamlit as st

from src.svg_image_generator.ui_state_manager import UIStateManager


@pytest.fixture(autouse=True)
def clear_session_state():
    # Clear Streamlit session_state before each test
    st.session_state.clear()
    yield
    st.session_state.clear()


def test_initialization_sets_defaults():
    manager = UIStateManager()
    for key, value in manager.DEFAULTS.items():
        assert st.session_state[key] == value


def test_get_returns_value_or_default():
    manager = UIStateManager()
    st.session_state["current_step"] = "test_step"
    assert manager.get("current_step") == "test_step"
    assert manager.get("nonexistent_key") is None  # default fallback


def test_set_updates_state_and_logs(monkeypatch):
    logs = []

    class DummyLogger:
        def info(self, msg):
            logs.append(msg)

    manager = UIStateManager(logger=DummyLogger())
    manager.set("current_step", "new_step")
    assert st.session_state["current_step"] == "new_step"
    assert any("State updated: current_step" in log for log in logs)


def test_reset_restores_defaults(monkeypatch):
    logs = []

    class DummyLogger:
        def info(self, msg):
            logs.append(msg)

    manager = UIStateManager(logger=DummyLogger())
    manager.set("current_step", "changed")
    manager.reset()
    for key, value in manager.DEFAULTS.items():
        assert st.session_state[key] == value
    assert any("State reset: current_step" in log for log in logs)


def test_has_key_returns_true_for_managed_keys():
    manager = UIStateManager()
    assert manager.has_key("current_step") is True
    assert manager.has_key("form_data") is True
    assert manager.has_key("nonexistent_key") is False


def test_get_all_state_returns_complete_state():
    manager = UIStateManager()
    manager.set("current_step", "custom_step")
    all_state = manager.get_all_state()

    # Should contain all managed keys
    for key in manager.DEFAULTS:
        assert key in all_state

    # Should return custom value for modified key
    assert all_state["current_step"] == "custom_step"

    # Should return default for unmodified keys
    assert all_state["form_data"] == {}


def test_set_with_none_value_logs_correctly():
    logs = []

    class DummyLogger:
        def info(self, msg):
            logs.append(msg)

    manager = UIStateManager(logger=DummyLogger())
    manager.set("user_context", None)
    assert st.session_state["user_context"] is None
    assert any("State updated: user_context" in log for log in logs)

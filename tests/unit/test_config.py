"""Tests for the config module."""

from dbterd.config import model_config


def test_model_config():
    """Test that model_config is correctly defined."""
    assert model_config["protected_namespaces"] == ()

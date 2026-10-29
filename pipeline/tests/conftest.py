"""Shared pytest config — handles --run-live flag and skips live tests by default."""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run live tests that make real API calls (incurs cost)",
    )
    parser.addoption(
        "--max-cost",
        type=float,
        default=0.10,
        help="Documented budget for live session (informational)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "live: calls real AI APIs (cost money, need --run-live)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-live"):
        return
    skip_live = pytest.mark.skip(
        reason="need --run-live to run (real API calls cost money)"
    )
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
import pytest
from config.settings import settings


@pytest.fixture(autouse=True)
def force_mock_for_tests(monkeypatch):
    """Garantit que les tests unitaires s'exécutent de façon hermétique et instantanée."""
    monkeypatch.setattr(settings, "mock_mode", True)

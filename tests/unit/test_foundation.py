"""C01 checks for package and settings foundations."""

from strategic_intelligence import __version__
from strategic_intelligence.config import Settings


def test_package_imports() -> None:
    assert __version__ == "0.1.0"


def test_settings_load_safe_defaults(monkeypatch) -> None:
    for name in ("APP_ENV", "LOG_LEVEL", "DATA_DIR", "LOG_DIR"):
        monkeypatch.delenv(name, raising=False)

    settings = Settings.from_environment()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.data_dir.as_posix() == "data"
    assert settings.log_dir.as_posix() == "logs"

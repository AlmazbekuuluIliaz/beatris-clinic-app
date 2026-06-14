"""Сверка реализованного API с каноничным контрактом.

Каноничный контракт — `contract/openapi.yaml` (версионируемая копия внешнего
`openapi.yaml`). Тест гарантирует, что каждый путь+метод контракта реализован в
живом приложении (`app.openapi()`). Дополнительные backend-маршруты (extra) —
разрешены по задумке и тест их не валит.
"""

from pathlib import Path

import yaml

from app.main import app

CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contract" / "openapi.yaml"
API_PREFIX = "/api/v1"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def _operations(paths: dict, prefix: str = "") -> set[tuple[str, str]]:
    ops: set[tuple[str, str]] = set()
    for path, item in (paths or {}).items():
        for method in item:
            if method.lower() in HTTP_METHODS:
                ops.add((method.lower(), prefix + path))
    return ops


def _contract_operations() -> set[tuple[str, str]]:
    spec = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    return _operations(spec.get("paths"), API_PREFIX)


def _live_operations() -> set[tuple[str, str]]:
    return _operations(app.openapi().get("paths"))


def test_contract_file_exists() -> None:
    assert CONTRACT_PATH.is_file(), f"Каноничный контракт не найден: {CONTRACT_PATH}"


def test_all_contract_endpoints_are_implemented() -> None:
    missing = sorted(_contract_operations() - _live_operations())
    assert not missing, "Не реализованы эндпоинты из контракта:\n" + "\n".join(
        f"  {method.upper()} {path}" for method, path in missing
    )

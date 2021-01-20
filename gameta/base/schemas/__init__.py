from typing import Dict, Tuple

from .schema import Schema, get_schema_version
from .version025 import v025
from .version030 import v030


__all__ = ['schema_versions', 'get_schema_version', 'Schema']


schema_versions: Dict[Tuple[int, int, int], Schema] = {
    (0, 2, 5): v025,
    (0, 3, 0): v030
}

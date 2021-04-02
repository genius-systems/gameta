from typing import Dict, Tuple

from .schema import Schema, to_schema_str, to_schema_tuple
from .version025 import v025
from .version030 import v030

__all__ = ['supported_versions', 'to_schema_tuple', 'to_schema_str', 'Schema']


supported_versions: Dict[Tuple[int, int, int], Schema] = {
    (0, 2, 5): v025,
    (0, 3, 0): v030
}

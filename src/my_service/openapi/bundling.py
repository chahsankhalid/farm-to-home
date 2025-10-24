import os
from typing import Any, Dict

import prance


# This allows us to split up the OpenAPI spec into separate files
# See https://github.com/zalando/connexion/issues/254#issuecomment-497194240
def get_bundled_specs(main_file_path: str) -> Dict[str, Any]:
    parser = prance.ResolvingParser(str(os.path.abspath(main_file_path)), lazy=True, strict=True)
    parser.parse()
    return parser.specification

import importlib.util
import sys
from decimal import Decimal
from pathlib import Path


workspace = Path(sys.argv[1])
source = workspace / "Sources/quantity.py"
spec = importlib.util.spec_from_file_location("quantity", source)
if spec is None or spec.loader is None:
    raise SystemExit("could not load production quantity module")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

for valid in (7, 2.5, float("inf"), Decimal("2.5"), True):
    if module.import_quantity({"value": valid}) != valid:
        raise SystemExit(f"positive import behavior changed: {valid!r}")

for invalid in (0, -3, Decimal("-3"), Decimal("0")):
    try:
        module.import_quantity({"value": invalid})
    except ValueError:
        continue
    raise SystemExit(f"invalid imported quantity was accepted: {invalid!r}")

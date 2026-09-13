import sys
import pytest
import matplotlib
matplotlib.use('Agg')

is_integration = False
for i, arg in enumerate(sys.argv):
    if arg == "integration" and sys.argv[i-1] == "-m":
        is_integration = True

if not is_integration:
    from unittest.mock import MagicMock
    # Completely mock ultralytics to avoid cv2/matplotlib local import hangs during unit testing
    sys.modules['ultralytics'] = MagicMock()
    sys.modules['cv2'] = MagicMock()

def pytest_collection_modifyitems(config, items):
    markexpr = config.getoption("markexpr")
    if markexpr == "integration":
        pass
    elif not markexpr:
        skip_int = pytest.mark.skip(reason="Run with -m integration to execute real model tests")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_int)

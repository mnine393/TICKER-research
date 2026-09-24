import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tsla_model.assumptions import default_assumptions  # noqa: E402
from tsla_model.data_ingestion import get_data  # noqa: E402

VAL_DATE = date(2026, 9, 24)


@pytest.fixture(scope="session")
def bundle():
    # Offline: tests must be deterministic and must not depend on network access.
    return get_data(live=False)


@pytest.fixture()
def aset(bundle):
    return default_assumptions(bundle)


@pytest.fixture()
def val_date():
    return VAL_DATE

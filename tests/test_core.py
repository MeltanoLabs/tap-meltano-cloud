"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_meltanocloud.tap import TapMeltanoCloud

SAMPLE_CONFIG = {}


# Run standard built-in tap tests from the SDK:
TestTapMeltanoCloud = get_tap_test_class(
    tap_class=TapMeltanoCloud,
    config=SAMPLE_CONFIG,
)

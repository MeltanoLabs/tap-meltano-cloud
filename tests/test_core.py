"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_meltano_cloud.tap import TapMeltanoCloud

# Run standard built-in tap tests from the SDK:
TestTapMeltanoCloud = get_tap_test_class(
    tap_class=TapMeltanoCloud,
    config={},
    suite_config=SuiteConfig(max_records_limit=50),
)

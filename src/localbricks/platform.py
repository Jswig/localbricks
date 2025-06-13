"""Utilities for determining the platform the code is running on"""

import os


def is_databricks_driver() -> bool:
    """Check if the current Python process is running on a Databricks driver.

    :returns: True if the current Python process is running on a Databricks driver,
    False otherwise.
    """
    # DATABRICKS_RUNTIME_VERSION is always set on driver nodes, but not on worker nodes
    # It also should not be set on non-Databricks environments
    return os.environ.get("DATABRICKS_RUNTIME_VERSION") is not None

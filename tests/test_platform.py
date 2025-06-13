from localbricks.platform import is_databricks_driver


def test_is_databricks_driver_when_running_on_databricks(monkeypatch):
    monkeypatch.setenv("DATABRICKS_RUNTIME_VERSION", "client.2.5")
    assert is_databricks_driver() is True


def test_is_databricks_driver_when_not_running_on_databricks():
    assert is_databricks_driver() is False

from localbricks.spark import get_spark_session
from pyspark.sql import SparkSession  # type: ignore


def is_databricks_driver_stub() -> bool:
    return True


def test_get_spark_session_on_driver(monkeypatch):
    monkeypatch.setattr(
        "localbricks.spark.is_databricks_driver",
        is_databricks_driver_stub,
    )
    spark = get_spark_session()
    assert isinstance(spark, SparkSession)

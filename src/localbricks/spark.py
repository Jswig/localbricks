from pyspark.sql import SparkSession
from pyspark.sql.connect.session import SparkSession as SparkConnectSession

from databricks.connect import DatabricksSession

from .platform import is_databricks_driver


def get_spark_session() -> SparkSession | SparkConnectSession:
    if is_databricks_driver():
        return SparkSession.builder.getOrCreate()
    else:
        return DatabricksSession.builder.remote().getOrCreate()

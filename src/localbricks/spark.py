from pyspark.sql import SparkSession
from pyspark.sql.connect.session import SparkSession as SparkConnectSession

from databricks.connect import DatabricksSession

from .platform import is_databricks_driver

# On a Databricks cluster driver in Standard access mode (a.k.a shared) and on 
# Serveless Databrickscompute, the global 'spark' variable is a Spark Connect session.
# In Dedicated access mode (a.k.a. single user), 'spark' is a regular Spark session.
# Finally, a session created through Databricks Connect will always be a Spark Connect
# session.
def get_spark_session() -> SparkSession | SparkConnectSession:
    if is_databricks_driver():
        return SparkSession.builder.getOrCreate()
    else:
        return DatabricksSession.builder.remote().getOrCreate()

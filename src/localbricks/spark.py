import importlib.util

from pyspark.sql import SparkSession
from pyspark.sql.connect.session import SparkSession as SparkConnectSession

if (
    # databricks-connect is structured as a submodule of a 'databricks' module, and
    # find_spec() raises an error instead of returning 'None' if the parent module of
    # the submodule does not exist, so we need to first check for the parent module.
    importlib.util.find_spec("databricks") is not None
    and importlib.util.find_spec("databricks.connect") is not None
):
    _databricks_connect_available = True
    # I haven't found a good way to type this import when regular pyspark is installed
    # as a dev-dependency, but it's not necessary for providint accurate return types.
    # TODO: find a better way to handle this.
    from databricks.connect import DatabricksSession  # type: ignore
else:
    _databricks_connect_available = False

from .platform import is_databricks_driver


# On a Databricks cluster driver in Standard access mode (a.k.a shared) and on
# Serveless Databrickscompute, the global 'spark' variable is a Spark Connect session.
# In Dedicated access mode (a.k.a. single user), 'spark' is a regular Spark session.
# Finally, a session created through Databricks Connect will always be a Spark Connect
# session.
def get_spark_session() -> SparkSession | SparkConnectSession:
    if is_databricks_driver():
        return SparkSession.builder.getOrCreate()
    elif _databricks_connect_available:
        return DatabricksSession.builder.remote().getOrCreate()
    else:
        raise ImportError("databricks-connect is not installed")

# localbricks

`localbricks` makes it easy to write code that is portable between Databricks and local
machines running against remote Databricks compute.

## Features

Detect whether you are running in Databricks:

```py
from localbricks.platform import is_databricks_driver

if is_databricks_driver():
    print("This Python process is running on a Databricks driver node!")
```

Automatically get the existing Spark Session in Databricks, or via Databricks connect
if locally:

```py
from localbricks.spark import get_spark_session

spark = get_spark_session()
df = spark.range(10)
df.show()
```

Uniform API for working with files in the Databricks Workspace or Volumes, whether
you are developing locally or in a Databricks notebook:

```py
import pandas as pd
from localbricks.files import open_file

# write a CSV file
df_1 = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
with open_file("/Volumes/my_catalog/my_schema/my_volume/example.csv", "w") as f:
    df_1.to_csv(f, index=False)

# read it back
with open_file("/Volumes/my_catalog/my_schema/my_volume/example.csv", "r") as f
    df_2 = pd.read_csv(f)

assert df_1.equals(df_2)
```

## Development requirements

- [uv](https://docs.astral.sh/uv/)
- Java Runtime Environment 11 or 17

Run formatting, linting, type checking and tests
```sh
sh scripts/build.sh
```

Build the Sphinx documentation
```sh
sh scripts/docs.sh
```

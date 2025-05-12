# [augmented urban data triangulation (audt)]
# AUDT Data

A Python package for processing and analyzing ACS data.

## Installation

```bash
pip install -e .
```

## Usage

```python
from audt_data.acs import get_acs_data

# Example usage
data = get_acs_data(2019, "demographic", {"B01001_001E": "total_population"})
```

## Code Guidelines 
- prepend all code files (including notebooks) with: [augmented urban data triangulation (audt)] \n [repo] \n [short script title] \n [description] \n [authors (w @usernames)]
- do not use Jupyter Notebooks but for exploratory data analysis & sanity checks.
- store tabular data as .parquet files, and geographic data as .parquet files (with WKB serialization, see [here](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_parquet.html), etc.)
- use common boilerplate wherever possible. Avoid writing duplicate code or code with duplicate functionality.
- provide support for parallel / distributed processing (through pandarallel, asyncio, etc.) wherever possible.


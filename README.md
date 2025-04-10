# audt-data
Repository that houses data sourcing and preprocessing tooling for the audt [augmented urban data triangulation] platform 

## code guidelines 
- prepend all code files (including notebooks) with: [augmented urban data triangulation (audt)] \n [repo] \n [short script title] \n [description] \n [authors (w @usernames)]
- do not use Jupyter Notebooks but for exploratory data analysis & sanity checks.
- store tabular data as .parquet files, and geographic data as .parquet files (with WKB serialization, see [here](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_parquet.html), etc.)
- use common boilerplate wherever possible. Avoid writing duplicate code or code with duplicate functionality.
- provide support for parallel / distributed processing (through pandarallel, asyncio, etc.) wherever possible. 


# ERP ↔ Web Consolidation for Bottleneck

Usage
-----

Place your monthly exports in a folder and run:

```bash
python consolidate_bottleneck.py --erp erp.xlsx --web web.xlsx --liaison liaison.xlsx --out-dir results
```

Outputs
-------

- `results/consolidated.xlsx` and `results/consolidated.csv`: consolidated dataset
- `results/anomalies_report.json`: counts of detected/corrected anomalies

Notes
-----

- The script excludes ERP rows with negative `price` and rows with `onsale_web == 0`.
- Negative `stock_quantity` values are corrected to 0 and `stock_status` is recalculated from `stock_quantity`.
- Web rows with missing `sku`, non-`product` `post_type`, or missing `product_type` are excluded.
- Joins are performed via `liaison.product_id -> liaison.id_web` then matching `id_web` to `web.sku` or `web.id_web` when present.

Notebook usage
--------------

Import the helper and call from a Jupyter notebook (no CLI required):

```python
from erp_web_consolidation.notebook_api import consolidate_files

# paths or pandas DataFrames accepted
consolidated_df, report = consolidate_files(
    erp='path/to/erp.xlsx',
    web='path/to/web.xlsx',
    liaison='path/to/liaison.xlsx',
    out_dir='results',        # optional
    write_outputs=False       # set True to save files
)

print(report)
consolidated_df.head()
```

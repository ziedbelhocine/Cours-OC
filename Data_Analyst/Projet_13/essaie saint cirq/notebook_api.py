"""Notebook-friendly API for the Bottleneck consolidation.

Import `consolidate_files` in a notebook to run consolidation interactively.

Example (in a Jupyter cell):

from erp_web_consolidation.notebook_api import consolidate_files
consolidated_df, report = consolidate_files(
    erp='path/to/erp.xlsx', web='path/to/web.xlsx', liaison='path/to/liaison.xlsx', out_dir='results', write_outputs=False
)

"""
from pathlib import Path
from typing import Union, Tuple, Optional

import pandas as pd

try:
    from . import consolidate_bottleneck as core
except Exception:
    # Fallback when notebook_api.py is imported as a top-level module (not as a package)
    import consolidate_bottleneck as core


def _load_input(maybe_df_or_path: Union[str, Path, pd.DataFrame], reader=core.read_excel_safe) -> pd.DataFrame:
    if isinstance(maybe_df_or_path, pd.DataFrame):
        return maybe_df_or_path
    return reader(Path(maybe_df_or_path))


def consolidate_files(
    erp: Union[str, Path, pd.DataFrame],
    web: Union[str, Path, pd.DataFrame],
    liaison: Union[str, Path, pd.DataFrame],
    out_dir: Optional[Union[str, Path]] = None,
    write_outputs: bool = True,
) -> Tuple[pd.DataFrame, dict]:
    """Load inputs (or accept DataFrames), run consolidation and optionally write outputs.

    Returns (consolidated_df, anomalies_report_dict).
    """
    erp_df = _load_input(erp)
    web_df = _load_input(web)
    liaison_df = _load_input(liaison)

    consolidated, agg = core.consolidate(erp_df, web_df, liaison_df)

    if out_dir and write_outputs:
        core.write_outputs(consolidated, agg, Path(out_dir))

    return consolidated, agg

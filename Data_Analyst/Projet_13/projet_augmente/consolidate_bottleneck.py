#!/usr/bin/env python3
"""Consolidate ERP and Web exports for Bottleneck.

Usage example:
  python consolidate_bottleneck.py \
    --erp erp.xlsx --web web.xlsx --liaison liaison.xlsx \
    --out-dir output

Outputs:
  - consolidated.xlsx / consolidated.csv in --out-dir
  - anomalies_report.json in --out-dir

The script applies the cleaning rules described in the project brief and
produces counts of anomalies detected and corrected.
"""
from pathlib import Path
import argparse
import json
import logging
import sys
from typing import Dict, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("consolidate_bottleneck")


def read_excel_safe(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_excel(path, **kwargs)


def clean_erp(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    counts = {
        "initial_rows_erp": int(len(df)),
        "excluded_price_negative": 0,
        "corrected_stock_negative_to_zero": 0,
        "excluded_onsale_web": 0,
        "duplicates_removed_erp": 0,
        "recalculated_stock_status_changed": 0,
    }

    df = df.copy()

    # Ensure numeric types
    df["price"] = pd.to_numeric(df.get("price"), errors="coerce")
    df["purchase_price"] = pd.to_numeric(df.get("purchase_price"), errors="coerce")
    df["stock_quantity"] = pd.to_numeric(df.get("stock_quantity"), errors="coerce").fillna(0)

    # Exclude negative prices
    neg_price_mask = df["price"] < 0
    counts["excluded_price_negative"] = int(neg_price_mask.sum())
    df = df.loc[~neg_price_mask]

    # Correct negative stock quantities to zero
    neg_stock_mask = df["stock_quantity"] < 0
    counts["corrected_stock_negative_to_zero"] = int(neg_stock_mask.sum())
    df.loc[neg_stock_mask, "stock_quantity"] = 0

    # Recalculate stock_status from stock_quantity
    def compute_status(qty):
        try:
            return "instock" if float(qty) > 0 else "outofstock"
        except Exception:
            return "outofstock"

    recalculated = df["stock_quantity"].apply(compute_status)
    # Compare to existing stock_status where present
    if "stock_status" in df.columns:
        changed = (df["stock_status"].astype(str).fillna("") != recalculated.astype(str))
        counts["recalculated_stock_status_changed"] = int(changed.sum())
    df["stock_status"] = recalculated

    # Exclude items with onsale_web == 0 (not on sale)
    if "onsale_web" in df.columns:
        onsale_mask = df["onsale_web"].fillna(0) == 0
        counts["excluded_onsale_web"] = int(onsale_mask.sum())
        df = df.loc[~onsale_mask]

    # Remove duplicates on product_id
    if "product_id" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["product_id"], keep="first")
        counts["duplicates_removed_erp"] = int(before - len(df))

    return df.reset_index(drop=True), counts


def clean_web(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    counts = {
        "initial_rows_web": int(len(df)),
        "excluded_missing_sku": 0,
        "excluded_post_type_not_product": 0,
        "excluded_missing_product_type": 0,
        "duplicates_removed_web": 0,
    }

    df = df.copy()

    # Normalize column names to avoid spacing issues
    df.columns = [c.strip() for c in df.columns]

    # Exclude missing sku
    if "sku" in df.columns:
        missing_sku_mask = df["sku"].isna() | (df["sku"].astype(str).str.strip() == "")
        counts["excluded_missing_sku"] = int(missing_sku_mask.sum())
        df = df.loc[~missing_sku_mask]

    # Exclude non-product post_type
    if "post_type" in df.columns:
        bad_post_mask = df["post_type"].astype(str).fillna("") != "product"
        counts["excluded_post_type_not_product"] = int(bad_post_mask.sum())
        df = df.loc[~bad_post_mask]

    # Exclude missing product_type
    if "product_type" in df.columns:
        missing_type_mask = df["product_type"].isna() | (df["product_type"].astype(str).str.strip() == "")
        counts["excluded_missing_product_type"] = int(missing_type_mask.sum())
        df = df.loc[~missing_type_mask]

    # Remove duplicates on sku (and id_web if exists)
    dedupe_cols = []
    if "sku" in df.columns:
        dedupe_cols.append("sku")
    if "id_web" in df.columns:
        dedupe_cols.append("id_web")
    if dedupe_cols:
        before = len(df)
        df = df.drop_duplicates(subset=dedupe_cols, keep="first")
        counts["duplicates_removed_web"] = int(before - len(df))

    return df.reset_index(drop=True), counts


def find_web_key_for_liaison(web_df: pd.DataFrame, liaison_df: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    # liaison.id_web should match either web.id_web or web.sku
    if "id_web" in web_df.columns:
        return "id_web", web_df
    if "sku" in web_df.columns:
        return "sku", web_df
    # fallback: if there's a numeric 'ID' or 'post_id' column, try it
    for candidate in ("id", "post_id", "ID", "post_ID"):
        if candidate in web_df.columns:
            return candidate, web_df
    raise RuntimeError("Cannot find a join key in web file to match liaison.id_web. Ensure web file contains 'sku' or 'id_web' or similar.")


def consolidate(erp: pd.DataFrame, web: pd.DataFrame, liaison: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    # Counts aggregation
    agg = {}

    clean_erp_df, erp_counts = clean_erp(erp)
    agg.update(erp_counts)

    clean_web_df, web_counts = clean_web(web)
    agg.update(web_counts)

    # Prepare liaison
    liaison = liaison.copy()
    if "product_id" not in liaison.columns or "id_web" not in liaison.columns:
        raise KeyError("Liaison file must contain 'product_id' and 'id_web' columns")

    # Merge ERP with liaison (inner join to keep only mapped products)
    before_liaison = len(clean_erp_df)
    merged = pd.merge(clean_erp_df, liaison[["product_id", "id_web"]], on="product_id", how="left", indicator="_merge_liaison")
    missing_liaison = merged["id_web"].isna().sum()
    agg["erp_without_liaison_matches"] = int(missing_liaison)
    # Keep only rows with an id_web (we cannot match to web otherwise)
    merged = merged.loc[merged["id_web"].notna()].copy()

    # Decide web join key
    web_key, web_df_for_join = find_web_key_for_liaison(clean_web_df, liaison)

    # If join key is sku but liaison.id_web is numeric, cast both to string for safe join
    if web_key == "sku":
        merged["id_web"] = merged["id_web"].astype(str)
        web_df_for_join = web_df_for_join.copy()
        web_df_for_join["sku"] = web_df_for_join["sku"].astype(str)
        joined = pd.merge(merged, web_df_for_join, left_on="id_web", right_on="sku", how="left", indicator="_merge_web")
    else:
        joined = pd.merge(merged, web_df_for_join, left_on="id_web", right_on=web_key, how="left", indicator="_merge_web")

    agg["erp_liaison_matched_rows"] = int(len(joined))
    agg["erp_web_unmatched_after_join"] = int((joined["_merge_web"] == "left_only").sum())

    # Drop rows that did not match web (we want consolidated products present on web)
    final = joined.loc[joined["_merge_web"] == "both"].copy()

    # Build consolidated columns (give precedence to web info for some fields, keep ERP prices/stock)
    # Keep a clear column set for output
    out_cols = []
    # ERP side
    for c in ["product_id", "price", "purchase_price", "stock_quantity", "stock_status"]:
        if c in final.columns:
            out_cols.append(c)
    # Liaison id_web
    if "id_web" in final.columns:
        out_cols.append("id_web")
    # Web side useful fields
    for c in ["sku", "post_title", "tax_status", "total_sales", "product_type"]:
        if c in final.columns:
            out_cols.append(c)

    consolidated = final.loc[:, [c for c in out_cols if c in final.columns]].copy()

    # Final cleanup: ensure types and order
    consolidated = consolidated.reset_index(drop=True)

    # Additional metrics
    agg["final_consolidated_rows"] = int(len(consolidated))

    return consolidated, agg


def write_outputs(consolidated: pd.DataFrame, agg: Dict[str, int], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    excel_path = out_dir / "consolidated.xlsx"
    csv_path = out_dir / "consolidated.csv"
    report_path = out_dir / "anomalies_report.json"

    consolidated.to_excel(excel_path, index=False)
    consolidated.to_csv(csv_path, index=False)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2, ensure_ascii=False)

    logger.info(f"Wrote consolidated data to: {excel_path}")
    logger.info(f"Wrote consolidated CSV to: {csv_path}")
    logger.info(f"Wrote anomalies report to: {report_path}")


def parse_args():
    p = argparse.ArgumentParser(description="Consolidate ERP and Web exports for Bottleneck")
    p.add_argument("--erp", required=True, help="Path to erp.xlsx")
    p.add_argument("--web", required=True, help="Path to web.xlsx")
    p.add_argument("--liaison", required=True, help="Path to liaison.xlsx")
    p.add_argument("--out-dir", default="output", help="Output directory")
    return p.parse_args()


def main():
    args = parse_args()
    erp_path = Path(args.erp)
    web_path = Path(args.web)
    liaison_path = Path(args.liaison)
    out_dir = Path(args.out_dir)

    try:
        erp = read_excel_safe(erp_path)
        web = read_excel_safe(web_path)
        liaison = read_excel_safe(liaison_path)
    except Exception as e:
        logger.error(f"Error reading input files: {e}")
        sys.exit(2)

    consolidated, agg = consolidate(erp, web, liaison)

    # Write outputs and print summary
    write_outputs(consolidated, agg, out_dir)

    logger.info("Summary of anomalies and actions:")
    for k, v in sorted(agg.items()):
        logger.info(f" - {k}: {v}")


if __name__ == "__main__":
    main()

"""
Basic tests for River AI Rangers — app.py helper functions.
Run with: pytest tests/test_app.py
"""

import io
import sys
import os
import re
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Helpers copied from app.py so tests run without a Streamlit import
# ---------------------------------------------------------------------------

def sanitise_label(name):
    clean = re.sub(r"[^a-zA-Z0-9 \-_()\.,]", "", name)
    return clean[:80].strip() or "Uploaded river"


def has_season_column(df):
    return any("season" in c.lower() for c in df.columns)


def prepare_data_summary(df):
    """Trimmed version matching the logic in app.py."""
    cols = [c.lower() for c in df.columns]
    original_row_count = len(df)

    display_col_keywords = ["site", "river", "date", "season", "ph", "nitrate",
                             "phosphate", "ammonia", "oxygen", "turbid", "temp"]
    if original_row_count <= 20:
        display_col_keywords.append("notes")

    display_cols = []
    for c in df.columns:
        cl = c.lower()
        if any(k in cl for k in display_col_keywords):
            display_cols.append(c)

    display_df = df[display_cols].copy() if display_cols else df.copy()

    if original_row_count > 100:
        site_cols = [c for c in display_df.columns if c.lower() in ("site", "river")]
        season_cols = [c for c in display_df.columns if "season" in c.lower()]
        numeric_cols = display_df.select_dtypes(include="number").columns.tolist()

        if site_cols and numeric_cols:
            if season_cols:
                group_cols = site_cols + season_cols
            else:
                group_cols = site_cols
            agg_dict = {col: ["mean", "min", "max"] for col in numeric_cols}
            agg_df = display_df.groupby(group_cols, as_index=False).agg(agg_dict)
            agg_df.columns = [
                "_".join(c).strip("_") if isinstance(c, tuple) else c
                for c in agg_df.columns
            ]
            for col in agg_df.select_dtypes(include="number").columns:
                agg_df[col] = agg_df[col].round(2)
            return agg_df.to_string(index=False), display_cols, original_row_count, len(agg_df)

        summary = display_df.to_string(index=False, max_rows=50)
        return summary, display_cols, original_row_count, min(original_row_count, 50)

    summary = display_df.to_string(index=False)
    return summary, display_cols, original_row_count, original_row_count


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSanitiseLabel:
    def test_removes_angle_brackets(self):
        assert "<script>" not in sanitise_label("<script>alert(1)</script>")

    def test_keeps_normal_name(self):
        assert sanitise_label("River Ching 2024") == "River Ching 2024"

    def test_empty_string_becomes_default(self):
        assert sanitise_label("") == "Uploaded river"

    def test_all_unsafe_chars_becomes_default(self):
        assert sanitise_label("!!!###$$$") == "Uploaded river"

    def test_truncates_long_name(self):
        long = "A" * 200
        assert len(sanitise_label(long)) <= 80


class TestHasSeasonColumn:
    def test_detects_season_column(self):
        df = pd.DataFrame({"site": ["A"], "Season": ["spring"], "ph": [7.0]})
        assert has_season_column(df) is True

    def test_no_false_positive_for_site(self):
        df = pd.DataFrame({"site": ["A"], "ph": [7.0]})
        assert has_season_column(df) is False


class TestPrepareDataSummary:
    def _make_small_df(self):
        return pd.DataFrame({
            "site": ["A", "B"],
            "ph": [7.1, 6.8],
            "phosphate": [0.05, 0.12],
        })

    def _make_large_df(self, n=150, with_season=False):
        sites = ["Upstream", "Midpoint", "Downstream"] * (n // 3 + 1)
        data = {
            "site": sites[:n],
            "ph": [7.0 + (i % 5) * 0.1 for i in range(n)],
            "phosphate": [0.05 + (i % 10) * 0.01 for i in range(n)],
        }
        if with_season:
            seasons = ["spring", "summer", "autumn", "winter"] * (n // 4 + 1)
            data["season"] = seasons[:n]
        return pd.DataFrame(data)

    def test_small_df_returns_all_rows(self):
        df = self._make_small_df()
        _, _, original, displayed = prepare_data_summary(df)
        assert original == 2
        assert displayed == 2

    def test_large_df_without_season_aggregates_by_site(self):
        df = self._make_large_df(n=150)
        _, _, original, displayed = prepare_data_summary(df)
        assert original == 150
        # Should have 3 rows (one per site)
        assert displayed == 3

    def test_large_df_with_season_aggregates_by_site_and_season(self):
        df = self._make_large_df(n=160, with_season=True)
        _, _, original, displayed = prepare_data_summary(df)
        assert original == 160
        # Should have more groups than just by site alone
        assert displayed > 3

    def test_summary_string_contains_site_name(self):
        df = self._make_large_df(n=150)
        summary, _, _, _ = prepare_data_summary(df)
        assert "Upstream" in summary

    def test_mean_min_max_columns_present_for_large_df(self):
        df = self._make_large_df(n=150)
        summary, _, _, _ = prepare_data_summary(df)
        # After aggregation the summary should reference mean, min or max column suffixes
        assert "mean" in summary or "min" in summary or "max" in summary


class TestColumnDetection:
    """Verify that display column selection picks up expected indicators."""

    def test_detects_ph_column(self):
        df = pd.DataFrame({"site": ["A"], "ph": [7.0], "notes": ["ok"]})
        _, display_cols, _, _ = prepare_data_summary(df)
        lower_cols = [c.lower() for c in display_cols]
        assert "ph" in lower_cols

    def test_detects_phosphate_column(self):
        df = pd.DataFrame({"site": ["A"], "Phosphate_mg_L": [0.05]})
        _, display_cols, _, _ = prepare_data_summary(df)
        lower_cols = [c.lower() for c in display_cols]
        assert any("phosphate" in c for c in lower_cols)

    def test_excludes_notes_for_large_datasets(self):
        sites = ["A"] * 150
        df = pd.DataFrame({
            "site": sites,
            "ph": [7.0] * 150,
            "notes": ["good"] * 150,
        })
        _, display_cols, _, _ = prepare_data_summary(df)
        lower_cols = [c.lower() for c in display_cols]
        assert "notes" not in lower_cols

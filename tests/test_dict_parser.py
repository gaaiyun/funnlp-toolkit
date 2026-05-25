"""dict_parser.py 测试。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.dict_parser import (
    DictEntry,
    dict_stats,
    filter_by_length,
    filter_chinese_only,
    filter_contains,
    parse_dict_text,
    parse_dict_with_metadata,
)


# --- parse_dict_text -----------------------------------------------

def test_parse_basic_one_per_line():
    text = "苹果\n香蕉\n橘子"
    assert parse_dict_text(text) == ["苹果", "香蕉", "橘子"]


def test_parse_thuocl_format():
    """THUOCL: word\\tfreq → 只取 word。"""
    text = "计算机\t100\n程序员\t50"
    assert parse_dict_text(text) == ["计算机", "程序员"]


def test_parse_keeps_frequency_when_requested():
    text = "计算机\t100"
    out = parse_dict_text(text, keep_frequency=True)
    assert out == ["计算机:100"]


def test_parse_skips_comments():
    text = "# 注释行\n苹果\n// 另一种注释\n香蕉"
    assert parse_dict_text(text) == ["苹果", "香蕉"]


def test_parse_skips_empty_lines():
    text = "苹果\n\n\n香蕉\n   \n橘子"
    assert parse_dict_text(text) == ["苹果", "香蕉", "橘子"]


def test_parse_strips_utf8_bom():
    text = "﻿苹果\n香蕉"
    out = parse_dict_text(text)
    assert "苹果" in out
    # BOM 字符不应作为第一个词的一部分
    assert out[0] == "苹果"


def test_parse_handles_crlf():
    text = "苹果\r\n香蕉\r\n橘子"
    assert parse_dict_text(text) == ["苹果", "香蕉", "橘子"]


def test_parse_deduplicate():
    text = "苹果\n香蕉\n苹果\n橘子\n香蕉"
    out = parse_dict_text(text, deduplicate=True)
    assert out == ["苹果", "香蕉", "橘子"]


def test_parse_empty_text():
    assert parse_dict_text("") == []
    assert parse_dict_text(None) == []


def test_parse_only_comments_and_empty():
    text = "# only comments\n\n// nothing\n   "
    assert parse_dict_text(text) == []


def test_parse_no_skip_comments():
    text = "# 注释\n苹果"
    out = parse_dict_text(text, skip_comments=False)
    assert "# 注释" in out


def test_parse_no_skip_empty():
    """skip_empty=False 时不剔除完全空白行。

    注意：行 strip 后还是空字符串的会被 `if not word: continue` 跳过；
    skip_empty 主要控制 "before-strip 空行" 这一步。
    """
    text = "苹果\n\n香蕉"
    out = parse_dict_text(text, skip_empty=False)
    # 即使关掉 skip_empty，stripped="" 仍被 inner 的 if not word: continue 跳
    assert "苹果" in out and "香蕉" in out


# --- parse_dict_with_metadata --------------------------------------

def test_parse_metadata_extracts_frequency():
    text = "计算机\t100\n程序员\t50"
    out = parse_dict_with_metadata(text)
    assert len(out) == 2
    assert out[0].word == "计算机"
    assert out[0].frequency == 100
    assert out[1].frequency == 50


def test_parse_metadata_no_freq():
    text = "苹果\n香蕉"
    out = parse_dict_with_metadata(text)
    assert all(e.frequency is None for e in out)


def test_parse_metadata_invalid_freq():
    """字段不是数字时 frequency 应为 None，不应抛错。"""
    text = "词\t非数字"
    out = parse_dict_with_metadata(text)
    assert out[0].word == "词"
    assert out[0].frequency is None


def test_dict_entry_to_dict_serializable():
    import json
    e = DictEntry(word="测试", frequency=42)
    json.dumps(e.to_dict(), ensure_ascii=False)


# --- dict_stats ----------------------------------------------------

def test_stats_empty():
    s = dict_stats([])
    assert s["count"] == 0
    assert s["unique"] == 0
    assert s["avg_length"] == 0.0


def test_stats_basic():
    s = dict_stats(["苹果", "香蕉", "橘子"])
    assert s["count"] == 3
    assert s["unique"] == 3
    assert s["avg_length"] == 2.0
    assert s["min_length"] == 2
    assert s["max_length"] == 2


def test_stats_with_duplicates():
    s = dict_stats(["a", "a", "b", "c"])
    assert s["count"] == 4
    assert s["unique"] == 3


def test_stats_length_distribution():
    s = dict_stats(["a", "ab", "abc", "abcd"])
    # 长度 1/2/3/4 各一个
    dist = s["length_distribution"]
    assert dist.get("1") == 1
    assert dist.get("4") == 1


def test_stats_long_words_grouped_to_11plus():
    s = dict_stats(["a" * 15, "b" * 20])
    assert s["length_distribution"].get("11+") == 2


# --- filter_by_length ---------------------------------------------

def test_filter_length_basic():
    out = filter_by_length(["a", "ab", "abc", "abcd"], min_len=2, max_len=3)
    assert out == ["ab", "abc"]


def test_filter_length_empty_input():
    assert filter_by_length([], min_len=1, max_len=10) == []


def test_filter_length_excludes_empty_strings():
    out = filter_by_length(["", "a", "ab"], min_len=1)
    assert "" not in out


# --- filter_contains ----------------------------------------------

def test_filter_contains_basic():
    out = filter_contains(["计算机", "汽车", "计算器"], "计算")
    assert out == ["计算机", "计算器"]


def test_filter_contains_empty_substring_keeps_all():
    out = filter_contains(["a", "b"], "")
    assert out == ["a", "b"]


def test_filter_contains_no_match():
    assert filter_contains(["a", "b"], "xyz") == []


# --- filter_chinese_only ------------------------------------------

def test_filter_chinese_only():
    out = filter_chinese_only(["苹果", "apple", "苹果 mix", "香蕉"])
    assert out == ["苹果", "香蕉"]


def test_filter_chinese_excludes_empty():
    out = filter_chinese_only(["", "苹果"])
    assert out == ["苹果"]


def test_filter_chinese_excludes_pure_ascii():
    assert filter_chinese_only(["hello", "world"]) == []

"""funNLP / THUOCL 词典解析（v2 解耦版）。

v1 的 ``scripts/load_dict.py`` 把"扫描文件路径 + 解析文件内容"耦在一起，
路径硬编码 ``../../funNLP/data``，导致：
1. 没法在 CI 跑（funNLP 没 checkout）
2. 没法测试解析逻辑

v2 拆出 ``parse_dict_text(text)`` 纯函数，输入字符串内容，输出词列表。
文件路径扫描留在 ``load_dict.py``（v1 接口保持）。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence


@dataclass
class DictEntry:
    """词条 + 可选元数据（如 THUOCL 的 frequency）。"""
    word: str
    frequency: Optional[int] = None
    extra: dict = None

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "frequency": self.frequency,
            "extra": self.extra or {},
        }


# --- 解析 -----------------------------------------------------------

def parse_dict_text(
    text: str,
    *,
    skip_comments: bool = True,
    skip_empty: bool = True,
    deduplicate: bool = False,
    keep_frequency: bool = False,
) -> List[str]:
    """从词典文本解析出词列表。

    支持的格式：
    - 一行一词（最常见）
    - THUOCL：``word\\tfreq``（频率丢掉，只留词）
    - 带注释：``#`` 或 ``//`` 开头的行
    - UTF-8 BOM 自动剥掉
    - Windows 换行 (\\r\\n) 自动处理

    Parameters
    ----------
    text : 词典原始内容
    skip_comments : 跳过 ``#`` 或 ``//`` 开头的行
    skip_empty : 跳过空白行
    deduplicate : 去重（保留第一次出现的顺序）
    keep_frequency : 若行含 ``\\t``，第二列是 freq，是否保留为 ``词:freq``
    """
    if not text:
        return []
    # 剥 BOM
    if text.startswith("﻿"):
        text = text[1:]

    words: List[str] = []
    seen = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if skip_empty and not line:
            continue
        if skip_comments and (line.startswith("#") or line.startswith("//")):
            continue
        # THUOCL 格式：word\tfreq
        if "\t" in line:
            parts = line.split("\t", 1)
            if keep_frequency:
                word = f"{parts[0].strip()}:{parts[1].strip()}"
            else:
                word = parts[0].strip()
        else:
            word = line
        if not word:
            continue
        if deduplicate:
            if word in seen:
                continue
            seen.add(word)
        words.append(word)
    return words


def parse_dict_with_metadata(text: str) -> List[DictEntry]:
    """同 parse_dict_text，但返回结构化 DictEntry（含 frequency）。"""
    if not text:
        return []
    if text.startswith("﻿"):
        text = text[1:]

    out: List[DictEntry] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("//"):
            continue
        freq: Optional[int] = None
        word = line
        if "\t" in line:
            parts = line.split("\t", 1)
            word = parts[0].strip()
            try:
                freq = int(parts[1].strip())
            except (ValueError, IndexError):
                freq = None
        if not word:
            continue
        out.append(DictEntry(word=word, frequency=freq))
    return out


# --- 统计 -----------------------------------------------------------

def dict_stats(words: Sequence[str]) -> dict:
    """计算词典统计：词数 / 唯一数 / 平均长度 / 长度分布。"""
    if not words:
        return {
            "count": 0, "unique": 0,
            "avg_length": 0.0, "min_length": 0, "max_length": 0,
            "length_distribution": {},
        }
    unique = set(words)
    lengths = [len(w) for w in words]
    # 长度分布（1-10 + 11+）
    dist: dict = {}
    for L in lengths:
        bucket = str(L) if L <= 10 else "11+"
        dist[bucket] = dist.get(bucket, 0) + 1
    return {
        "count": len(words),
        "unique": len(unique),
        "avg_length": sum(lengths) / len(lengths),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "length_distribution": dist,
    }


# --- 过滤 -----------------------------------------------------------

def filter_by_length(words: Sequence[str], min_len: int = 1,
                      max_len: int = 100) -> List[str]:
    """按词长过滤（含空字符串过滤）。"""
    return [w for w in words if min_len <= len(w) <= max_len]


def filter_contains(words: Sequence[str], substring: str) -> List[str]:
    """保留含子串的词。"""
    if not substring:
        return list(words)
    return [w for w in words if substring in w]


def filter_chinese_only(words: Sequence[str]) -> List[str]:
    """只保留全中文的词（CJK 字符）。"""
    def _is_cjk_char(c: str) -> bool:
        return "一" <= c <= "鿿"
    return [w for w in words if w and all(_is_cjk_char(c) for c in w)]

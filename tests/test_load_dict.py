"""load_dict.py 测试：验证词典目录可配置（FUNNLP_DATA_DIR / --data-dir）。

重点是"去硬编码路径"：不依赖 checkout funNLP，用临时目录造几个词典文件，
验证 CLI 参数 / 环境变量 / 缺省值 的解析优先级以及扫描+加载能跑通。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# scripts/ 没有 __init__.py，直接把它加进 sys.path 再导入模块。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import load_dict  # noqa: E402
from load_dict import (  # noqa: E402
    ENV_DATA_DIR,
    list_available_dicts,
    load_dict as load_dict_fn,
    resolve_data_dir,
    scan_available_dicts,
)


@pytest.fixture
def sample_dict_dir(tmp_path: Path) -> Path:
    """造一个临时词典目录，含 stopwords + 一个 THUOCL 词库。"""
    (tmp_path / "stopwords.txt").write_text(
        "的\n了\n# 注释\n在\n", encoding="utf-8"
    )
    # THUOCL 格式：word\tfreq
    (tmp_path / "THUOCL_it.txt").write_text(
        "计算机\t100\n程序员\t50\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch):
    """每个测试前清掉真实环境里的 FUNNLP_DATA_DIR，避免互相污染。"""
    monkeypatch.delenv(ENV_DATA_DIR, raising=False)


# --- resolve_data_dir 优先级 ---------------------------------------

def test_resolve_falls_back_to_default():
    """既没 CLI 也没环境变量 → 回退缺省值。"""
    assert resolve_data_dir() == load_dict.DEFAULT_DATA_DIR


def test_resolve_uses_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv(ENV_DATA_DIR, str(tmp_path))
    assert resolve_data_dir() == tmp_path


def test_resolve_cli_overrides_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """CLI 参数优先级高于环境变量。"""
    other = tmp_path / "from_env"
    other.mkdir()
    cli = tmp_path / "from_cli"
    cli.mkdir()
    monkeypatch.setenv(ENV_DATA_DIR, str(other))
    assert resolve_data_dir(str(cli)) == cli


def test_resolve_expands_user(monkeypatch: pytest.MonkeyPatch):
    """~ 应被展开（不再硬编码绝对路径）。"""
    monkeypatch.setenv(ENV_DATA_DIR, "~/some_dicts")
    resolved = resolve_data_dir()
    assert "~" not in str(resolved)


# --- scan / load 走临时目录（核心：可配置且无需 funNLP） ------------

def test_scan_via_cli_arg(sample_dict_dir: Path):
    dict_map = scan_available_dicts(sample_dict_dir)
    assert "stopwords" in dict_map
    assert "it" in dict_map
    assert dict_map["stopwords"].name == "stopwords.txt"


def test_scan_via_env(monkeypatch: pytest.MonkeyPatch, sample_dict_dir: Path):
    monkeypatch.setenv(ENV_DATA_DIR, str(sample_dict_dir))
    dict_map = scan_available_dicts()  # 不传参，靠环境变量解析
    assert "stopwords" in dict_map and "it" in dict_map


def test_scan_missing_dir_returns_empty(tmp_path: Path):
    """指向不存在的目录 → 空 map，不抛错。"""
    assert scan_available_dicts(tmp_path / "nope") == {}


def test_load_dict_from_temp_dir(sample_dict_dir: Path):
    """加载停用词：注释被跳过。"""
    words = load_dict_fn("stopwords", data_dir=sample_dict_dir)
    assert words == ["的", "了", "在"]


def test_load_thuocl_strips_frequency(sample_dict_dir: Path):
    """THUOCL 词库只取 word，丢掉 freq。"""
    words = load_dict_fn("it", data_dir=sample_dict_dir)
    assert words == ["计算机", "程序员"]


def test_load_unknown_type_raises(sample_dict_dir: Path):
    with pytest.raises(ValueError):
        load_dict_fn("does_not_exist", data_dir=sample_dict_dir)


def test_list_available_via_env(monkeypatch: pytest.MonkeyPatch, sample_dict_dir: Path):
    monkeypatch.setenv(ENV_DATA_DIR, str(sample_dict_dir))
    available = list_available_dicts()
    assert set(available) == {"stopwords", "it"}

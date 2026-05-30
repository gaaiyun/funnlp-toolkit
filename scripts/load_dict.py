#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
funNLP Dictionary Loader
Load common Chinese NLP dictionaries from funNLP project
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Union

# 缺省词典目录：相对 workspace 推断出同级 checkout 的 funNLP/data。
# 没 checkout funNLP 的人可以用环境变量 FUNNLP_DATA_DIR 或 CLI 参数 --data-dir
# 指向自己的词典目录覆盖（见 resolve_data_dir）。
DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent.parent / "funNLP" / "data"

# 环境变量名
ENV_DATA_DIR = "FUNNLP_DATA_DIR"


def resolve_data_dir(cli_arg: Optional[Union[str, Path]] = None) -> Path:
    """解析词典目录，优先级：CLI 参数 > 环境变量 FUNNLP_DATA_DIR > 缺省值。

    缺省值是相对本仓库推断的同级 ``funNLP/data``；没 checkout funNLP 时
    可传 ``--data-dir`` 或设 ``FUNNLP_DATA_DIR`` 指向自己的词典目录。
    """
    if cli_arg:
        return Path(cli_arg).expanduser()
    env_val = os.environ.get(ENV_DATA_DIR)
    if env_val:
        return Path(env_val).expanduser()
    return DEFAULT_DATA_DIR


def scan_available_dicts(data_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
    """Scan and find available dictionary files.

    data_dir: 词典目录；为 None 时按 resolve_data_dir 解析
    （CLI > 环境变量 > 缺省）。
    """
    dict_map: Dict[str, Path] = {}

    base = resolve_data_dir(data_dir)
    if not base.exists():
        return dict_map

    # Scan for common dictionary files
    for txt_file in base.rglob("*.txt"):
        filename = txt_file.name.lower()
        
        # Map common file patterns
        if "stopword" in filename or "stop_word" in filename:
            dict_map["stopwords"] = txt_file
        elif "thuocl_it" in filename:
            dict_map["it"] = txt_file
        elif "thuocl_animal" in filename:
            dict_map["animals"] = txt_file
        elif "thuocl_medical" in filename:
            dict_map["medical"] = txt_file
        elif "thuocl_law" in filename:
            dict_map["law"] = txt_file
        elif "thuocl_caijing" in filename:
            dict_map["finance"] = txt_file
        elif "thuocl_food" in filename:
            dict_map["food"] = txt_file
        elif "thuocl_car" in filename:
            dict_map["car"] = txt_file
        elif "thuocl_diming" in filename:
            dict_map["place_names"] = txt_file
        elif "idiom" in filename and "thuocl" not in filename:
            dict_map["idioms"] = txt_file
    
    return dict_map


def load_dict(dict_type: str, encoding: str = "utf-8",
              data_dir: Optional[Union[str, Path]] = None) -> List[str]:
    """Load dictionary by type"""
    dict_map = scan_available_dicts(data_dir)

    if dict_type not in dict_map:
        available = list(dict_map.keys())
        raise ValueError(f"Unknown dict type: {dict_type}. Available: {available}")
    
    dict_path = dict_map[dict_type]
    
    words = []
    with open(dict_path, "r", encoding=encoding, errors="ignore") as f:
        for line in f:
            word = line.strip()
            if word and not word.startswith("#"):
                # Handle THUOCL format: word\tfreq
                if "\t" in word:
                    word = word.split("\t")[0]
                words.append(word)
    
    return words


def get_dict_stats(dict_type: str,
                   data_dir: Optional[Union[str, Path]] = None) -> Dict:
    """Get dictionary statistics"""
    words = load_dict(dict_type, data_dir=data_dir)

    return {
        "type": dict_type,
        "count": len(words),
        "unique": len(set(words)),
        "preview": words[:10] if len(words) > 10 else words,
    }


def list_available_dicts(
        data_dir: Optional[Union[str, Path]] = None) -> List[str]:
    """List all available dictionary types"""
    return list(scan_available_dicts(data_dir).keys())


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Load funNLP dictionaries")
    parser.add_argument("--type", help="Dictionary type")
    parser.add_argument("--list", action="store_true", help="List available types")
    parser.add_argument("--preview", action="store_true", help="Show preview")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument(
        "--data-dir",
        help=(
            "词典目录（覆盖环境变量 FUNNLP_DATA_DIR 和缺省值）。"
            "没 checkout funNLP 时用它指向自己的词典目录。"
        ),
    )

    args = parser.parse_args()

    data_dir = args.data_dir

    try:
        if args.list:
            available = list_available_dicts(data_dir)
            print(f"Available dictionary types ({len(available)}):")
            for dt in sorted(available):
                print(f"  - {dt}")
            return

        if not args.type:
            parser.error("--type is required (or use --list)")

        if args.stats or args.preview:
            stats = get_dict_stats(args.type, data_dir=data_dir)
            
            if args.output == "json":
                import json
                print(json.dumps(stats, ensure_ascii=False, indent=2))
            else:
                print(f"Dictionary Type: {stats['type']}")
                print(f"Total Words: {stats['count']}")
                print(f"Unique Words: {stats['unique']}")
                if args.preview:
                    print(f"\nPreview (first 10):")
                    for word in stats['preview']:
                        print(f"  - {word}")
        else:
            words = load_dict(args.type, data_dir=data_dir)

            if args.output == "json":
                import json
                print(json.dumps(words, ensure_ascii=False, indent=2))
            else:
                for word in words:
                    print(word)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

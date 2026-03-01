#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
funNLP Dictionary Loader
Load common Chinese NLP dictionaries from funNLP project
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# funNLP data directory (relative to workspace)
FUNNLP_DATA_DIR = Path(__file__).parent.parent.parent.parent / "funNLP" / "data"


def scan_available_dicts() -> Dict[str, Path]:
    """Scan and find available dictionary files"""
    dict_map = {}
    
    if not FUNNLP_DATA_DIR.exists():
        return dict_map
    
    # Scan for common dictionary files
    for txt_file in FUNNLP_DATA_DIR.rglob("*.txt"):
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


def load_dict(dict_type: str, encoding: str = "utf-8") -> List[str]:
    """Load dictionary by type"""
    dict_map = scan_available_dicts()
    
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


def get_dict_stats(dict_type: str) -> Dict:
    """Get dictionary statistics"""
    words = load_dict(dict_type)
    
    return {
        "type": dict_type,
        "count": len(words),
        "unique": len(set(words)),
        "preview": words[:10] if len(words) > 10 else words,
    }


def list_available_dicts() -> List[str]:
    """List all available dictionary types"""
    return list(scan_available_dicts().keys())


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Load funNLP dictionaries")
    parser.add_argument("--type", help="Dictionary type")
    parser.add_argument("--list", action="store_true", help="List available types")
    parser.add_argument("--preview", action="store_true", help="Show preview")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    try:
        if args.list:
            available = list_available_dicts()
            print(f"Available dictionary types ({len(available)}):")
            for dt in sorted(available):
                print(f"  - {dt}")
            return
        
        if not args.type:
            parser.error("--type is required (or use --list)")
        
        if args.stats or args.preview:
            stats = get_dict_stats(args.type)
            
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
            words = load_dict(args.type)
            
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

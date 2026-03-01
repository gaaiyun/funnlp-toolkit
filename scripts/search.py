#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
funNLP Resource Search
Search NLP resources from funNLP README
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict

FUNNLP_README = Path(__file__).parent.parent.parent.parent / "funNLP" / "README.md"


def parse_readme() -> List[Dict]:
    """Parse funNLP README and extract resources"""
    if not FUNNLP_README.exists():
        raise FileNotFoundError(f"README not found: {FUNNLP_README}")
    
    resources = []
    current_category = None
    
    with open(FUNNLP_README, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            
            # Category header
            if line.startswith("##") and not line.startswith("###"):
                current_category = line.replace("##", "").strip()
            
            # Resource link
            elif "[" in line and "](" in line and current_category:
                match = re.search(r'\[([^\]]+)\]\(([^\)]+)\)', line)
                if match:
                    title = match.group(1)
                    url = match.group(2)
                    
                    # Extract description
                    desc = line.split(")", 1)[1].strip() if ")" in line else ""
                    
                    resources.append({
                        "category": current_category,
                        "title": title,
                        "url": url,
                        "description": desc
                    })
    
    return resources


def search_resources(query: str, resources: List[Dict]) -> List[Dict]:
    """Search resources by query"""
    query_lower = query.lower()
    results = []
    
    for res in resources:
        score = 0
        
        if query_lower in res["title"].lower():
            score += 10
        if query_lower in res["category"].lower():
            score += 5
        if query_lower in res["description"].lower():
            score += 3
        
        if score > 0:
            results.append({**res, "score": score})
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Search funNLP resources")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    
    args = parser.parse_args()
    
    try:
        resources = parse_readme()
        results = search_resources(args.query, resources)[:args.limit]
        
        if args.output == "json":
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"Found {len(results)} results for '{args.query}':\n")
            for i, res in enumerate(results, 1):
                print(f"{i}. [{res['category']}] {res['title']}")
                print(f"   URL: {res['url']}")
                if res['description']:
                    print(f"   Desc: {res['description']}")
                print()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

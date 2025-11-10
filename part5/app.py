#!/usr/bin/env python3
"""
Part 5 starter CLI.

WHAT'S NEW IN PART 5
- Data moved from Python module to JSON: load sonnets from sonnets.json
- Persist UI settings using a JSON config file: config.json

BUT:
- Keep the Exercise 4 "search mode" concept (AND/OR)

"""
from selectors import SelectSelector
from typing import List, Dict, Any
import json
import os
from .constants import BANNER, HELP

def find_spans(text: str, pattern: str):
    """Return [(start, end), ...] for all (possibly overlapping) matches.
    Inputs should already be lowercased by the caller."""

    spans = []

    for i in range(len(text)-len(pattern)+1):
        if text[i:i+len(pattern)] == pattern:
            spans.append((i, i + len(pattern)))

    return spans

def ansi_highlight(text: str, spans):
    if not spans:
        return text
    spans = sorted(spans)
    merged = []
    for s, e in spans:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    out, i = [], 0
    for s, e in merged:
        if s > i:
            out.append(text[i:s])
        out.append("\x1b[1m\x1b[43m")
        out.append(text[s:e])
        out.append("\x1b[0m")
        i = e
    out.append(text[i:])
    return "".join(out)

def search_sonnet(sonnet, query: str):
    title_raw = str(sonnet["title"])
    lines_raw = sonnet["lines"]  # list[str]

    q = query.lower()
    title_spans = find_spans(title_raw.lower(), q)

    line_matches = []
    for idx, line_raw in enumerate(lines_raw, start=1):  # 1-based line numbers
        spans = find_spans(line_raw.lower(), q)
        if spans:
            line_matches.append({"line_no": idx, "text": line_raw, "spans": spans})

    total = len(title_spans) + sum(len(lm["spans"]) for lm in line_matches)
    return {
        "title": title_raw,
        "title_spans": title_spans,
        "line_matches": line_matches,
        "matches": total,
    }

def combine_results(result1, result2):
    # Start out by using result1 as the combined result
    combined = result1

    # Combine the simpler properties, e.g., "matches" and "title_spans"
    combined["matches"] += result2["matches"]
    combined["title_spans"] = sorted(combined["title_spans"] + result2["title_spans"])

    # Now, for "line_matches", init a list of line matches we only have in result2
    lms_only_in_result2 = []

    for lm2 in result2["line_matches"]:
        # Search for each line match of result2 in result1
        found = False
        for lm1 in combined["line_matches"]:
            # Check whether we already have a match for that line
            if lm1["line_no"] == lm2["line_no"]:
                # Yes, combine and sort them
                lm1["spans"] = sorted(lm1["spans"] + lm2["spans"])
                found = True
                break
        if not found:
            # This line match only is in lm2, remember it
            lms_only_in_result2.append(lm2)

    # Add all line matches we only found in result2
    combined["line_matches"].extend(lms_only_in_result2)
    # Sort all line matches by line no
    combined["line_matches"] = sorted(combined["line_matches"], key=lambda lm: lm["line_no"])

    return combined

def print_results(query: str, results, highlight: bool):
    total_docs = len(results)
    matched = [r for r in results if r["matches"] > 0]
    print(f'{len(matched)} out of {total_docs} sonnets contain "{query}".')

    for idx, r in enumerate(matched, start=1):
        title_line = ansi_highlight(r["title"], r["title_spans"]) if highlight else r["title"]
        print(f"\n[{idx}/{total_docs}] {title_line}")
        for lm in r["line_matches"]:
            line_out = ansi_highlight(lm["text"], lm["spans"]) if highlight else lm["text"]
            print(f"  [{lm["line_no"]:2}] {line_out}")


def module_relative_path(name: str) -> str:
    """Return absolute path to sonnets.json sitting next to this module."""
    return os.path.join(os.path.dirname(__file__), name)

# Replace the placeholder function with code that opens part5/sonnets.json and loads it.
# Keep the same in-memory structure as before: a list of dicts with keys "title" and "lines".
def load_sonnets() -> List[Dict[str, object]]:
    with open(module_relative_path("sonnets.json"), "r", encoding="utf-8") as f:
        sonnets = json.load(f)

    return sonnets


CONFIG_DEFAULTS = { "highlight": True, "search_mode": "AND" }

def load_config() -> Dict[str, object]:
    config = {}
    path = module_relative_path("config.json")

    if os.path.isfile(path):
        with open(module_relative_path("config.json"), "r", encoding="utf-8") as f:
            try:
                tmp = json.load(f)
            except json.decoder.JSONDecodeError:
                tmp = {}
    else:
        return CONFIG_DEFAULTS

    for x in CONFIG_DEFAULTS.keys():
        if x in tmp:
            config[x] = tmp[x]
        else:
            config[x] = CONFIG_DEFAULTS[x]

    return config

def save_config(cfg: Dict[str, object]) -> None:
    tmp = {}
    path = module_relative_path("config.json")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                tmp = json.load(f)
            except json.decoder.JSONDecodeError:
                tmp = {}

        for x in cfg.keys():
            tmp[x] = cfg[x]

    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(tmp, indent=2, ensure_ascii=False))

def main() -> None:

    # Load the sonnets from the JSON file
    sonnets = load_sonnets()

    # Load the configuration from the JSON file
    config = load_config()

    print(BANNER)
    print()  # blank line after banner
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        if raw.startswith(":"):
            if raw == ":quit":
                print("Bye.")
                break
            if raw == ":help":
                print(HELP)
                continue
            if raw.startswith(":highlight"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].lower() in ("on", "off"):
                    config["highlight"] = (parts[1].lower() == "on")
                    print("Highlighting", "ON" if config["highlight"] else "OFF")
                    # DONE; ToDo 3: Use save_config(...) to write the config.json file when the highlight setting changes
                    save_config(config)
                else:
                    print("Usage: :highlight on|off")
                continue
            # DONE; ToDo 0 - Copy (and adapt) your implementation of the search mode CLI from part 4 of the exercise
            if raw.startswith(":search-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("AND", "OR"):
                    config["search_mode"] = parts[1].upper()
                    print("Search mode set to", "AND" if config["search_mode"] == "AND" else "OR")
                    save_config(config)
                else:
                    print("Usage: :search-mode AND|OR")
                continue
            print("Unknown command. Type :help for commands.")
            continue

            print("Unknown command. Type :help for commands.")
            continue

        # query
        combined_results = []

        words = raw.split()

        for word in words:
            # Searching for the word in all sonnets
            results = [search_sonnet(s, word) for s in sonnets]

            if not combined_results:
                # No results yet. We store the first list of results in combined_results
                combined_results = results
            else:
                # We have an additional result, we have to merge the two results: loop all sonnets
                for i in range(len(combined_results)):
                    # Checking each sonnet individually
                    combined_result = combined_results[i]
                    result = results[i]

                    # DONE; ToDo 0 - Copy your implementation of the search mode from part 4 of the exercise
                    if config["search_mode"] == "AND":
                        if combined_result["matches"] > 0 and result["matches"] > 0:
                            # Only if we have matches in both results, we consider the sonnet (logical AND!)
                            combined_results[i] = combine_results(combined_result, result)
                        else:
                            # Not in both. No match!
                            combined_result["matches"] = 0
                    else:
                        combined_results[i] = combine_results(combined_result, result)

        print_results(raw, combined_results, bool(config["highlight"]))

if __name__ == "__main__":
    main()

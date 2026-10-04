"""Offline checks for the LCEL cheatsheet catalog and local playground."""

from __future__ import annotations

import unittest

from catalog import CATEGORIES, ENTRIES, filter_entries, titles_for
from playground import LOCAL_PATTERNS, run_pattern


REQUIRED = {"id", "title", "category", "tags", "summary", "when", "openai", "anthropic", "notes"}


class CatalogTests(unittest.TestCase):
    def test_entries_are_complete_and_unique(self):
        ids = [e["id"] for e in ENTRIES]
        self.assertEqual(len(ids), len(set(ids)))
        for entry in ENTRIES:
            missing = REQUIRED - set(entry)
            self.assertFalse(missing, msg=f"{entry.get('id')}: missing {missing}")
            self.assertIn(entry["category"], CATEGORIES)
            self.assertTrue(entry["openai"].strip())
            self.assertTrue(entry["anthropic"].strip())
            self.assertTrue("import " in entry["openai"] or "Runnable" in entry["openai"])

    def test_search_filters(self):
        hits = filter_entries("fallback", "All")
        self.assertTrue(any(e["id"] == "fallbacks" for e in hits))
        rag = filter_entries("", "RAG")
        self.assertTrue(rag)
        self.assertTrue(all(e["category"] == "RAG" for e in rag))
        self.assertTrue(titles_for(ENTRIES))


class LocalPlaygroundTests(unittest.TestCase):
    def test_local_patterns_do_not_need_keys(self):
        for pattern in LOCAL_PATTERNS:
            output, graph = run_pattern(pattern, "OpenAI", "gpt-4o-mini", "", "", "def pipe(a, b): return a | b")
            self.assertFalse(output.startswith("Run failed"), msg=f"{pattern}: {output}")
            self.assertTrue(output)
            self.assertTrue(graph)


if __name__ == "__main__":
    unittest.main()

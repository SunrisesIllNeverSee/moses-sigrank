import json
import unittest

from ingest import ingest_meta
from metrics import SEED, compute


class MetricLockTests(unittest.TestCase):
    def test_moses_seed_metrics_are_canonical(self):
        metrics = compute(*SEED["MO§ES (ccusage)"])

        self.assertAlmostEqual(metrics["yield"], 18436.98, places=2)
        self.assertAlmostEqual(metrics["leverage"], 2042.2, places=1)
        self.assertAlmostEqual(metrics["dev10x"], 3.31, places=2)
        self.assertAlmostEqual(metrics["avg_cost_1m"], 0.527, places=3)

    def test_cascade_identity_holds_for_every_seed_row(self):
        for name, raw in SEED.items():
            with self.subTest(operator=name):
                metrics = compute(*raw)
                self.assertIsNotNone(metrics["dev10x"])

                lhs = (
                    metrics["transmission"]
                    * metrics["commitment"]
                    * metrics["reuse"]
                )

                self.assertAlmostEqual(lhs, metrics["leverage"], places=12)


class CodexParserLockTests(unittest.TestCase):
    def test_alpha_path_uses_output_times_two_baseline(self):
        payload = {
            "data": [
                {
                    "inputTokens": 1_000,
                    "cachedInputTokens": 3_000,
                    "outputTokens": 200,
                    "reasoningOutputTokens": 50,
                }
            ]
        }

        input_tokens, output_tokens, cache_create, cache_read, meta = ingest_meta(
            json.dumps(payload)
        )

        self.assertEqual(input_tokens, 500)
        self.assertEqual(output_tokens, 250)
        self.assertEqual(cache_create, 500)
        self.assertEqual(cache_read, 3_000)
        self.assertEqual(meta["source"], "codex")
        self.assertIs(meta["estimated"], True)
        self.assertTrue(meta["caveat"].startswith("* AA 2:1 baseline"))

    def test_beta_path_uses_claude_operator_ratio(self):
        payload = {
            "totals": {
                "input_tokens": 2_000,
                "cached_input_tokens": 5_000,
                "output_tokens": 300,
                "reasoning_output_tokens": 100,
            }
        }
        operator_profile = {"model_type": "claude", "io_ratio": 1.25}

        input_tokens, output_tokens, cache_create, cache_read, meta = ingest_meta(
            json.dumps(payload), operator_profile=operator_profile
        )

        self.assertEqual(input_tokens, 500)
        self.assertEqual(output_tokens, 400)
        self.assertEqual(cache_create, 1_500)
        self.assertEqual(cache_read, 5_000)
        self.assertEqual(meta["source"], "codex")
        self.assertIs(meta["estimated"], True)
        self.assertTrue(meta["caveat"].startswith("* Claude operating-ratio 1.250:1"))


if __name__ == "__main__":
    unittest.main()

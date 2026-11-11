"""Reproducible checks of dynamics, not semantic-quality benchmarks."""
import json
import unittest
import numpy as np
from memory_experiment import EngramMemory, MemoryConfig


class Codebook:
    def __init__(self, dimensions):
        self.dimensions = dimensions

    def __call__(self, text):
        result = np.zeros(self.dimensions)
        result[{"alpha": 0, "alpha-variant": 0, "beta": 1, "gamma": 2}[text]] = 1
        return result


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.config = MemoryConfig(neurons=120, assembly_size=10, embedding_dim=8, seed=9)
        self.encoder = Codebook(8)
        self.model = EngramMemory(self.config, self.encoder)

    def test_cue_recovers_assembly(self):
        self.model.write("alpha")
        self.model.write("beta")
        hits = self.model.recall("alpha-variant", reset_activity=True)
        self.assertIn("m0", [h.memory_id for h in hits])
        scores = {h.memory_id: h.score for h in self.model.read(threshold=-1)}
        self.assertGreater(scores["m0"], scores["m1"])

    def test_weights_budget_and_symmetry(self):
        for text in ["alpha", "beta", "gamma"] * 30:
            self.model.write(text)
        w = self.model.weights
        np.testing.assert_allclose(w, w.T, atol=1e-12)
        np.testing.assert_allclose(np.diag(w), 0)
        self.assertGreaterEqual(w.min(), 0)
        self.assertLessEqual(w.sum(axis=1).max(), self.config.synaptic_budget + 1e-10)
        self.assertTrue(np.all(self.model.thresholds <= self.config.max_threshold))
        self.assertTrue(np.all(self.model.thresholds >= self.config.min_threshold))

    def test_activity_bounds(self):
        self.model.write("alpha")
        self.model.advance(100)
        self.assertGreaterEqual(float(self.model.activity.min()), 0)
        self.assertLessEqual(float(self.model.activity.max()), 1)

    def test_memory_assemblies_overlap(self):
        self.model.write("alpha")
        self.model.write("alpha-variant")
        self.assertGreater(float(self.model.records[0].pattern @ self.model.records[1].pattern), 0)

    def test_snapshot_roundtrip(self):
        self.model.write("alpha")
        self.model.recall("alpha", reset_activity=True)
        restored = EngramMemory.restore(json.loads(json.dumps(self.model.snapshot())), self.encoder)
        np.testing.assert_array_equal(restored.weights, self.model.weights)
        np.testing.assert_array_equal(restored.activity, self.model.activity)
        self.assertEqual(restored.read(), self.model.read())
        self.assertEqual(restored.write("beta"), self.model.write("beta"))
        np.testing.assert_array_equal(restored.weights, self.model.weights)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.model.write(" ")
        with self.assertRaises((KeyError, ValueError)):
            self.model.recall("unknown")
        with self.assertRaises(ValueError):
            self.model.advance(-1)
        with self.assertRaises(ValueError):
            self.model.advance(stimulus=np.zeros(2))



class RecallRegressionTests(unittest.TestCase):
    """Issue #10: stimulus-free settling erased lexical-v1 cue discrimination."""

    FACTS = [
        "production database runs PostgreSQL 16 on port 5432",
        "deployment uses Argo CD into the bluefin staging cluster",
        "api rate limit is 120 requests per tenant per minute",
        "logs are kept in an S3 bucket in eu-central for 30 days",
        "the mobile app is written in Flutter and ships weekly",
        "authentication uses OAuth 2.0 with PKCE short lived tokens",
        "billing runs monthly and invoices on the third of each month",
        "cache is Redis 7 with a 15 minute TTL on product pages",
        "backups run nightly at 02:00 UTC and verify weekly",
        "the search index is rebuilt every Sunday by an Airflow DAG",
    ]

    def test_default_recall_does_not_erase_cues(self):
        from memory_experiment.dsh_bridge import CONFIG, encode

        model = EngramMemory(CONFIG, encode)
        for fact in self.FACTS:
            model.write(fact)

        for index, fact in enumerate(self.FACTS):
            with self.subTest(index=index):
                hits = model.recall(fact, reset_activity=True)
                self.assertTrue(hits, "a known cue must have a matching hit")
                self.assertEqual(hits[0].memory_id, f"m{index}")
                explicit_zero = model.recall(
                    fact, reset_activity=True, settle_steps=0
                )
                self.assertEqual(hits, explicit_zero)



if __name__ == "__main__":
    unittest.main()

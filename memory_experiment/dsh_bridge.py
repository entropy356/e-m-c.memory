"""JSON stdio adapter for the DSH bundle."""

from contextlib import closing
from dataclasses import asdict
from hashlib import blake2b
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata

import numpy as np

from .model import EngramMemory, MemoryConfig


ENCODER = "lexical-v1"
CONFIG = MemoryConfig(embedding_dim=512)
MAX_TEXT_BYTES = 16 * 1024
HAN = r"\u3400-\u4dbf\u4e00-\u9fff"
TOKENS = re.compile(rf"[{HAN}]+|[^\W{HAN}]+")
HAN_CHAR = re.compile(rf"[{HAN}]")


def encode(text: str) -> np.ndarray:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    vector = np.zeros(CONFIG.embedding_dim)
    for token in TOKENS.findall(normalized) or [normalized.strip()]:
        features = [token]
        if HAN_CHAR.match(token):
            features = [*token, *(token[i:i + 2] for i in range(len(token) - 1))]
        for feature in features:
            digest = blake2b(feature.encode("utf-8"), digest_size=4).digest()
            vector[int.from_bytes(digest, "little") % vector.size] += 1
    return np.sqrt(vector)


def run(database: Path, operation: str, text: str) -> dict:
    if operation not in {"write", "recall"}:
        raise ValueError("unknown operation")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("memory text or recall query must be non-blank")
    if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        raise ValueError("memory text or recall query exceeds 16 KiB UTF-8")

    database.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with closing(sqlite3.connect(database, timeout=8)) as db, db:
        if operation == "write":
            # Serialize the entire read, model update, and commit across DSH processes.
            db.execute("BEGIN IMMEDIATE")
        db.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                encoder TEXT NOT NULL,
                snapshot TEXT NOT NULL
            )
        """)
        stored = db.execute("SELECT encoder, snapshot FROM memory WHERE id = 1").fetchone()
        if stored is None:
            model = EngramMemory(CONFIG, encode)
        else:
            encoder, snapshot = stored
            if encoder != ENCODER:
                raise ValueError("incompatible e-m-c Memory encoder")
            model = EngramMemory.restore(json.loads(snapshot), encode)

        if operation == "recall":
            hits = model.recall(text, reset_activity=True)
            return {"hits": [asdict(hit) for hit in hits[:3]]}

        memory_id = model.write(text)
        db.execute(
            "INSERT INTO memory VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET snapshot = excluded.snapshot",
            (ENCODER, json.dumps(model.snapshot(), separators=(",", ":"), allow_nan=False)),
        )
        return {"memory_id": memory_id}


def main() -> None:
    request = json.loads(sys.stdin.buffer.read())
    result = run(Path(sys.argv[1]), request["operation"], request["text"])
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, sqlite3.Error, OSError) as error:
        sys.exit(f"e-m-c Memory: {error}")

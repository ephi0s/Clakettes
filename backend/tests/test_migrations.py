"""Tests for the Alembic migration chain integrity.

Every schema change must ship exactly one migration so that ``upgrade head``
(also run automatically at application startup) converges any database
without manual reconfiguration.
"""

import ast
from pathlib import Path

VERSIONS = Path(__file__).resolve().parent.parent / "alembic" / "versions"


def _load_revisions():
    revisions = {}
    for path in VERSIONS.glob("*.py"):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and target.id in ("revision", "down_revision"):
                    values[target.id] = ast.literal_eval(node.value)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id in ("revision", "down_revision") and node.value is not None:
                    values[node.target.id] = ast.literal_eval(node.value)
        assert "revision" in values, f"{path.name} has no revision"
        revisions[values["revision"]] = values.get("down_revision")
        source = path.read_text(encoding="utf-8")
        assert "def upgrade(" in source, f"{path.name} has no upgrade()"
        assert "def downgrade(" in source, f"{path.name} has no downgrade()"
    return revisions


class TestMigrationChain:
    def test_single_head(self):
        revisions = _load_revisions()
        referenced = {d for d in revisions.values() if d is not None}
        heads = [r for r in revisions if r not in referenced]
        assert len(heads) == 1, f"expected a single head, found: {heads}"

    def test_chain_continuity(self):
        revisions = _load_revisions()
        for revision, down_revision in revisions.items():
            if down_revision is None:
                continue
            assert down_revision in revisions, f"{revision} points at unknown {down_revision}"

    def test_no_duplicate_revisions(self):
        seen = {}
        for path in VERSIONS.glob("*.py"):
            if path.name == "__init__.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                if (
                    isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "revision"
                ):
                    revision = ast.literal_eval(node.value)
                    assert revision not in seen, f"duplicate revision {revision} in {path.name} and {seen[revision]}"
                    seen[revision] = path.name

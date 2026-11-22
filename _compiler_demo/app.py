"""Read-only WSGI demo. Set CONTEXT_COMPILER_ROOT to the private source checkout.
Run "python _compiler_demo/app.py export" to refresh the static host's public runs.
Mount application at /compiler/{domain}/runs/{case}.json for on-demand compilation.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

SITE = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("CONTEXT_COMPILER_ROOT", SITE.parent / "context-compiler"))
sys.path.insert(0, str(ROOT))
import context_compiler as cc

CASES = {"investing": ("315", "475", "300"), "legal": ("signed", "missing")}
PUBLIC = ["public"]


def load(path):
    return json.loads(path.read_bytes())


def investment_inputs(case):
    fixtures = ROOT / "docs/contracts/fixtures/s2"
    directory = fixtures / "cases" / f"we1-{case}"
    declaration = load(directory / "snapshot.json")
    files = {path.name.split(".")[0]: path for path in (fixtures / "sources").iterdir()}

    def read(source_id):
        return files[source_id].read_bytes()

    return (cc.load_pack(ROOT / "packs/investment_research"),
            cc.snapshot(declaration["sources"], declaration["inventory"]),
            load(directory / "task.json"), read)


def legal_inputs(case):
    pack = cc.load_pack(SITE / "_compiler_demo/legal")
    sources = []
    records = {}
    clauses = [
        ("agreement", "Alder supply agreement, §8.2", "cure_period", "30",
         "The supplier has 30 calendar days after deemed receipt of written notice to cure a material breach."),
        ("schedule", "Notice schedule, §2", "deemed_receipt_delay", "2",
         "Notice sent by courier is deemed received two calendar days after dispatch."),
    ]
    date = "2026-01-01T00:00:00Z"
    for source_id, title, predicate, amount, clause in clauses:
        if case == "missing" and source_id == "schedule":
            continue
        data = json.dumps([{"subject": "contract:alder", "predicate": predicate, "qualifiers": {},
                            "amount": amount, "unit": "calendar_days", "clause": clause}]).encode()
        records[source_id] = data
        sources.append({"source_id": source_id, "title": title, "issuer": "parties:alder",
                        "authority_class": "record", "access_labels": PUBLIC, "about": None,
                        "published_at": date, "known_at": date, "withdrawn_at": None,
                        "supersedes": [], "read_coverage": "complete", "adapter": "records_json.v1",
                        "media_type": "application/json",
                        "content_hash": "sha256:" + hashlib.sha256(data).hexdigest()})
    task = {"schema_version": 1, "task_type": "report", "pack": {"id": pack["id"], "version": 1},
            "access_scope": PUBLIC, "as_of": date, "require_settled": True, "on_incomplete": "refuse",
            "params": {"subject": "contract:alder", "predicate": "cure_period"},
            "budget": {"counter": "unit_table.v1", "limit": 200}, "artifact_limit_bytes": None,
            "policies": dict.fromkeys(("attention", "authority", "closure", "compression")),
            "question": None, "pins": None, "target": None}
    snapshot = cc.snapshot(sources, {"scope": "Supplied Alder agreement records", "state": "closed"})
    return pack, snapshot, task, records.__getitem__


def public_run(domain, case):
    pack, snapshot, task, read = (investment_inputs if domain == "investing" else legal_inputs)(case)
    ir = cc.derive(snapshot, read, pack)
    result, _ = cc.compile(snapshot, ir, task, pack)
    if result["release_labels"] != PUBLIC:
        raise ValueError("Unexpected release scope")
    view = {"id": result["compilation_id"], "outcome": result["outcome"],
            "refusal": result["refusal"], "evidence": []}
    context = result["context"]
    if context:
        sources = {s["handle"]: s for s in context["sources"]}
        for entry in context["entries"]:
            for key in entry["keys"]:
                for point in key["points"]:
                    witness = cc.resolve_handle(result, point["handle"], snapshot, read, PUBLIC)
                    view["evidence"].append({
                        "predicate": entry["predicate"], "unit": entry["unit"], "role": key["role"],
                        "period": key["series"], "amount": point["value"]["amount"],
                        "handle": point["handle"], "source": sources[point["source"]]["title"],
                        "locator": point["locator"], "witness": witness.decode()})
    return view


ROUTES = {f"/compiler/{domain}/runs/{case}.json": (domain, case)
          for domain, cases in CASES.items() for case in cases}


def application(environ, start_response):
    route = ROUTES.get(environ["PATH_INFO"])
    if not route:
        start_response("404 Not Found", [])
        return [b""]
    if environ["REQUEST_METHOD"] not in ("GET", "HEAD"):
        start_response("405 Method Not Allowed", [("Allow", "GET, HEAD")])
        return [b""]
    body = json.dumps(public_run(*route), ensure_ascii=False).encode()
    start_response("200 OK", [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
    return [body] if environ["REQUEST_METHOD"] == "GET" else []


if __name__ == "__main__":
    if sys.argv[1:] == ["export"]:
        for route, selection in ROUTES.items():
            (SITE / route.lstrip("/")).write_text(json.dumps(public_run(*selection), indent=2, ensure_ascii=False) + "\n")
    else:
        from wsgiref.simple_server import make_server
        with make_server("127.0.0.1", 8091, application) as server:
            server.serve_forever()

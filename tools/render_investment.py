"""Refresh the two static exhibits from the public JSON release, using only stdlib."""

import argparse
from html import escape
import json
from pathlib import Path


def h(value):
    return escape(str(value), quote=True)


def amount(p):
    return (
        (p["amount"] if p["kind"] == "decimal" else p["low"] + " to " + p["high"])
        + " "
        + p["unit"]
    )


def card(state, p):
    source = next(s for s in state["sources"] if s["handle"] == p["source"])
    witness = state["witnesses"][p["handle"]]
    original = p["reported"]
    reported = (
        f'<p>Reported as {h(original["amount"])} {h(original["unit"])}.</p>'
        if original
        else ""
    )
    return f"""<div class="point"><details><summary id="{h(state["state_id"])}-{h(p["handle"])}"><strong>{h(amount(p))}</strong> <span>{h(p["handle"])}</span></summary>
<div class="citation"><h5>{h(source["title"])}</h5><p>{h(source["authority_class"])} &middot; {h(source["issuer"])}</p>
<p>Published {h(source["published"])} &middot; Known {h(source["known"])}</p>
<code>{h(witness["locator"])}</code><blockquote>{h(witness["text"])}</blockquote></div></details>
{reported}<small>{h(p["standing"])} &middot; {h(p["classification"])}</small></div>"""


def show_state(s):
    sid = s["state_id"]
    coverage = s["coverage"]

    def tally(key):
        v = coverage[key]
        return "not evaluated" if v is None else f'{v["listed"]} of {v["count"]} listed'

    out = [
        f'<article id="{sid}" class="record-state" aria-labelledby="{sid}-title">',
        f'<p class="label">Recorded state {sid}</p><h2 id="{sid}-title">{h(s["outcome"].capitalize())}</h2>',
        f'<p class="coverage">Coverage {h(coverage["state"])}. Required {tally("required")}. Supporting {tally("supporting")}.</p>',
    ]
    refusal = s["refusal"]
    if refusal:
        if "limit" in refusal:
            out.append(
                f'<p class="decision">Required evidence costs {refusal["required_cost"]} units. The limit is {refusal["limit"]}.</p>'
            )
        else:
            out.append('<p class="decision">Required coverage is incomplete.</p><ul>')
            for gap in refusal["gaps"]:
                out.append(
                    f'<li>{h(gap["label"])} ({h(gap["period"])}) &mdash; {h(gap["absence"].replace("_"," "))}. Required by {h(gap["required_by_label"])}.</li>'
                )
            out.append("</ul>")
    group_names = {
        "subject": "Requested figures",
        "required": "Required components",
        "supporting": "Supporting evidence",
    }
    for role, name in group_names.items():
        rows = [i for i in s["items"] if i["role"] == role]
        if not rows:
            continue
        out.append(
            f'<h3>{name}</h3><table class="evidence-table"><thead><tr><th>Measure and period</th><th>Value and source</th></tr></thead><tbody>'
        )
        for item in rows:
            status = " &middot; ".join(
                h(x) for x in [item["relation_label"], item["state"]] if x
            )
            out.append(
                f'<tr id="{sid}-{h(item["ref"])}"><th scope="row">{h(item["label"])}<small>{h(item["period"])} &middot; {status}</small></th><td><div class="points">'
            )
            out.extend(card(s, p) for p in item["points"])
            out.append("</div></td></tr>")
        out.append("</tbody></table>")
    if s["links"]:
        ref = {i["ref"]: i for i in s["items"]}

        def link(k):
            i = ref[k]
            return f'<a href="#{sid}-{h(k)}">{h(i["label"])} ({h(i["period"])})</a>'

        out.append(
            '<details class="relationships"><summary>Inspect relationships</summary><ul>'
        )
        for edge in s["links"]:
            out.append(
                f'<li>{link(edge["from"])} &mdash; {h(edge["kind"])} {h(edge["label"])} &mdash; {link(edge["to"])}</li>'
            )
        out.append("</ul></details>")
    if s["left_out"]:
        out.append("<h3>Left out</h3><ul>")
        for x in s["left_out"]:
            out.append(
                f'<li>{h(x["label"])} &middot; {h(x["class"])} &middot; {h(x["reason"])}</li>'
            )
        out.append("</ul>")
    out.append(
        '<details class="inventory" open><summary>Evidence supplied</summary><ul>'
    )
    for r in s["inventory"]:
        later = (
            " &middot; Not yet known on this date" if not r["known_at_as_of"] else ""
        )
        out.append(
            f'<li><strong>{h(r["title"])}</strong> &middot; {h(r["authority_class"])} &middot; {h(r["issuer"])}'
            f'<small>Published {h(r["published"])} &middot; Known {h(r["known"])}{later}</small></li>'
        )
    out.append(
        f'</ul></details><a class="text-link" href="runs/{sid}.json">Download {sid} as JSON</a></article>'
    )
    return "\n".join(out)


def excerpt(s):
    sources = s["sources"][:3]
    out = ['<div class="exhibit"><div><h3>Selected sources</h3><ul>']
    for src in sources:
        out.append(
            f'<li>{h(src["title"])}<small>{h(src["authority_class"])} &middot; {h(src["issuer"])}</small></li>'
        )
    out.extend(
        [
            '</ul></div><p class="process">Authority, dependencies, Attention</p><div><h3>Filing evidence</h3>',
            "<table><thead><tr><th>Measure</th><th>Period</th><th>Value</th></tr></thead><tbody>",
        ]
    )
    for item in s["items"]:
        if item["role"] in ("subject", "required"):
            (p,) = item["points"]
            out.append(
                f'<tr><th scope="row">{h(item["label"])}</th><td>{h(item["period"])}</td><td><a class="figure-link" href="/compiler/investing/?state=S4#{h(s["state_id"])}-{h(p["handle"])}">{h(amount(p))}</a></td></tr>'
            )
    i = next(i for i in s["items"] if i["role"] == "subject")
    p = i["points"][0]
    src = next(r for r in s["sources"] if r["handle"] == p["source"])
    w = s["witnesses"][p["handle"]]
    out.append(
        f'</tbody></table><details><summary>Trace {h(p["handle"])} to its filing cell</summary><p>{h(src["title"])}</p><code>{h(w["locator"])}</code><blockquote>{h(w["text"])}</blockquote></details></div></div>'
    )
    return "\n".join(out)


def insert(path, key, fragment):
    start = f"<!-- {key} -->"
    end = f"<!-- end {key} -->"
    text = path.read_text()
    assert text.count(start) == text.count(end) == 1
    before, tail = text.split(start)
    _, after = tail.split(end)
    path.write_text(before + start + "\n" + fragment + "\n" + end + after)


def render(site):
    folder = site / "compiler/investing"
    manifest = json.loads((folder / "runs/manifest.json").read_bytes())
    states = {
        r["state_id"]: json.loads((folder / "runs" / r["file"]).read_bytes())
        for r in manifest["states"]
    }
    insert(
        folder / "index.html",
        "recorded states",
        "\n".join(
            show_state(states[s]) for s in ["S4", *[s for s in states if s != "S4"]]
        ),
    )
    insert(site / "compiler/index.html", "recorded excerpt", excerpt(states["S4"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "site", nargs="?", type=Path, default=Path(__file__).resolve().parents[1]
    )
    render(parser.parse_args().site)

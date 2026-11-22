/* Select among complete, pre-rendered recordings. */
(async function () {
    "use strict";
    const controls = document.getElementById("controls");
    const announcement = document.getElementById("change");
    const fields = { budget: "budget_stop", policy: "policy_label", as_of: "as_of", note: "note_present" };
    const captions = { budget: "Budget", policy: "Policy", as_of: "As-of date", note: "Broker note" };
    const hints = {
        budget: "Recorded with the default policy, later date and broker note.",
        policy: "Recorded at budget stop 4 on the later date with the note.",
        as_of: "Recorded at budget stop 4 with the default policy and the note.",
        note: "Recorded on the earlier date with the default policy at budget stop 4."
    };
    async function get(file) {
        const response = await fetch("runs/" + file);
        if (!response.ok) throw new Error("Recording unavailable");
        return response.json();
    }
    function display(control, state) {
        const c = state.controls;
        if (control === "budget") return "Stop " + c.budget_stop + " · " + c.budget_limit + " units";
        if (control === "as_of") return c.as_of.slice(0, 10);
        if (control === "note") return c.note_present ? "Present" : "Absent";
        return c.policy_label;
    }
    try {
        const manifest = await get("manifest.json");
        const states = await Promise.all(manifest.states.map(row => get(row.file)));
        const byId = new Map(states.map(state => [state.state_id, state]));
        let current;
        function address() {
            const url = new URL(location.href);
            const id = url.searchParams.get("state") || url.hash.slice(1).split("-")[0];
            return byId.get(id) || byId.get(manifest.default_state);
        }
        function reachable(start, control) {
            const seen = new Set([start]);
            for (const id of seen) {
                for (const edge of manifest.transitions) {
                    if (edge.from === id && edge.control === control) seen.add(edge.to);
                }
            }
            return states.filter(s => seen.has(s.state_id));
        }
        function difference(prev, next) {
            const before = prev.coverage.supporting;
            const after = next.coverage.supporting;
            if (prev.controls.note_present !== next.controls.note_present && next.refusal?.gaps.length) {
                const absence = next.refusal.gaps[0].absence.replaceAll("_", " ");
                return "Both components are now reported " + absence + ".";
            }
            if (next.refusal?.reason === "required_exceeds_budget") {
                return "Required evidence costs " + next.refusal.required_cost + " units against a limit of " + next.refusal.limit + ".";
            }
            if (next.refusal) return next.refusal.gaps.length + " required components are missing.";
            if (prev.controls.policy_label !== next.controls.policy_label && before && after) {
                const conflict = next.items.find(i => i.points.length > 1);
                return conflict ? "The policy admits " + conflict.points.length + " competing estimates." :
                    "The broker estimates are left out and the drivers return.";
            }
            if (!before) return after.listed + " supporting items accompany the required figures.";
            const delta = after.listed - before.listed;
            return Math.abs(delta) + " supporting item" + (Math.abs(delta) === 1 ? "" : "s") +
                (delta < 0 ? " left" : " entered") + "; the required evidence is unchanged.";
        }
        function show(next, control) {
            const prev = current;
            current = next;
            for (const state of states) {
                document.getElementById(state.state_id).hidden = state !== next;
            }
            for (const key of Object.keys(fields)) {
                const group = document.getElementById(key);
                const choices = group.querySelector(".choices");
                const options = reachable(next.state_id, key);
                const field = fields[key];
                const values = new Map(states.map(s => [s.controls[field], s]));
                if (!choices.children.length) {
                    for (const [value, state] of values) {
                        const label = document.createElement("label");
                        const input = document.createElement("input");
                        input.type = "radio";
                        input.name = key;
                        input.dataset.option = String(value);
                        const text = document.createElement("span");
                        text.textContent = display(key, state);
                        label.append(input, text);
                        choices.append(label);
                    }
                }
                group.disabled = options.length === 1;
                for (const input of choices.querySelectorAll("input")) {
                    const target = options.find(row => String(row.controls[field]) === input.dataset.option);
                    input.checked = String(next.controls[field]) === input.dataset.option;
                    input.disabled = !target;
                    input.value = target?.state_id || "";
                }
                document.getElementById(key + "-reason").textContent = group.disabled ? hints[key] : "";
            }
            if (prev && prev !== next) {
                const step = control ? captions[control] + " from " + display(control, prev) +
                    " to " + display(control, next) : prev.state_id + " to " + next.state_id;
                const detail = difference(prev, next);
                announcement.textContent = step + " (" + next.state_id + ", " + next.outcome +
                    "): " + detail.charAt(0).toLowerCase() + detail.slice(1);
            } else {
                announcement.textContent = next.state_id + " " + next.outcome + ".";
            }
        }
        for (const key of Object.keys(fields)) {
            document.getElementById(key).addEventListener("change", event => {
                const next = byId.get(event.target.value);
                const url = new URL(location.href);
                url.searchParams.set("state", next.state_id);
                url.hash = "";
                history.pushState(null, "", url);
                show(next, key);
            });
        }
        window.addEventListener("popstate", () => show(address()));
        document.documentElement.classList.add("interactive");
        controls.hidden = false;
        show(address());
    } catch {
        document.documentElement.classList.remove("interactive");
        for (const panel of document.querySelectorAll(".record-state")) panel.hidden = false;
        controls.hidden = true;
        announcement.textContent = "Use the recorded-state links to inspect the static tables.";
    }
})();

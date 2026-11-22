const bench = document.querySelector('[data-demo]');
const statusHeading = document.querySelector('#run-status');
const result = document.querySelector('#run-result');
const labels = {
    cost_of_total_deposits: 'Cost of total deposits',
    avg_interest_bearing_deposits: 'Average interest-bearing deposits',
    avg_noninterest_bearing_deposits: 'Average noninterest-bearing deposits',
    interest_expense_deposits: 'Interest expense on deposits',
    cost_of_interest_bearing_deposits: 'Cost of interest-bearing deposits',
    policy_rate_upper: 'Upper bound of the policy rate',
    cure_period: 'Time to cure after deemed receipt',
    deemed_receipt_delay: 'Deemed receipt after courier dispatch'
};
const groups = { subject: 'Requested values', required: 'Required dependencies', supporting: 'Supporting evidence' };

function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
}

function evidenceRow(point) {
    const row = element('details');
    const summary = element('summary');
    const name = element('span', labels[point.predicate]);
    if (point.period) name.append(element('small', point.period.split('/')[0]));
    const units = { percent: '%', usd_mn: ' million USD', calendar_days: ' calendar days' };
    summary.append(name, element('strong', Number(point.amount).toLocaleString('en-US', {maximumFractionDigits: 3}) + units[point.unit]));
    const citation = element('div', undefined, 'citation');
    const witness = bench.dataset.demo === 'legal' ? JSON.parse(point.witness).clause : point.witness;
    citation.append(element('p', point.source), element('code', point.handle + ' · ' + point.locator), element('blockquote', witness));
    row.append(summary, citation);
    return row;
}

function display(run, url) {
    if (run.outcome === 'refused') {
        statusHeading.textContent = 'Compilation refused';
        const reason = run.refusal;
        const message = reason.reason === 'required_exceeds_budget'
            ? 'The required filing evidence costs ' + reason.detail.required_cost + ' units. With a limit of ' + reason.detail.limit + ', the compiler withholds the context.'
            : 'The notice schedule is missing. Without its deemed-receipt rule, the compiler withholds the cure period.';
        result.append(element('p', message, 'result-note'));
    } else {
        statusHeading.textContent = 'Compiled context';
        result.append(element('p', 'Open a value to inspect its source.', 'result-note'));
        for (const [role, title] of Object.entries(groups)) {
            const points = run.evidence.filter(point => point.role === role);
            if (!points.length) continue;
            result.append(element('h3', title));
            for (const point of points) result.append(evidenceRow(point));
        }
    }
    const link = element('a', 'Inspect public run JSON', 'text-link');
    link.href = url;
    result.append(link);
}

let requestNumber = 0;
async function selectCase() {
    const current = ++requestNumber;
    const choice = bench.querySelector('input:checked').value;
    const url = '/compiler/' + bench.dataset.demo + '/runs/' + choice + '.json';
    result.replaceChildren();
    statusHeading.textContent = 'Loading evidence…';
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Run unavailable');
        const run = await response.json();
        if (current === requestNumber) display(run, url);
    } catch {
        if (current !== requestNumber) return;
        result.replaceChildren();
        statusHeading.textContent = 'This run could not be loaded.';
        const retry = element('button', 'Retry');
        retry.type = 'button';
        retry.addEventListener('click', selectCase);
        result.append(retry);
    }
}
bench.addEventListener('change', selectCase);
selectCase();

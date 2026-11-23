(() => {
    const form = document.querySelector('#controls');
    const records = [...document.querySelectorAll('.record')];
    const bank = form.querySelector('#bank');
    const question = form.querySelector('#question');
    const date = form.querySelector('#date');

    function options(select, values) {
        const previous = select.value;
        select.replaceChildren(...[...new Set(values)].map(value => new Option(value, value)));
        if (values.includes(previous)) select.value = previous;
    }

    function updateDates() {
        const matches = records.filter(r => r.dataset.bank === bank.value && r.dataset.question === question.value);
        options(date, matches.map(r => r.dataset.date));
        date.disabled = date.options.length === 1;
        document.querySelector('#date-note').textContent = date.disabled
            ? 'One recorded date for this question.' : 'Only sources available on this date are eligible.';
    }

    function updateQuestions() {
        options(question, records.filter(r => r.dataset.bank === bank.value).map(r => r.dataset.question));
        question.disabled = question.options.length === 1;
        updateDates();
    }

    function display(record) {
        for (const r of records) r.hidden = r !== record;
        bank.value = record.dataset.bank;
        updateQuestions();
        question.value = record.dataset.question;
        updateDates();
        date.value = record.dataset.date;
    }

    function restore() {
        const key = new URL(location.href).searchParams.get('replay');
        display(records.find(r => r.id === key) || records[0]);
    }

    options(bank, records.map(r => r.dataset.bank));
    restore();
    form.hidden = false;
    bank.addEventListener('change', updateQuestions);
    question.addEventListener('change', updateDates);
    window.addEventListener('popstate', restore);
    form.addEventListener('submit', event => {
        event.preventDefault();
        const record = records.find(r => r.dataset.bank === bank.value &&
            r.dataset.question === question.value && r.dataset.date === date.value);
        const url = new URL(location.href);
        if (url.searchParams.get('replay') !== record.id) {
            url.searchParams.set('replay', record.id);
            history.pushState(null, '', url);
        }
        display(record);
        record.querySelector('h2').focus();
        document.querySelector('#status').textContent = 'Recorded result for ' + bank.value + ', ' + date.value;
    });
})();

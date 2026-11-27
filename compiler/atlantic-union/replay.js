// Without JavaScript each question links to its full recorded result below.
const questions = [...document.querySelectorAll('.replay-questions a')];
const states = [...document.querySelectorAll('.replay-state')];

function showSelection(moveFocus) {
    const selected = states.find(state => '#' + state.id === location.hash) || states[0];
    for (const state of states) state.hidden = state !== selected;
    for (const question of questions) {
        if (question.hash === '#' + selected.id) question.setAttribute('aria-current', 'step');
        else question.removeAttribute('aria-current');
    }
    if (moveFocus) selected.querySelector('h2').focus();
}

showSelection(false);
window.addEventListener('hashchange', () => showSelection(true));

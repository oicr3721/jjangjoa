let selectedTags = new Set();
let conditionMap = {};

function initTagGrid(conditions) {

  const grid = document.getElementById('tagGrid');
  grid.innerHTML = '';

  conditionMap = {};

  conditions.forEach((cond, i) => {

    conditionMap[cond.key] = cond;

    const btn = document.createElement('button');

    btn.className = 'tag-btn';

    btn.dataset.key = cond.key;

    btn.style.animationDelay = `${i * 40}ms`;

    btn.innerHTML = `
      <span class="tag-emoji">${cond.emoji}</span>
      ${cond.label}
    `;

    btn.onclick = () => toggleTag(cond.key, btn);

    grid.appendChild(btn);
  });
}

function toggleTag(key, btn) {

  if (selectedTags.has(key)) {

    selectedTags.delete(key);

    btn.classList.remove('active');

  } else {

    selectedTags.add(key);

    btn.classList.add('active');
  }

  updateSelectedBar();
}

function updateSelectedBar() {

  const bar = document.getElementById('selectedBar');
  const chips = document.getElementById('selectedChips');

  if (selectedTags.size === 0) {

    bar.classList.add('hidden');

    return;
  }

  bar.classList.remove('hidden');

  chips.innerHTML = '';

  selectedTags.forEach(key => {

    const condition = conditionMap[key];

    const chip = document.createElement('span');

    chip.className = 'selected-chip';

    chip.innerHTML = `
      ${condition.emoji} ${condition.label}
      <span
        class="chip-remove"
        onclick="removeTag('${key}')"
      >
        ✕
      </span>
    `;

    chips.appendChild(chip);
  });
}

function removeTag(key) {

  selectedTags.delete(key);

  const btn = document.querySelector(
    `.tag-btn[data-key="${key}"]`
  );

  if (btn) {
    btn.classList.remove('active');
  }

  updateSelectedBar();
}

function clearAll() {

  selectedTags.clear();

  document
    .querySelectorAll('.tag-btn')
    .forEach(btn => btn.classList.remove('active'));

  updateSelectedBar();
}

function getSelectedConditions() {

  return Array.from(selectedTags);

  // 결과:
  // ["spicy", "meal", "no_seafood"]
}

function applyPreset(tags) {

  clearAll();

  tags.forEach(key => {

    selectedTags.add(key);

    const btn = document.querySelector(
      `.tag-btn[data-key="${key}"]`
    );

    if (btn) {
      btn.classList.add('active');
    }
  });

  updateSelectedBar();
}
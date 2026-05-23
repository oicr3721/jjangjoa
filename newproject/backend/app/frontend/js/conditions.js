// 태그 이모지 매핑
const TAG_EMOJI = {

  // 맵기
  "안 매운 음식": "🥛",
  "매운 음식": "🌶️",

  // 해산물
  "해산물 제외": "🚫🦑",
  "해산물": "🦞",

  // 날 것
  "날 것 제외": "🔥",
  "날 것": "🍣",

  // 식사 유형
  "식사류": "🍚",
  "간식": "🍰",

  // 든든함
  "든든한 음식": "💪",
  "가벼운 음식": "🥗",

  // 혼밥 / 모임
  "혼밥 가능": "🧍",
  "단체 모임": "👥",

  // 면
  "면 제외": "🚫🍜",
  "면 요리": "🍜",

  // 분위기
  "데이트": "💑",
  "조용한 분위기": "🌙",
  "술자리": "🍻"
};

let selectedTags = new Set();

function initTagGrid(conditions) {
  const grid = document.getElementById('tagGrid');
  grid.innerHTML = '';

  conditions.forEach((cond, i) => {
    const btn = document.createElement('button');
    btn.className = 'tag-btn';
    btn.dataset.cond = cond;
    btn.style.animationDelay = `${i * 40}ms`;
    const emoji = TAG_EMOJI[cond] || '🍴';
    btn.innerHTML = `<span class="tag-emoji">${emoji}</span>${cond}`;
    btn.onclick = () => toggleTag(cond, btn);
    grid.appendChild(btn);
  });
}

function toggleTag(cond, btn) {
  if (selectedTags.has(cond)) {
    selectedTags.delete(cond);
    btn.classList.remove('active');
  } else {
    selectedTags.add(cond);
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
  selectedTags.forEach(cond => {
    const chip = document.createElement('span');
    chip.className = 'selected-chip';
    chip.innerHTML = `${cond}<span class="chip-remove" onclick="removeTag('${cond}')">✕</span>`;
    chips.appendChild(chip);
  });
}

function removeTag(cond) {
  selectedTags.delete(cond);
  const btn = document.querySelector(`.tag-btn[data-cond="${cond}"]`);
  if (btn) btn.classList.remove('active');
  updateSelectedBar();
}

function clearAll() {
  selectedTags.clear();
  document.querySelectorAll('.tag-btn').forEach(b => b.classList.remove('active'));
  updateSelectedBar();
}

function getSelectedConditions() {
  return Array.from(selectedTags);
}

function applyPreset(tags) {
  clearAll();
  tags.forEach(tag => {
    selectedTags.add(tag);
    const btn = document.querySelector(`.tag-btn[data-cond="${tag}"]`);
    if (btn) btn.classList.add('active');
  });
  updateSelectedBar();
}

let presets = [];
let presetPanelOpen = false;

function buildPresetLabel(tags) {

  return tags
    .map(tag => {

      const condition = conditionMap[tag];

      if (!condition) {
        return tag;
      }

      return `${condition.emoji} ${condition.label}`;
    })
    .join(' · ');
}

function loadPresets() {

  try {

    const saved = localStorage.getItem(
      'foodfinder_presets'
    );

    presets = saved
      ? JSON.parse(saved)
      : [];

    // 기존 데이터도 자동 변환
    presets.forEach(p => {
      p.label = buildPresetLabel(p.tags);
    });

  } catch (e) {

    console.error(e);

    presets = [];
  }

  renderPresetList();
}

function saveCurrentAsPreset() {

  const tags = getSelectedConditions();

  if (tags.length === 0) {

    showToast('조건을 먼저 선택해주세요');

    return;
  }

  const key = [...tags]
    .sort()
    .join('|');

  const exists = presets.some(
    p => [...p.tags]
      .sort()
      .join('|') === key
  );

  if (exists) {

    showToast('이미 저장된 조합입니다');

    return;
  }

  const preset = {

    id: Date.now(),

    tags: [...tags],

    label: buildPresetLabel(tags)
  };

  presets.push(preset);

  localStorage.setItem(
    'foodfinder_presets',
    JSON.stringify(presets)
  );

  renderPresetList();

  showToast('프리셋이 저장되었습니다 ✓');
}

function deletePreset(id) {

  presets = presets.filter(
    p => p.id !== id
  );

  localStorage.setItem(
    'foodfinder_presets',
    JSON.stringify(presets)
  );

  renderPresetList();
}

function togglePresetPanel() {

  presetPanelOpen = !presetPanelOpen;

  const panel = document.getElementById(
    'presetPanel'
  );

  panel.classList.toggle(
    'hidden',
    !presetPanelOpen
  );
}

function renderPresetList() {

  const list = document.getElementById(
    'presetList'
  );

  const empty = document.getElementById(
    'presetEmpty'
  );

  list.innerHTML = '';

  if (presets.length === 0) {

    empty.classList.remove('hidden');

    return;
  }

  empty.classList.add('hidden');

  presets.forEach(p => {

    const item = document.createElement('div');

    item.className = 'preset-item';

    item.innerHTML = `
      <span class="preset-item-name">
        ${p.label}
      </span>

      <span
        class="preset-item-del"
        onclick="deletePreset(${p.id})"
      >
        ✕
      </span>
    `;

    item.querySelector(
      '.preset-item-name'
    ).onclick = () => applyPreset(p.tags);

    list.appendChild(item);
  });
}
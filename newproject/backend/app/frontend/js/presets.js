let presets = [];
let presetPanelOpen = false;

function loadPresets() {
  try {
    const saved = localStorage.getItem('foodfinder_presets');
    presets = saved ? JSON.parse(saved) : [];
  } catch (e) {
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

  // 동일한 조합이 이미 있는지 확인
  const key = [...tags].sort().join('|');
  const exists = presets.some(p => [...p.tags].sort().join('|') === key);
  if (exists) {
    showToast('이미 저장된 조합입니다');
    return;
  }

  const preset = {
    id: Date.now(),
    label: tags.join(', '),
    tags: tags
  };
  presets.push(preset);
  localStorage.setItem('foodfinder_presets', JSON.stringify(presets));
  renderPresetList();
  showToast('프리셋이 저장되었습니다 ✓');
}

function deletePreset(id) {
  presets = presets.filter(p => p.id !== id);
  localStorage.setItem('foodfinder_presets', JSON.stringify(presets));
  renderPresetList();
}

function togglePresetPanel() {
  presetPanelOpen = !presetPanelOpen;
  const panel = document.getElementById('presetPanel');
  panel.classList.toggle('hidden', !presetPanelOpen);
}

function renderPresetList() {
  const list = document.getElementById('presetList');
  const empty = document.getElementById('presetEmpty');
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
      <span onclick="applyPreset(${JSON.stringify(p.tags).replace(/"/g, '&quot;')})">${p.label}</span>
      <span class="preset-item-del" onclick="deletePreset(${p.id})">✕</span>
    `;
    list.appendChild(item);
  });
}

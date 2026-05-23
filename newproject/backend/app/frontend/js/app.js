window._restaurants = [];
window._allKeywords = [];   // 추천 결과 전체 키워드 풀
window._activeKeywords = new Set(); // 현재 필터 중인 키워드

window.onload = async function () {
  loadPresets();

  try {
    const res = await fetch('/conditions');
    const data = await res.json();
    initTagGrid(data.conditions);
  } catch (e) {
    console.error('조건 로드 실패:', e);
  }

  getCurrentLocation().catch(() => {});
};

// ── 검색 시작 ──────────────────────────────────────────────────────
async function startSearch() {
  if (currentLatitude === null || currentLongitude === null) {
    showToast('위치 정보를 아직 가져오지 못했습니다');
    return;
  }

  const conditions = getSelectedConditions();
  const freeText = (document.getElementById('freeTextInput')?.value || '').trim();

  showScreen('screen-results');
  showLoading(true);

  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));

  try { initMap(currentLatitude, currentLongitude); }
  catch (e) { console.warn('지도 초기화 실패:', e); }

  try {
    console.log('추천 요청:', { conditions, freeText, lat: currentLatitude, lng: currentLongitude });
    const data = await requestRecommendations(conditions, currentLatitude, currentLongitude, freeText);
    console.log('응답:', data);

    window._restaurants = data.restaurants || [];

    // 키워드 풀 초기화: 전체 선택
    const kwSet = new Set();
    window._restaurants.forEach(r => (r.matched_keywords || []).forEach(k => kwSet.add(k)));
    window._allKeywords = [...kwSet].sort();
    window._activeKeywords = new Set(window._allKeywords);

    renderKeywordFilter();
    renderRestaurants(getFilteredRestaurants());

    try { placeMarkers(window._restaurants); }
    catch (e) { console.warn('마커 표시 실패:', e); }

    document.getElementById('resultCount').textContent = `${window._restaurants.length}곳 발견`;
  } catch (e) {
    console.error('추천 요청 실패:', e);
    renderError(e.message);
  } finally {
    showLoading(false);
  }
}

// ── 키워드 필터 렌더 ───────────────────────────────────────────────
function renderKeywordFilter() {
  const bar = document.getElementById('keywordFilterBar');
  if (!bar) return;

  if (window._allKeywords.length === 0) {
    bar.innerHTML = '';
    bar.classList.add('hidden');
    return;
  }
  bar.classList.remove('hidden');

  const chips = window._allKeywords.map(kw => {
    const active = window._activeKeywords.has(kw);
    return `<button class="kw-chip ${active ? 'active' : ''}" onclick="toggleKeyword('${kw}')">${kw}</button>`;
  }).join('');

  bar.innerHTML = `
    <div class="kw-filter-inner">
      <span class="kw-filter-label">키워드 필터</span>
      <div class="kw-chips">${chips}</div>
      <button class="kw-all-btn" onclick="selectAllKeywords()">전체</button>
      <button class="kw-none-btn" onclick="clearAllKeywords()">해제</button>
    </div>`;
}

function toggleKeyword(kw) {
  if (window._activeKeywords.has(kw)) window._activeKeywords.delete(kw);
  else window._activeKeywords.add(kw);
  renderKeywordFilter();
  renderRestaurants(getFilteredRestaurants());
}

function selectAllKeywords() {
  window._activeKeywords = new Set(window._allKeywords);
  renderKeywordFilter();
  renderRestaurants(getFilteredRestaurants());
}

function clearAllKeywords() {
  window._activeKeywords.clear();
  renderKeywordFilter();
  renderRestaurants(getFilteredRestaurants());
}

function getFilteredRestaurants() {
  if (window._activeKeywords.size === 0) return [];
  return window._restaurants.filter(r =>
    (r.matched_keywords || []).some(k => window._activeKeywords.has(k))
  );
}

// ── 식당 카드 렌더 ─────────────────────────────────────────────────
function renderRestaurants(restaurants) {
  const list = document.getElementById('results');
  list.innerHTML = '';

  if (restaurants.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <p class="empty-state-title">근처에서 찾지 못했어요</p>
        <p class="empty-state-sub">조건을 바꾸거나 다른 위치에서 시도해보세요</p>
      </div>`;
    return;
  }

  restaurants.forEach((r, i) => {
    // 실제 인덱스 (필터 전 전체 배열 기준 — 마커 연동용)
    const globalIdx = window._restaurants.indexOf(r);
    const card = document.createElement('div');
    card.className = 'restaurant-card';
    card.style.animationDelay = `${i * 45}ms`;
    card.onclick = () => {
      highlightMarker(globalIdx);
      document.querySelectorAll('.restaurant-card').forEach((el, j) => {
        el.classList.toggle('highlighted', j === i);
      });
    };

    const distText = r.distance_m >= 1000
      ? `${(r.distance_m / 1000).toFixed(1)}km`
      : `${r.distance_m}m`;

    const keywords = (r.matched_keywords || [])
      .map(k => `<span class="keyword-chip">${k}</span>`).join('');

    const categoryShort = (r.category || '').split('>').pop().trim();

    // 이미지: 음식 카테고리 기반 이모지 아이콘
    const emoji = _getCategoryEmoji(r.category, r.matched_keywords);

    card.innerHTML = `
      <div class="card-img-wrap">
        <div class="card-img-emoji">${emoji}</div>
      </div>
      <div class="card-body">
        <div class="card-header">
          <span class="card-name">${r.name}</span>
          <span class="card-score">★ ${r.score}</span>
        </div>
        <p class="card-address">${r.address || '주소 정보 없음'}</p>
        <div class="card-meta">
          <span class="card-distance">📍 ${distText}</span>
          ${categoryShort ? `<span class="card-category">${categoryShort}</span>` : ''}
        </div>
        ${keywords ? `<div class="card-keywords">${keywords}</div>` : ''}
      </div>`;
    list.appendChild(card);
  });
}

function _getCategoryEmoji(category, keywords) {
  const cat = (category || '').toLowerCase();
  const kws = (keywords || []).join(' ');
  const text = cat + ' ' + kws;

  if (/초밥|스시|회|사시미/.test(text)) return '🍣';
  if (/라멘|우동|칼국수|냉면|국수/.test(text)) return '🍜';
  if (/피자/.test(text)) return '🍕';
  if (/햄버거|버거/.test(text)) return '🍔';
  if (/삼겹살|고기|갈비|돼지/.test(text)) return '🥩';
  if (/치킨|닭/.test(text)) return '🍗';
  if (/카레/.test(text)) return '🍛';
  if (/파스타|이탈리안/.test(text)) return '🍝';
  if (/국밥|탕|찌개|설렁탕|곰탕/.test(text)) return '🍲';
  if (/덮밥|볶음밥|비빔밥/.test(text)) return '🍚';
  if (/샐러드|브런치/.test(text)) return '🥗';
  if (/카페|디저트/.test(text)) return '☕';
  if (/떡볶이|분식/.test(text)) return '🌶️';
  if (/중식|짜장|짬뽕|마라/.test(text)) return '🥢';
  return '🍽️';
}

function renderError(msg) {
  document.getElementById('results').innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">⚠️</div>
      <p class="empty-state-title">오류가 발생했습니다</p>
      <p class="empty-state-sub">${msg || '잠시 후 다시 시도해주세요'}</p>
    </div>`;
}

// ── 화면 전환 ──────────────────────────────────────────────────────
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.remove('active');
    s.style.display = 'none';
  });
  const target = document.getElementById(id);
  target.style.display = 'flex';
  target.classList.add('active');
}

function goBack() {
  showScreen('screen-tags');
  kakaoMap = null;
}

function showLoading(show) {
  document.getElementById('loadingOverlay').classList.toggle('hidden', !show);
}

let toastTimer = null;
function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add('hidden'), 2500);
}

window._restaurants = [];   // 원본 데이터 (서버에서 받은 그대로)
let _sortMode = 'score';    // 현재 정렬 모드
window._allKeywords = [];
window._activeKeywords = new Set();

// ──────────────────────────────────────────────────────────────────────────
// 카테고리별 이모지 (사진 로드 실패 시 폴백용)
// ──────────────────────────────────────────────────────────────────────────
const CATEGORY_EMOJI = {
  '한식': '🍚', '중식': '🥡', '일식': '🍣', '양식': '🍝',
  '치킨': '🍗', '피자': '🍕', '햄버거': '🍔', '분식': '🥢',
  '패스트푸드': '🍔', '카페': '☕', '베이커리': '🥐', '디저트': '🍰',
  '삼겹살': '🥩', '곱창': '🫀', '족발': '🦶', '보쌈': '🥬',
  '국밥': '🍲', '순대': '🌭', '떡볶이': '🌶️', '냉면': '🍜',
  '라면': '🍜', '초밥': '🍣', '회': '🐟', '짜장면': '🥢',
  '짬뽕': '🍜', '탕수육': '🥩', '스테이크': '🥩', '파스타': '🍝',
  '샐러드': '🥗', '샌드위치': '🥙', '브런치': '🥞',
};

function getCategoryEmoji(category) {
  if (!category) return '🍴';
  for (const [key, emoji] of Object.entries(CATEGORY_EMOJI)) {
    if (category.includes(key)) return emoji;
  }
  return '🍴';
}

// ──────────────────────────────────────────────────────────────────────────
// 초기화
// ──────────────────────────────────────────────────────────────────────────
window.onload = async function () {

  try {

    const res = await fetch('/conditions');
    const conditions = await res.json();

    initTagGrid(conditions);

    // conditionMap 만들어진 뒤
    loadPresets();

  } catch (e) {

    console.error('조건 로드 실패:', e);
  }

  getCurrentLocation().catch(() => {});
};

// ──────────────────────────────────────────────────────────────────────────
// 검색 시작
// ──────────────────────────────────────────────────────────────────────────
async function startSearch() {
  if (currentLatitude === null || currentLongitude === null) {
    showToast('위치 정보를 아직 가져오지 못했습니다');
    return;
  }

  const conditions = getSelectedConditions();
  const freeText = (document.getElementById('freeTextInput')?.value || '').trim();

  showScreen('screen-results');
  showLoading(true);

  // 정렬 초기화
  _sortMode = 'score';
  setSortButtonActive('score');

  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));

  try {
    initMap(currentLatitude, currentLongitude);
  } catch (e) {
    console.warn('지도 초기화 실패:', e);
  }

  try {
    const data = await requestRecommendations(
      conditions, currentLatitude, currentLongitude, freeText
    );

    window._restaurants = data.restaurants || [];

    // 키워드 풀 생성
    const kwSet = new Set();
    window._restaurants.forEach(r => {

      Object.keys(
        r.menus || {}
      ).forEach(k => kwSet.add(k));

    });

    window._allKeywords = [...kwSet].sort();
    window._activeKeywords = new Set(window._allKeywords);

    renderKeywordFilter();

    const filtered = getFilteredRestaurants();
    renderRestaurants(getSortedRestaurants(filtered, _sortMode));

    // 정렬 바 + 키워드 필터 표시
    const sortBar = document.getElementById('sortBar');
    if (sortBar) sortBar.classList.toggle('hidden', window._restaurants.length === 0);

    try { placeMarkers(window._restaurants); } catch (e) { /* ignore */ }

    document.getElementById('resultCount').textContent =
      `${window._restaurants.length}곳 발견`;
  } catch (e) {
    console.error('추천 요청 실패:', e);
    renderError(e.message);
  } finally {
    showLoading(false);
  }
}

// ──────────────────────────────────────────────────────────────────────────
// 정렬
// ──────────────────────────────────────────────────────────────────────────
function setSortMode(mode) {
  _sortMode = mode;
  setSortButtonActive(mode);

  const filtered = getFilteredRestaurants();
  const sorted = getSortedRestaurants(filtered, mode);

  renderRestaurants(sorted);

  try {
    placeMarkers(sorted);
  } catch (e) {}
}

function setSortButtonActive(mode) {
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.sort === mode);
  });
}

function getSortedRestaurants(list, mode) {
  const copy = [...list];
  switch (mode) {
    case 'score':
      return copy.sort((a, b) => b.score - a.score);
    case 'distance':
      return copy.sort((a, b) => a.distance_m - b.distance_m);
    case 'keyword':
      return copy.sort(
        (a, b) =>
          getFilteredMenuCount(b)
          - getFilteredMenuCount(a)
      );
    case 'review':
      return copy.sort((a, b) => {
        const ra = a.review_score ?? -1;
        const rb = b.review_score ?? -1;
        return rb - ra;
      });
    default:
      return copy;
  }
}

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

    return `
      <button
        class="kw-chip ${active ? 'active' : ''}"
        onclick="toggleKeyword('${kw}')">
        ${kw}
      </button>`;
  }).join('');

  bar.innerHTML = `
    <div class="kw-filter-inner">
      <span class="kw-filter-label">키워드 필터</span>

      <div class="kw-chips">
        ${chips}
      </div>

      <button class="kw-all-btn" onclick="selectAllKeywords()">전체</button>
      <button class="kw-none-btn" onclick="clearAllKeywords()">해제</button>
    </div>
  `;
}

function toggleKeyword(kw) {
  if (window._activeKeywords.has(kw))
    window._activeKeywords.delete(kw);
  else
    window._activeKeywords.add(kw);

  updateKeywordFiltering();
}

function selectAllKeywords() {
  window._activeKeywords = new Set(window._allKeywords);
  updateKeywordFiltering();
}

function clearAllKeywords() {
  window._activeKeywords.clear();
  updateKeywordFiltering();
}

function getFilteredRestaurants() {

  if (window._activeKeywords.size === 0)
    return [];

  return window._restaurants.filter(r => {

    const menus = r.menus || {};

    return [...window._activeKeywords]
      .some(keyword => menus[keyword]);
  });
}

function getFilteredMenuCount(restaurant) {

  const menus = getVisibleMenus(restaurant);

  return Object.values(menus)
    .reduce(
      (sum, arr) => sum + arr.length,
      0
    );
}

function updateKeywordFiltering() {
  renderKeywordFilter();

  const filtered = getFilteredRestaurants();
  const sorted = getSortedRestaurants(filtered, _sortMode);

  renderRestaurants(sorted);

  try {
    placeMarkers(sorted);
  } catch (e) {}

  document.getElementById('resultCount').textContent =
    `${filtered.length}곳 발견`;
}

// ──────────────────────────────────────────────────────────────────────────
// 렌더링
// ──────────────────────────────────────────────────────────────────────────
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
    const card = document.createElement('div');
    card.className = 'restaurant-card';
    card.style.animationDelay = `${i * 40}ms`;
    card.onclick = () => {
      // 원본 인덱스를 찾아서 마커 하이라이트
      const origIdx = window._restaurants.indexOf(r);
      if (origIdx !== -1) highlightMarker(origIdx);
      document.querySelectorAll('.restaurant-card').forEach((el, j) => {
        el.classList.toggle('highlighted', j === i);
      });
    };

    const distText = r.distance_m >= 1000
      ? `${(r.distance_m / 1000).toFixed(1)}km`
      : `${r.distance_m}m`;

    const visibleMenus = getVisibleMenus(r);

    const menuHtml = Object.entries(visibleMenus)
      .flatMap(([_, items]) =>
        items.map(menu =>
          `<span class="keyword-chip">${menu.name}</span>`
        )
      )
      .join('');

    const categoryShort = (r.category || '').split('>').pop().trim();

    // 리뷰 점수 렌더링
    const reviewHtml = (r.review_score != null)
      ? `<span class="card-review">⭐ ${Number(r.review_score).toFixed(1)}</span>`
      : `<span class="card-review no-review">리뷰 없음</span>`;

    // 사진 영역 – 이미지 있으면 img, 없으면 이모지
    const emoji = getCategoryEmoji(r.category);
    const imgHtml = r.image_url
      ? `<img
            class="card-thumb"
            src="${r.image_url}"
            alt="${r.name}"
            loading="lazy"
            onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"
          >
          <div class="card-thumb-fallback" style="display:none">${emoji}</div>`
      : `<div class="card-thumb-fallback">${emoji}</div>`;

    // 카카오맵 링크
    const linkHtml = r.place_url
      ? `<a class="card-kakao-link" href="${r.place_url}" target="_blank" rel="noopener noreferrer">
           카카오맵 보기 ↗
         </a>`
      : '';
    
    const openHtml = r.is_open
      ? `
        <span class="card-open open">
          🟢 ${r.open_status}
          ${r.open_hours_info ? `(${r.open_hours_info})` : ''}
        </span>
      `
      : `
        <span class="card-open closed">
          🔴 ${r.open_status || '영업 종료'}
          ${r.open_hours_info ? `(${r.open_hours_info})` : ''}
        </span>
      `;

    const priceHtml = r.average_price
      ? `
        <div class="card-price">
          💰 ${r.price_level}
          · 평균 ${Number(r.average_price).toLocaleString()}원
          <br>
          <small>${r.price_range}</small>
        </div>
      `
      : `
        <div class="card-price no-price">
          💰 가격 정보 없음
        </div>
      `;

    card.innerHTML = `
      <div class="card-left">
        <div class="card-thumb-wrap">${imgHtml}</div>
      </div>
      <div class="card-right">
        <div class="card-header">
          <span class="card-name">${r.name}</span>
          <span class="card-score">✨ ${r.score}</span>
        </div>
        <p class="card-address">${r.address || '주소 정보 없음'}</p>
        <div class="card-meta">
          <span class="card-distance">📍 ${distText}</span>
          ${categoryShort ? `<span class="card-category">${categoryShort}</span>` : ''}
          ${reviewHtml}
          ${openHtml}
        </div>
        ${menuHtml
          ? `<div class="card-keywords">${menuHtml}</div>`
          : ''}
        ${priceHtml}
        ${linkHtml}
      </div>
    `;
    list.appendChild(card);
  });
}

function renderError(msg) {
  document.getElementById('results').innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">⚠️</div>
      <p class="empty-state-title">오류가 발생했습니다</p>
      <p class="empty-state-sub">${msg || '잠시 후 다시 시도해주세요'}</p>
    </div>`;
}

// ──────────────────────────────────────────────────────────────────────────
// 화면 전환 / 유틸
// ──────────────────────────────────────────────────────────────────────────
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
  document.getElementById('sortBar')?.classList.add('hidden');
  document.getElementById('keywordFilterBar')?.classList.add('hidden');
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

function getVisibleMenus(restaurant) {

  const result = {};

  for (const keyword of window._activeKeywords) {

    if (restaurant.menus?.[keyword]) {
      result[keyword] = restaurant.menus[keyword];
    }
  }

  return result;
}
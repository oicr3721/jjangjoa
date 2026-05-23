let kakaoMap = null;
let markers = [];
let userMarker = null;
let highlightOverlay = null;

function initMap(lat, lng) {
  const container = document.getElementById('map');
  const center = new kakao.maps.LatLng(lat, lng);
  kakaoMap = new kakao.maps.Map(container, { center, level: 4 });
  _placeUserDot(center);
}

function _placeUserDot(pos) {
  if (userMarker) userMarker.setMap(null);
  userMarker = new kakao.maps.CustomOverlay({
    position: pos,
    content: '<div class="blue-dot"></div>',
    xAnchor: 0.5,
    yAnchor: 0.5
  });
  userMarker.setMap(kakaoMap);
}

function placeMarkers(restaurants) {
  markers.forEach(m => m.setMap(null));
  markers = [];

  restaurants.forEach((r, i) => {
    const pos = new kakao.maps.LatLng(r.latitude, r.longitude);
    const marker = new kakao.maps.Marker({ map: kakaoMap, position: pos, title: r.name });
    markers.push(marker);

    kakao.maps.event.addListener(marker, 'click', () => {
      // 마커 클릭 → 카드 강조 + overlay 업데이트
      _showHighlightOverlay(pos);
      highlightCard(i);
      kakaoMap.panTo(pos);
    });
  });
}

function highlightMarker(index) {
  const r = window._restaurants && window._restaurants[index];
  if (!r || !kakaoMap) return;
  const pos = new kakao.maps.LatLng(r.latitude, r.longitude);
  _showHighlightOverlay(pos);
  kakaoMap.panTo(pos);
}

// ── overlay 위치 버그 수정 ──────────────────────────────────────────
// xAnchor: 0.5, yAnchor: 0.5 → 콘텐츠 div의 중앙이 좌표에 정확히 위치
// CSS에서 transform 이중 적용 제거
function _showHighlightOverlay(pos) {
  if (highlightOverlay) highlightOverlay.setMap(null);
  highlightOverlay = new kakao.maps.CustomOverlay({
    position: pos,
    content: `<div class="highlight-marker"><div class="pulse"></div><div class="core"></div></div>`,
    xAnchor: 0.5,
    yAnchor: 0.5,
    zIndex: 3
  });
  highlightOverlay.setMap(kakaoMap);
}

function highlightCard(index) {
  document.querySelectorAll('.restaurant-card').forEach((el, i) => {
    el.classList.toggle('highlighted', i === index);
  });
  const card = document.querySelectorAll('.restaurant-card')[index];
  if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

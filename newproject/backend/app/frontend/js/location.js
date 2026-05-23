let currentLatitude = null;
let currentLongitude = null;

function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    const dot = document.querySelector('.location-dot');
    const text = document.getElementById('locationText');

    if (!navigator.geolocation) {
      if (text) text.textContent = '위치 정보 미지원 브라우저';
      if (dot) dot.className = 'location-dot error';
      reject(new Error('geolocation not supported'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        currentLatitude = position.coords.latitude;
        currentLongitude = position.coords.longitude;
        if (text) text.textContent = `${currentLatitude.toFixed(4)}, ${currentLongitude.toFixed(4)}`;
        if (dot) dot.className = 'location-dot active';
        resolve({ lat: currentLatitude, lng: currentLongitude });
      },
      (error) => {
        if (text) text.textContent = '위치를 가져올 수 없습니다';
        if (dot) dot.className = 'location-dot error';
        reject(error);
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  });
}

function refreshLocation() {
  const dot = document.querySelector('.location-dot');
  const text = document.getElementById('locationText');
  if (dot) dot.className = 'location-dot';
  if (text) text.textContent = '위치 새로고침 중…';
  getCurrentLocation().catch(() => {});
}

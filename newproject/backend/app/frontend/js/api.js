async function requestRecommendations(conditions, latitude, longitude, freeText = "") {
  const response = await fetch('/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conditions, latitude, longitude, free_text: freeText })
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

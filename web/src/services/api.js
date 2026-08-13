const API_BASE = 'http://localhost:5000/api';

export async function fetchStats(date = '') {
  try {
    const res = await fetch(`${API_BASE}/stats${date ? `?date=${date}` : ''}`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Backend API offline, using fallback stats');
  }
  return null;
}

export async function fetchPersons() {
  try {
    const res = await fetch(`${API_BASE}/persons`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Backend API offline, using fallback persons');
  }
  return null;
}

export async function addPersonApi(personData) {
  try {
    const res = await fetch(`${API_BASE}/persons`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(personData),
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error('Error adding person API:', e);
  }
  return { success: false };
}

export async function deletePersonApi(personId) {
  try {
    const res = await fetch(`${API_BASE}/persons/${personId}`, {
      method: 'DELETE',
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error('Error deleting person API:', e);
  }
  return { success: false };
}

export async function fetchLogs(date = '', search = '') {
  try {
    const url = new URL(`${API_BASE}/logs`);
    if (date) url.searchParams.append('date', date);
    if (search) url.searchParams.append('search', search);
    const res = await fetch(url);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Backend API offline, using fallback logs');
  }
  return null;
}

export async function deleteLogApi(logId) {
  try {
    const res = await fetch(`${API_BASE}/logs/${logId}`, {
      method: 'DELETE',
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error('Error deleting log API:', e);
  }
  return { success: false };
}

export async function clearLogsApi(date = '') {
  try {
    const res = await fetch(`${API_BASE}/logs/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date }),
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error('Error clearing logs API:', e);
  }
  return { success: false };
}

export async function recognizeFrameApi(base64Image) {
  try {
    const res = await fetch(`${API_BASE}/recognize-frame`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Image }),
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error('Frame recognition error:', e);
  }
  return { faces: [] };
}

export async function markAttendanceApi(personId, confidence = 95) {
  try {
    const res = await fetch(`${API_BASE}/mark-attendance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ person_id: personId, confidence }),
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error('Mark attendance API error:', e);
  }
  return { success: false, message: 'Unable to mark attendance' };
}

export async function enrollSampleApi(personId, base64Image, sampleIdx) {
  try {
    const res = await fetch(`${API_BASE}/enroll-sample`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ person_id: personId, image: base64Image, sample_idx: sampleIdx }),
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error('Enroll sample API error:', e);
  }
  return { success: false };
}

export async function trainModelApi() {
  try {
    const res = await fetch(`${API_BASE}/train`, {
      method: 'POST',
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.error('Train model API error:', e);
  }
  return { success: false };
}

export function getExportUrl(format, date = '') {
  return `${API_BASE}/export/${format}${date ? `?date=${date}` : ''}`;
}

/**
 * 后端 API 服务封装
 */
// 智能选择后端：本地用 localhost，公网用隧道
function getApiBase() {
  if (import.meta?.env?.VITE_API_BASE) return import.meta.env.VITE_API_BASE;
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host.startsWith('192.168.') || host.startsWith('172.')) {
    return 'http://localhost:8000';  // 本地直连，0延迟
  }
  return 'https://few-satisfactory-seating-equation.trycloudflare.com';  // 公网隧道
}
const API_BASE = getApiBase();

// Token 管理
function getToken() {
  return localStorage.getItem('disease_token');
}
function setToken(t) {
  localStorage.setItem('disease_token', t);
}
function clearToken() {
  localStorage.removeItem('disease_token');
  localStorage.removeItem('disease_user');
}

// 通用请求
async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { ...options.headers };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    const res = await fetch(url, { ...options, headers, signal: controller.signal });
    clearTimeout(timeout);
    const data = await res.json();
    if (!res.ok) {
      const msg = data.detail || `服务器错误 (${res.status})`;
      throw new Error(msg);
    }
    return data;
  } catch (e) {
    if (e.name === 'AbortError') {
      throw new Error('请求超时，请检查网络连接');
    }
    if (e.message.includes('Failed to fetch') || e.message.includes('NetworkError')) {
      throw new Error('无法连接服务器，请确认后端已启动');
    }
    throw e;
  }
}

export default {
  // ========== 认证 ==========
  async register(username, email, password) {
    const data = await request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
    setToken(data.access_token);
    localStorage.setItem('disease_user', JSON.stringify({ username: data.username }));
    return data;
  },
  async login(username, password) {
    const data = await request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    setToken(data.access_token);
    localStorage.setItem('disease_user', JSON.stringify({ username: data.username }));
    return data;
  },
  logout() {
    clearToken();
  },
  isLoggedIn() {
    return !!getToken();
  },
  getUser() {
    const u = localStorage.getItem('disease_user');
    return u ? JSON.parse(u) : null;
  },
  async fetchUserInfo() {
    return await request('/api/auth/me');
  },

  // ========== 诊断 ==========
  async predict(imageFile, enableGradcam = false) {
    const form = new FormData();
    form.append('image', imageFile);
    return await request(`/api/predict?enable_gradcam=${enableGradcam}`, {
      method: 'POST',
      body: form,
    });
  },
  async predictBatch(files) {
    const form = new FormData();
    files.forEach(f => form.append('images', f));
    return await request('/api/predict/batch', { method: 'POST', body: form });
  },

  // ========== 历史 ==========
  async getHistory(skip = 0, limit = 20) {
    return await request(`/api/auth/history?skip=${skip}&limit=${limit}`);
  },

  // ========== 反馈 ==========
  async submitFeedback(category, title, content) {
    return await request('/api/feedback', {
      method: 'POST',
      body: JSON.stringify({ category, title, content }),
    });
  },
  async getMyFeedbacks() {
    return await request('/api/feedback/my');
  },

  // ========== 纠错 ==========
  async correctPrediction(diagnosisId, originalPred, correctedLabel) {
    return await request('/api/correct', {
      method: 'POST',
      body: JSON.stringify({
        diagnosis_id: diagnosisId,
        original_prediction: originalPred,
        corrected_label: correctedLabel,
      }),
    });
  },

  // ========== 导出 ==========
  async exportExcel() {
    const token = getToken();
    const res = await fetch(`${API_BASE}/api/export/excel`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('导出失败');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '叶片病害诊断记录.xlsx';
    a.click();
    URL.revokeObjectURL(url);
  },

  // ========== 个人中心 ==========
  async getProfile() {
    return await request('/api/auth/profile');
  },
  async updateProfile(username, avatarBase64) {
    return await request('/api/auth/profile', {
      method: 'PUT',
      body: JSON.stringify({ username: username || '', avatar_base64: avatarBase64 || '' }),
    });
  },
  async changePassword(oldPwd, newPwd) {
    return await request('/api/auth/password', {
      method: 'PUT',
      body: JSON.stringify({ old_password: oldPwd, new_password: newPwd }),
    });
  },
  async resetPassword(username, email, newPassword) {
    // 两步：先验证身份，再重置
    await request('/api/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ username, email }),
    });
    return await request('/api/auth/reset-password', {
      method: 'PUT',
      body: JSON.stringify({ username, email, new_password: newPassword }),
    });
  },
  async uploadAvatar(file) {
    const form = new FormData();
    form.append('image', file);
    return await request('/api/auth/avatar', {
      method: 'POST',
      body: form,
    });
  },

  // ========== 公共留言板 ==========
  async getGuestbookMessages(skip = 0) {
    return await request('/api/guestbook?skip=' + skip + '&limit=50');
  },
  async postGuestbookMessage(nickname, content) {
    return await request('/api/guestbook', {
      method: 'POST',
      body: JSON.stringify({ nickname, content }),
    });
  },

  // ========== 健康检查 ==========
  async healthCheck() {
    return await request('/api/health');
  },

  API_BASE,
};

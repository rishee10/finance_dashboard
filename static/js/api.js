/* =============================================================
   api.js — Shared API client, auth helpers, toast, sidebar
   Used by every page. Load BEFORE page-specific scripts.
   ============================================================= */

// ── Config ─────────────────────────────────────────────────────────────────
const API_BASE = 'http://127.0.0.1:8000/api/v1';

// ── Auth helpers ────────────────────────────────────────────────────────────
const Auth = {
  getToken()  { return localStorage.getItem('access_token'); },
  getUser()   { return JSON.parse(localStorage.getItem('user') || 'null'); },
  setSession(data) {
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
  },
  clear() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
  isLoggedIn()  { return !!this.getToken() && !!this.getUser(); },
  isAdmin()     { return this.getUser()?.role === 'admin'; },
  isAnalyst()   { const r = this.getUser()?.role; return r === 'analyst' || r === 'admin'; },

  // Call this at top of every protected page
  requireAuth() {
    if (!this.isLoggedIn()) { window.location.href = '/'; return false; }
    return true;
  },

  // Redirect logged-in users away from login page
  redirectIfLoggedIn() {
    if (this.isLoggedIn()) { window.location.href = '/dashboard/'; }
  },

  logout() {
    this.clear();
    window.location.href = '/';
  },
};

// ── API client ──────────────────────────────────────────────────────────────
const API = {
  async request(method, path, body = null, params = {}) {
    const url = new URL(API_BASE + path);
    Object.entries(params).forEach(([k, v]) => {
      if (v !== '' && v !== null && v !== undefined) url.searchParams.set(k, v);
    });

    const headers = { 'Content-Type': 'application/json' };
    const token = Auth.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    let res;
    try {
      res = await fetch(url, opts);
    } catch (e) {
      throw { network: true, message: 'Cannot connect to server. Is the backend running?' };
    }

    if (res.status === 401) {
      Auth.logout();
      return null;
    }

    const isJson = res.headers.get('content-type')?.includes('application/json');
    const data = isJson ? await res.json() : {};

    if (!res.ok) throw data;
    return data;
  },

  get(path, params = {})         { return this.request('GET',    path, null,  params); },
  post(path, body = {})          { return this.request('POST',   path, body); },
  patch(path, body = {})         { return this.request('PATCH',  path, body); },
  put(path, body = {})           { return this.request('PUT',    path, body); },
  delete(path)                   { return this.request('DELETE', path); },
};

// ── Toast ───────────────────────────────────────────────────────────────────
function toast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '✓', error: '✕', info: 'i' };
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.innerHTML = `<span class="toast-icon">${icons[type]}</span><span class="toast-msg">${message}</span>`;
  container.appendChild(el);
  setTimeout(() => {
    el.style.transition = 'opacity 0.3s, transform 0.3s';
    el.style.opacity = '0'; el.style.transform = 'translateX(16px)';
    setTimeout(() => el.remove(), 350);
  }, 3200);
}

// ── Format helpers ──────────────────────────────────────────────────────────
function fmtCurrency(n) {
  const num = parseFloat(n) || 0;
  return '₹' + num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
}

function getInitials(name) {
  return (name || '?').charAt(0).toUpperCase();
}

// ── Debounce ────────────────────────────────────────────────────────────────
function debounce(fn, ms = 350) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// ── Sidebar builder ─────────────────────────────────────────────────────────
function buildSidebar(activePage) {
  const user = Auth.getUser();
  if (!user) return;

  const isAdmin   = user.role === 'admin';
  const isAnalyst = user.role === 'analyst' || user.role === 'admin';
  const base      = '/';

  const links = [
    { id:'dashboard', href:'/dashboard/'  },
    { id:'records',   href:'/records/'    },
    { id:'analytics', href:'/analytics/'  },
    { id:'users',     href:'/users/'      },
    { id:'profile',   href:'/profile/'    },
    
  ];

  const navHTML = `
    <div class="nav-label">Main</div>
    ${links.filter(l => l.show && ['dashboard','records','analytics'].includes(l.id)).map(l => `
      <a href="${l.href}" class="nav-link ${activePage === l.id ? 'active' : ''}">
        ${l.icon} ${l.label}
      </a>`).join('')}

    ${isAdmin ? '<div class="nav-label">Admin</div>' : ''}
    ${links.filter(l => l.show && l.id === 'users').map(l => `
      <a href="${l.href}" class="nav-link ${activePage === l.id ? 'active' : ''}">
        ${l.icon} ${l.label}
      </a>`).join('')}

    <div class="nav-label">Account</div>
    ${links.filter(l => l.id === 'profile').map(l => `
      <a href="${l.href}" class="nav-link ${activePage === l.id ? 'active' : ''}">
        ${l.icon} ${l.label}
      </a>`).join('')}
  `;

  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  sidebar.innerHTML = `
    <div class="sidebar-logo">
      <div class="logo-icon">◈</div>
      <div class="logo-name">Finance<span>OS</span></div>
    </div>
    <nav class="sidebar-nav">${navHTML}</nav>
    <div class="sidebar-footer">
      <div class="user-pill" onclick="window.location.href='${base}profile.html'">
        <div class="user-pill-avatar">${getInitials(user.username)}</div>
        <div class="user-pill-info">
          <div class="user-pill-name truncate">${user.username}</div>
          <div class="user-pill-role">${user.role}</div>
        </div>
        <span class="badge badge-${user.role}">${user.role[0].toUpperCase()}</span>
      </div>
    </div>
  `;
}

// ── SVG Icons ───────────────────────────────────────────────────────────────
function iconGrid()    { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>`; }
function iconRecords() { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 0 2-2h2a2 2 0 0 0 2 2"/></svg>`; }
function iconChart()   { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" d="M7 12l3-8 3 8 2-4 2 4"/><path stroke-linecap="round" d="M3 20h18"/></svg>`; }
function iconUsers()   { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path stroke-linecap="round" d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>`; }
function iconProfile() { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="8" r="4"/><path stroke-linecap="round" d="M6 20v-1a6 6 0 0 1 12 0v1"/></svg>`; }
function iconLogout()  { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3h4a3 3 0 0 1 3 3v1"/></svg>`; }
function iconPlus()    { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M12 4v16M4 12h16"/></svg>`; }
function iconEdit()    { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" d="M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5m-1.414-9.414a2 2 0 1 1 2.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>`; }
function iconTrash()   { return `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" d="M19 7l-.867 12.142A2 2 0 0 1 16.138 21H7.862a2 2 0 0 1-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v3M4 7h16"/></svg>`; }

// ── Modal helpers ────────────────────────────────────────────────────────────
function openModal(id)  { const m = document.getElementById(id); if(m) { m.classList.remove('hidden'); m.style.display='flex'; } }
function closeModal(id) { const m = document.getElementById(id); if(m) { m.style.display='none'; } }

document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) e.target.style.display = 'none';
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.querySelectorAll('.modal-overlay').forEach(m => m.style.display='none');
});

// ── Topbar builder ──────────────────────────────────────────────────────────
function buildTopbar(title, extraActions = '') {
  const bar = document.getElementById('topbar');
  if (!bar) return;
  bar.innerHTML = `
    <div class="topbar-title">${title}</div>
    <div class="topbar-actions">
      ${extraActions}
      <button class="btn-icon" title="Sign out" onclick="Auth.logout()">${iconLogout()}</button>
    </div>
  `;
}
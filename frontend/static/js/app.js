const API = 'http://localhost:8000'
let token = localStorage.getItem('token')
let currentUser = JSON.parse(localStorage.getItem('user') || 'null')
let currentPage = 0
const limit = 10

// ─── UTILS ───────────────────────────────────────────────
function fmt(amount) {
  return '₹' + Number(amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })
}

function fmtDate(d) {
  return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function api(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = 'Bearer ' + token
  const res = await fetch(API + path, { method, headers, body: body ? JSON.stringify(body) : null })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Something went wrong')
  return data
}

function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'))
  document.getElementById(id).classList.add('active')
}

function showTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'))
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'))
  document.getElementById('tab-' + name).classList.add('active')
  event.currentTarget.classList.add('active')
  if (name === 'transactions') loadTransactions()
  if (name === 'users') loadUsers()
}

function showModal(id) { document.getElementById(id).classList.remove('hidden') }
function hideModal(id) { document.getElementById(id).classList.add('hidden') }

function showError(id, msg) {
  const el = document.getElementById(id)
  el.textContent = msg
  el.classList.remove('hidden')
}

function hideError(id) { document.getElementById(id).classList.add('hidden') }

// ─── AUTH ─────────────────────────────────────────────────
async function login() {
  hideError('login-error')
  const email = document.getElementById('login-email').value
  const password = document.getElementById('login-password').value
  try {
    const data = await api('POST', '/auth/login', { email, password })
    token = data.access_token
    currentUser = data.user
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(currentUser))
    initDashboard()
  } catch (e) {
    showError('login-error', e.message)
  }
}

async function register() {
  hideError('register-error')
  const body = {
    full_name: document.getElementById('reg-name').value,
    email: document.getElementById('reg-email').value,
    password: document.getElementById('reg-password').value,
    role: document.getElementById('reg-role').value
  }
  try {
    await api('POST', '/auth/register', body)
    document.getElementById('register-success').textContent = 'Account created! Please sign in.'
    document.getElementById('register-success').classList.remove('hidden')
    setTimeout(() => showPage('login-page'), 1500)
  } catch (e) {
    showError('register-error', e.message)
  }
}

function logout() {
  token = null
  currentUser = null
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  showPage('login-page')
}

// ─── DASHBOARD INIT ───────────────────────────────────────
function initDashboard() {
  showPage('dashboard-page')
  document.getElementById('sidebar-name').textContent = currentUser.full_name
  document.getElementById('sidebar-role').textContent = currentUser.role
  document.getElementById('user-avatar').textContent = currentUser.full_name[0].toUpperCase()
  document.getElementById('header-date').textContent = new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

  if (currentUser.role === 'admin' || currentUser.role === 'analyst') {
    document.getElementById('add-tx-btn').style.display = 'inline-block'
    document.getElementById('trends-panel').style.display = 'block'
    loadTrends()
  }
  if (currentUser.role === 'admin') {
    document.getElementById('nav-users').style.display = 'flex'
  }

  // Set today's date as default in add transaction form
  document.getElementById('tx-date').value = new Date().toISOString().split('T')[0]

  loadSummary()
}

// ─── SUMMARY ──────────────────────────────────────────────
async function loadSummary() {
  try {
    const data = await api('GET', '/dashboard/summary')
    document.getElementById('total-income').textContent = fmt(data.total_income)
    document.getElementById('total-expense').textContent = fmt(data.total_expense)
    document.getElementById('net-balance').textContent = fmt(data.net_balance)
    document.getElementById('total-count').textContent = data.total_transactions

    // Category breakdown
    const max = Math.max(...data.category_breakdown.map(c => c.total), 1)
    document.getElementById('category-list').innerHTML = data.category_breakdown.slice(0, 6).map(c => `
      <div class="category-item">
        <div class="category-name">${c.category}</div>
        <div class="category-bar-wrap">
          <div class="category-bar" style="width:${(c.total / max * 100).toFixed(1)}%"></div>
        </div>
        <div class="category-amount">${fmt(c.total)}</div>
      </div>
    `).join('')

    // Recent transactions
    document.getElementById('recent-list').innerHTML = data.recent_transactions.map(t => `
      <div class="recent-item">
        <div class="recent-info">
          <div class="recent-cat">${t.category}</div>
          <div class="recent-date">${fmtDate(t.date)}</div>
        </div>
        <div class="recent-amount ${t.type === 'income' ? 'amount-income' : 'amount-expense'}">
          ${t.type === 'income' ? '+' : '-'}${fmt(t.amount)}
        </div>
      </div>
    `).join('')
  } catch (e) {
    console.error(e)
  }
}

// ─── TRENDS ───────────────────────────────────────────────
async function loadTrends() {
  try {
    const data = await api('GET', '/dashboard/trends')
    const maxVal = Math.max(...data.flatMap(t => [t.income, t.expense]), 1)
    document.getElementById('trends-list').innerHTML = data.map(t => `
      <div class="trend-item">
        <div class="trend-month">${t.month}</div>
        <div class="trend-bar-wrap">
          <div class="trend-label">Income</div>
          <div class="trend-bar-bg"><div class="trend-bar trend-income-bar" style="width:${(t.income/maxVal*100).toFixed(1)}%"></div></div>
          <div class="trend-val amount-income">${fmt(t.income)}</div>
        </div>
        <div class="trend-bar-wrap">
          <div class="trend-label">Expense</div>
          <div class="trend-bar-bg"><div class="trend-bar trend-expense-bar" style="width:${(t.expense/maxVal*100).toFixed(1)}%"></div></div>
          <div class="trend-val amount-expense">${fmt(t.expense)}</div>
        </div>
      </div>
    `).join('')
  } catch (e) { console.error(e) }
}

// ─── TRANSACTIONS ─────────────────────────────────────────
async function loadTransactions() {
  const type = document.getElementById('filter-type').value
  const category = document.getElementById('filter-category').value
  const from = document.getElementById('filter-from').value
  const to = document.getElementById('filter-to').value

  let url = `/transactions/?skip=${currentPage * limit}&limit=${limit}`
  if (type) url += `&type=${type}`
  if (category) url += `&category=${category}`
  if (from) url += `&date_from=${from}T00:00:00`
  if (to) url += `&date_to=${to}T23:59:59`

  try {
    const data = await api('GET', url)
    const canEdit = currentUser.role === 'admin' || currentUser.role === 'analyst'
    const canDelete = currentUser.role === 'admin'

    document.getElementById('transactions-tbody').innerHTML = data.map(t => `
      <tr>
        <td>${fmtDate(t.date)}</td>
        <td>${t.category}</td>
        <td><span class="badge badge-${t.type}">${t.type}</span></td>
        <td class="${t.type === 'income' ? 'amount-income' : 'amount-expense'}" style="font-weight:600">
          ${t.type === 'income' ? '+' : '-'}${fmt(t.amount)}
        </td>
        <td style="color:var(--text-muted);font-size:0.85rem">${t.notes || '—'}</td>
        <td>
          ${canDelete ? `<button class="btn btn-sm btn-danger" onclick="deleteTransaction('${t.id}')">Delete</button>` : '—'}
        </td>
      </tr>
    `).join('') || '<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:32px">No transactions found</td></tr>'

    document.getElementById('page-info').textContent = `Page ${currentPage + 1}`
  } catch (e) { console.error(e) }
}

function prevPage() { if (currentPage > 0) { currentPage--; loadTransactions() } }
function nextPage() { currentPage++; loadTransactions() }

function clearFilters() {
  document.getElementById('filter-type').value = ''
  document.getElementById('filter-category').value = ''
  document.getElementById('filter-from').value = ''
  document.getElementById('filter-to').value = ''
  currentPage = 0
  loadTransactions()
}

async function addTransaction() {
  hideError('tx-error')
  const body = {
    amount: parseFloat(document.getElementById('tx-amount').value),
    type: document.getElementById('tx-type').value,
    category: document.getElementById('tx-category').value,
    date: document.getElementById('tx-date').value + 'T00:00:00',
    notes: document.getElementById('tx-notes').value || null
  }
  if (!body.amount || !body.category || !body.date) {
    return showError('tx-error', 'Please fill all required fields')
  }
  try {
    await api('POST', '/transactions/', body)
    hideModal('add-transaction-modal')
    loadTransactions()
    loadSummary()
    // Reset form
    document.getElementById('tx-amount').value = ''
    document.getElementById('tx-category').value = ''
    document.getElementById('tx-notes').value = ''
  } catch (e) {
    showError('tx-error', e.message)
  }
}

async function deleteTransaction(id) {
  if (!confirm('Delete this transaction?')) return
  try {
    await api('DELETE', '/transactions/' + id)
    loadTransactions()
    loadSummary()
  } catch (e) { alert(e.message) }
}

// ─── USERS ────────────────────────────────────────────────
async function loadUsers() {
  try {
    const data = await api('GET', '/users/')
    document.getElementById('users-tbody').innerHTML = data.map(u => `
      <tr>
        <td style="font-weight:500">${u.full_name}</td>
        <td style="color:var(--text-muted)">${u.email}</td>
        <td><span class="badge badge-${u.role}">${u.role}</span></td>
        <td><span class="badge ${u.is_active ? 'badge-active' : 'badge-inactive'}">${u.is_active ? 'Active' : 'Inactive'}</span></td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="toggleStatus('${u.id}', ${u.is_active})">
            ${u.is_active ? 'Deactivate' : 'Activate'}
          </button>
        </td>
      </tr>
    `).join('')
  } catch (e) { console.error(e) }
}

async function toggleStatus(id, currentStatus) {
  try {
    await api('PATCH', `/users/${id}/status`, { is_active: !currentStatus })
    loadUsers()
  } catch (e) { alert(e.message) }
}

// ─── INIT ─────────────────────────────────────────────────
if (token && currentUser) {
  initDashboard()
} else {
  showPage('login-page')
}
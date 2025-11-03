// Import Supabase authentication functions
import { 
  signInWithPassword, 
  signOut, 
  getCurrentSession, 
  getUserRole, 
  onAuthStateChange,
  clearSessionCookies 
} from './auth.js'

// Minimal interactivity with mock data to demonstrate flows
(function(){
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  
  // Role-based login visual + subtitle
  const roleSelect = $('#role');
  const roleTrigger = $('#roleTrigger');
  const roleTriggerText = $('#roleTriggerText');
  const roleMenu = $('#roleMenu');
  const roleWrap = $('#roleSelectWrap');
  const subtitleEl = $('#loginSubtitle');
  const authVisual = document.querySelector('.auth-visual');
  const roleMeta = {
    student: {
      subtitle: 'African Leadership Academy • Student Clearance Portal',
      bg: "url('/static/images/students.jpeg')"
    },
    teacher: {
      subtitle: 'African Leadership Academy • Teacher Clearance Dashboard',
      bg: "url('/static/images/teacher.jpeg')"
    },
    finance: {
      subtitle: 'African Leadership Academy • Finance Clearance Dashboard',
      bg: "url('/static/images/finance.jpeg')"
    },
    hall: {
      subtitle: 'African Leadership Academy • Hall Clearance Dashboard',
      bg: "url('/static/images/hall.jpeg')"
    },
    coach: {
      subtitle: 'African Leadership Academy • Sports Clearance Dashboard',
      bg: "url('/static/images/coach.jpeg')"
    },
    lab: {
      subtitle: 'African Leadership Academy • Labs Clearance Dashboard',
      bg: "url('/static/images/lab.jpeg')"
    }
  };

  let fadeTimer = null;
  function preloadImage(url, onload) {
    const img = new Image();
    img.onload = onload;
    img.src = url.replace(/^url\(['"]?|['"]?\)$/g, '').replace(/^url\('/, '').replace(/'\)$/, '');
  }
  function applyRoleVisual(role) {
    const meta = roleMeta[role] || roleMeta.student;
    if (!authVisual) return;

    // Debounce rapid changes
    if (fadeTimer) { clearTimeout(fadeTimer); fadeTimer = null; }

    // Subtitle fade
    if (subtitleEl) {
      subtitleEl.style.opacity = '0';
      setTimeout(() => {
        subtitleEl.textContent = meta.subtitle;
        subtitleEl.style.opacity = '1';
      }, 120);
    }

    // Preload image before animating to avoid flicker
    preloadImage(meta.bg.replace(/^url\(|\)$/g, '').replace(/['"]/g, ''), () => {
      authVisual.style.setProperty('--auth-visual-bg-next', meta.bg);
      authVisual.classList.add('fade-in');
      fadeTimer = setTimeout(() => {
        authVisual.style.setProperty('--auth-visual-bg', meta.bg);
        authVisual.style.setProperty('--auth-visual-bg-next', 'none');
        authVisual.classList.remove('fade-in');
        fadeTimer = null;
      }, 360);
    });
  }

  if (roleSelect) {
    applyRoleVisual(roleSelect.value);
    roleSelect.addEventListener('change', (e) => applyRoleVisual(e.target.value));
  }

  // Custom dropdown wiring (progressive enhancement)
  if (roleTrigger && roleMenu && roleSelect && roleWrap) {
    const options = Array.from(roleMenu.querySelectorAll('.select-option'));
    function closeMenu() {
      roleWrap.classList.remove('select-open');
      roleTrigger.setAttribute('aria-expanded', 'false');
    }
    function openMenu() {
      roleWrap.classList.add('select-open');
      roleTrigger.setAttribute('aria-expanded', 'true');
    }
    roleTrigger.addEventListener('click', () => {
      const isOpen = roleWrap.classList.contains('select-open');
      isOpen ? closeMenu() : openMenu();
    });
    options.forEach(opt => {
      opt.addEventListener('click', () => {
        const value = opt.getAttribute('data-value');
        roleSelect.value = value;
        roleTriggerText.textContent = opt.textContent;
        options.forEach(o => o.setAttribute('aria-selected', String(o === opt)));
        roleSelect.dispatchEvent(new Event('change'));
        closeMenu();
      });
      opt.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); opt.click(); }
        if (e.key === 'Escape') { closeMenu(); roleTrigger.focus(); }
        const idx = options.indexOf(opt);
        if (e.key === 'ArrowDown') { e.preventDefault(); (options[idx + 1] || options[0]).focus(); }
        if (e.key === 'ArrowUp') { e.preventDefault(); (options[idx - 1] || options[options.length - 1]).focus(); }
      });
    });
    document.addEventListener('click', (e) => { if (!roleWrap.contains(e.target)) closeMenu(); });
    // Sync trigger text with initial value
    const active = options.find(o => o.getAttribute('data-value') === roleSelect.value) || options[0];
    if (active) { roleTriggerText.textContent = active.textContent; options.forEach(o => o.setAttribute('aria-selected', String(o === active))); }
  }

  // Footer year
  const y = $('#year'); if (y) y.textContent = new Date().getFullYear();

  // Enhanced Login with Supabase Authentication
  const loginBtn = $('#loginBtn');
  if (loginBtn) {
    // Add error display element if not exists
    let errorEl = $('#loginError');
    if (!errorEl) {
      errorEl = document.createElement('div');
      errorEl.id = 'loginError';
      errorEl.style.color = '#ef4444';
      errorEl.style.marginTop = '8px';
      errorEl.style.display = 'none';
      loginBtn.parentNode.insertBefore(errorEl, loginBtn);
    }

    loginBtn.addEventListener('click', async () => {
      // Clear previous errors
      errorEl.style.display = 'none';
      errorEl.textContent = '';
      
      // Show loading state
      const originalText = loginBtn.textContent;
      loginBtn.textContent = 'Signing in...';
      loginBtn.disabled = true;

      try {
        // Get form values
        const email = $('#id').value.trim();
        const password = $('#password').value.trim();
        const selectedRole = $('#role').value;

        if (!email || !password) {
          throw new Error('Please enter both email and password');
        }

        // Attempt Supabase authentication
        const { user, session, error } = await signInWithPassword(email, password);

        if (error) {
          throw new Error(error);
        }

        if (user && session) {
          // Store session for Flask to verify
          console.log(`Login successful for ${user.email}`);
          
          // Let the backend determine the actual user role by checking database tables
          // Instead of relying on frontend metadata, redirect to a generic dashboard
          // route that will detect the role server-side and redirect appropriately
          window.location.href = '/dashboard/student'; // Backend will redirect to correct role
        } else {
          throw new Error('Login failed - no session created');
        }

      } catch (err) {
        console.error('Login error:', err);
        errorEl.textContent = err.message || 'Login failed. Please try again.';
        errorEl.style.display = 'block';
      } finally {
        // Reset button state
        loginBtn.textContent = originalText;
        loginBtn.disabled = false;
      }
    });

    // Enable Enter key submission
    ['#id', '#password'].forEach(selector => {
      const input = $(selector);
      if (input) {
        input.addEventListener('keypress', (e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            loginBtn.click();
          }
        });
      }
    });
  }

  // Session check is now handled server-side to prevent flashing

  // Add logout functionality for dashboard pages
  const logoutBtn = $('#logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      
      try {
        await signOut();
        clearSessionCookies();
        window.location.href = '/login';
      } catch (err) {
        console.error('Logout error:', err);
        // Force redirect even if logout fails
        clearSessionCookies();
        window.location.href = '/login';
      }
    });
  }

  // Listen to auth state changes globally
  onAuthStateChange((event, session) => {
    if (event === 'SIGNED_OUT') {
      // Only redirect if we're not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
  });

  // Student dashboard - real data now handled server-side in templates
  // Portals and progress are generated from actual student enrollment data
  
  // Only keep essential JavaScript functionality that doesn't override server-side content

  // Subject detail page
  const subjectTitle = $('#subjectTitle');
  if (subjectTitle) {
    const params = new URLSearchParams(location.search); const s = params.get('subject') || 'Subject';
    subjectTitle.textContent = s;
    const items = [
      { text: `${s} S1 Book`, done: false },
      { text: 'Return Calculator', done: true },
      { text: `${s} P1 Book`, done: false },
    ];
    const pct = Math.round((items.filter(i => i.done).length / items.length) * 100);
    $('#subjectPct').textContent = pct + '%';
    $('#subjectFill').style.width = pct + '%';
    const wrap = $('#subjectTodo');
    items.forEach(i => {
      const row = document.createElement('div'); row.style.display = 'flex'; row.style.justifyContent = 'space-between'; row.style.alignItems = 'center'; row.style.gap = '8px';
      row.innerHTML = `<span>${i.text}</span><span class="badge ${i.done ? 'badge-success' : 'badge-warning'}">${i.done ? 'Completed' : 'Press to Clear Now'}</span>`;
      wrap.appendChild(row);
    });
  }

  // Teacher dashboard mock
  const teacherTable = $('#teacherTable tbody');
  if (teacherTable) {
    // Scoped to classes taught by this teacher
    const items = [
      { class: 'Math Y2-A', student: 'S12345 • Ama N.', subject: 'Mathematics', item: 'Textbook MATH-BOOK-12', returned: false },
      { class: 'Math Y2-A', student: 'S12002 • Malik O.', subject: 'Mathematics', item: 'Workbook MATH-WB-07', returned: true },
      { class: 'Physics Y1-B', student: 'S12811 • Tumi K.', subject: 'Physics', item: 'Calculator CALC-84', returned: false },
    ];
    items.forEach(it => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${it.class}</td>
        <td>${it.student}</td>
        <td>${it.subject}</td>
        <td>${it.item}</td>
        <td><span class="badge ${it.returned ? 'badge-success' : 'badge-warning'}">${it.returned ? 'Returned' : 'Not Returned'}</span></td>
        <td>
          <button class="button button-primary">Mark Returned</button>
          <button class="button">Flag Issue</button>
        </td>
      `;
      teacherTable.appendChild(tr);
    });
    // Signature pad
    const canvas = $('#sigPad');
    if (canvas) {
      const ctx = canvas.getContext('2d');
      let drawing = false; let last = null;
      canvas.addEventListener('pointerdown', (e) => { drawing = true; last = [e.offsetX, e.offsetY]; });
      canvas.addEventListener('pointerup', () => { drawing = false; last = null; });
      canvas.addEventListener('pointermove', (e) => {
        if (!drawing) return; const [lx, ly] = last; const x = e.offsetX, y = e.offsetY; ctx.strokeStyle = '#e5e7eb'; ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(lx, ly); ctx.lineTo(x, y); ctx.stroke(); last = [x, y];
      });
      $('#clearSig')?.addEventListener('click', () => { ctx.clearRect(0,0,canvas.width, canvas.height); });
      $('#saveSig')?.addEventListener('click', () => { alert('Signature saved (mock).'); });
    }
  }

  // Finance dashboard mock
  const financeTable = $('#financeTable tbody');
  if (financeTable) {
    const students = [
      { name: 'S12345 • Ama N.', tuition: 0, replace: 0, status: 'Clear' },
      { name: 'S12002 • Malik O.', tuition: 300, replace: 0, status: 'Due' },
      { name: 'S12811 • Tumi K.', tuition: 0, replace: 45, status: 'Due' }
    ];
    const statusClass = (s) => s === 'Clear' ? 'badge-success' : 'badge-danger';
    students.forEach(s => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${s.name}</td>
        <td>$${s.tuition}</td>
        <td>$${s.replace}</td>
        <td><span class="badge ${statusClass(s.status)}">${s.status}</span></td>
      `;
      financeTable.appendChild(tr);
    });
  }

  // Hall dashboard mock
  const hallTable = $('#hallTable tbody');
  if (hallTable) {
    // Only students in assigned hall (mock)
    const rooms = [
      { student: 'S12345 • Ama N.', hall: 'Kibo', room: 'A-203', status: 'OK' },
      { student: 'S12002 • Malik O.', hall: 'Kibo', room: 'A-118', status: 'Not OK' }
    ];
    const statusClass = (s) => s === 'OK' ? 'badge-success' : 'badge-danger';
    rooms.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.student}</td>
        <td>${r.hall}</td>
        <td>${r.room}</td>
        <td><span class="badge ${statusClass(r.status)}">${r.status}</span></td>
        <td>
          <button class="button button-primary">Mark OK</button>
          <button class="button">Mark Not OK</button>
        </td>
      `;
      hallTable.appendChild(tr);
    });
  }

  // Coach dashboard mock
  const coachTable = $('#coachTable tbody');
  if (coachTable) {
    // Only students who do sport (mock scope)
    const sports = [
      { student: 'S12345 • Ama N.', sport: 'Basketball', item: 'Jersey #12', status: 'Returned' },
      { student: 'S12811 • Tumi K.', sport: 'Soccer', item: 'Shin Guards', status: 'Lost' }
    ];
    const statusClass = (s) => s === 'Returned' ? 'badge-success' : 'badge-danger';
    sports.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.student}</td>
        <td>${r.sport}</td>
        <td>${r.item}</td>
        <td><span class="badge ${statusClass(r.status)}">${r.status}</span></td>
        <td>
          <button class="button button-primary">Mark Returned</button>
          <button class="button">Flag Lost</button>
        </td>
      `;
      coachTable.appendChild(tr);
    });
  }

  // Lab dashboard mock
  const labTable = $('#labTable tbody');
  if (labTable) {
    const labs = [
      { student: 'S12345 • Ama N.', subject: 'Chemistry', item: 'Goggles', cost: 0, status: 'OK' },
      { student: 'S12002 • Malik O.', subject: 'Biology', item: 'Lab Manual', cost: 15, status: 'Cost' }
    ];
    const statusClass = (s) => s === 'OK' ? 'badge-success' : 'badge-warning';
    labs.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.student}</td>
        <td>${r.subject}</td>
        <td>${r.item}</td>
        <td>$${r.cost}</td>
        <td><span class="badge ${statusClass(r.status)}">${r.status}</span></td>
        <td>
          <button class="button button-primary">Resolve</button>
        </td>
      `;
      labTable.appendChild(tr);
    });
  }
})();
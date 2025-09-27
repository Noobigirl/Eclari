// Modern interactivity with animations
(function(){
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  
  // Add smooth scrolling
  document.documentElement.style.scrollBehavior = 'smooth';
  
  // Intersection Observer for scroll animations
  const observeElements = () => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fadeInUp');
        }
      });
    }, { 
      threshold: 0.1,
      rootMargin: '50px'
    });
    
    // Observe all cards and important elements
    $$('.card, .subject-card, .portal-card, .quick-action-item').forEach(el => {
      observer.observe(el);
    });
  };
  
  // Staggered animations for grid items
  const addStaggeredAnimations = () => {
    $$('.subject-card, .portal-card').forEach((card, index) => {
      card.classList.add(`stagger-${(index % 5) + 1}`);
      card.classList.add('animate-fadeInUp');
    });
  };
  
  // Loading animation
  const initLoadingAnimation = () => {
    // Add loading screen
    const loadingScreen = document.createElement('div');
    loadingScreen.className = 'loading-screen';
    loadingScreen.innerHTML = `
      <div class="loading-content">
        <img src="/static/images/favicon_io/favicon-32x32.png" alt="Eclari" class="loading-logo">
        <div class="loading-text">Eclari</div>
        <div class="loading-progress">
          <div class="loading-bar"></div>
        </div>
      </div>
    `;
    
    // Add loading screen styles
    const loadingStyles = document.createElement('style');
    loadingStyles.textContent = `
      .loading-screen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, var(--ala-maroon), var(--ala-gold));
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        transition: opacity 0.5s ease-out;
      }
      .loading-content {
        text-align: center;
        color: white;
      }
      .loading-logo {
        width: 48px;
        height: 48px;
        animation: pulse 1.5s ease-in-out infinite;
        margin-bottom: 16px;
      }
      .loading-text {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 24px;
        animation: fadeInUp 0.8s ease-out;
      }
      .loading-progress {
        width: 200px;
        height: 4px;
        background: rgba(255,255,255,0.3);
        border-radius: 2px;
        overflow: hidden;
        margin: 0 auto;
      }
      .loading-bar {
        height: 100%;
        background: white;
        animation: loadingProgress 2s ease-in-out infinite;
      }
      @keyframes loadingProgress {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
      }
    `;
    document.head.appendChild(loadingStyles);
    document.body.appendChild(loadingScreen);
    
    // Hide loading screen when page loads
    window.addEventListener('load', () => {
      setTimeout(() => {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
          loadingScreen.remove();
          loadingStyles.remove();
        }, 500);
      }, 1000); // Show for at least 1 second
      
      // Add staggered animations after load
      setTimeout(addStaggeredAnimations, 1200);
    });
  };
  
  // Initialize animations
  initLoadingAnimation();
  
  // Animate progress bars
  const animateProgressBars = () => {
    $$('.progress-fill').forEach(progressBar => {
      const targetWidth = progressBar.getAttribute('data-width') || progressBar.style.width;
      if (targetWidth) {
        progressBar.style.width = '0%';
        // Use requestAnimationFrame for smooth animation
        setTimeout(() => {
          progressBar.style.width = targetWidth;
        }, 300);
      }
    });
  };
  
  // Enhanced hover effects
  const addHoverEffects = () => {
    $$('.card, .subject-card, .portal-card').forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-8px) scale(1.02)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
      });
    });
    
    // Button ripple effect
    $$('button, .button').forEach(button => {
      button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
          position: absolute;
          width: ${size}px;
          height: ${size}px;
          left: ${x}px;
          top: ${y}px;
          background: rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          transform: scale(0);
          animation: ripple 0.6s ease-out;
          pointer-events: none;
        `;
        
        this.appendChild(ripple);
        
        setTimeout(() => {
          ripple.remove();
        }, 600);
      });
    });
  };
  
  // Enhanced scroll effects
  const addScrollEffects = () => {
    let ticking = false;
    
    const updateScrollEffects = () => {
      const scrolled = window.pageYOffset;
      
      // Header scroll effect
      const header = $('.site-header');
      if (header) {
        if (scrolled > 50) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      }
      
      // Fade in elements on scroll
      $$('.fade-in-on-scroll').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.8) {
          el.classList.add('visible');
        }
      });
      
      ticking = false;
    };
    
    const requestScrollTick = () => {
      if (!ticking) {
        requestAnimationFrame(updateScrollEffects);
        ticking = true;
      }
    };
    
    window.addEventListener('scroll', requestScrollTick);
  };
  
  // Add notification system
  const showNotification = (message, type = 'info') => {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: white;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 16px 20px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      z-index: 1000;
      max-width: 300px;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOutNotification 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  };
  
  // Enhanced form interactions
  const enhanceFormInputs = () => {
    $$('input, textarea, select').forEach(input => {
      input.addEventListener('focus', function() {
        this.parentElement?.classList.add('input-focused');
      });
      
      input.addEventListener('blur', function() {
        this.parentElement?.classList.remove('input-focused');
      });
      
      // Add typing animation for inputs
      input.addEventListener('input', function() {
        this.style.animation = 'inputPulse 0.3s ease-out';
        setTimeout(() => {
          this.style.animation = '';
        }, 300);
      });
    });
  };
  
  // Add ripple animation CSS
  const style = document.createElement('style');
  style.textContent = `
    @keyframes ripple {
      to {
        transform: scale(2);
        opacity: 0;
      }
    }
    @keyframes slideOutNotification {
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
    @keyframes inputPulse {
      0% { box-shadow: 0 0 0 0 rgba(74, 35, 35, 0.4); }
      70% { box-shadow: 0 0 0 8px rgba(74, 35, 35, 0); }
      100% { box-shadow: 0 0 0 0 rgba(74, 35, 35, 0); }
    }
    button, .button {
      position: relative;
      overflow: hidden;
    }
    .input-focused {
      transform: scale(1.02);
    }
  `;
  document.head.appendChild(style);
  
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      observeElements();
      animateProgressBars();
      addHoverEffects();
      addScrollEffects();
      enhanceFormInputs();
    });
  } else {
    observeElements();
    animateProgressBars();
    addHoverEffects();
    addScrollEffects();
    enhanceFormInputs();
  }
  
  // Expose notification function globally
  window.showNotification = showNotification;
  
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

  // Login routing -> Flask endpoints
  const loginBtn = $('#loginBtn');
  if (loginBtn) {
    loginBtn.addEventListener('click', () => {
      const role = $('#role').value;
      const routes = { student: '/student', teacher: '/teacher', finance: '/finance', hall: '/hall', coach: '/coach', lab: '/lab' };
      window.location.href = routes[role] || '/student';
    });
  }

  // Student dashboard - real data now handled server-side in templates
  // Portals and progress are generated from actual student enrollment data

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



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
          observer.unobserve(entry.target); // Stop observing once animated
        }
      });
    }, { 
      threshold: 0.05, // Reduced from 0.1 for faster triggering
      rootMargin: '30px' // Reduced from 50px
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
        background: var(--ala-maroon);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        transition: opacity 0.3s ease-out;
      }
      .loading-content {
        text-align: center;
        color: var(--ala-gold);
      }
      .loading-logo {
        width: 48px;
        height: 48px;
        filter: hue-rotate(45deg) brightness(1.2);
        animation: pulse 1.5s ease-in-out infinite;
        margin-bottom: 16px;
      }
      .loading-text {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 24px;
        color: var(--ala-gold);
        animation: fadeInUp 0.6s ease-out;
      }
      .loading-progress {
        width: 200px;
        height: 4px;
        background: rgba(218, 165, 32, 0.3);
        border-radius: 2px;
        overflow: hidden;
        margin: 0 auto;
      }
      .loading-bar {
        height: 100%;
        background: var(--ala-gold);
        animation: loadingProgress 1.5s ease-in-out infinite;
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
        }, 300);
      }, 400); // Reduced from 1000ms to 400ms
      
      // Add staggered animations after load
      setTimeout(addStaggeredAnimations, 500); // Reduced from 1200ms to 500ms
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
        requestAnimationFrame(() => {
          setTimeout(() => {
            progressBar.style.width = targetWidth;
          }, 150); // Reduced from 300ms to 150ms
        });
      }
    });
  };
  
  // Enhanced hover effects (only for clickable subject cards)
  const addHoverEffects = () => {
    $$('.subject-card').forEach(card => {
      // Only add hover effects to subject cards which are clickable
      if (card.onclick || card.getAttribute('onclick')) {
        card.addEventListener('mouseenter', function() {
          this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
          this.style.transform = 'translateY(0) scale(1)';
        });
      }
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
  
  // Optimized scroll effects with throttling
  const addScrollEffects = () => {
    let ticking = false;
    let lastScrollY = 0;
    
    const updateScrollEffects = () => {
      const scrolled = window.pageYOffset;
      
      // Only update if scroll changed significantly (performance optimization)
      if (Math.abs(scrolled - lastScrollY) < 5) {
        ticking = false;
        return;
      }
      
      lastScrollY = scrolled;
      
      // Header scroll effect
      const header = $('.site-header');
      if (header) {
        if (scrolled > 50) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      }
      
      ticking = false;
    };
    
    const requestScrollTick = () => {
      if (!ticking) {
        requestAnimationFrame(updateScrollEffects);
        ticking = true;
      }
    };
    
    window.addEventListener('scroll', requestScrollTick, { passive: true });
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
  
  // Enhanced form interactions (removed hover effects, keep focus only)
  const enhanceFormInputs = () => {
    $$('input, textarea, select').forEach(input => {
      input.addEventListener('focus', function() {
        this.parentElement?.classList.add('input-focused');
      });
      
      input.addEventListener('blur', function() {
        this.parentElement?.classList.remove('input-focused');
      });
      
      // Removed input animation on typing
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
  }

  // Signature pad functionality (moved outside conditional blocks)
  const canvas = $('#sigPad');
  if (canvas) {
    console.log('Signature canvas found, initializing...'); // Debug log
    const ctx = canvas.getContext('2d');
    let drawing = false; 
    let last = null;
    
    // Set initial canvas style
    ctx.strokeStyle = '#4A2323'; // ALA maroon color
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    // Function to get coordinates (works for both mouse and touch)
    const getCoords = (e) => {
      const rect = canvas.getBoundingClientRect();
      const clientX = e.clientX || (e.touches && e.touches[0].clientX);
      const clientY = e.clientY || (e.touches && e.touches[0].clientY);
      return [clientX - rect.left, clientY - rect.top];
    };
    
    // Hide/show prompt text
    const signaturePrompt = $('#signaturePrompt');
    const hidePrompt = () => {
      if (signaturePrompt) signaturePrompt.style.display = 'none';
    };
    const showPrompt = () => {
      if (signaturePrompt) signaturePrompt.style.display = 'block';
    };
    
    // Check if canvas has content
    const hasContent = () => {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      return imageData.data.some(channel => channel !== 0);
    };
    
    // Mouse/Touch events
    const startDrawing = (e) => {
      console.log('Start drawing triggered'); // Debug log
      e.preventDefault();
      drawing = true; 
      last = getCoords(e);
      hidePrompt();
    };
    
    const stopDrawing = (e) => {
      e.preventDefault();
      drawing = false; 
      last = null;
    };
    
    const draw = (e) => {
      e.preventDefault();
      if (!drawing) return; 
      const [lx, ly] = last; 
      const [x, y] = getCoords(e);
      
      ctx.beginPath(); 
      ctx.moveTo(lx, ly); 
      ctx.lineTo(x, y); 
      ctx.stroke(); 
      last = [x, y];
    };
    
    // Add event listeners for both mouse and touch
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);
    
    console.log('Signature event listeners added'); // Debug log
    
    // Prevent scrolling when touching the canvas
    canvas.addEventListener('touchstart', (e) => e.preventDefault());
    canvas.addEventListener('touchmove', (e) => e.preventDefault());
    
    $('#clearSig')?.addEventListener('click', () => { 
      ctx.clearRect(0, 0, canvas.width, canvas.height); 
      showPrompt();
    });
    
    $('#saveSig')?.addEventListener('click', () => { 
      if (!hasContent()) {
        alert('Please draw a signature before saving.');
        return;
      }
      // Convert canvas to image data
      const imageData = canvas.toDataURL();
      // Here you could send this to your server
      alert('Signature saved successfully!'); 
    });
  }  // Finance dashboard mock
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

  // Hall Page Custom Select Functionality
  const initializeHallSelects = () => {
    // Year Group Filter
    const yearGroupTrigger = $('#yearGroupTrigger');
    const yearGroupMenu = $('#yearGroupMenu');
    const yearGroupText = $('#yearGroupText');
    const yearGroupHidden = $('#yearGroupFilter');
    
    if (yearGroupTrigger && yearGroupMenu) {
      yearGroupTrigger.addEventListener('click', () => {
        const isOpen = yearGroupTrigger.parentElement.classList.contains('select-open');
        
        // Close other selects
        document.querySelectorAll('.select-wrap').forEach(wrap => wrap.classList.remove('select-open'));
        
        if (!isOpen) {
          yearGroupTrigger.parentElement.classList.add('select-open');
        }
      });
      
      yearGroupMenu.querySelectorAll('.select-option').forEach(option => {
        option.addEventListener('click', () => {
          const value = option.dataset.value;
          yearGroupText.textContent = option.textContent;
          yearGroupHidden.value = value;
          
          // Update selected state
          yearGroupMenu.querySelectorAll('.select-option').forEach(opt => opt.removeAttribute('aria-selected'));
          option.setAttribute('aria-selected', 'true');
          
          yearGroupTrigger.parentElement.classList.remove('select-open');
          
          // Trigger filter update
          filterTable();
        });
      });
    }
    
    // Status Filter
    const statusTrigger = $('#statusTrigger');
    const statusMenu = $('#statusMenu');
    const statusText = $('#statusText');
    const statusHidden = $('#statusFilter');
    
    if (statusTrigger && statusMenu) {
      statusTrigger.addEventListener('click', () => {
        const isOpen = statusTrigger.parentElement.classList.contains('select-open');
        
        // Close other selects
        document.querySelectorAll('.select-wrap').forEach(wrap => wrap.classList.remove('select-open'));
        
        if (!isOpen) {
          statusTrigger.parentElement.classList.add('select-open');
        }
      });
      
      statusMenu.querySelectorAll('.select-option').forEach(option => {
        option.addEventListener('click', () => {
          const value = option.dataset.value;
          statusText.textContent = option.textContent;
          statusHidden.value = value;
          
          // Update selected state
          statusMenu.querySelectorAll('.select-option').forEach(opt => opt.removeAttribute('aria-selected'));
          option.setAttribute('aria-selected', 'true');
          
          statusTrigger.parentElement.classList.remove('select-open');
          
          // Trigger filter update
          filterTable();
        });
      });
    }
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.select-wrap')) {
        document.querySelectorAll('.select-wrap').forEach(wrap => wrap.classList.remove('select-open'));
      }
    });
  };

  // Hall Page Functionality
  const hallSearch = $('#hallSearch');
  const yearGroupFilter = $('#yearGroupFilter');
  const statusFilter = $('#statusFilter');
  const hallTableMain = $('#hallTable');
  const visibleCount = $('#visibleCount');

  if (hallSearch && hallTableMain) {
    let allRows = [];
    
    // Initialize rows array
    const initializeRows = () => {
      allRows = Array.from(hallTableMain.querySelectorAll('.table-row'));
    };
    
    // Filter and search functionality
    const filterTable = () => {
      if (allRows.length === 0) initializeRows();
      
      const searchTerm = hallSearch.value.toLowerCase().trim();
      const yearGroupValue = yearGroupFilter?.value || '';
      const statusValue = statusFilter?.value || '';
      
      let visibleRowCount = 0;
      
      allRows.forEach(row => {
        const studentName = row.dataset.studentName?.toLowerCase() || '';
        const room = row.dataset.room?.toLowerCase() || '';
        const yearGroup = row.dataset.yearGroup || '';
        const status = row.dataset.status || '';
        
        // Check search term (name or room)
        const matchesSearch = !searchTerm || 
          studentName.includes(searchTerm) || 
          room.includes(searchTerm);
        
        // Check year group filter
        const matchesYearGroup = !yearGroupValue || yearGroup === yearGroupValue;
        
        // Check status filter
        const matchesStatus = !statusValue || status === statusValue;
        
        // Show/hide row based on all criteria
        const isVisible = matchesSearch && matchesYearGroup && matchesStatus;
        
        if (isVisible) {
          row.style.display = '';
          visibleRowCount++;
        } else {
          row.style.display = 'none';
        }
      });
      
      // Update visible count
      if (visibleCount) {
        visibleCount.textContent = visibleRowCount;
      }
      
      // Show empty state if no results
      updateEmptyState(visibleRowCount === 0 && allRows.length > 0);
    };
    
    // Update empty state
    const updateEmptyState = (show) => {
      let emptyRow = hallTableMain.querySelector('.empty-row');
      
      if (show && !emptyRow) {
        emptyRow = document.createElement('tr');
        emptyRow.className = 'empty-row';
        emptyRow.innerHTML = `
          <td colspan="6" style="text-align: center; padding: 60px 20px; color: var(--muted);">
            <div style="font-size: 48px; margin-bottom: 16px;">🔍</div>
            <h3 style="margin: 0 0 8px; color: var(--text);">No Results Found</h3>
            <p style="margin: 0;">Try adjusting your search or filter criteria.</p>
          </td>
        `;
        hallTableMain.querySelector('tbody').appendChild(emptyRow);
      } else if (!show && emptyRow) {
        emptyRow.remove();
      }
    };
    
    // Event listeners
    hallSearch.addEventListener('input', filterTable);
    yearGroupFilter?.addEventListener('change', filterTable);
    statusFilter?.addEventListener('change', filterTable);
    
    // Initialize on page load
    setTimeout(initializeRows, 100);
    
    // Initialize custom selects
    initializeHallSelects();
  }

  // Update Hall Clearance functionality
  window.updateHallClearance = function(studentId, status) {
    const statusText = status === 'approved' ? 'Approved' : 'Rejected';
    
    if (window.showNotification) {
      const message = `Hall clearance ${statusText.toLowerCase()} for student ${studentId}`;
      window.showNotification(message, status === 'approved' ? 'success' : 'warning');
    }
    
    // Here you would typically make an API call to update the database
    console.log(`Updating hall clearance for student ${studentId} to ${status}`);
    
    // Update button states
    const row = document.querySelector(`tr[data-student-name*="${studentId}"]`);
    if (row) {
      const buttons = row.querySelectorAll('.hall-clearance-buttons button');
      buttons.forEach(button => {
        button.classList.remove('button-success', 'button-error');
        button.classList.add('button-outline');
      });
      
      // Highlight the selected button
      const targetButton = Array.from(buttons).find(btn => 
        btn.textContent.includes(status === 'approved' ? 'Approve' : 'Reject')
      );
      if (targetButton) {
        targetButton.classList.remove('button-outline');
        targetButton.classList.add(status === 'approved' ? 'button-success' : 'button-error');
      }
      
      // Update the row's data attribute for filtering
      row.setAttribute('data-status', status);
    }
  };

})();



// Handles Supabase's email-confirmation and password-reset redirects.
//
// Supabase sends users back to the Site URL with the session in the URL
// *fragment*, e.g. https://example.com/#access_token=...&refresh_token=...
// The fragment never reaches our server, so we read it here and hand it to
// /auth/session, which turns it into our normal httpOnly session cookies.
(function () {
  if (!location.hash || location.hash.indexOf("access_token=") === -1) return;

  var params = new URLSearchParams(location.hash.slice(1));
  var accessToken = params.get("access_token");
  var refreshToken = params.get("refresh_token");

  // Always strip the tokens out of the visible URL, success or not.
  function cleanUrl() {
    history.replaceState(null, "", location.pathname + location.search);
  }

  if (!accessToken || !refreshToken) {
    cleanUrl();
    return;
  }

  fetch("/auth/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ access_token: accessToken, refresh_token: refreshToken }),
  })
    .then(function (res) {
      if (res.ok) {
        window.location.replace("/dashboard");
      } else {
        cleanUrl();
      }
    })
    .catch(cleanUrl);
})();

// Dark/light theme toggle. The <html class="dark"> state itself is set
// inline in base.html (before first paint, to avoid a flash) — this just
// wires up the button and remembers the choice.
(function () {
  var btn = document.getElementById("theme-toggle");
  if (!btn) return;
  btn.addEventListener("click", function () {
    var isDark = document.documentElement.classList.toggle("dark");
    try {
      localStorage.setItem("theme", isDark ? "dark" : "light");
    } catch (e) {}
  });
})();

// Homepage hero slider: auto-rotates every 5s, plus clickable dots.
// However many .hero-slide elements the server rendered (one per admin
// "hero_slides" row), that's how many this cycles through.
(function () {
  var root = document.getElementById("hero-slider");
  if (!root) return;
  var slides = root.querySelectorAll(".hero-slide");
  var dots = document.querySelectorAll(".hero-dot");
  if (slides.length < 2) return;

  var current = 0;
  var timer;

  function show(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach(function (el, i) {
      var active = i === current;
      el.classList.toggle("opacity-100", active);
      el.classList.toggle("z-10", active);
      el.classList.toggle("opacity-0", !active);
      el.classList.toggle("z-0", !active);
      el.classList.toggle("pointer-events-none", !active);
    });
    dots.forEach(function (dot, i) {
      dot.classList.toggle("bg-white", i === current);
      dot.classList.toggle("bg-white/40", i !== current);
    });
  }

  function restart() {
    clearInterval(timer);
    timer = setInterval(function () {
      show(current + 1);
    }, 5000);
  }

  dots.forEach(function (dot) {
    dot.addEventListener("click", function () {
      show(parseInt(dot.getAttribute("data-goto"), 10));
      restart();
    });
  });

  restart();
})();

// Floating Assistant (FAQ) widget. Fetches /api/faqs once; if there's
// nothing to show, the button never appears at all.
(function () {
  var fab = document.getElementById("assistant-fab");
  var panel = document.getElementById("assistant-panel");
  var body = document.getElementById("assistant-body");
  var closeBtn = document.getElementById("assistant-close");
  if (!fab || !panel || !body) return;

  var faqs = [];

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function renderList() {
    if (!faqs.length) {
      body.innerHTML = '<p class="p-4 text-sm text-slate-400">No questions yet.</p>';
      return;
    }
    body.innerHTML = faqs
      .map(function (faq, i) {
        return (
          '<button type="button" data-faq="' +
          i +
          '" class="faq-question w-full text-left px-4 py-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center justify-between gap-2 transition">' +
          '<span class="text-sm font-medium text-slate-700 dark:text-slate-200">' +
          escapeHtml(faq.question) +
          '</span>' +
          '<span class="text-slate-300 dark:text-slate-600 flex-shrink-0">&rsaquo;</span>' +
          "</button>"
        );
      })
      .join("");
    body.querySelectorAll(".faq-question").forEach(function (btn) {
      btn.addEventListener("click", function () {
        renderAnswer(faqs[parseInt(btn.getAttribute("data-faq"), 10)]);
      });
    });
  }

  function renderAnswer(faq) {
    body.innerHTML =
      '<div class="p-4">' +
      '<button type="button" id="faq-back" class="text-xs font-semibold text-brand mb-3">&lsaquo; Back</button>' +
      '<div class="font-semibold text-sm text-slate-800 dark:text-slate-100 mb-2">' +
      escapeHtml(faq.question) +
      "</div>" +
      '<div class="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">' +
      escapeHtml(faq.answer) +
      "</div>" +
      "</div>";
    document.getElementById("faq-back").addEventListener("click", renderList);
  }

  function togglePanel() {
    var isHidden = panel.hasAttribute("hidden");
    if (isHidden) {
      panel.removeAttribute("hidden");
      renderList();
    } else {
      panel.setAttribute("hidden", "");
    }
  }

  fetch("/api/faqs")
    .then(function (res) {
      return res.ok ? res.json() : [];
    })
    .then(function (data) {
      faqs = Array.isArray(data) ? data : [];
      if (faqs.length) {
        fab.removeAttribute("hidden");
      }
    })
    .catch(function () {});

  fab.addEventListener("click", togglePanel);
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      panel.setAttribute("hidden", "");
    });
  }
})();

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
        window.location.replace("/admin");
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

// Mobile menu (hamburger) in the navbar.
(function () {
  var btn = document.getElementById("menu-toggle");
  var menu = document.getElementById("mobile-menu");
  if (!btn || !menu) return;
  btn.addEventListener("click", function () {
    var open = menu.hasAttribute("hidden");
    menu.toggleAttribute("hidden", !open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
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
      dot.classList.toggle("w-6", i === current);
      dot.classList.toggle("bg-white/50", i !== current);
      dot.classList.toggle("w-2", i !== current);
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
  var emptyLabel = panel.getAttribute("data-empty") || "No questions yet.";
  var backLabel = panel.getAttribute("data-back") || "Back";

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function renderList() {
    if (!faqs.length) {
      body.innerHTML = '<p class="p-4 text-sm text-slate-400">' + escapeHtml(emptyLabel) + "</p>";
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
      '<button type="button" id="faq-back" class="text-xs font-semibold text-brand mb-3">&lsaquo; ' +
      escapeHtml(backLabel) +
      "</button>" +
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

// Blog "share / copy link" buttons: phones get the native share sheet
// (WhatsApp, Messenger, ...); elsewhere the link is copied to the clipboard.
(function () {
  document.querySelectorAll(".share-link").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var url = btn.getAttribute("data-share-url");
      var title = btn.getAttribute("data-share-title") || document.title;
      if (navigator.share) {
        navigator.share({ title: title, url: url }).catch(function () {});
        return;
      }
      function done() {
        var tip = document.createElement("span");
        tip.textContent = btn.getAttribute("data-copied") || "Link copied!";
        tip.className =
          "absolute -top-9 right-0 whitespace-nowrap bg-slate-900 text-white text-xs px-2 py-1 rounded-md";
        btn.appendChild(tip);
        setTimeout(function () {
          tip.remove();
        }, 1600);
      }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(done, function () {
          window.prompt("", url);
        });
      } else {
        window.prompt("", url);
      }
    });
  });
})();

// Sliders (products: two at a time, one on phones; homepage services: one at
// a time via data-per-view="1"): moves one step
// every data-interval seconds (set in Admin -> Products), loops back to the
// start, pauses while the pointer or keyboard focus is on it, and can be
// moved with the arrows, the dots or a swipe.
(function () {
  document.querySelectorAll(".product-carousel").forEach(function (root) {
    var track = root.querySelector(".product-track");
    var slides = root.querySelectorAll(".product-slide");
    var dotsBox = root.querySelector(".product-dots");
    var controls = root.querySelector(".product-controls");
    var seconds = parseFloat(root.getAttribute("data-interval")) || 5;
    var index = 0;
    var timer = null;
    var paused = false;

    var fixedPerView = parseInt(root.getAttribute("data-per-view"), 10);
    function perView() {
      if (fixedPerView) return fixedPerView;
      return window.matchMedia("(min-width: 768px)").matches ? 2 : 1;
    }
    function maxIndex() {
      return Math.max(0, slides.length - perView());
    }

    function renderDots() {
      if (!dotsBox) return;
      dotsBox.innerHTML = "";
      for (var i = 0; i <= maxIndex(); i++) {
        var dot = document.createElement("button");
        dot.type = "button";
        dot.setAttribute("aria-label", String(i + 1));
        dot.className = "h-2 rounded-full transition-all " + (i === index ? "w-6 bg-slate-900 dark:bg-white" : "w-2 bg-slate-300 dark:bg-slate-600");
        (function (i) {
          dot.addEventListener("click", function () {
            go(i);
            restart();
          });
        })(i);
        dotsBox.appendChild(dot);
      }
    }

    function go(i) {
      var max = maxIndex();
      index = i > max ? 0 : i < 0 ? max : i;
      track.style.transform = "translateX(-" + index * (100 / perView()) + "%)";
      slides.forEach(function (s, n) {
        var visible = n >= index && n < index + perView();
        s.toggleAttribute("aria-hidden", !visible);
      });
      renderDots();
    }

    function restart() {
      clearInterval(timer);
      if (maxIndex() === 0) return; // everything already fits — nothing to move
      timer = setInterval(function () {
        if (!paused && !document.hidden) go(index + 1);
      }, seconds * 1000);
    }

    function layout() {
      if (controls) controls.hidden = maxIndex() === 0;
      go(Math.min(index, maxIndex()));
      restart();
    }

    var prev = root.querySelector(".product-prev");
    var next = root.querySelector(".product-next");
    if (prev) prev.addEventListener("click", function () { go(index - 1); restart(); });
    if (next) next.addEventListener("click", function () { go(index + 1); restart(); });

    root.addEventListener("mouseenter", function () { paused = true; });
    root.addEventListener("mouseleave", function () { paused = false; });
    root.addEventListener("focusin", function () { paused = true; });
    root.addEventListener("focusout", function () { paused = false; });

    var startX = null;
    root.addEventListener("touchstart", function (e) { startX = e.touches[0].clientX; }, { passive: true });
    root.addEventListener("touchend", function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) { go(index + (dx < 0 ? 1 : -1)); restart(); }
      startX = null;
    });

    window.addEventListener("resize", layout);
    layout();
  });
})();

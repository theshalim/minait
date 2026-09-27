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

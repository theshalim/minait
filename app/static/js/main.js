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

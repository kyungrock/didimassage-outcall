function toggleMode() {
  document.body.classList.toggle("light-mode");
  localStorage.setItem(
    "site-mode",
    document.body.classList.contains("light-mode") ? "light" : "dark"
  );
}

function blogNavHref() {
  const path = window.location.pathname || "";
  if (path.includes("/blog/")) return "../blog.html";
  return path.endsWith("/") || path.endsWith("index.html") ? "blog.html" : "blog.html";
}

function injectBlogNavLink() {
  document.querySelectorAll(".top-nav").forEach((nav) => {
    if (nav.querySelector('a[href*="blog.html"]')) return;
    const a = document.createElement("a");
    a.href = blogNavHref();
    a.textContent = "블로그";
    nav.insertBefore(a, nav.firstChild);
  });
}

window.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("site-mode") === "light") {
    document.body.classList.add("light-mode");
  }
  injectBlogNavLink();
});

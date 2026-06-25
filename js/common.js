function blogNavHref() {
  const path = window.location.pathname || "";
  if (path.includes("/blog/")) return "../blog.html";
  return path.endsWith("/") || path.endsWith("index.html") ? "blog.html" : "blog.html";
}

function injectBlogNavLink() {
  document.querySelectorAll(".site-nav, .top-nav").forEach((nav) => {
    if (nav.querySelector('a[href*="blog.html"]')) return;
    const a = document.createElement("a");
    a.href = blogNavHref();
    a.textContent = "블로그";
    nav.appendChild(a);
  });
}

window.addEventListener("DOMContentLoaded", () => {
  injectBlogNavLink();
});

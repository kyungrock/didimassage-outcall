function toggleMode() {
  document.body.classList.toggle("light-mode");
  localStorage.setItem(
    "site-mode",
    document.body.classList.contains("light-mode") ? "light" : "dark"
  );
}

window.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("site-mode") === "light") {
    document.body.classList.add("light-mode");
  }
});

(function () {
  "use strict";

  function parsePriceMin(price) {
    var raw = String(price || "").split("~")[0];
    var digits = raw.replace(/[^\d]/g, "");
    return digits ? parseInt(digits, 10) : 999999;
  }

  function initAggregationSort() {
    var section = document.getElementById("shops");
    if (!section || section.dataset.pageType !== "aggregation") return;

    var grid = document.getElementById("shopCardsGrid");
    var toolbar = section.querySelector(".shop-agg-toolbar");
    if (!grid || !toolbar) return;

    var defaultOrder = Array.prototype.slice.call(grid.querySelectorAll(".shop-card"));

    toolbar.addEventListener("click", function (e) {
      var btn = e.target.closest(".shop-agg-btn");
      if (!btn) return;

      toolbar.querySelectorAll(".shop-agg-btn").forEach(function (b) {
        b.classList.remove("is-active");
      });
      btn.classList.add("is-active");

      var sort = btn.getAttribute("data-sort");
      var cards = Array.prototype.slice.call(grid.querySelectorAll(".shop-card"));

      if (sort === "default") {
        defaultOrder.forEach(function (card) {
          grid.appendChild(card);
        });
        return;
      }

      cards.sort(function (a, b) {
        var pa = parseInt(a.getAttribute("data-price-min") || "999999", 10);
        var pb = parseInt(b.getAttribute("data-price-min") || "999999", 10);
        return sort === "price-asc" ? pa - pb : pb - pa;
      });
      cards.forEach(function (card) {
        grid.appendChild(card);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAggregationSort);
  } else {
    initAggregationSort();
  }
})();

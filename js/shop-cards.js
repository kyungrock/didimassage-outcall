(function () {
  "use strict";

  function normalizeAreaText(value) {
    return (value || "")
      .toString()
      .trim()
      .replace(/특별자치도|특별시|광역시/g, "")
      .replace(/[^\p{L}\p{N}]/gu, "")
      .replace(/(시|구|군|읍|면|동|도)$/u, "");
  }

  function splitComposite(value) {
    return (value || "")
      .split(/[,\u00b7/]/g)
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function regionTokensMatch(shopRegion, pageRegion) {
    const pageNorm = normalizeAreaText(pageRegion);
    if (!pageNorm) return true;

    const shopPieces = splitComposite(shopRegion);
    if (!shopPieces.length) return false;

    return shopPieces.some((piece) => {
      const shopNorm = normalizeAreaText(piece);
      if (!shopNorm) return false;
      return (
        shopNorm === pageNorm ||
        shopNorm.includes(pageNorm) ||
        pageNorm.includes(shopNorm)
      );
    });
  }

  function districtTokensMatch(shopDistrict, pageDistrict) {
    const pageNorm = normalizeAreaText(pageDistrict);
    if (!pageNorm) return true;

    const pieces = splitComposite(shopDistrict);
    if (!pieces.length) return false;

    return pieces.some((piece) => {
      if (piece.includes("전지역")) return false;
      const pieceNorm = normalizeAreaText(piece);
      if (!pieceNorm) return false;
      return (
        pieceNorm === pageNorm ||
        pieceNorm.includes(pageNorm) ||
        pageNorm.includes(pieceNorm)
      );
    });
  }

  function districtServesPage(shop, pageRegion, pageDistrict) {
    if (!pageDistrict) return true;

    const shopDistrict = shop.district || "";
    if (districtTokensMatch(shopDistrict, pageDistrict)) return true;
    if (
      shopDistrict.includes("전지역") &&
      regionTokensMatch(shop.region, pageRegion)
    ) {
      return true;
    }
    if (!shopDistrict.trim() && regionTokensMatch(shop.region, pageRegion)) {
      return true;
    }
    return false;
  }

  function resolveImage(src) {
    if (!src) return "images/placeholder-shop.jpg";
    if (/^https?:\/\/msg1000\.com\/images\//i.test(src)) {
      src = src.replace(/^https?:\/\/msg1000\.com\//i, "");
    }
    if (src.startsWith("http")) return src;
    if (src.startsWith("/images/")) return src.slice(1);
    if (src.startsWith("images/")) return src;
    return src.startsWith("/") ? src.slice(1) : src;
  }

  function renderStars(rating) {
    const r = Math.round(Number(rating) || 0);
    return "★".repeat(Math.min(5, r)) + "☆".repeat(Math.max(0, 5 - r));
  }

  function isCapitalShop(shop) {
    return ["서울", "경기", "인천"].some((name) =>
      regionTokensMatch(shop.region, name)
    );
  }

  function filterShops(pageRegion, pageDistrict, capitalOnly) {
    const data = Array.isArray(window.outcallShopCardData)
      ? window.outcallShopCardData
      : [];
    if (!data.length) return [];

    return data.filter((shop) => {
      if (shop.type && shop.type !== "출장마사지") return false;
      if (capitalOnly && !isCapitalShop(shop)) return false;
      if (!regionTokensMatch(shop.region, pageRegion)) return false;
      return districtServesPage(shop, pageRegion, pageDistrict);
    });
  }

  function dedupeShops(shops) {
    const map = new Map();
    shops.forEach((shop) => {
      const key = shop.id || shop.name;
      if (!map.has(key)) map.set(key, shop);
    });
    return [...map.values()];
  }

  function buildDetailUrl(shop) {
    const params = new URLSearchParams();
    params.set("id", String(shop.id));
    if (shop.file) params.set("file", shop.file);
    return "shop-detail.html?" + params.toString();
  }

  function cleanLocationPart(value) {
    return (value || "")
      .split("·")
      .map(function (p) {
        return p.trim();
      })
      .filter(function (p) {
        return p && p !== "불가" && p !== "관리";
      })
      .join(" · ");
  }

  function formatShopLocation(shop, displayLabel) {
    const shopDistrict = shop.district || "";
    if (
      displayLabel &&
      (shopDistrict.includes("전지역") || !shopDistrict.trim())
    ) {
      return displayLabel + " 출장 가능";
    }
    let location = cleanLocationPart(shop.region);
    const district = cleanLocationPart(shopDistrict);
    const dong = cleanLocationPart(shop.dong);
    if (district) location += " · " + district;
    if (dong) location += " · " + dong;
    return location;
  }

  function cardImageAlt(shop, displayLabel) {
    const name = shop.name || "";
    const price = shop.price || "상담";
    let prefix = displayLabel;
    if (!prefix) {
      const region = (shop.region || "전국").split(",")[0].split("·")[0].trim();
      prefix = region || "전국";
    }
    return prefix + " 출장마사지 " + name + " - 24시간 후불, " + price;
  }

  function parsePriceMin(price) {
    const raw = String(price || "").split("~")[0];
    const digits = raw.replace(/[^\d]/g, "");
    return digits ? parseInt(digits, 10) : 999999;
  }

  function createCard(shop, displayLabel) {
    const link = document.createElement("a");
    link.className = "shop-card";
    link.href = buildDetailUrl(shop);
    link.setAttribute("aria-label", shop.name + " 상세보기");
    link.setAttribute("data-price-min", String(parsePriceMin(shop.price)));

    const imageWrap = document.createElement("div");
    imageWrap.className = "shop-card-image-wrap";

    const img = document.createElement("img");
    img.className = "shop-card-image";
    img.src = resolveImage(shop.image);
    img.alt = cardImageAlt(shop, displayLabel);
    img.loading = "lazy";
    img.decoding = "async";
    img.onerror = function () {
      this.onerror = null;
      this.src = "images/placeholder-shop.jpg";
    };
    imageWrap.appendChild(img);

    const badge = document.createElement("span");
    badge.className = "shop-card-badge";
    badge.textContent = "출장마사지";
    imageWrap.appendChild(badge);

    const body = document.createElement("div");
    body.className = "shop-card-body";

    const name = document.createElement("h3");
    name.className = "shop-card-name";
    name.textContent = shop.name;

    const meta = document.createElement("div");
    meta.className = "shop-card-meta";
    meta.innerHTML =
      '<span class="shop-card-rating">' +
      renderStars(shop.rating) +
      " " +
      (shop.rating || "-") +
      "</span>" +
      '<span class="shop-card-price">' +
      (shop.price || "상담") +
      "</span>";

    const location = document.createElement("p");
    location.className = "shop-card-location";
    location.textContent = formatShopLocation(shop, displayLabel);

    body.appendChild(name);
    body.appendChild(meta);
    body.appendChild(location);

    if (shop.greeting) {
      const greeting = document.createElement("p");
      greeting.className = "shop-card-greeting";
      greeting.textContent = shop.greeting;
      body.appendChild(greeting);
    }

    const tags = document.createElement("div");
    tags.className = "shop-card-tags";
    (shop.services || []).slice(0, 3).forEach((service) => {
      const tag = document.createElement("span");
      tag.className = "shop-card-tag";
      tag.textContent = service;
      tags.appendChild(tag);
    });
    if (tags.childElementCount) body.appendChild(tags);

    link.appendChild(imageWrap);
    link.appendChild(body);
    return link;
  }

  function renderShopCards() {
    const section = document.getElementById("shops");
    const grid = document.getElementById("shopCardsGrid");
    const countEl = document.getElementById("shopCardsCount");
    if (!section || !grid) return;

    const pageRegion = section.dataset.region || "";
    const pageDistrict = section.dataset.district || "";
    const displayLabel = section.dataset.regionLabel || "";
    const capitalOnly = section.dataset.capitalOnly === "true";
    const cacheKey = [pageRegion, pageDistrict, capitalOnly ? "capital" : ""].join("|");

    if (
      grid.dataset.renderedFor === cacheKey &&
      grid.querySelector(".shop-card")
    ) {
      const count = grid.querySelectorAll(".shop-card").length;
      if (countEl) countEl.textContent = count + "개 업체";
      return;
    }

    let shops = dedupeShops(filterShops(pageRegion, pageDistrict, capitalOnly));

    if (!shops.length && !pageRegion && !capitalOnly) {
      shops = dedupeShops(
        (window.outcallShopCardData || []).filter(
          (s) => !s.type || s.type === "출장마사지"
        )
      );
    }

    grid.innerHTML = "";
    if (countEl) countEl.textContent = shops.length + "개 업체";

    const emptyLabel = displayLabel || pageDistrict || pageRegion || "전국";

    if (!shops.length) {
      const empty = document.createElement("div");
      empty.className = "shop-cards-empty";
      empty.textContent =
        "현재 선택 지역(" +
        emptyLabel +
        ")에 등록된 출장마사지 업체가 없습니다.";
      grid.appendChild(empty);
      grid.dataset.renderedFor = cacheKey;
      return;
    }

    const labelForCards = pageDistrict ? displayLabel : "";
    shops.forEach((shop) =>
      grid.appendChild(createCard(shop, labelForCards))
    );
    grid.dataset.renderedFor = cacheKey;
  }

  window.renderShopCards = renderShopCards;
  window.addEventListener("DOMContentLoaded", renderShopCards);
})();

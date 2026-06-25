(function () {
  "use strict";

  function resolveImage(src) {
    if (!src) return "img/hero-brand.svg";
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

  function getQuery() {
    return new URLSearchParams(window.location.search);
  }

  function findCardById(cardId) {
    const list = window.outcallShopCardData || [];
    return list.find((s) => String(s.id) === String(cardId));
  }

  function findDetailByCard(card) {
    const payload = window.shopsOutcallDetail || { shops: [], index: [] };
    const idx = (payload.index || []).find(
      (e) => String(e.cardId) === String(card.id)
    );
    if (idx && idx.detail) return idx.detail;

    return (payload.shops || []).find((s) => s.name === card.name) || null;
  }

  function pickImage(card, detail) {
    const cardImg = card?.image;
    const detailImg = detail?.image;
    if (cardImg && cardImg.startsWith("images/")) return cardImg;
    if (detailImg && detailImg.startsWith("images/")) return detailImg;
    return detailImg || cardImg;
  }

  function mergeShopData(card, detail) {
    const reviews = detail?.reviews?.length
      ? detail.reviews.map((r) => ({
          author: r.name || r.author || "고객",
          rating: r.rating,
          date: r.date,
          review: r.comment || r.review || "",
        }))
      : card.reviews || [];

    return {
      name: detail?.name || card.name,
      type: detail?.type || card.type || "출장마사지",
      region: detail?.region || card.region,
      district: detail?.district || card.district,
      address: detail?.address || card.address,
      detailAddress: detail?.detailAddress || card.detailAddress,
      phone: detail?.phone || card.phone,
      price: detail?.price || card.price,
      operatingHours: detail?.operatingHours || card.operatingHours,
      rating: detail?.rating ?? card.rating,
      reviewCount: detail?.reviewCount ?? card.reviewCount ?? reviews.length,
      image: pickImage(card, detail),
      alt: card.alt || card.name,
      description: detail?.description || card.description,
      services: detail?.services || card.services || [],
      courses: detail?.courses || [],
      staffInfo: detail?.staffInfo || "",
      features: detail?.features || [],
      reviews: reviews,
      greeting: card.greeting || "",
    };
  }

  function renderCourses(courses) {
    const wrap = document.getElementById("shopCourses");
    if (!wrap) return;
    wrap.innerHTML = "";

    if (!courses || !courses.length) {
      wrap.innerHTML =
        '<p class="muted">코스 상세는 전화/카톡 상담 시 안내드립니다.</p>';
      return;
    }

    courses.forEach((cat) => {
      const block = document.createElement("article");
      block.className = "course-category";

      const title = document.createElement("h3");
      title.className = "course-category-title";
      title.textContent = cat.category;
      block.appendChild(title);

      (cat.items || []).forEach((item) => {
        const row = document.createElement("div");
        row.className = "course-item";
        row.innerHTML =
          '<div class="course-item-head">' +
          '<span class="course-item-name">' +
          (item.name || "") +
          "</span>" +
          '<span class="course-item-duration">' +
          (item.duration || "") +
          "</span>" +
          '<span class="course-item-price">' +
          (item.price || "") +
          "</span>" +
          "</div>" +
          (item.description
            ? '<div class="course-item-desc">' + item.description + "</div>"
            : "");
        block.appendChild(row);
      });

      wrap.appendChild(block);
    });
  }

  function renderReviews(reviews) {
    const wrap = document.getElementById("shopReviews");
    if (!wrap) return;
    wrap.innerHTML = "";

    if (!reviews || !reviews.length) {
      wrap.innerHTML = '<p class="muted">등록된 리뷰가 없습니다.</p>';
      return;
    }

    reviews.forEach((r) => {
      const item = document.createElement("div");
      item.className = "review-item";
      item.innerHTML =
        '<div class="review-head">' +
        '<span class="review-author">' +
        (r.author || r.name || "고객") +
        "</span>" +
        '<span class="review-date">' +
        (r.date || "") +
        "</span>" +
        "</div>" +
        '<div class="review-stars">' +
        renderStars(r.rating) +
        "</div>" +
        '<p class="review-text">' +
        (r.review || r.comment || "") +
        "</p>";
      wrap.appendChild(item);
    });
  }

  function renderFeatures(features) {
    const wrap = document.getElementById("shopFeatures");
    if (!wrap) return;
    wrap.innerHTML = "";
    if (!features || !features.length) {
      wrap.closest("section")?.classList.add("hidden");
      return;
    }
    features.forEach((f) => {
      const tag = document.createElement("span");
      tag.className = "feature-tag";
      tag.textContent = f;
      wrap.appendChild(tag);
    });
  }

  function renderDetail() {
    const params = getQuery();
    const cardId = params.get("id");
    const card = cardId ? findCardById(cardId) : null;

    if (!card) {
      document.getElementById("shopDetailRoot").innerHTML =
        '<div class="container"><div class="card"><h1>업체를 찾을 수 없습니다</h1><p class="muted"><a href="index.html">메인으로</a></p></div></div>';
      return;
    }

    const detail = findDetailByCard(card);
    const shop = mergeShopData(card, detail);

    document.title = shop.name + " 출장마사지 상세 | 20대, 30대 힐링 출장마사지";

    const meta = document.querySelector('meta[name="description"]');
    if (meta) {
      meta.setAttribute(
        "content",
        (shop.region || "") +
          " " +
          (shop.district || "") +
          " " +
          shop.name +
          " 출장마사지. " +
          (shop.price || "") +
          " · " +
          (shop.operatingHours || "")
      );
    }

    const heroImg = document.getElementById("shopHeroImage");
    if (heroImg) {
      heroImg.src = resolveImage(shop.image);
      heroImg.alt = shop.alt || shop.name;
    }

    document.getElementById("shopName").textContent = shop.name;
    document.getElementById("shopDistrict").textContent =
      (shop.region || "") + " · " + (shop.district || "");
    document.getElementById("shopRatingText").textContent =
      (shop.rating || "-") +
      " (" +
      (shop.reviewCount ? shop.reviewCount + "개 리뷰" : "리뷰 없음") +
      ")";
    document.getElementById("shopStars").textContent = renderStars(shop.rating);
    document.getElementById("shopDescription").textContent = shop.description || "";

    document.getElementById("shopAddress").textContent = shop.address || "-";
    document.getElementById("shopDetailAddress").textContent =
      shop.detailAddress || "";
    document.getElementById("shopPhone").innerHTML =
      '<a href="tel:' +
      (shop.phone || "").replace(/-/g, "") +
      '">' +
      (shop.phone || "-") +
      "</a>";
    document.getElementById("shopHours").textContent =
      shop.operatingHours || "-";
    document.getElementById("shopPrice").textContent = shop.price || "상담";

    const callBtn = document.getElementById("shopCallBtn");
    if (callBtn && shop.phone) {
      callBtn.href = "tel:" + shop.phone.replace(/-/g, "");
    }

    const staff = document.getElementById("shopStaff");
    if (staff) {
      if (shop.staffInfo) {
        staff.textContent = shop.staffInfo;
      } else {
        staff.closest("section")?.classList.add("hidden");
      }
    }

    renderCourses(shop.courses);
    renderReviews(shop.reviews);
    renderFeatures(shop.features);

    const back = document.getElementById("shopBackBtn");
    if (back && document.referrer && document.referrer.includes(location.host)) {
      back.href = document.referrer;
    }
  }

  window.addEventListener("DOMContentLoaded", renderDetail);
})();

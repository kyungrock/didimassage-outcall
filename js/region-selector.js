(function () {
  "use strict";

  const MOBILE_MQ = window.matchMedia("(max-width: 720px)");

  function getBar() {
    return document.getElementById("regionSelectorBar");
  }

  function getMetroSelect() {
    return document.getElementById("metroSelect");
  }

  function getDistrictSelect() {
    return document.getElementById("districtSelect");
  }

  function getMetros() {
    return (window.regionsData && window.regionsData.metros) || [];
  }

  function findMetro(metroId) {
    return getMetros().find((m) => m.id === metroId) || null;
  }

  function isMobile() {
    return MOBILE_MQ.matches;
  }

  function formatMetroAdmin(name, type) {
    if (!name) return "";
    if (type === "특별시") return name + " 특별시";
    if (type === "광역시") return name + "광역시";
    if (type === "특별자치도") return name + "특별자치도";
    if (type === "도") return name + "도";
    return name;
  }

  function metroLabel(metro) {
    if (!metro) return "";
    return metro.label || formatMetroAdmin(metro.name, metro.type);
  }

  function shortMetroName(text) {
    return (text || "")
      .replace(/\s*(특별시|광역시|특별자치도|도)\s*$/u, "")
      .trim();
  }

  function getSelectedLabel(select) {
    if (!select || !select.value) return "";
    const opt = select.options[select.selectedIndex];
    return opt ? opt.textContent.trim() : "";
  }

  function updateCompactText() {
    const textEl = document.getElementById("regionCompactText");
    if (!textEl) return;

    const metro = findMetro(getMetroSelect()?.value);
    const metroLabelText = metro ? metroLabel(metro) : shortMetroName(getSelectedLabel(getMetroSelect()));
    const districtLabel = getSelectedLabel(getDistrictSelect());

    if (metroLabelText && districtLabel && getDistrictSelect()?.value) {
      textEl.textContent = metroLabelText + " · " + districtLabel + " 선택중";
    } else if (metroLabelText) {
      textEl.textContent = metroLabelText + " · 구/시 선택";
    } else {
      textEl.textContent = "지역 · 구 선택";
    }
  }

  function setPanelExpanded(expanded) {
    const panel = document.getElementById("regionPickerPanel");
    const bar = getBar();
    const btn = document.getElementById("regionCompactBtn");
    if (!panel || !bar) return;

    if (!isMobile()) {
      panel.classList.remove("region-picker-panel--collapsed");
      bar.classList.remove("is-collapsed");
      if (btn) btn.setAttribute("aria-expanded", "true");
      return;
    }

    panel.classList.toggle("region-picker-panel--collapsed", !expanded);
    bar.classList.toggle("is-collapsed", !expanded);
    if (btn) btn.setAttribute("aria-expanded", String(expanded));
  }

  function collapseIfHasSelection() {
    if (!isMobile()) return;
    const hasMetro = Boolean(getMetroSelect()?.value);
    setPanelExpanded(!hasMetro);
  }

  function fillMetroOptions(selectedId) {
    const select = getMetroSelect();
    if (!select) return;

    select.innerHTML = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "지역 선택 (서울·경기·인천…)";
    select.appendChild(placeholder);

    getMetros().forEach((metro) => {
      const opt = document.createElement("option");
      opt.value = metro.id;
      opt.textContent = metroLabel(metro);
      if (metro.id === selectedId) opt.selected = true;
      select.appendChild(opt);
    });
    updateCompactText();
  }

  function fillDistrictOptions(metroId, selectedSlug) {
    const select = getDistrictSelect();
    if (!select) return;

    select.innerHTML = "";
    const metro = findMetro(metroId);

    if (!metro) {
      select.disabled = true;
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "먼저 지역을 선택하세요";
      select.appendChild(opt);
      updateCompactText();
      return;
    }

    select.disabled = false;
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "구/시 선택";
    select.appendChild(placeholder);

    (metro.areas || []).forEach((area) => {
      const opt = document.createElement("option");
      opt.value = area.slug;
      opt.textContent = area.name;
      if (area.slug === selectedSlug) opt.selected = true;
      select.appendChild(opt);
    });
    updateCompactText();
  }

  function updateShopRegion(metroId, regionName, districtShort) {
    const shops = document.getElementById("shops");
    if (!shops) return;

    shops.dataset.metro = metroId || "";
    shops.dataset.region = regionName || "";
    shops.dataset.district = districtShort || "";

    const title = document.getElementById("shopCardsTitle");
    if (title) {
      const metro = findMetro(metroId);
      if (regionName && districtShort) {
        title.textContent =
          "💆 " + regionName + " " + districtShort + " 출장마사지 업체";
      } else if (metro) {
        title.textContent = "💆 " + metroLabel(metro) + " 업체";
      } else {
        title.textContent = "💆 전국 출장마사지 업체";
      }
    }

    if (typeof window.renderShopCards === "function") {
      window.renderShopCards();
    }
  }

  function getCurrentPage() {
    const path = location.pathname.split("/").pop();
    return path || "index.html";
  }

  function navigateToMetro(metroId) {
    if (!metroId) {
      if (getCurrentPage() !== "index.html") {
        location.href = "index.html#shops";
      } else {
        updateShopRegion("", "", "");
        setPanelExpanded(false);
        document.getElementById("shops")?.scrollIntoView({ behavior: "smooth" });
      }
      return;
    }

    const target = metroId + ".html";
    const current = getCurrentPage();

    if (current === target) {
      const metro = findMetro(metroId);
      fillDistrictOptions(metroId, "");
      if (metro) {
        updateShopRegion(metroId, metro.name, "");
      }
      setPanelExpanded(false);
      document.getElementById("shops")?.scrollIntoView({ behavior: "smooth" });
      return;
    }

    location.href = target + "#shops";
  }

  function navigateToArea(slug) {
    if (!slug) return;
    const current = location.pathname.split("/").pop();
    if (current === slug + ".html") {
      setPanelExpanded(false);
      document.getElementById("shops")?.scrollIntoView({ behavior: "smooth" });
      return;
    }
    location.href = slug + ".html#shops";
  }

  function applySelection() {
    const metroSelect = getMetroSelect();
    const districtSelect = getDistrictSelect();
    if (!metroSelect || !districtSelect) return;

    const metroId = metroSelect.value;
    const slug = districtSelect.value;
    const metro = findMetro(metroId);

    if (slug) {
      navigateToArea(slug);
      return;
    }

    if (metro) {
      navigateToMetro(metroId);
    }
  }

  function onMetroChange() {
    const metroId = getMetroSelect().value;
    if (!metroId) {
      fillDistrictOptions("", "");
      navigateToMetro("");
      return;
    }
    navigateToMetro(metroId);
  }

  function onDistrictChange() {
    const slug = getDistrictSelect().value;
    updateCompactText();
    if (slug) {
      navigateToArea(slug);
    }
  }

  function onCompactClick() {
    const panel = document.getElementById("regionPickerPanel");
    const isCollapsed = panel?.classList.contains(
      "region-picker-panel--collapsed"
    );
    setPanelExpanded(Boolean(isCollapsed));
    if (isCollapsed) {
      getMetroSelect()?.focus();
    }
  }

  function init() {
    const bar = getBar();
    if (!bar) return;

    const metroId = bar.dataset.metroId || "";
    const slug = bar.dataset.slug || "";

    fillMetroOptions(metroId);
    fillDistrictOptions(metroId, slug);

    if (metroId) {
      const metro = findMetro(metroId);
      let districtShort = "";
      if (slug) {
        const area = metro?.areas?.find((a) => a.slug === slug);
        districtShort = area?.short || area?.name || "";
      }
      if (metro) {
        updateShopRegion(metroId, metro.name, districtShort);
      }
    }

    getMetroSelect()?.addEventListener("change", onMetroChange);
    getDistrictSelect()?.addEventListener("change", onDistrictChange);
    document
      .getElementById("regionSearchBtn")
      ?.addEventListener("click", applySelection);
    document
      .getElementById("regionCompactBtn")
      ?.addEventListener("click", onCompactClick);

    MOBILE_MQ.addEventListener("change", () => {
      collapseIfHasSelection();
      updateCompactText();
    });

    collapseIfHasSelection();
    updateCompactText();

    if (location.hash === "#shops") {
      setTimeout(() => {
        document.getElementById("shops")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
  }

  window.addEventListener("DOMContentLoaded", init);
})();

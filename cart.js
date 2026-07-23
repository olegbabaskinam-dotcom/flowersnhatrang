/* ============================================================
   КОРЗИНА — общий скрипт (localStorage), подключается на страницах
   каталога, главной, наборов, тортов, товара.
   Делает 3 вещи:
     1) хранит корзину (flw_cart) и даёт window.Cart API;
     2) сам вставляет кнопку «В корзину» в карточки .product-card;
     3) рисует плавающий мини-виджет корзины (справа снизу) со счётчиком.
   ============================================================ */
(function () {
  var LS = "flw_cart";
  var ROSE = "#c0687a", ROSE_D = "#a94f63";

  // Курсы: сколько ДОНГОВ за 1 единицу валюты (базовая — донг).
  window.FLW_CFG = {
    rates: { VND: 1, USD: 25000, RUB: 290, KZT: 50 },
    sym:   { VND: "₫", USD: "$",  RUB: "₽",  KZT: "₸" },
    order: ["VND", "USD", "RUB", "KZT"],
    names: { VND: "Донги", USD: "Доллары", RUB: "Рубли", KZT: "Тенге" }
  };

  function read() { try { return JSON.parse(localStorage.getItem(LS)) || []; } catch (_) { return []; } }
  function write(c) { localStorage.setItem(LS, JSON.stringify(c)); document.dispatchEvent(new Event("cart:change")); }

  var Cart = {
    items: read,
    count: function () { return read().reduce(function (s, i) { return s + i.qty; }, 0); },
    total: function () { return read().reduce(function (s, i) { return s + i.price * i.qty; }, 0); }, // в ₫
    add: function (it) {
      var c = read();
      var ex = c.filter(function (x) { return x.id === it.id; })[0];
      if (ex) ex.qty += (it.qty || 1);
      else c.push({ id: it.id, name: it.name, price: it.price, img: it.img, cat: it.cat, qty: it.qty || 1 });
      write(c);
    },
    setQty: function (id, q) {
      var c = read();
      c = c.map(function (x) { if (x.id === id) x.qty = Math.max(1, q); return x; });
      write(c);
    },
    remove: function (id) { write(read().filter(function (x) { return x.id !== id; })); },
    clear: function () { write([]); }
  };
  window.Cart = Cart;

  // ---- конвертация/формат валюты ----
  window.fmtMoney = function (vnd, cur) {
    var r = window.FLW_CFG.rates[cur] || 1, s = window.FLW_CFG.sym[cur] || "₫";
    var v = vnd / r;
    var rounded = cur === "VND" ? Math.round(v / 1000) * 1000
               : cur === "USD" ? Math.round(v)
               : cur === "KZT" ? Math.round(v / 100) * 100
               : Math.round(v / 10) * 10; // RUB
    var str = rounded.toLocaleString("ru-RU").replace(/,/g, " ");
    return cur === "USD" ? (s + str) : (str + " " + s);
  };

  // ---- toast ----
  function toast(msg) {
    var t = document.getElementById("flw-toast");
    if (!t) {
      t = document.createElement("div"); t.id = "flw-toast";
      t.style.cssText = "position:fixed;left:50%;bottom:88px;transform:translateX(-50%);background:#292524;color:#fff;padding:11px 18px;border-radius:12px;font:600 14px system-ui;z-index:9999;opacity:0;transition:.25s;box-shadow:0 6px 20px rgba(0,0,0,.25);white-space:nowrap";
      document.body.appendChild(t);
    }
    t.textContent = msg; t.style.opacity = "1";
    clearTimeout(t._h); t._h = setTimeout(function () { t.style.opacity = "0"; }, 1800);
  }

  // ---- плавающий мини-виджет ----
  function fab() {
    var f = document.getElementById("flw-fab");
    if (!f) {
      f = document.createElement("a"); f.id = "flw-fab"; f.href = "cart.html";
      f.setAttribute("aria-label", "Корзина");
      f.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:9998;display:none;align-items:center;gap:8px;background:" + ROSE + ";color:#fff;text-decoration:none;padding:12px 16px;border-radius:999px;font:700 14px system-ui;box-shadow:0 6px 20px rgba(192,104,122,.45)";
      f.innerHTML = '<span style="font-size:18px">🛒</span><span>Корзина</span><span id="flw-fab-c" style="background:#fff;color:' + ROSE_D + ';border-radius:999px;min-width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-size:13px;padding:0 6px"></span>';
      document.body.appendChild(f);
    }
    var n = Cart.count();
    document.getElementById("flw-fab-c").textContent = n;
    f.style.display = n > 0 ? "flex" : "none";
  }

  // ---- вставка кнопок «В корзину» в карточки каталога ----
  function parseCard(card) {
    var a = card.querySelector("a[href*='catalog/']");
    if (!a) return null;
    var m = a.getAttribute("href").match(/catalog\/(.+?)-(?:ru|en|ko)\.html/);
    var id = m ? m[1] : (a.getAttribute("href"));
    var h3 = card.querySelector("h3");
    var priceEl = card.querySelector("a .font-bold");
    var img = card.querySelector(".pcard-slide");
    var price = priceEl ? parseInt((priceEl.textContent || "").replace(/[^\d]/g, ""), 10) : 0;
    return {
      id: id,
      name: h3 ? h3.textContent.trim() : "Товар",
      price: price || 0,
      img: img ? img.getAttribute("src") : "",
      cat: card.getAttribute("data-cat") || ""
    };
  }
  function injectButtons() {
    document.querySelectorAll(".product-card").forEach(function (card) {
      if (card.querySelector(".flw-add")) return;
      var d = parseCard(card);
      if (!d || !d.price) return;
      var isCake = /(^|\s)cakes(\s|$)/.test(d.cat);
      var btn = document.createElement("button");
      btn.type = "button"; btn.className = "flw-add";
      btn.textContent = isCake ? "🎂 Добавить к заказу" : "🛒 В корзину";
      btn.style.cssText = "display:block;width:calc(100% - 2.5rem);margin:0 1.25rem 1.25rem;padding:11px;border:none;border-radius:.75rem;background:" + ROSE + ";color:#fff;font:600 13px system-ui;cursor:pointer";
      btn.addEventListener("mouseenter", function () { btn.style.background = ROSE_D; });
      btn.addEventListener("mouseleave", function () { btn.style.background = ROSE; });
      btn.addEventListener("click", function (e) {
        e.preventDefault(); e.stopPropagation();
        Cart.add(d);
        toast("Добавлено ✓ " + d.name);
      });
      card.appendChild(btn);
    });
  }

  function refresh() { fab(); }
  document.addEventListener("cart:change", refresh);
  document.addEventListener("DOMContentLoaded", function () {
    injectButtons(); fab();
    // каталог может дорисовывать карточки/сортировать — периодически проверяем
    var n = 0; var iv = setInterval(function () { injectButtons(); if (++n > 10) clearInterval(iv); }, 400);
  });
})();

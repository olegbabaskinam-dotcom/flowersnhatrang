/* ============================================================
   КОРЗИНА — общий скрипт (localStorage). Подключается на страницах
   каталога, главной, наборов, тортов, шаров и товара (RU/EN/KO).
     1) хранит корзину (flw_cart) + window.Cart API;
     2) вставляет кнопку «В корзину» в карточки .product-card и на страницу товара;
     3) плавающий мини-виджет корзины + пункты меню; надписи локализованы.
   ============================================================ */
(function () {
  var LS = "flw_cart";
  var ROSE = "#c0687a", ROSE_D = "#a94f63";

  // товары лежат в /catalog/<slug>-<lang>.html → путь до корня "../"
  var BASE = /\/catalog\//.test(location.pathname) ? "../" : "";

  // ---- язык страницы ----
  function pageLang() {
    var l = (document.documentElement.getAttribute("lang") || "").toLowerCase();
    if (l.indexOf("en") === 0) return "en";
    if (l.indexOf("ko") === 0 || l.indexOf("kr") === 0) return "ko";
    var p = location.pathname;
    if (/-en\.html|catalog-en|index-en|balloons-en|torty-en|nabory-en/.test(p)) return "en";
    if (/-ko\.html|-kr\.html|catalog-ko|index-kr|balloons-kr|torty-kr|nabory-kr/.test(p)) return "ko";
    return "ru";
  }
  var LBL = {
    ru: { add:"🛒 В корзину", addcake:"🎂 Добавить к заказу", added:"Добавлено ✓", cart:"🛒 Корзина", order:"🧾 Оформить заказ", fab:"Корзина" },
    en: { add:"🛒 Add to cart", addcake:"🎂 Add to order", added:"Added ✓", cart:"🛒 Cart", order:"🧾 Order online", fab:"Cart" },
    ko: { add:"🛒 장바구니에 담기", addcake:"🎂 주문에 추가", added:"담김 ✓", cart:"🛒 장바구니", order:"🧾 주문하기", fab:"장바구니" }
  };
  function L() { return LBL[pageLang()]; }

  // Курсы: сколько ДОНГОВ за 1 единицу (базовая — донг).
  window.FLW_CFG = {
    rates: { VND: 1, USD: 25000, RUB: 290, KZT: 50 },
    sym:   { VND: "₫", USD: "$",  RUB: "₽",  KZT: "₸" },
    order: ["VND", "USD", "RUB", "KZT"],
    names: { VND: "Донги", USD: "Доллары", RUB: "Рубли", KZT: "Тенге" }
  };

  function read() { try { return JSON.parse(localStorage.getItem(LS)) || []; } catch (_) { return []; } }
  function write(c) { localStorage.setItem(LS, JSON.stringify(c)); document.dispatchEvent(new Event("cart:change")); }
  function normImg(s) { return String(s || "").replace(/^(\.\.\/)+/, ""); } // пути к корню

  var Cart = {
    items: read,
    count: function () { return read().reduce(function (s, i) { return s + i.qty; }, 0); },
    total: function () { return read().reduce(function (s, i) { return s + i.price * i.qty; }, 0); },
    add: function (it) {
      var c = read();
      var ex = c.filter(function (x) { return x.id === it.id; })[0];
      if (ex) ex.qty += (it.qty || 1);
      else c.push({ id: it.id, name: it.name, price: it.price, img: normImg(it.img), cat: it.cat, qty: it.qty || 1 });
      write(c);
    },
    setQty: function (id, q) { write(read().map(function (x) { if (x.id === id) x.qty = Math.max(1, q); return x; })); },
    remove: function (id) { write(read().filter(function (x) { return x.id !== id; })); },
    clear: function () { write([]); }
  };
  window.Cart = Cart;

  window.fmtMoney = function (vnd, cur) {
    var r = window.FLW_CFG.rates[cur] || 1, s = window.FLW_CFG.sym[cur] || "₫";
    var v = vnd / r;
    var rounded = cur === "VND" ? Math.round(v / 1000) * 1000
               : cur === "USD" ? Math.round(v)
               : cur === "KZT" ? Math.round(v / 100) * 100
               : Math.round(v / 10) * 10;
    var str = rounded.toLocaleString("ru-RU").replace(/,/g, " ");
    return cur === "USD" ? (s + str) : (str + " " + s);
  };

  function toast(msg) {
    var t = document.getElementById("flw-toast");
    if (!t) {
      t = document.createElement("div"); t.id = "flw-toast";
      t.style.cssText = "position:fixed;left:50%;bottom:88px;transform:translateX(-50%);background:#292524;color:#fff;padding:11px 18px;border-radius:12px;font:600 14px system-ui;z-index:9999;opacity:0;transition:.25s;box-shadow:0 6px 20px rgba(0,0,0,.25);max-width:90%;text-align:center";
      document.body.appendChild(t);
    }
    t.textContent = msg; t.style.opacity = "1";
    clearTimeout(t._h); t._h = setTimeout(function () { t.style.opacity = "0"; }, 1800);
  }

  function fab() {
    var f = document.getElementById("flw-fab");
    if (!f) {
      f = document.createElement("a"); f.id = "flw-fab"; f.href = BASE + "cart.html";
      f.setAttribute("aria-label", "Cart");
      f.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:9998;display:none;align-items:center;gap:8px;background:" + ROSE + ";color:#fff;text-decoration:none;padding:12px 16px;border-radius:999px;font:700 14px system-ui;box-shadow:0 6px 20px rgba(192,104,122,.45)";
      f.innerHTML = '<span style="font-size:18px">🛒</span><span>' + L().fab + '</span><span id="flw-fab-c" style="background:#fff;color:' + ROSE_D + ';border-radius:999px;min-width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-size:13px;padding:0 6px"></span>';
      document.body.appendChild(f);
    }
    var n = Cart.count();
    document.getElementById("flw-fab-c").textContent = n;
    f.style.display = n > 0 ? "flex" : "none";
  }

  // карточки каталога
  function parseCard(card) {
    var a = card.querySelector("a[href*='catalog/']");
    if (!a) return null;
    var m = a.getAttribute("href").match(/catalog\/(.+?)-(?:ru|en|ko)\.html/);
    var id = m ? m[1] : a.getAttribute("href");
    var h3 = card.querySelector("h3");
    var priceEl = card.querySelector("a p.font-bold") || card.querySelector("a .font-bold"); // цена = <p>, не заголовок
    var img = card.querySelector(".pcard-slide");
    var price = priceEl ? parseInt((priceEl.textContent || "").replace(/[^\d]/g, ""), 10) : 0;
    return { id: id, name: h3 ? h3.textContent.trim() : "Товар", price: price || 0,
             img: img ? img.getAttribute("src") : "", cat: card.getAttribute("data-cat") || "" };
  }
  function mkBtn(d, wide) {
    var isCake = /(^|\s)cakes(\s|$)/.test(d.cat) || /^(tort|cake)/.test(d.id);
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = wide ? "flw-add-detail" : "flw-add";
    btn.textContent = isCake ? L().addcake : L().add;
    var m = wide ? "0 0 12px" : "0 1.25rem 1.25rem";
    var w = wide ? "100%" : "calc(100% - 2.5rem)";
    btn.style.cssText = "display:block;width:" + w + ";margin:" + m + ";padding:" + (wide ? "14px" : "11px") + ";border:none;border-radius:.75rem;background:" + ROSE + ";color:#fff;font:700 " + (wide ? "15px" : "13px") + " system-ui;cursor:pointer";
    btn.addEventListener("mouseenter", function () { btn.style.background = ROSE_D; });
    btn.addEventListener("mouseleave", function () { btn.style.background = ROSE; });
    btn.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); Cart.add(d); toast(L().added + " " + d.name); });
    return btn;
  }
  function injectButtons() {
    document.querySelectorAll(".product-card").forEach(function (card) {
      if (card.querySelector(".flw-add")) return;
      var d = parseCard(card);
      if (!d || !d.price) return;
      // «подробнее» делаем вторичной кнопкой (контур), чтобы не было двух одинаковых
      var det = card.querySelector(".btn-rose-filled");
      if (det) {
        det.className = "flw-det";
        det.style.cssText = "display:block;text-align:center;border:1px solid #e3c4cd;color:#a94f63;background:#fff;font-weight:600;padding:10px 16px;border-radius:.75rem;font-size:12px;";
      }
      card.appendChild(mkBtn(d, false));
    });
  }

  // страница товара (detail): цена в .price-box
  function injectProductPage() {
    var pb = document.querySelector(".price-box");
    if (!pb || document.querySelector(".flw-add-detail")) return;
    var m = location.pathname.match(/catalog\/(.+?)-(?:ru|en|ko)\.html/);
    var id = m ? m[1] : location.pathname;
    var h1 = document.querySelector("h1");
    var priceEl = pb.querySelector(".font-bold");
    var price = priceEl ? parseInt((priceEl.textContent || "").replace(/[^\d]/g, ""), 10) : 0;
    if (!price) return;
    var img = document.querySelector(".pcard-slide");
    var d = { id: id, name: h1 ? h1.textContent.trim() : "Товар", price: price,
              img: img ? img.getAttribute("src") : "", cat: /^(tort|cake)/.test(id) ? "cakes" : "" };
    pb.parentNode.insertBefore(mkBtn(d, true), pb.nextSibling);
  }

  // пункты меню «Оформить заказ» + «Корзина» (десктоп-nav и мобильное #mnav)
  function injectNav() {
    var nav = document.querySelector("header nav");
    if (nav && !nav.querySelector(".flw-nav")) {
      var sep = nav.querySelector("span.w-px");
      var mk = function (href, label) {
        var a = document.createElement("a"); a.href = BASE + href;
        a.className = "flw-nav px-3 py-1.5 rounded-lg text-xs font-medium text-stone-500 hover:text-[#c0687a] hover:bg-stone-50 transition";
        a.textContent = label; return a;
      };
      var lq = pageLang()!=="ru" ? ("?lang="+pageLang()) : "";
      var l1 = mk("order.html"+lq, L().order), l2 = mk("cart.html"+lq, L().cart);
      if (sep) { nav.insertBefore(l2, sep); nav.insertBefore(l1, l2); }
      else { nav.appendChild(l1); nav.appendChild(l2); }
    }
    var mm = document.getElementById("mnav");
    if (mm && !mm.querySelector(".flw-mnav")) {
      var st = "display:block;padding:10px 8px;border-radius:8px;text-decoration:none;color:#57534e";
      var lq2 = pageLang()!=="ru" ? ("?lang="+pageLang()) : "";
      mm.insertAdjacentHTML("afterbegin",
        '<a href="' + BASE + 'order.html' + lq2 + '" class="flw-mnav" style="' + st + '">' + L().order + '</a>' +
        '<a href="' + BASE + 'cart.html' + lq2 + '" class="flw-mnav" style="' + st + '">' + L().cart + '</a>');
    }
  }

  document.addEventListener("cart:change", fab);
  document.addEventListener("DOMContentLoaded", function () {
    try { localStorage.setItem("flw_lang", pageLang()); } catch (e) {}
    injectButtons(); injectProductPage(); injectNav(); fab();
    var n = 0, iv = setInterval(function () { injectButtons(); if (++n > 10) clearInterval(iv); }, 400);
  });
})();

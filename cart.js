/* Градиент Instagram для цветных иконок (30.09.2026) */
(function(){function a(){try{if(document.getElementById('igGradDefs'))return;document.body.insertAdjacentHTML('afterbegin','<svg id="igGradDefs" width="0" height="0" style="position:absolute;width:0;height:0" aria-hidden="true"><defs><radialGradient id="igGrad" cx="30%" cy="107%" r="150%"><stop offset="0" stop-color="#fdf497"/><stop offset=".05" stop-color="#fdf497"/><stop offset=".45" stop-color="#fd5949"/><stop offset=".6" stop-color="#d6249f"/><stop offset=".9" stop-color="#285AEB"/></radialGradient></defs></svg>');}catch(e){}}if(document.body)a();else document.addEventListener('DOMContentLoaded',a);})();
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
    ru: { add:"🛒 В корзину", addcake:"🎂 Добавить к заказу", added:"Добавлено ✓", cart:"🛒 Корзина", order:"🧾 Оформить заказ", fab:"Корзина", schedule:"📅 Важно: 3 сентября онлайн-заказы принимаем до 14:00. 4 сентября — выходной. С 5 сентября работаем в обычном режиме.", closed:"📅 Онлайн-заказы закрыты до 5 сентября: 4 сентября мы не работаем. С 5 сентября — обычный режим." },
    en: { add:"🛒 Add to cart", addcake:"🎂 Add to order", added:"Added ✓", cart:"🛒 Cart", order:"🧾 Order online", fab:"Cart", schedule:"📅 Important: online orders are accepted until 14:00 on September 3. We are closed on September 4 and return to normal hours on September 5.", closed:"📅 Online ordering is closed until September 5: we are closed on September 4. Normal hours resume September 5." },
    ko: { add:"🛒 장바구니에 담기", addcake:"🎂 주문에 추가", added:"담김 ✓", cart:"🛒 장바구니", order:"🧾 주문하기", fab:"장바구니", schedule:"📅 중요: 9월 3일 온라인 주문은 14:00까지 접수합니다. 9월 4일은 휴무이며 9월 5일부터 정상 운영합니다.", closed:"📅 온라인 주문은 9월 5일까지 마감되었습니다. 9월 4일은 휴무이며 9월 5일부터 정상 운영합니다." }
  };
  function L() { return LBL[pageLang()]; }

  // Курсы: сколько ДОНГОВ за 1 единицу (базовая — донг).
  window.FLW_CFG = {
    rates: { VND: 1, USD: 25000, RUB: 270, KRW: 18.8 },
    sym:   { VND: "₫", USD: "$",  RUB: "₽",  KRW: "₩" },
    order: ["VND", "USD", "RUB", "KRW"],
    names: { VND: "Донги", USD: "Доллары", RUB: "Рубли", KRW: "Воны" },
    namesL: {
      ru: { VND: "Донги", USD: "Доллары", RUB: "Рубли", KRW: "Воны" },
      en: { VND: "Dong", USD: "Dollars", RUB: "Rubles", KRW: "Won" },
      ko: { VND: "동", USD: "달러", RUB: "루블", KRW: "원" }
    }
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
               : cur === "KRW" ? Math.round(v / 100) * 100
               : cur === "RUB" ? Math.ceil(v / 100) * 100
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
      f = document.createElement("a"); f.id = "flw-fab"; f.href = BASE + "cart.html" + (pageLang()!=="ru" ? ("?lang="+pageLang()) : "");
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
      // в статичном мобильном меню уже есть «🛒 Корзина» внизу — убираем её, чтобы не было двух корзин
      mm.querySelectorAll('a[href$="cart.html"], a[href*="cart.html?"]').forEach(function (x) { if (!x.classList.contains("flw-mnav")) x.remove(); });
      var st = "display:block;padding:10px 8px;border-radius:8px;text-decoration:none;color:#57534e";
      var lq2 = pageLang()!=="ru" ? ("?lang="+pageLang()) : "";
      mm.insertAdjacentHTML("afterbegin",
        '<a href="' + BASE + 'order.html' + lq2 + '" class="flw-mnav" style="' + st + '">' + L().order + '</a>' +
        '<a href="' + BASE + 'cart.html' + lq2 + '" class="flw-mnav" style="' + st + '">' + L().cart + '</a>');
    }
  }

  // Временный график 3–4 сентября 2026 (время Нячанга). После 5 сентября баннер исчезает сам.
  function nhaTrangNow() {
    try {
      var f = new Intl.DateTimeFormat("en-CA", { timeZone:"Asia/Ho_Chi_Minh", year:"numeric", month:"2-digit", day:"2-digit", hour:"2-digit", minute:"2-digit", hour12:false });
      var p = {}; f.formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
      return { date:p.year+"-"+p.month+"-"+p.day, hour:+p.hour, minute:+p.minute };
    } catch (_) { return null; }
  }
  function injectSpecialSchedule() {
    var t = nhaTrangNow();
    if (!t || t.date < "2026-08-22" || t.date > "2026-09-04") return;
    var b = document.getElementById("flw-special-schedule");
    if (!b) {
      b = document.createElement("div"); b.id = "flw-special-schedule";
      b.style.cssText = "position:relative;z-index:49;background:#fff4e8;border-bottom:1px solid #f0d2ad;color:#8a531d;padding:10px 16px;text-align:center;font:700 13px/1.45 system-ui,-apple-system,sans-serif";
      var header = document.querySelector("header");
      if (header && header.parentNode) header.parentNode.insertBefore(b, header.nextSibling);
      else document.body.insertBefore(b, document.body.firstChild);
    }
    var closed = t.date === "2026-09-04" || (t.date === "2026-09-03" && (t.hour > 14 || (t.hour === 14 && t.minute >= 0)));
    b.textContent = closed ? L().closed : L().schedule;
  }

  document.addEventListener("cart:change", fab);
  document.addEventListener("DOMContentLoaded", function () {
    try { localStorage.setItem("flw_lang", pageLang()); } catch (e) {}
    injectButtons(); injectProductPage(); injectNav(); injectSpecialSchedule(); fab();
    var n = 0, iv = setInterval(function () { injectButtons(); if (++n > 10) clearInterval(iv); }, 400);
  });
})();

/* ============================================================
   🎈 СКОЛЬКО ЛЕТАЮТ ШАРЫ (01.10.2026, требование Олега — честно предупреждаем):
   фольгированные — в среднем 7 дней, резиновые (латекс) — в среднем 12 часов.
   Пометка на карточках с шарами, на странице товара и в корзине (window.FLW_BAL).
   LATEX / LATEX_ONLY — тот же список, что в catalog-*.html, build_site.py, tg/app.js, build_category_landings.py.
   ============================================================ */
(function () {
  var LATEX = ["nabor-sharov-s-2-cifry-10-sharov", "101-belaya-roza-korzina-shary-serdca", "101-belaya-roza-rozovaya-upakovka-cifry-25-sharov", "35-serebristo-chernyh-gelievyh-sharov-pod-potolok", "101-rozovaya-roza-korzina-25-persikovyh-roz-15-sharov", "yarkaya-sbornaya-korzina-15-rozovyh-sharov", "27-cherno-belyh-rezinovyh-geliyevyh-sharov-svyazka", "svyazka-20-sinih-rezinovyh-sharov"];
  var LATEX_ONLY = ["35-serebristo-chernyh-gelievyh-sharov-pod-potolok", "27-cherno-belyh-rezinovyh-geliyevyh-sharov-svyazka", "svyazka-20-sinih-rezinovyh-sharov"];
  var T = {"ru": {"f": ["Фольгированные шары", "летают в среднем 7 дней"], "l": ["Резиновые шары", "летают в среднем 12 часов"]},
           "en": {"f": ["Foil balloons", "float about 7 days on average"], "l": ["Latex balloons", "float about 12 hours on average"]},
           "ko": {"f": ["호일 풍선", "평균 약 7일 동안 떠 있습니다"], "l": ["라텍스 풍선", "평균 약 12시간 동안 떠 있습니다"]}};
  var cats = null, waiters = [];
  function lang() {
    var w = window.FLW_LANG; if (w === "en" || w === "ko") return w;
    var l = (document.documentElement.getAttribute("lang") || "").toLowerCase();
    if (l.indexOf("en") === 0) return "en";
    if (l.indexOf("ko") === 0 || l.indexOf("kr") === 0) return "ko";
    return "ru";
  }
  function type(slug, cat) {
    slug = String(slug || "");
    if (/^dop-folgirovannyy-shar/.test(slug)) return "f";
    var c = String(cat || "").split(/\s+/).filter(Boolean);
    if (c.indexOf("balloons") < 0 && cats && cats[slug]) c = cats[slug];
    if (c.indexOf("balloons") < 0) return "";
    if (LATEX_ONLY.indexOf(slug) > -1) return "l";
    if (LATEX.indexOf(slug) > -1) return "fl";
    return "f";
  }
  function lines(t) { var x = T[lang()], a = []; if (t.indexOf("f") > -1) a.push(x.f); if (t.indexOf("l") > -1) a.push(x.l); return a; }
  function txt(p) { return "🎈 " + p[0] + " — " + p[1]; }
  function note(t, big) {
    if (!t) return "";
    return '<div class="flw-bnote" style="display:flex;flex-direction:column;gap:4px;margin:' + (big ? "10px 0 12px" : "6px 0 0") + '">' +
      lines(t).map(function (p) {
        return '<div style="padding:' + (big ? "9px 12px" : "5px 9px") + ';border-radius:10px;background:#eef6fb;border:1.5px solid #9cc7df;color:#0f3c57;font:' +
          (big ? "14px" : "12px") + '/1.35 system-ui,-apple-system,sans-serif">🎈 <b>' + p[0] + '</b> — <b>' + p[1] + '</b></div>';
      }).join("") + "</div>";
  }
  function ready(cb) { if (cats) cb(); else waiters.push(cb); }
  window.FLW_BAL = { type: type, note: note, lines: lines, ready: ready };
  function cardsNotes() {
    document.querySelectorAll(".product-card").forEach(function (card) {
      if (card.querySelector(".flw-bnote")) return;
      var a = card.querySelector("a[href*='catalog/']"); if (!a) return;
      var m = a.getAttribute("href").match(/catalog\/(.+?)-(?:ru|en|ko)\.html/); if (!m) return;
      var t = type(m[1], card.getAttribute("data-cat")); if (!t) return;
      var anchor = card.querySelector(".combo-note") || card.querySelector("h3"); if (!anchor) return;
      anchor.insertAdjacentHTML("afterend", note(t, false));
    });
  }
  function pageNote() {
    var pb = document.querySelector(".price-box");
    if (!pb || document.querySelector(".flw-bnote-page")) return;
    var m = location.pathname.match(/catalog\/(.+?)-(?:ru|en|ko)\.html/); if (!m) return;
    var t = type(m[1], ""); if (!t) return;
    pb.insertAdjacentHTML("afterend", note(t, true).replace('class="flw-bnote"', 'class="flw-bnote flw-bnote-page"'));
  }
  function load() {
    fetch("/products.json").then(function (r) { return r.json(); }).then(function (d) {
      var L = Array.isArray(d) ? d : (d.products || []); cats = {};
      L.forEach(function (p) { cats[p.slug] = p.cats || []; });
    }).catch(function () { cats = {}; }).then(function () {
      pageNote(); var w = waiters; waiters = []; w.forEach(function (f) { try { f(); } catch (e) {} });
    });
  }
  function run() { cardsNotes(); load(); var n = 0, iv = setInterval(function () { cardsNotes(); if (++n > 10) clearInterval(iv); }, 500); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run); else run();
})();

/* ==== ПОДАРКИ К ЗАКАЗУ (22.10.2026) — «чем больше заказ, тем больше подарков» ====
   Общий модуль: корзина сайта (cart.html), плашка на страницах каталога (через cart.js) и Telegram (tg/).
   Правила:
   • 25/51 роза → 💌 открытка + 💎 гранулы-кристаллы
   • 101 роза или сборный букет (mixed от 1 500 000 ₫) → + 🎈 фольгированный шар на выбор
   • то же + набор шаров (категория balloons) → 🏺 тара для букета вместо шара
   • заказ от 3 000 000 ₫ → открытка, кристаллы, 🎈 шар или 🏺 тара на выбор + 🧸 мягкая игрушка на выбор (выбор обязателен)
   • 25/51 + набор шаров — тара НЕ идёт.
   Мягкие игрушки: TOYS ниже (по 300 000 ₫, можно купить отдельно). Фото — добавить в img (поле img), когда Олег пришлёт. */
(function () {
  var BIG = 3000000;
  var TOYS = [
    { id: "dop-myagkaya-igrushka-1", price: 300000, img: "/img/products/dop-myagkaya-igrushka-1/1.webp", name: { ru: "Розовый мишка", en: "Pink teddy bear", ko: "핑크 곰 인형" } },
    { id: "dop-myagkaya-igrushka-4", price: 300000, img: "/img/products/dop-myagkaya-igrushka-4/1.webp", name: { ru: "Щенок-бульдог", en: "Bulldog puppy", ko: "불독 강아지 인형" } }
  ];
  var BALLOONS = [
    ["dop-folgirovannyy-shar-zvezda-happy-birthday", "Звезда «Happy Birthday»", "Star “Happy Birthday”", "별 “Happy Birthday”"],
    ["dop-folgirovannyy-shar-krug-happy-birthday-belyy", "Круг «Happy Birthday» белый", "Round “Happy Birthday”, white", "원형 “Happy Birthday” 화이트"],
    ["dop-folgirovannyy-shar-krug-happy-birthday-raduzhnyy", "Круг «Happy Birthday» радужный", "Round “Happy Birthday”, rainbow", "원형 “Happy Birthday” 무지개"],
    ["dop-folgirovannyy-shar-krug-happy-birthday-chernyy", "Круг «Happy Birthday» чёрный", "Round “Happy Birthday”, black", "원형 “Happy Birthday” 블랙"],
    ["dop-folgirovannyy-shar-serdce-i-love-you", "Сердце «I love you»", "Heart “I love you”", "하트 “I love you”"],
    ["dop-folgirovannyy-shar-serdce-krasnoe", "Сердце красное", "Red heart", "빨간 하트"],
    ["dop-folgirovannyy-shar-serdce-ayvori", "Сердце айвори", "Ivory heart", "아이보리 하트"],
    ["dop-folgirovannyy-shar-serdce-bezhevyy", "Сердце бежевое", "Beige heart", "베이지 하트"],
    ["dop-folgirovannyy-shar-serdce-serebristyy", "Сердце серебристое", "Silver heart", "실버 하트"],
    ["dop-folgirovannyy-shar-serdce-zolotoe", "Сердце золотое", "Gold heart", "골드 하트"],
    ["dop-folgirovannyy-shar-zvezda-serebristaya", "Звезда серебристая", "Silver star", "실버 별"],
    ["dop-folgirovannyy-shar-zvezda-zolotaya", "Звезда золотая", "Gold star", "골드 별"]
  ].map(function (b) { return { id: b[0], img: "/img/products/" + b[0] + "/1.webp", name: { ru: b[1], en: b[2], ko: b[3] } }; });

  var T = {
    ru: { head: "🎁 В этом заказе в подарок:", card: "💌 Открытка с вашим текстом", cry: "💎 Гранулы-кристаллы для свежести цветов",
      bal: "🎈 Фольгированный гелиевый шар на выбор (летает до 7 дней)", tara: "🏺 Тара для букета — вместо шара",
      bt: "🎈 Шар или 🏺 тара для букета на выбор", toy: "🧸 Мягкая игрушка на выбор",
      pickBal: "Выберите шар в подарок:", auto: "Подберём сами", pickBT: "Что положить в подарок?", optBal: "🎈 Шар", optTara: "🏺 Тару для букета",
      pickToy: "Выберите мягкую игрушку:", req: "обязательно",
      hToy: "Добавьте ещё {x} — и мягкая игрушка в подарок 🧸", hTara: "Добавьте набор шаров — и тара для букета в подарок 🏺",
      hBal: "Возьмите 101 розу или сборный букет — и фольгированный шар в подарок 🎈", top: "👑 Максимум подарков в этом заказе",
      errToy: "🧸 Выберите мягкую игрушку в подарок (блок «Подарки» в корзине).", errBT: "🎁 Выберите подарок: шар или тара для букета (блок «Подарки» в корзине).",
      toysH: "🧸 Мягкие игрушки", toysSub: "можно купить отдельно · при заказе от 3 000 000 ₫ — одна в подарок", add: "＋ Добавить", inOrder: "в заказе" },
    en: { head: "🎁 Gifts included in this order:", card: "💌 Greeting card with your text", cry: "💎 Water crystals to keep flowers fresh",
      bal: "🎈 Foil helium balloon of your choice (floats up to 7 days)", tara: "🏺 Vase for the bouquet — instead of the balloon",
      bt: "🎈 Balloon or 🏺 vase of your choice", toy: "🧸 Soft toy of your choice",
      pickBal: "Choose your gift balloon:", auto: "Let us choose", pickBT: "Which gift would you like?", optBal: "🎈 Balloon", optTara: "🏺 Vase for the bouquet",
      pickToy: "Choose a soft toy:", req: "required",
      hToy: "Add {x} more — and get a soft toy as a gift 🧸", hTara: "Add a balloon set — and get a vase for the bouquet as a gift 🏺",
      hBal: "Choose 101 roses or a mixed bouquet — and get a foil balloon as a gift 🎈", top: "👑 Maximum gifts in this order",
      errToy: "🧸 Please choose your gift soft toy (Gifts block in the cart).", errBT: "🎁 Please choose your gift: balloon or vase (Gifts block in the cart).",
      toysH: "🧸 Soft toys", toysSub: "sold separately · one is free with orders from 3 000 000 ₫", add: "＋ Add", inOrder: "in order" },
    ko: { head: "🎁 이 주문에 포함된 선물:", card: "💌 원하시는 문구의 카드", cry: "💎 꽃을 싱싱하게 유지하는 워터 크리스탈",
      bal: "🎈 원하시는 호일 헬륨 풍선 (최대 7일)", tara: "🏺 풍선 대신 꽃병",
      bt: "🎈 풍선 또는 🏺 꽃병 중 선택", toy: "🧸 원하시는 봉제 인형",
      pickBal: "선물 풍선을 골라 주세요:", auto: "저희가 골라 드릴게요", pickBT: "어떤 선물을 원하세요?", optBal: "🎈 풍선", optTara: "🏺 꽃병",
      pickToy: "봉제 인형을 골라 주세요:", req: "필수",
      hToy: "{x} 더 담으시면 봉제 인형을 선물로 드려요 🧸", hTara: "풍선 세트를 추가하시면 꽃병을 선물로 드려요 🏺",
      hBal: "장미 101송이 또는 믹스 꽃다발을 고르시면 호일 풍선을 선물로 드려요 🎈", top: "👑 이 주문은 최대 선물 구성이에요",
      errToy: "🧸 선물 봉제 인형을 골라 주세요 (장바구니의 선물 블록).", errBT: "🎁 선물을 골라 주세요: 풍선 또는 꽃병 (장바구니의 선물 블록).",
      toysH: "🧸 봉제 인형", toysSub: "따로 구매 가능 · 3 000 000동 이상 주문 시 1개 선물", add: "＋ 추가", inOrder: "담김" }
  };
  function lang(l) { l = l || window.FLW_LANG || (document.documentElement.getAttribute("lang") || "ru").slice(0, 2); return T[l] ? l : "ru"; }
  function fmt(v) { return window.fmtMoney ? window.fmtMoney(v, "VND") : (String(v).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " ₫"); }

  /* items: [{cats:[...]|cat:"a b", price|price_vnd, qty}] */
  function norm(items) {
    return (items || []).map(function (x) {
      var c = x.cats || String(x.cat || "").split(/\s+/);
      return { cats: c.filter(Boolean), price: +(x.price_vnd != null ? x.price_vnd : x.price) || 0, qty: +x.qty || 1 };
    });
  }
  function has(it, c) { return it.cats.indexOf(c) >= 0; }
  function state(items) {
    var L = norm(items), total = 0, small = false, big = false, set = false;
    L.forEach(function (it) {
      total += it.price * it.qty;
      if (has(it, "addon") || has(it, "cakes") && it.cats.length === 1) return;
      if (has(it, "r101") || (has(it, "mixed") && it.price >= 1500000)) big = true;
      else if (has(it, "r25") || has(it, "r51") || has(it, "mixed")) small = true;
      if (has(it, "balloons")) set = true;
    });
    var tier = "";
    if (total >= BIG) tier = "D";
    else if (big && set) tier = "C";
    else if (big) tier = "B";
    else if (small) tier = "A";
    return { tier: tier, total: total, big: big, small: small, set: set };
  }
  function gifts(st, l) {
    var t = T[lang(l)];
    if (!st.tier) return [];
    var g = [t.card, t.cry];
    if (st.tier === "B") g.push(t.bal);
    if (st.tier === "C") g.push(t.tara);
    if (st.tier === "D") { g.push(t.bt); g.push(t.toy); }
    return g;
  }
  function hints(st, l) {
    var t = T[lang(l)], h = [];
    if (!st.total) return h;
    if (st.tier === "D") return [t.top];
    /* 25.10.2026: у каждой подсказки — кнопка, чтобы сразу добавить нужное (на сайте; в TG-боте без ссылок) */
    var LL = lang(l), web = !/\/tg\//.test(location.pathname);
    var cat = "/catalog-" + (LL === "ko" ? "ko" : LL) + ".html#";
    var B = {
      ru: { r101: "Выбрать 101 розу →", mixed: "Сборные букеты →", bal: "Выбрать набор шаров →", set: "Добавить подарочный набор ↓", more: "Выбрать в каталоге →" },
      en: { r101: "Choose 101 roses →", mixed: "Mixed bouquets →", bal: "Choose a balloon set →", set: "Add a gift set ↓", more: "Open the catalog →" },
      ko: { r101: "장미 101송이 고르기 →", mixed: "믹스 꽃다발 →", bal: "풍선 세트 고르기 →", set: "선물 세트 추가 ↓", more: "카탈로그 보기 →" }
    }[LL];
    var btn = function (href, txt, scroll) {
      return '<a href="' + href + '"' + (scroll ? ' data-scroll="' + scroll + '"' : '') + ' style="display:inline-block;margin:7px 6px 0 0;background:#c0687a;color:#fff;text-decoration:none;font-weight:700;font-size:12.5px;padding:7px 12px;border-radius:9px">' + txt + '</a>';
    };
    var add = function (txt, links) { h.push(web ? txt + '<br>' + links : txt); };
    if (st.tier === "A" && !st.big) add(t.hBal, btn(cat + "r101", B.r101) + btn(cat + "mixed", B.mixed));
    if (st.tier === "B") add(t.hTara, btn(cat + "balloons", B.bal));
    var onCart = /\/cart\.html$/.test(location.pathname) && document.getElementById("setBox");
    add(t.hToy.replace("{x}", fmt(BIG - st.total)), onCart ? btn("#setBox", B.set, "setBox") + btn(cat, B.more) : btn(cat, B.more));
    return h;
  }
  /* выбор клиента */
  var SK = "flw_gift_sel";
  function sel() { try { return JSON.parse(localStorage.getItem(SK)) || {}; } catch (_) { return {}; } }
  function setSel(k, v) { var s = sel(); s[k] = v; try { localStorage.setItem(SK, JSON.stringify(s)); } catch (_) {} }
  function byId(list, id) { return list.filter(function (x) { return x.id === id; })[0]; }
  function check(items, l) {
    var st = state(items), t = T[lang(l)], s = sel();
    if (st.tier !== "D") return "";
    if (s.bt !== "balloon" && s.bt !== "tara") return t.errBT;
    if (!byId(TOYS, s.toy)) return t.errToy;
    return "";
  }
  /* текст для заявки (всегда по-русски — для оператора/Финашки/Карты заказов) */
  function orderText(items) {
    var st = state(items), s = sel(), r = T.ru;
    if (!st.tier) return "";
    var bName = byId(BALLOONS, s.bal) ? byId(BALLOONS, s.bal).name.ru : "подобрать самим";
    var p = ["💌 открытка", "💎 гранулы-кристаллы"];
    if (st.tier === "B") p.push("🎈 фольгированный шар: " + bName);
    if (st.tier === "C") p.push("🏺 тара для букета");
    if (st.tier === "D") {
      p.push(s.bt === "tara" ? "🏺 тара для букета" : "🎈 фольгированный шар: " + bName);
      var toy = byId(TOYS, s.toy); p.push("🧸 игрушка: " + (toy ? toy.name.ru : "—"));
    }
    return "🎁 ПОДАРКИ: " + p.join(" · ");
  }
  /* ---- виджет в корзине ---- */
  var CSS = ".fg-box{background:#fff7f9;border:1.5px solid #f3c6d1;border-radius:16px;padding:14px 16px;margin:14px 0;font:14px/1.45 system-ui,-apple-system,sans-serif;color:#1a1a1a}" +
    ".fg-h{font-weight:800;font-size:15px;margin-bottom:6px}.fg-li{padding:2px 0}.fg-q{font-weight:700;margin:12px 0 6px;font-size:13.5px}.fg-q i{color:#c0687a;font-style:normal;font-weight:600;font-size:12px}" +
    ".fg-row{display:flex;gap:8px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding:2px 2px 8px}.fg-ch{flex:0 0 auto;width:92px;border:1.5px solid #f0e0e5;background:#fff;border-radius:12px;padding:6px;cursor:pointer;text-align:center;font-size:11.5px;line-height:1.2;color:#1a1a1a}" +
    ".fg-ch img,.fg-ch .fg-ph{width:78px;height:78px;border-radius:9px;object-fit:cover;display:block;margin:0 auto 4px;background:#fdf2f5}.fg-ph{display:flex!important;align-items:center;justify-content:center;font-size:36px}" +
    ".fg-ch.on{border-color:#c0687a;box-shadow:0 0 0 2px #c0687a inset;background:#fff1f4}.fg-tg{display:flex;gap:8px}.fg-tg button{flex:1;border:1.5px solid #f0e0e5;background:#fff;border-radius:12px;padding:10px;font-weight:700;cursor:pointer;font-size:14px}" +
    ".fg-tg button.on{border-color:#c0687a;background:#c0687a;color:#fff}.fg-hint{margin-top:10px;padding:8px 11px;border-radius:10px;background:#fff;border:1px dashed #e3a5b4;color:#a8566a;font-weight:600;font-size:13px}";
  function css() { if (document.getElementById("fg-css")) return; var s = document.createElement("style"); s.id = "fg-css"; s.textContent = CSS; document.head.appendChild(s); }
  function chip(o, on, l, kind) {
    var im = o.img ? '<img src="' + o.img + '" alt="" loading="lazy">' : '<span class="fg-ph">' + (kind === "toy" ? "🧸" : "✨") + '</span>';
    return '<button type="button" class="fg-ch' + (on ? " on" : "") + '" data-k="' + kind + '" data-v="' + o.id + '">' + im + o.name[l] + '</button>';
  }
  function render(el, items, l, onChange) {
    if (!el) return; css(); l = lang(l);
    var st = state(items), t = T[l], s = sel(), g = gifts(st, l), h = hints(st, l);
    if (!g.length && !h.length) { el.innerHTML = ""; return; }
    var html = '<div class="fg-box">';
    if (g.length) html += '<div class="fg-h">' + t.head + '</div>' + g.map(function (x) { return '<div class="fg-li">' + x + '</div>'; }).join("");
    var autoB = { id: "", img: "", name: { ru: t.auto, en: t.auto, ko: t.auto } };
    var balRow = function () { return '<div class="fg-q">' + t.pickBal + '</div><div class="fg-row">' + chip(autoB, !byId(BALLOONS, s.bal), l, "bal") + BALLOONS.map(function (b) { return chip(b, s.bal === b.id, l, "bal"); }).join("") + '</div>'; };
    if (st.tier === "B") html += balRow();
    if (st.tier === "D") {
      html += '<div class="fg-q">' + t.pickBT + ' <i>· ' + t.req + '</i></div><div class="fg-tg"><button type="button" data-bt="balloon" class="' + (s.bt === "balloon" ? "on" : "") + '">' + t.optBal + '</button><button type="button" data-bt="tara" class="' + (s.bt === "tara" ? "on" : "") + '">' + t.optTara + '</button></div>';
      if (s.bt === "balloon") html += balRow();
      html += '<div class="fg-q">' + t.pickToy + ' <i>· ' + t.req + '</i></div><div class="fg-row">' + TOYS.map(function (o) { return chip(o, s.toy === o.id, l, "toy"); }).join("") + '</div>';
    }
    h.forEach(function (x) { html += '<div class="fg-hint">' + x + '</div>'; });
    el.innerHTML = html + '</div>';
    el.querySelectorAll('[data-scroll]').forEach(function (a) { a.onclick = function (e) { var t2 = document.getElementById(a.dataset.scroll); if (t2) { e.preventDefault(); t2.scrollIntoView({ behavior: 'smooth', block: 'start' }); } }; });
    el.querySelectorAll(".fg-ch").forEach(function (b) {
      b.onclick = function () { setSel(b.dataset.k === "toy" ? "toy" : "bal", b.dataset.v); render(el, items, l, onChange); if (onChange) onChange(); };
    });
    el.querySelectorAll("[data-bt]").forEach(function (b) {
      b.onclick = function () { setSel("bt", b.dataset.bt); render(el, items, l, onChange); if (onChange) onChange(); };
    });
  }
  /* ---- ряд «Мягкие игрушки» (покупка отдельно) ---- */
  function toysRow(el, items, l, onAdd) {
    if (!el) return; css(); l = lang(l); var t = T[l];
    var q = function (id) { var x = (items || []).filter(function (i) { return i.id === id; })[0]; return x ? x.qty : 0; };
    el.innerHTML = '<div class="fg-q" style="font-size:15px;margin-top:16px">' + t.toysH + ' · ' + fmt(300000) + '</div><div style="color:#78716c;font-size:12.5px;margin:-4px 0 8px">' + t.toysSub + '</div><div class="fg-row">' +
      TOYS.map(function (o) { var n = q(o.id); return '<button type="button" class="fg-ch' + (n ? " on" : "") + '" data-toy="' + o.id + '">' + (o.img ? '<img src="' + o.img + '" alt="">' : '<span class="fg-ph">🧸</span>') + o.name[l] + '<br><b style="color:#c0687a">' + (n ? t.inOrder + " (" + n + ")" : t.add) + '</b></button>'; }).join("") + '</div>';
    el.querySelectorAll("[data-toy]").forEach(function (b) { b.onclick = function () { onAdd(byId(TOYS, b.dataset.toy), l); }; });
  }
  /* ---- плашка-подсказка на страницах каталога (над кнопкой корзины) ---- */
  function bubble() {
    if (/\/cart\.html$/.test(location.pathname) || /\/tg\//.test(location.pathname) || !window.Cart) return;
    var st = state(Cart.items()); if (!st.total) return;
    var l = lang(), h = hints(st, l), g = gifts(st, l);
    var b = document.getElementById("fg-bubble");
    if (!b) {
      b = document.createElement("div"); b.id = "fg-bubble";
      b.style.cssText = "position:fixed;right:16px;bottom:74px;z-index:9998;max-width:290px;background:#fff;border:1.5px solid #e3a5b4;border-radius:14px;padding:10px 32px 10px 13px;font:600 13px/1.4 system-ui,-apple-system,sans-serif;color:#a8566a;box-shadow:0 8px 24px rgba(168,86,106,.22);transition:opacity .3s;opacity:0";
      document.body.appendChild(b);
    }
    var head = g.length ? '<div style="color:#1a1a1a;margin-bottom:3px">' + T[l].head + ' ' + g.map(function (x) { return x.split(" ")[0]; }).join(" ") + '</div>' : "";
    b.innerHTML = '<span style="position:absolute;top:4px;right:9px;cursor:pointer;color:#a8a29e;font-size:17px" onclick="this.parentNode.style.display=\'none\'">×</span>' + head + h.join("<br>");
    b.style.display = "block"; requestAnimationFrame(function () { b.style.opacity = "1"; });
    clearTimeout(b._t); b._t = setTimeout(function () { b.style.opacity = "0"; setTimeout(function () { b.style.display = "none"; }, 300); }, 7000);
  }
  document.addEventListener("cart:change", bubble);

  window.FLW_GIFTS = { TOYS: TOYS, BALLOONS: BALLOONS, BIG: BIG, state: state, gifts: gifts, hints: hints, check: check, orderText: orderText, render: render, toysRow: toysRow, sel: sel, T: T };
})();

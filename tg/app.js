/* ============================================================
   Telegram Mini App — витрина «Цветы Нячанг».
   Источник товаров: /products.json (генерится из seo/products.csv).
   Заказы уходят в тот же Apps Script Web App, что и сайт, с пометкой source=Telegram.
   ============================================================ */

var CONFIG = {
  API: "https://script.google.com/macros/s/AKfycbzDz8tCuWtC4oIA3ajYgt_m5Ui9fZPTgVRiXzVjJTNVrSiP4vNvaNzblCpWJSELOqVC/exec",
  BUHPROXY: "https://buhproxy.olegbabaskin-am.workers.dev/",
  SOURCE: "Telegram",
  NHATRANG: [12.2388, 109.1967],
  DOMAIN: "https://flowers-nha-trang.online"
};

/* ---- Telegram SDK ---- */
var TG = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
var TG_USER = null;
if (TG) {
  try { TG.ready(); TG.expand(); } catch (e) {}
  try { TG_USER = TG.initDataUnsafe && TG.initDataUnsafe.user ? TG.initDataUnsafe.user : null; } catch (e) {}
}

/* ---- деньги (курсы как на сайте) ---- */
var RATES = { VND: 1, USD: 25000, RUB: 280 };
var SYM   = { VND: "₫", USD: "$", RUB: "₽" };
var CUR_ORDER = ["VND", "RUB", "USD"];
var CUR = localStorage.getItem("flw_tg_cur") || "VND";
function money(vnd, cur) {
  cur = cur || CUR;
  var r = RATES[cur] || 1, s = SYM[cur] || "₫", v = vnd / r;
  var rounded = cur === "VND" ? Math.round(v / 1000) * 1000
              : cur === "USD" ? Math.round(v)
              : cur === "RUB" ? Math.ceil(v / 100) * 100
              : Math.round(v / 10) * 10;
  var str = rounded.toLocaleString("ru-RU").replace(/,/g, " ");
  return cur === "USD" ? (s + str) : (str + " " + s);
}

/* ---- корзина (localStorage) ---- */
var LS = "flw_tg_cart";
function cartRead() { try { return JSON.parse(localStorage.getItem(LS)) || []; } catch (_) { return []; } }
function cartWrite(c) { localStorage.setItem(LS, JSON.stringify(c)); syncFab(); }
function cartCount() { return cartRead().reduce(function (s, i) { return s + i.qty; }, 0); }
function cartTotal() { return cartRead().reduce(function (s, i) { return s + i.price_vnd * i.qty; }, 0); }
function cartQty(id) { var x = cartRead().filter(function (i) { return i.id === id; })[0]; return x ? x.qty : 0; }
function cartAdd(p) {
  var c = cartRead(), ex = c.filter(function (x) { return x.id === p.id; })[0];
  if (ex) ex.qty++;
  else c.push({ id: p.id, slug: p.slug, name: p.name, price_vnd: p.price_vnd, price_sub: p.price_sub, img: p.images[0], cats: p.cats, qty: 1 });
  cartWrite(c);
}
function cartSet(id, q) {
  var c = cartRead();
  c = c.map(function (x) { if (x.id === id) x.qty = q; return x; }).filter(function (x) { return x.qty > 0; });
  cartWrite(c);
}

/* ---- состояние ---- */
var DATA = null, PRODUCTS = [], activeCat = "all", searchQ = "";

/* ---- загрузка источника ---- */
fetch("/products.json").then(function (r) { return r.json(); }).then(function (d) {
  DATA = d; PRODUCTS = d.products || [];
  renderTabs(); renderGrid(); syncFab();
}).catch(function () {
  document.getElementById("grid").innerHTML = "<div class='empty'>Не удалось загрузить каталог. Обновите страницу.</div>";
});

/* ---- вкладки категорий (только непустые) ---- */
function renderTabs() {
  var box = document.getElementById("tabs");
  box.innerHTML = "";
  DATA.categories.forEach(function (c) {
    if (c.key !== "all") {
      var has = PRODUCTS.some(function (p) { return p.cats.indexOf(c.key) >= 0; });
      if (!has) return;
    }
    var b = document.createElement("button");
    b.className = "tab" + (c.key === activeCat ? " on" : "");
    b.textContent = c.label;
    b.onclick = function () { activeCat = c.key; renderTabs(); renderGrid(); window.scrollTo(0, 0); };
    box.appendChild(b);
  });
}

/* ---- карточки товаров ---- */
function filtered() {
  return PRODUCTS.filter(function (p) {
    if (activeCat !== "all" && p.cats.indexOf(activeCat) < 0) return false;
    if (searchQ && p.name.toLowerCase().indexOf(searchQ) < 0) return false;
    return true;
  });
}
function renderGrid() {
  var grid = document.getElementById("grid"), empty = document.getElementById("gridEmpty");
  var list = filtered();
  empty.classList.toggle("hidden", list.length > 0);
  grid.innerHTML = "";
  list.forEach(function (p) {
    var imgs = p.images.map(function (im) { return "/" + im; });
    var card = document.createElement("div");
    card.className = "pc";
    var dots = imgs.length > 1
      ? '<div class="dots">' + imgs.map(function (_, i) { return '<i class="' + (i === 0 ? "on" : "") + '"></i>'; }).join("") + '</div>' : "";
    var nav = imgs.length > 1
      ? '<div class="nav"><button data-d="-1">‹</button><button data-d="1">›</button></div>' : "";
    card.innerHTML =
      '<div class="ph"><img src="' + imgs[0] + '" alt="" loading="lazy">' + nav + dots + '</div>' +
      '<div class="bd">' +
        '<h3>' + esc(p.name) + '</h3>' +
        '<div class="pr">' + money(p.price_vnd) + '</div>' +
        '<div class="sub">' + esc(p.price_sub) + '</div>' +
        '<div class="act"></div>' +
      '</div>';
    // карусель
    var idx = 0, imgEl = card.querySelector(".ph img");
    var dotEls = card.querySelectorAll(".dots i");
    card.querySelectorAll(".nav button").forEach(function (b) {
      b.onclick = function (e) {
        e.stopPropagation();
        idx = (idx + parseInt(b.dataset.d) + imgs.length) % imgs.length;
        imgEl.src = imgs[idx];
        dotEls.forEach(function (d, i) { d.className = i === idx ? "on" : ""; });
      };
    });
    renderAct(card.querySelector(".act"), p);
    grid.appendChild(card);
  });
}
function renderAct(box, p) {
  var q = cartQty(p.id);
  if (q > 0) {
    box.innerHTML = '<div class="qtybox"><button>−</button><span>' + q + ' шт</span><button>+</button></div>';
    var bs = box.querySelectorAll("button");
    bs[0].onclick = function () { cartSet(p.id, q - 1); renderAct(box, p); };
    bs[1].onclick = function () { cartAdd(p); renderAct(box, p); };
  } else {
    var isCake = p.cats.indexOf("cakes") >= 0;
    box.innerHTML = '<button class="add">' + (isCake ? "🎂 Добавить" : "🛒 В корзину") + '</button>';
    box.querySelector("button").onclick = function () { cartAdd(p); renderAct(box, p); toast("Добавлено ✓"); };
  }
}

/* ---- поиск ---- */
document.getElementById("q").addEventListener("input", function () {
  searchQ = this.value.trim().toLowerCase(); renderGrid();
});

/* ---- FAB корзины ---- */
function syncFab() {
  var n = cartCount(), fab = document.getElementById("fab");
  document.getElementById("fabC").textContent = n;
  fab.classList.toggle("show", n > 0 && document.getElementById("scrCatalog").classList.contains("on"));
}

/* ---- переключение экранов ---- */
function show(id) {
  ["scrCatalog", "scrCart", "scrPay", "scrDone"].forEach(function (s) {
    document.getElementById(s).classList.toggle("on", s === id);
  });
  window.scrollTo(0, 0); syncFab();
}
function showCatalog() { show("scrCatalog"); }
function showCart() { show("scrCart"); renderCart(); }

/* ---- отрисовка корзины ---- */
function renderCart() {
  var empty = document.getElementById("cartEmpty"), full = document.getElementById("cartFull");
  var c = cartRead();
  empty.classList.toggle("hidden", c.length > 0);
  full.classList.toggle("hidden", c.length === 0);
  if (!c.length) return;

  // переключатель валют
  var cb = document.getElementById("curbar");
  cb.innerHTML = CUR_ORDER.map(function (k) {
    return '<button class="' + (k === CUR ? "on" : "") + '" data-c="' + k + '">' + k + '</button>';
  }).join("");
  cb.querySelectorAll("button").forEach(function (b) {
    b.onclick = function () { CUR = b.dataset.c; localStorage.setItem("flw_tg_cur", CUR); renderCart(); refreshZone(); };
  });

  var list = document.getElementById("cartList");
  list.innerHTML = "";
  c.forEach(function (it) {
    var d = document.createElement("div");
    d.className = "ci";
    d.innerHTML =
      '<img src="/' + it.img + '" alt="">' +
      '<div class="info"><h4>' + esc(it.name) + '</h4>' +
      '<div class="pr">' + money(it.price_vnd) + '</div><div class="sub">' + esc(it.price_sub || "") + '</div>' +
      '<div class="ctr"><button class="qbtn">−</button><span>' + it.qty + ' шт</span><button class="qbtn">+</button>' +
      '<button class="rm">удалить</button></div></div>';
    var b = d.querySelectorAll(".ctr button");
    b[0].onclick = function () { cartSet(it.id, it.qty - 1); renderCart(); };
    b[1].onclick = function () { cartSet(it.id, it.qty + 1); renderCart(); };
    d.querySelector(".rm").onclick = function () { cartSet(it.id, 0); renderCart(); };
    list.appendChild(d);
  });
  refreshZone();
}

/* ---- предварительный итог (товары + доставка) ---- */
function preTotHtml() {
  var sub = cartTotal();
  var fee = (window.__outside ? 0 : (window.__delFee || 0));
  var label = window.__delLabel || "";
  var rows = '<div class="row"><span>Товары</span><span>' + money(sub) + '</span></div>';
  if (window.__island) {
    rows += '<div class="row"><span>Доставка · порт</span><span style="color:var(--ok);font-weight:600">бесплатно</span></div>';
  } else if (fee > 0) {
    rows += '<div class="row"><span>Доставка · ' + esc(label) + '</span><span style="color:var(--warn);font-weight:600">+' + money(fee) + '</span></div>';
  } else if (label) {
    rows += '<div class="row"><span>Доставка · ' + esc(label) + '</span><span style="color:var(--ok);font-weight:600">бесплатно</span></div>';
  }
  rows += '<div class="row grand"><span>Итого</span><span>' + money(sub + fee) + '</span></div>';
  return rows;
}
function refreshZone() {
  document.getElementById("preTot").innerHTML = preTotHtml();
}

/* ============ ДАТА / ВРЕМЯ (как на сайте) ============ */
function ntParts(now) {
  var f = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Ho_Chi_Minh", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false });
  var p = {}; f.formatToParts(now || new Date()).forEach(function (x) { p[x.type] = x.value; });
  return { y: +p.year, mo: +p.month, d: +p.day, h: +p.hour, mi: +p.minute };
}
function pad(n) { return n < 10 ? "0" + n : "" + n; }
function isoDate(t) { return t.y + "-" + pad(t.mo) + "-" + pad(t.d); }
function isClosedDeliveryDate(iso) { return iso === "2026-09-04"; }
function skipClosedDeliveryDate(base) {
  while (isClosedDeliveryDate(base.getUTCFullYear() + "-" + pad(base.getUTCMonth() + 1) + "-" + pad(base.getUTCDate()))) base.setUTCDate(base.getUTCDate() + 1);
  return base;
}
function specialOrderClosed(now) {
  var t = ntParts(now), d = isoDate(t);
  return d === "2026-09-04" || (d === "2026-09-03" && (t.h > 14 || (t.h === 14 && t.mi >= 0)));
}
function updateSpecialOrderUi() {
  var t = ntParts(), d = isoDate(t), active = d >= "2026-08-22" && d <= "2026-09-04";
  var notice = document.getElementById("specialScheduleNotice");
  if (notice) {
    notice.classList.toggle("hidden", !active);
    notice.textContent = specialOrderClosed()
      ? "📅 Онлайн-заказы закрыты до 5 сентября: 4 сентября мы не работаем. С 5 сентября оформление снова доступно."
      : "📅 Важно: 3 сентября онлайн-заказы принимаем до 14:00. 4 сентября — выходной. С 5 сентября работаем в обычном режиме.";
  }
  var btn = document.getElementById("submitBtn"), closed = specialOrderClosed();
  if (btn) {
    if (closed) { if (!btn.dataset.normalText) btn.dataset.normalText = btn.textContent; btn.disabled = true; btn.textContent = "Онлайн-заказы закрыты до 5 сентября"; }
    else if (btn.dataset.normalText) { btn.disabled = false; btn.textContent = btn.dataset.normalText; delete btn.dataset.normalText; }
  }
}
var MIN_DATE, MIN_START;
function initDate() {
  var t = ntParts(), base = new Date(Date.UTC(t.y, t.mo - 1, t.d));
  if (t.h >= 6 && t.h < 22) { base.setUTCDate(base.getUTCDate() + 1); MIN_START = 6; }
  else { if (t.h >= 22) base.setUTCDate(base.getUTCDate() + 1); MIN_START = 9; }
  skipClosedDeliveryDate(base);
  MIN_DATE = base.getUTCFullYear() + "-" + pad(base.getUTCMonth() + 1) + "-" + pad(base.getUTCDate());
  var inp = document.getElementById("deliveryDate");
  inp.min = MIN_DATE; inp.value = MIN_DATE;
  inp.addEventListener("change", rebuildTimes);
  rebuildTimes();
  updateSpecialOrderUi();
  setInterval(updateSpecialOrderUi, 30000);
}
async function rebuildTimes() {
  var inp = document.getElementById("deliveryDate");
  if (inp.value && inp.value < MIN_DATE) inp.value = MIN_DATE;
  var selectedDate = inp.value;
  var adjusted = isClosedDeliveryDate(selectedDate);
  if (adjusted) inp.value = "2026-09-05";
  var dateNotice = document.getElementById("dateScheduleNotice");
  if (dateNotice) {
    var message = selectedDate === "2026-09-03"
      ? "Здравствуйте! 3 сентября заказы принимаем только до 14:00. 4 сентября мы не работаем. Спасибо за понимание 🌸"
      : selectedDate === "2026-09-04"
        ? "Здравствуйте! 4 сентября у нас полный выходной, поэтому оформить доставку на эту дату нельзя. Календарь перенесён на 5 сентября. Спасибо за понимание 🌸"
        : "";
    dateNotice.classList.toggle("hidden", !message);
    dateNotice.textContent = message;
  }
  var sel = document.getElementById("deliveryTime"); var hint = document.getElementById("timeHint");
  var zone = window.__zoneKey;
  if (!zone || window.__outside) { sel.innerHTML = '<option value="">Сначала укажите адрес на карте</option>'; hint.textContent = "Сначала укажите адрес на карте"; return; }
  var startMin = ((inp.value === MIN_DATE) ? MIN_START : 6) * 60;
  sel.innerHTML = '<option value="">Загружаем свободное время…</option>'; hint.textContent = "Загружаем свободное время…";
  var myDate = inp.value;
  try {
    var r = await fetch(CONFIG.BUHPROXY, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "slotsPublic", date: myDate, zone: zone }) }).then(function (x) { return x.json(); });
    if (document.getElementById("deliveryDate").value !== myDate) return;
    var free = (r && r.ok && r.free) ? r.free : [];
    free = free.filter(function (t) { var p2 = t.split(":"); return (+p2[0] * 60 + +p2[1]) >= startMin; });
    if (!free.length) { sel.innerHTML = '<option value="">На этот день всё занято — выберите другой день</option>'; hint.textContent = "На этот день всё занято — выберите другой день"; return; }
    sel.innerHTML = ""; free.forEach(function (t) { var o = document.createElement("option"); o.value = t; o.textContent = t; sel.appendChild(o); });
    hint.textContent = "Выберите удобное время прибытия — доставим ±10–15 мин";
  } catch (e) {
    sel.innerHTML = ""; for (var h = Math.ceil(startMin / 60); h <= 21; h++) { var o = document.createElement("option"); o.value = pad(h) + ":00"; o.textContent = pad(h) + ":00"; sel.appendChild(o); }
    hint.textContent = "Выберите удобное время прибытия — доставим ±10–15 мин";
  }
}
function ruDate(iso) { var a = iso.split("-"); return a[2] + "." + a[1] + "." + a[0].slice(2); }

/* ============ КАРТА + ЗОНЫ (перенос с сайта) ============ */
var map, marker, latlng = null, foundLabel = "";
/* Южная граница доставки = аэропорт Камрань. Всё ЮЖНЕЕ (широта < AIRPORT_LAT) НЕ возим. */
var AIRPORT_LAT = 12.03;
function inArea(lat, lon) { return !!zoneForPoint(lat, lon); }
function validGeo(la, ln) { return la > 11.6 && la < 12.7 && ln > 109.0 && ln < 109.45; }
function isAirport(la, ln) { return la >= 11.97 && la <= 12.025 && ln >= 109.185 && ln <= 109.25; }
function isIsland(la, ln) { return la >= 12.15 && la <= 12.27 && ln >= 109.215 && ln <= 109.35; }
var PORT_MAPS = "https://maps.app.goo.gl/c5muBjFmnKhqNNGi8";
/* 5 ЗОН ДОСТАВКИ (полигоны, [lat,lng]) — как на сайте */
var DZONES={center:{fee:0,slots:2,min:0,label:"Центр",poly:[[12.290439,109.203415],[12.289432,109.206333],[12.281376,109.203415],[12.276676,109.203415],[12.271977,109.203587],[12.268452,109.206505],[12.264592,109.20393],[12.264088,109.201355],[12.258045,109.199123],[12.24596,109.196892],[12.236728,109.198093],[12.228502,109.200325],[12.22078,109.20496],[12.213897,109.210281],[12.211782,109.215088],[12.209936,109.217749],[12.208257,109.21629],[12.20641,109.216204],[12.204563,109.217319],[12.20129,109.218264],[12.198771,109.217577],[12.196169,109.21483],[12.194154,109.211569],[12.194322,109.207964],[12.1981,109.203501],[12.20364,109.198952],[12.205067,109.198694],[12.206326,109.197063],[12.20683,109.193544],[12.207501,109.189854],[12.207585,109.187708],[12.208341,109.18745],[12.208425,109.185562],[12.207166,109.178352],[12.213461,109.176207],[12.219085,109.177065],[12.224877,109.178782],[12.228066,109.178267],[12.231927,109.176636],[12.235368,109.175434],[12.24074,109.17449],[12.247849,109.172602],[12.251374,109.171486],[12.254228,109.170542],[12.254228,109.172001],[12.256326,109.173546],[12.259263,109.173117],[12.261193,109.172516],[12.262872,109.172773],[12.265473,109.173117],[12.267823,109.174919],[12.269418,109.176121],[12.269334,109.177923],[12.267823,109.180241],[12.267739,109.182386],[12.268159,109.184446],[12.267907,109.187622],[12.267823,109.188824],[12.269418,109.192085],[12.270425,109.193287],[12.272691,109.195948],[12.274789,109.196806],[12.275796,109.19672],[12.275544,109.194832],[12.275041,109.192858],[12.276131,109.189939],[12.276635,109.188223],[12.277306,109.185305],[12.277055,109.181099],[12.277726,109.179897],[12.281502,109.182558],[12.285027,109.184446],[12.288383,109.186077],[12.291236,109.186592],[12.293838,109.186935],[12.295768,109.18685],[12.296775,109.186678]]},
north:{fee:150000,slots:4,min:1000000,label:"Крайний север",poly:[[12.29199,109.208136],[12.295179,109.207277],[12.298283,109.206762],[12.303318,109.204016],[12.303234,109.206762],[12.302143,109.20908],[12.301472,109.211483],[12.300297,109.215088],[12.298283,109.219809],[12.297192,109.222212],[12.296605,109.226332],[12.296605,109.229851],[12.296857,109.231997],[12.298367,109.232941],[12.300549,109.231567],[12.302479,109.233541],[12.304577,109.235601],[12.306842,109.234657],[12.307262,109.235687],[12.307262,109.238691],[12.306674,109.240665],[12.305332,109.242897],[12.304745,109.243412],[12.302227,109.24221],[12.30122,109.241266],[12.299206,109.239721],[12.298703,109.237576],[12.29585,109.235945],[12.293668,109.234314],[12.292661,109.227362],[12.294423,109.2241],[12.294843,109.221182],[12.291402,109.222727],[12.290983,109.21792],[12.29199,109.215088],[12.293081,109.214315],[12.290563,109.210281],[12.291402,109.208393]]},
west:{fee:150000,slots:4,min:1000000,label:"Запад",poly:[[12.231378,109.164963],[12.238596,109.16153],[12.2438,109.159641],[12.255382,109.159813],[12.265788,109.159813],[12.266963,109.161186],[12.268306,109.167023],[12.26797,109.171829],[12.267747,109.173074],[12.26611,109.172301],[12.264348,109.172215],[12.261956,109.171915],[12.259396,109.172087],[12.258137,109.172516],[12.256669,109.172945],[12.255074,109.171872],[12.254654,109.170284],[12.253438,109.169984],[12.251591,109.170756],[12.249619,109.171658],[12.246555,109.172516],[12.241729,109.173632],[12.23917,109.173975],[12.237239,109.174662],[12.235309,109.174919]]},
south:{fee:300000,slots:4,min:1000000,label:"Ближний юг",poly:[[12.207425,109.186592],[12.204211,109.182472],[12.200518,109.175262],[12.194809,109.171143],[12.187422,109.166679],[12.179363,109.162216],[12.171304,109.173203],[12.166602,109.184875],[12.158543,109.199638],[12.154848,109.209938],[12.157199,109.214745],[12.164923,109.202728],[12.170632,109.202385],[12.172647,109.206505],[12.176005,109.207535],[12.179699,109.209938],[12.185407,109.209251],[12.190444,109.204788],[12.19716,109.199295],[12.202197,109.194145],[12.204883,109.190712]]},
camranh:{fee:600000,slots:6,min:1000000,label:"Камрань",poly:[[12.021975,109.212642],[12.021891,109.213886],[12.021471,109.215946],[12.022353,109.218178],[12.023067,109.219766],[12.024495,109.222426],[12.038583,109.219208],[12.053365,109.211998],[12.07621,109.203758],[12.096365,109.199295],[12.112488,109.201012],[12.121557,109.219894],[12.141708,109.226074],[12.154134,109.224701],[12.157573,109.217663],[12.153291,109.210367],[12.153291,109.214659],[12.151444,109.216805],[12.149681,109.218006],[12.146154,109.218435],[12.14246,109.210625],[12.135407,109.206505],[12.131461,109.206505],[12.128354,109.206505],[12.125079,109.206505],[12.121637,109.201183],[12.121889,109.195175],[12.119957,109.184446],[12.115507,109.183846],[12.110721,109.182301],[12.09191,109.178352],[12.084688,109.179382],[12.071503,109.182472],[12.067471,109.186592],[12.06176,109.188566],[12.056553,109.189682],[12.048574,109.19363],[12.041015,109.196548],[12.036647,109.201784],[12.031691,109.201956],[12.025307,109.2029],[12.023627,109.20599]]}};
function pointInPoly(la,ln,poly){var x=ln,y=la,inside=false;for(var i=0,j=poly.length-1;i<poly.length;j=i++){var yi=poly[i][0],xi=poly[i][1],yj=poly[j][0],xj=poly[j][1];var intersect=((yi>y)!=(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi);if(intersect)inside=!inside;}return inside;}
function zoneForPoint(la,ln){for(var k in DZONES){if(pointInPoly(la,ln,DZONES[k].poly))return {key:k,label:DZONES[k].label,fee:DZONES[k].fee,slots:DZONES[k].slots,min:DZONES[k].min};}return null;}
function zoneFor(lat) {
  if (lat >= 12.18) return { key: "nt", label: "Нячанг", fee: 0 };
  if (lat >= 12.14) return { key: "near", label: "рядом с Нячангом (юг)", fee: 300000 };
  return { key: "camranh", label: "Камрань", fee: 600000 };
}
function mapsLink() { return "https://www.google.com/maps?q=" + latlng.la + "," + latlng.ln; }

function initMap() {
  map = L.map("map", { zoomControl: true, attributionControl: false }).setView(CONFIG.NHATRANG, 13);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19 }).addTo(map);
  map.on("click", function (e) { setPoint(e.latlng.lat, e.latlng.lng, "Точка на карте"); reverseGeo(e.latlng.lat, e.latlng.lng); });
  setTimeout(function () { map.invalidateSize(); }, 200);
}
function setPoint(la, ln, label) {
  latlng = { la: la, ln: ln };
  if (label) foundLabel = label;
  if (!marker) marker = L.marker([la, ln], { draggable: true }).addTo(map);
  else marker.setLatLng([la, ln]);
  marker.off("dragend").on("dragend", function () { var p = marker.getLatLng(); latlng = { la: p.lat, ln: p.lng }; reverseGeo(p.lat, p.lng); updateFound(); try { rebuildTimes(); } catch (e) {} });
  map.setView([la, ln], 15);
  updateFound();
  try { rebuildTimes(); } catch (e) {}
}
function updateFound() {
  var box = document.getElementById("foundAddr");
  box.classList.remove("hidden");
  var head = "📍 <b>" + esc(foundLabel || "Точка на карте") + "</b><br><a href='" + mapsLink() + "' target='_blank'>" + mapsLink() + "</a>";
  if (isIsland(latlng.la, latlng.ln)) {
    window.__outside = false; window.__island = true; window.__delFee = 0; window.__delLabel = "порт (на остров не возим)";
    box.innerHTML = head + "<div style='margin-top:8px;padding:11px 13px;background:#fdf6ec;border:1px solid #f3e2c7;border-radius:12px;color:#8a6d3b;font-size:13px;line-height:1.55'>🏝️ Это остров (Винперл / Хон Че). <b>На остров не доставляем даже за доплату.</b> Но букет можно забрать <b>бесплатно в порту на материке</b>. <a href='" + PORT_MAPS + "' target='_blank'>📍 Порт на карте →</a></div>";
    refreshZone(); return;
  }
  window.__island = false;
  if (isAirport(latlng.la, latlng.ln) || latlng.la < AIRPORT_LAT) {
    window.__outside = true; window.__delFee = 0; window.__delLabel = "аэропорт";
    box.innerHTML = head + "<div style='margin-top:8px;font-weight:700;color:var(--err)'>✈️❌ Доставка в аэропорт и всё, что южнее аэропорта (за ним), не осуществляется. Возим только севернее — по Нячангу и северной части Камрани (Bãi Dài). Укажите адрес в зоне доставки.</div>";
    refreshZone(); return;
  }
  if (!inArea(latlng.la, latlng.ln)) {
    window.__outside = true; window.__delFee = 0; window.__delLabel = "вне зоны";
    box.innerHTML = head + "<div style='margin-top:8px;font-weight:700;color:var(--err)'>❌ Адрес вне зоны доставки. Возим по Нячангу, южным пригородам и Камрани.</div>";
    refreshZone(); return;
  }
  window.__outside = false;
  var z = zoneForPoint(latlng.la, latlng.ln) || {key:"",label:"Точка на карте",fee:0,slots:2,min:0};
  window.__delFee = z.fee; window.__delLabel = z.label; window.__zoneKey = z.key; window.__zoneSlots = z.slots; window.__zoneMin = z.min;
  var col = z.fee ? "#8a6d3b" : "#256b3c";
  var feeTxt = z.fee ? ("доплата +" + money(z.fee)) : "бесплатно";
  box.innerHTML = head +
    "<div style='margin-top:8px;font-weight:600;color:" + col + "'>🚚 Зона: " + z.label + " — " + feeTxt + "</div>" +
    (z.fee ? "<div style='font-size:12px;color:#8a6d3b;margin-top:2px'>В эту зону доставка возможна от 1 000 000 ₫.</div>" : "");
  refreshZone();
}

/* поиск через Photon */
var searchInput, resultsBox, searchTimer;
function bindSearch() {
  searchInput = document.getElementById("addrSearch");
  resultsBox = document.getElementById("results");
  searchInput.addEventListener("input", function () {
    var q = searchInput.value.trim();
    clearTimeout(searchTimer);
    if (q.length < 3) { resultsBox.classList.add("hidden"); return; }
    searchTimer = setTimeout(function () { photonSearch(q); }, 350);
  });
  document.addEventListener("click", function (e) { if (!e.target.closest(".searchbox")) resultsBox.classList.add("hidden"); });
}
function labelOf(p) {
  var a = []; if (p.name) a.push(p.name);
  var street = [p.street, p.housenumber].filter(Boolean).join(" "); if (street) a.push(street);
  var loc = p.district || p.city || p.county; if (loc) a.push(loc);
  return a;
}
function photonSearch(q) {
  var url = "https://photon.komoot.io/api/?q=" + encodeURIComponent(q) +
    "&lat=" + CONFIG.NHATRANG[0] + "&lon=" + CONFIG.NHATRANG[1] +
    "&bbox=109.03,11.82,109.32,12.42&lang=en&limit=8";
  fetch(url).then(function (r) { return r.json(); }).then(function (d) { renderResults(d.features || []); })
    .catch(function () { resultsBox.innerHTML = "<div class='empty'>Поиск недоступен, вставьте ссылку на карту.</div>"; resultsBox.classList.remove("hidden"); });
}
function renderResults(feats) {
  if (!feats.length) { resultsBox.innerHTML = "<div class='empty'>Ничего не найдено</div>"; resultsBox.classList.remove("hidden"); return; }
  resultsBox.innerHTML = "";
  feats.forEach(function (f) {
    var p = f.properties, c = f.geometry.coordinates;
    var parts = labelOf(p), title = parts[0] || "Точка", sub = parts.slice(1).join(", ");
    var div = document.createElement("div");
    div.innerHTML = "<div class='rtitle'>" + esc(title) + "</div>" + (sub ? "<div class='rsub'>" + esc(sub) + "</div>" : "");
    div.onclick = function () { searchInput.value = parts.join(", "); resultsBox.classList.add("hidden"); setPoint(c[1], c[0], parts.join(", ")); };
    resultsBox.appendChild(div);
  });
  resultsBox.classList.remove("hidden");
}
function reverseGeo(la, ln) {
  fetch("https://photon.komoot.io/reverse?lat=" + la + "&lon=" + ln).then(function (r) { return r.json(); }).then(function (d) {
    if (d.features && d.features[0]) { var lbl = labelOf(d.features[0].properties).join(", "); if (lbl) { foundLabel = lbl; searchInput.value = lbl; updateFound(); } }
  }).catch(function () {});
}

/* ссылка Google Карт → координаты */
function extractLatLng(s) {
  s = String(s || "");
  var m = s.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/) || s.match(/[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)/) ||
          s.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/) || s.match(/(-?\d{1,2}\.\d{4,}),\s*(-?\d{2,3}\.\d{4,})/);
  return m ? [parseFloat(m[1]), parseFloat(m[2])] : null;
}
function handleGmapLink() {
  var v = document.getElementById("gmapLink").value.trim();
  var err = document.getElementById("gmapErr"); err.textContent = "";
  if (!v) return;
  var c = extractLatLng(v);
  if (c && validGeo(c[0], c[1])) { document.getElementById("addrSearch").value = ""; setPoint(c[0], c[1], "Точка с карты"); reverseGeo(c[0], c[1]); return; }
  err.style.color = "#78716c"; err.textContent = "Определяем место…";
  fetch(CONFIG.API, { method: "POST", body: new URLSearchParams({ action: "geo", url: v }) })
    .then(function (r) { return r.json(); }).then(function (d) {
      if (d && d.ok && validGeo(d.lat, d.lng)) { err.textContent = ""; setPoint(d.lat, d.lng, "Точка с карты"); reverseGeo(d.lat, d.lng); }
      else { err.style.color = "#9b2c2c"; err.textContent = "Не удалось определить место. Найдите в поиске выше или подвиньте булавку."; }
    }).catch(function () { err.style.color = "#9b2c2c"; err.textContent = "Ошибка. Найдите место в поиске выше."; });
}

/* ============ ОТПРАВКА ЗАКАЗА ============ */
function apiPost(data) {
  return fetch(CONFIG.API, { method: "POST", body: new URLSearchParams(data) }).then(function (r) { return r.json(); });
}
var currentId = null, receiptB64 = null, payMethod = "";

function submitOrder(e) {
  e.preventDefault();
  if (document.getElementById("website").value) return;
  var err = document.getElementById("err1"); err.textContent = "";
  var form = e.target;
  if (specialOrderClosed()) { err.textContent = "Онлайн-заказы закрыты до 5 сентября: 4 сентября мы не работаем. С 5 сентября оформление снова доступно."; updateSpecialOrderUi(); return; }
  if (isClosedDeliveryDate(document.getElementById("deliveryDate").value)) { err.textContent = "4 сентября мы не работаем. Выберите 5 сентября или другую доступную дату."; return; }

  var its = cartRead();
  if (!its.length) { err.textContent = "Корзина пуста."; return; }
  // торт нельзя отдельно
  var hasCake = its.some(function (x) { return x.cats.indexOf("cakes") >= 0; });
  var hasOther = its.some(function (x) { return x.cats.indexOf("cakes") < 0; });
  if (hasCake && !hasOther) { err.textContent = "🎂 Торт заказывается только вместе с букетом, шарами или набором."; return; }

  if (!latlng) { err.textContent = "Укажите адрес доставки на карте."; return; }
  if (window.__outside) { err.textContent = (window.__delLabel === "аэропорт") ? "✈️ В аэропорт и южнее аэропорта доставки нет." : "Адрес вне зоны доставки."; return; }
  if (!document.getElementById("deliveryTime").value) { err.textContent = "Выберите время доставки."; return; }

  var sub = cartTotal(), fee = window.__delFee || 0;
  if (fee > 0 && sub < 1000000) { err.textContent = "В зону «" + window.__delLabel + "» доставка от 1 000 000 ₫. Сейчас в корзине " + money(sub, "VND") + "."; return; }

  var rcpt = document.getElementById("rcpt").value.trim();
  var addrText = document.getElementById("addrText").value.trim();
  var comment = document.getElementById("comment").value.trim();
  var chan = form.querySelector("input[name=chan]:checked").value;
  var contact = document.getElementById("contact").value.trim();
  var email = document.getElementById("email").value.trim();
  if (!rcpt || !addrText || !contact || !email) { err.textContent = "Заполните обязательные поля."; return; }
  var placeType = (form.querySelector("input[name=place_type]:checked") || {}).value || "";
  if (!placeType) { err.textContent = "Укажите: отель или частный дом."; return; }
  var hotelName = (document.getElementById("hotelName") || {}).value ? document.getElementById("hotelName").value.trim() : "";
  if (placeType === "hotel" && !hotelName) { err.textContent = "Впишите название отеля."; return; }
  var hotel = placeType === "hotel" ? hotelName : "Частный дом";
  var recipWho = (form.querySelector("input[name=recip_who]:checked") || {}).value || "self";
  var recipContact = (document.getElementById("recipContact") || {}).value ? document.getElementById("recipContact").value.trim() : "";
  if (recipWho === "other" && !recipContact) { err.textContent = "Укажите контакт получателя."; return; }
  var recipStr;
  if (recipWho === "other") {
    var rchan = (form.querySelector("input[name=recip_chan]:checked") || {}).value || "WhatsApp";
    recipStr = "Другой — " + rcpt + " · " + rchan + ": " + recipContact;
  } else {
    recipStr = "Я, сам заказчик · " + chan + ": " + contact;
  }

  // строки заказа
  var items = its.map(function (x) { return x.qty + "× " + x.name; }).join("\n");
  var photos = its.map(function (x) { return CONFIG.DOMAIN + "/" + String(x.img).replace(/\.webp$/i, ".jpg"); }).join("\n");
  var amountStr = fee > 0
    ? money(sub, "VND") + " + доставка " + money(fee, "VND") + " = " + money(sub + fee, "VND")
    : money(sub, "VND") + " · доставка бесплатно";
  var addr = rcpt + " — " + (foundLabel ? foundLabel + ", " : "") + addrText +
             (comment ? " (" + comment + ")" : "") +
             (window.__island ? " [самовывоз в порту]" : "") +
             " 📍 " + mapsLink();
  // контакт из Telegram (если есть) — добавим в заявку
  var tgTag = "";
  if (TG_USER) {
    var uname = TG_USER.username ? "@" + TG_USER.username : "";
    var fio = [TG_USER.first_name, TG_USER.last_name].filter(Boolean).join(" ");
    tgTag = " · TG: " + (fio || "") + (uname ? " " + uname : "") + (TG_USER.id ? " (id" + TG_USER.id + ")" : "");
  }

  var data = {
    action: "new",
    source: CONFIG.SOURCE,
    items: items,
    photos: photos,
    amount: amountStr,
    delivery: ruDate(document.getElementById("deliveryDate").value) + ", " + document.getElementById("deliveryTime").value,
    zone: window.__zoneKey || "",
    ddate: document.getElementById("deliveryDate").value,
    arrive: document.getElementById("deliveryTime").value,
    lat: latlng ? latlng.la : "",
    lng: latlng ? latlng.ln : "",
    address: addr,
    hotel: hotel,
    contact: chan + ": " + contact + tgTag,
    recipient: recipStr,
    email: email,
    lang: "ru",
    tg_id: (TG_USER && TG_USER.id) ? String(TG_USER.id) : ""
  };

  var btn = document.getElementById("submitBtn"), old = btn.innerHTML;
  btn.disabled = true; btn.innerHTML = '<span class="spin"></span>Отправляем…';
  apiPost(data).then(function (r) {
    if (!r || !r.ok) throw new Error();
    currentId = r.orderId;
    goPay(currentId);
  }).catch(function () {
    err.textContent = "Не удалось отправить. Попробуйте ещё раз.";
    btn.disabled = false; btn.innerHTML = old;
  });
}

/* ============ ОПЛАТА ============ */
var PAY = {
  cash: { title: "Наличными при получении", cash: true },
  rub: { title: "Рубли (СБП)", rows: [["Телефон", "+79627155432", "+79627155432"], ["Получатель", "Оксана Анатольевна Я.", null], ["Банк", "Сбербанк или Тинькофф", null]], warn: "Переведите точную сумму и пришлите скрин чека." },
  vnd: { title: "Донги (BIDV)", rows: [["Банк", "BIDV (PGD Bình Tân)", null], ["Счёт", "8865888241", "8865888241"], ["Получатель", "BABASKIN OLEG", null]], vietqr: "https://img.vietqr.io/image/970418-8865888241-qr_only.png?accountName=BABASKIN%20OLEG" },
  usdt: { title: "USDT (TRC-20)", rows: [["Сеть", "TRON (TRC-20)", null], ["Кошелёк", "TGniTscazmp3MJrmLxSgDPnNGeZPyMPVhb", "TGniTscazmp3MJrmLxSgDPnNGeZPyMPVhb"]], qrtext: "TGniTscazmp3MJrmLxSgDPnNGeZPyMPVhb", warn: "Только сеть TRON (TRC-20). 💡 Если переводите из Trust Wallet, иногда бывает ошибка (причина нам неизвестна) — попробуйте оплатить с другого кошелька или приложения, обычно всё проходит. Извините за неудобство 🙏" },
  kzt: { title: "Карта Kaspi", rows: [["Карта", "4400 4303 0499 7486", "4400430304997486"], ["Держатель", "Egor Merkulov", null], ["Банк", "Kaspi Bank", null]] }
};
var PAY_ORDER = [["cash", "💵 Наличные"], ["rub", "🇷🇺 Рубли"], ["vnd", "🇻🇳 Донги"], ["usdt", "USDT"], ["kzt", "Kaspi"]];

function goPay(id) {
  document.getElementById("payOid").textContent = id;
  renderPayChips();
  show("scrPay");
}
function backToData() { show("scrCart"); document.getElementById("submitBtn").textContent = "Сохранить и к оплате"; }

function renderPayChips() {
  var box = document.getElementById("pays");
  box.innerHTML = "";
  PAY_ORDER.forEach(function (pair) {
    var b = document.createElement("div");
    b.className = "pay"; b.textContent = pair[1]; b.dataset.m = pair[0];
    b.onclick = function () {
      box.querySelectorAll(".pay").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      selectPay(pair[0]);
    };
    box.appendChild(b);
  });
}
function selectPay(m) {
  payMethod = PAY[m].title;
  var p = PAY[m], box = document.getElementById("payDetails");
  var isCash = !!p.cash;
  document.getElementById("receiptCard").classList.toggle("hidden", isCash);
  document.getElementById("cashCard").classList.toggle("hidden", !isCash);
  if (isCash) { box.classList.add("hidden"); return; }
  box.classList.remove("hidden");
  var html = '<div style="font-weight:700;margin-bottom:6px">' + p.title + '</div>';
  p.rows.forEach(function (r) {
    html += '<div class="kv"><span style="color:var(--muted)">' + r[0] + '</span><b>' + r[1] +
      (r[2] ? ' <button class="copy" data-c="' + r[2] + '">копировать</button>' : "") + '</b></div>';
  });
  if (p.warn) html += '<div class="warnbox">' + p.warn + '</div>';
  html += '<div class="qr" id="qrBox"></div>';
  box.innerHTML = html;
  var qr = document.getElementById("qrBox");
  if (p.vietqr) { var im = new Image(); im.src = p.vietqr; im.alt = "QR"; im.width = 210; qr.appendChild(im); }
  else if (p.qrtext) { new QRCode(qr, { text: p.qrtext, width: 190, height: 190, correctLevel: QRCode.CorrectLevel.M }); }
  box.querySelectorAll(".copy").forEach(function (b) {
    b.onclick = function () { copyText(b.dataset.c); b.textContent = "скопировано"; setTimeout(function () { b.textContent = "копировать"; }, 1500); };
  });
}

/* чек */
function bindReceipt() {
  var fileWrap = document.getElementById("fileWrap"), fileInput = document.getElementById("receipt");
  fileWrap.onclick = function () { fileInput.click(); };
  fileInput.onchange = function () {
    var f = fileInput.files[0]; if (!f) return;
    var reader = new FileReader();
    reader.onload = function (e) {
      var img = new Image();
      img.onload = function () {
        var max = 1200, w = img.width, h = img.height;
        if (w > h && w > max) { h = Math.round(h * max / w); w = max; } else if (h > max) { w = Math.round(w * max / h); h = max; }
        var c = document.createElement("canvas"); c.width = w; c.height = h;
        c.getContext("2d").drawImage(img, 0, 0, w, h);
        var url = c.toDataURL("image/jpeg", 0.72);
        receiptB64 = url.split(",")[1];
        var pv = document.getElementById("preview"); pv.src = url; pv.style.display = "block";
        fileWrap.classList.add("ok"); fileWrap.textContent = "✓ Чек прикреплён";
        document.getElementById("sendReceipt").disabled = false;
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(f);
  };
  document.getElementById("sendReceipt").onclick = function () {
    if (!receiptB64) return;
    var btn = this, err = document.getElementById("err2"), old = btn.innerHTML;
    err.textContent = ""; btn.disabled = true; btn.innerHTML = '<span class="spin"></span>Отправляем чек…';
    apiPost({ action: "receipt", orderId: currentId, receipt_b64: receiptB64, mime: "image/jpeg", pay: payMethod, lang: "ru", tg_id: (TG_USER && TG_USER.id) ? String(TG_USER.id) : "" })
      .then(function (r) { if (!r || !r.ok) throw new Error(); finishOrder("💰 Оплата получена"); })
      .catch(function () { err.textContent = "Не удалось отправить чек. Попробуйте ещё раз."; btn.disabled = false; btn.innerHTML = old; });
  };
  document.getElementById("cashBtn").onclick = function () {
    var btn = this, err = document.getElementById("errCash"), old = btn.innerHTML;
    err.textContent = ""; btn.disabled = true; btn.innerHTML = '<span class="spin"></span>Отправляем…';
    apiPost({ action: "cash", orderId: currentId, lang: "ru", tg_id: (TG_USER && TG_USER.id) ? String(TG_USER.id) : "" })
      .then(function (r) { if (!r || !r.ok) throw new Error(); finishOrder("💵 Оплата наличными при получении"); })
      .catch(function () { err.textContent = "Ошибка. Попробуйте ещё раз."; btn.disabled = false; btn.innerHTML = old; });
  };
}
function finishOrder(note) {
  document.getElementById("doneText").innerHTML =
    note + " по заказу <span class='oid'>" + currentId + "</span>.<br>Подтвердим в течение ~10 минут (06:00–21:00). 🌸";
  localStorage.removeItem(LS);
  show("scrDone");
}
function restart() { currentId = null; receiptB64 = null; searchQ = ""; document.getElementById("q").value = ""; renderGrid(); show("scrCatalog"); }

/* ---- утилиты ---- */
function getParam(k) { try { return new URLSearchParams(location.search).get(k) || ""; } catch (_) { return ""; } }
function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
function copyText(t) { if (navigator.clipboard) navigator.clipboard.writeText(t); }
function toast(m) {
  var t = document.getElementById("toast");
  t.textContent = m; t.classList.add("show");
  clearTimeout(t._h); t._h = setTimeout(function () { t.classList.remove("show"); }, 1600);
}

/* ---- инициализация ---- */
document.addEventListener("DOMContentLoaded", function () {
  initDate(); initMap(); bindSearch(); bindReceipt();
  document.getElementById("gmapBtn").onclick = handleGmapLink;
  document.getElementById("gmapLink").addEventListener("paste", function () { setTimeout(handleGmapLink, 60); });
  document.getElementById("orderForm").addEventListener("submit", submitOrder);
  // автоподстановка контакта из Telegram
  if (TG_USER) {
    var cEl = document.getElementById("contact");
    if (TG_USER.username) cEl.value = "@" + TG_USER.username;
    var rEl = document.getElementById("rcpt");
    if (TG_USER.first_name && !rEl.value) rEl.placeholder = "Имя получателя (напр. " + TG_USER.first_name + ")";
  }
  // возврат к оплате по ссылке из бота (?order=ID или startapp=pay_ID)
  var reopen = getParam("order");
  if (!reopen && TG && TG.initDataUnsafe && TG.initDataUnsafe.start_param) {
    reopen = String(TG.initDataUnsafe.start_param).replace(/^pay[_-]?/i, "");
  }
  if (reopen) { currentId = reopen; goPay(reopen); }
});

// Получатель: контакт получателя обязателен и виден только для «Другой человек»
(function () {
  function wire() {
    var form = document.getElementById("orderForm");
    if (!form) return;
    var block = document.getElementById("recipContactBlock");
    var rc = document.getElementById("recipContact");
    var radios = form.querySelectorAll("input[name=recip_who]");
    if (!block || !radios.length) return;
    function upd() {
      var sel = form.querySelector("input[name=recip_who]:checked");
      var other = sel && sel.value === "other";
      block.style.display = other ? "" : "none";
      if (rc) { rc.required = !!other; if (!other) rc.value = ""; }
    }
    Array.prototype.forEach.call(radios, function (r) { r.addEventListener("change", upd); });
    upd();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();
})();

// Тип адреса: название отеля видно и обязательно только для «Отель»
(function () {
  function wire() {
    var form = document.getElementById("orderForm");
    if (!form) return;
    var block = document.getElementById("hotelNameBlock");
    var hn = document.getElementById("hotelName");
    var radios = form.querySelectorAll("input[name=place_type]");
    if (!block || !radios.length) return;
    function upd() {
      var sel = form.querySelector("input[name=place_type]:checked");
      var isHotel = sel && sel.value === "hotel";
      block.style.display = isHotel ? "" : "none";
      if (hn) { hn.required = !!isHotel; if (!isHotel) hn.value = ""; }
    }
    Array.prototype.forEach.call(radios, function (r) { r.addEventListener("change", upd); });
    upd();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();
})();

/* 📸 Карточка заказа в «Карте заказов» (16.11.2026): фото заказа (до 5), открытка и пожелания — текстом и/или по 1 фото.
   Подключается в /buh/ и /courier/. Фото с сайта (корзина) подтягиваются сами, остальные загружаются с телефона.
   OrderCard.mount(el, { id, api: function(action, extra){ return Promise }, canEdit: bool, toast: fn }) */
(function(){
  var CSS = '.oc{margin-top:12px}.oc .oc-box{background:#fff;border:1px solid #e7e2ef;border-radius:12px;padding:12px;margin-bottom:10px}'
    + '.oc .oc-h{font-weight:700;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center}'
    + '.oc .oc-h span{font-weight:400;color:#888;font-size:12px}'
    + '.oc .oc-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}'
    + '.oc .oc-th{position:relative;aspect-ratio:1/1;border-radius:10px;overflow:hidden;background:#f1eef6;cursor:pointer}'
    + '.oc .oc-th img{width:100%;height:100%;object-fit:cover;display:block}'
    + '.oc .oc-tag{position:absolute;left:4px;bottom:4px;background:rgba(0,0,0,.55);color:#fff;font-size:10px;padding:1px 5px;border-radius:6px}'
    + '.oc .oc-del{position:absolute;right:4px;top:4px;width:26px;height:26px;border-radius:50%;border:0;background:rgba(0,0,0,.6);color:#fff;font-size:14px;line-height:26px;padding:0;cursor:pointer}'
    + '.oc .oc-add{display:inline-block;margin-top:10px;padding:9px 14px;border-radius:10px;background:#efe9fb;color:#6d28d9;font-weight:700;font-size:14px;cursor:pointer}'
    + '.oc .oc-add input{display:none}'
    + '.oc textarea{width:100%;box-sizing:border-box;min-height:70px;border:1px solid #ddd;border-radius:10px;padding:9px;font:inherit;font-size:15px;resize:vertical}'
    + '.oc .oc-txt{white-space:pre-wrap;font-size:15px}.oc .oc-empty{color:#999;font-size:13px}'
    + '.oc .oc-one{width:110px;margin-top:8px}.oc .oc-st{color:#888;font-size:12px;margin-top:6px;min-height:14px}'
    + '.oc .oc-save{width:100%;padding:12px;border:0;border-radius:10px;background:#6d28d9;color:#fff;font-weight:700;font-size:15px;cursor:pointer}'
    + '.oc-full{position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:9999;display:flex;align-items:center;justify-content:center}'
    + '.oc-full img{max-width:100%;max-height:100%;object-fit:contain}';
  var styled = false, CACHE = {};
  function esc(s){ return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function addStyle(){ if(styled) return; var st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st); styled = true; }

  // сжатие фото на телефоне: JPEG, длинная сторона ≤1600 (если тяжело — меньше)
  function compress(file){
    return new Promise(function(res){
      var rd = new FileReader();
      rd.onload = function(){ var img = new Image();
        img.onload = function(){
          var steps = [[1600,.8],[1280,.72],[1024,.65],[800,.6]], out = '';
          for(var i = 0; i < steps.length; i++){
            var k = Math.min(1, steps[i][0] / Math.max(img.width, img.height));
            var c = document.createElement('canvas'); c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
            c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
            try{ out = c.toDataURL('image/jpeg', steps[i][1]); }catch(e){ out = ''; }
            if(out && out.length < 850000) break;
          }
          res(out && out.length < 850000 ? out : '');
        };
        img.onerror = function(){ res(''); }; img.src = rd.result; };
      rd.onerror = function(){ res(''); }; rd.readAsDataURL(file);
    });
  }
  function full(src){ var d = document.createElement('div'); d.className = 'oc-full'; d.innerHTML = '<img src="' + esc(src) + '">'; d.onclick = function(){ d.remove(); }; document.body.appendChild(d); }

  function mount(el, o){
    addStyle();
    var S = { data: null, busy: false };
    el.className = 'oc';
    el.innerHTML = '<div class="oc-box oc-empty">Загружаю фото и открытку…</div>';
    function toast(m){ if(o.toast) o.toast(m); }

    function thumb(p, canDel){
      var w = document.createElement('div'); w.className = 'oc-th';
      var im = document.createElement('img'); im.alt = '';
      if(p.src) im.src = p.src;
      else if(CACHE[p.id]) im.src = CACHE[p.id];
      else o.api('mapPhoto', { photoId: p.id }, true).then(function(r){ if(r && r.ok){ CACHE[p.id] = r.src; im.src = r.src; } });
      w.appendChild(im);
      if(p.kind === 'site'){ var t = document.createElement('span'); t.className = 'oc-tag'; t.textContent = 'с сайта'; w.appendChild(t); }
      w.onclick = function(){ var s = im.getAttribute('src'); if(s) full(s); };
      if(canDel){ var x = document.createElement('button'); x.className = 'oc-del'; x.textContent = '✕';
        x.onclick = function(e){ e.stopPropagation(); if(!confirm('Удалить это фото?')) return;
          o.api('mapPhotoDel', { id: o.id, photoId: p.id }).then(function(r){ if(r && r.ok){ S.data = r; render(); toast('Фото удалено'); } else toast((r && r.error) || 'Ошибка'); }); };
        w.appendChild(x); }
      return w;
    }
    function addBtn(label, kind, multiple, stEl){
      var l = document.createElement('label'); l.className = 'oc-add'; l.textContent = label;
      var inp = document.createElement('input'); inp.type = 'file'; inp.accept = 'image/*'; if(multiple) inp.multiple = true;
      inp.onchange = function(){ upload(kind, Array.prototype.slice.call(inp.files || []), stEl); inp.value = ''; };
      l.appendChild(inp); return l;
    }
    async function upload(kind, files, stEl){
      if(!files.length || S.busy) return;
      if(kind === 'order'){ var have = S.data.photos.filter(function(p){ return p.kind === 'order'; }).length, left = (S.data.maxOrder || 5) - have;
        if(left <= 0){ toast('Уже 5 фото — сначала удали лишнее'); return; }
        if(files.length > left){ toast('Добавлю только ' + left + ' (максимум 5)'); files = files.slice(0, left); } }
      else files = files.slice(0, 1);
      S.busy = true; var okN = 0;
      for(var i = 0; i < files.length; i++){
        stEl.textContent = 'Загружаю ' + (i + 1) + ' из ' + files.length + '…';
        var du = await compress(files[i]);
        if(!du){ toast('Не получилось прочитать фото'); continue; }
        var r = await o.api('mapPhotoAdd', { id: o.id, kind: kind, data: du }, true);
        if(r && r.ok){ S.data = r; okN++; } else { toast((r && r.error) || 'Ошибка загрузки'); break; }
      }
      S.busy = false; stEl.textContent = ''; render(); if(okN) toast(okN > 1 ? ('Добавлено фото: ' + okN) : 'Фото добавлено');
    }

    function section(title, kind, text, canEdit){
      var box = document.createElement('div'); box.className = 'oc-box';
      box.innerHTML = '<div class="oc-h">' + title + '</div>';
      var ta = null;
      if(canEdit){ ta = document.createElement('textarea'); ta.value = text || ''; ta.placeholder = kind === 'card' ? 'текст открытки' : 'пожелания клиента'; box.appendChild(ta); }
      else { var d = document.createElement('div'); if(text){ d.className = 'oc-txt'; d.textContent = text; } else { d.className = 'oc-empty'; d.textContent = '— нет —'; } box.appendChild(d); }
      var ph = S.data.photos.filter(function(p){ return p.kind === kind; })[0];
      if(ph){ var one = document.createElement('div'); one.className = 'oc-one'; one.appendChild(thumb(ph, canEdit)); box.appendChild(one); }
      var st = document.createElement('div'); st.className = 'oc-st';
      if(canEdit) box.appendChild(addBtn(ph ? '🔄 Заменить фото' : '📷 Фото ' + (kind === 'card' ? 'открытки' : 'пожеланий'), kind, false, st));
      box.appendChild(st);
      return { box: box, ta: ta };
    }

    function render(){
      var d = S.data, ce = !!o.canEdit; el.innerHTML = '';
      var site = d.photos.filter(function(p){ return p.kind === 'site'; }), up = d.photos.filter(function(p){ return p.kind === 'order'; });
      var b1 = document.createElement('div'); b1.className = 'oc-box';
      b1.innerHTML = '<div class="oc-h">📸 Фото заказа <span>' + up.length + ' из ' + (d.maxOrder || 5) + (site.length ? (' · с сайта: ' + site.length) : '') + '</span></div>';
      if(site.length || up.length){ var g = document.createElement('div'); g.className = 'oc-grid';
        site.concat(up).forEach(function(p){ g.appendChild(thumb(p, ce)); }); b1.appendChild(g); }
      else { var e = document.createElement('div'); e.className = 'oc-empty'; e.textContent = 'Фото пока нет'; b1.appendChild(e); }
      var st1 = document.createElement('div'); st1.className = 'oc-st';
      if(ce && up.length < (d.maxOrder || 5)) b1.appendChild(addBtn('➕ Добавить фото', 'order', true, st1));
      b1.appendChild(st1); el.appendChild(b1);
      var c = section('💌 Открытка', 'card', d.card, ce); el.appendChild(c.box);
      var w = section('🙏 Пожелания', 'wish', d.wish, ce); el.appendChild(w.box);
      if(ce){ var sv = document.createElement('button'); sv.className = 'oc-save'; sv.textContent = '💾 Сохранить открытку и пожелания';
        sv.onclick = function(){ o.api('mapCardSave', { id: o.id, card: c.ta.value.trim(), wish: w.ta.value.trim() }).then(function(r){ if(r && r.ok){ S.data = r; render(); toast('Сохранено'); } else toast((r && r.error) || 'Ошибка'); }); };
        el.appendChild(sv); }
    }

    o.api('mapCard', { id: o.id }, true).then(function(r){
      if(!r || !r.ok){ el.innerHTML = '<div class="oc-box oc-empty">' + esc((r && r.error) || 'Не удалось загрузить фото и открытку') + '</div>'; return; }
      S.data = r; render();
    });
  }
  window.OrderCard = { mount: mount };
})();

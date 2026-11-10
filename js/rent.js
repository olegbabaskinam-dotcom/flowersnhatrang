/* 👶 Календарь аренды колясок + онлайн-бронь (06.11.2026)
   Вставка: <div id="rentCal" data-lang="ru|en|ko"></div> + <script src="/js/rent.js?v=…" defer></script>
   Данные: воркер buhproxy (rentPublic / rentCheck / rentHold), заявка — Apps Script «Заявки» (action new). */
(function(){
  var API='https://buhproxy.olegbabaskin-am.workers.dev/';
  var ZAYAVKI='https://script.google.com/macros/s/AKfycbzDz8tCuWtC4oIA3ajYgt_m5Ui9fZPTgVRiXzVjJTNVrSiP4vNvaNzblCpWJSELOqVC/exec';
  var root=document.getElementById('rentCal'); if(!root) return;
  var L=(root.getAttribute('data-lang')||'ru'); if(L==='kr') L='ko';
  var T={
    ru:{mon:['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],wd:['вс','пн','вт','ср','чт','пт','сб'],
      title:'Свободные дни и онлайн-бронь',step:'1) Отметьте одну или несколько колясок · 2) нажмите день доставки · 3) нажмите день забора',
      col:'Коляска',free:'свободно',busy:'занято',part:'занято часть дня',sel:'ваши даты',loading:'Загружаю календарь…',err:'Календарь не загрузился. Напишите нам в WhatsApp или Telegram.',
      pickEnd:'Теперь нажмите день забора',pickItem:'Отметьте коляску',sum:'Итого',days:'дн.',perOne:'за коляску',deliv:'Доставка',pick:'Забор',time:'Время',
      hotel:'Отель',room:'Номер комнаты',guest:'Имя и фамилия на английском (как при заселении)',chan:'Где с вами связаться',contact:'Номер / ник',email:'Email (необязательно)',note:'Комментарий',
      btn:'Забронировать',sending:'Отправляю…',reset:'Сбросить',ok1:'Заявка №',ok2:'принята! Оператор напишет вам и подтвердит бронь. Оплата 100% при доставке, без залога.',
      eHotel:'Укажите отель',eRoom:'Укажите номер комнаты',eGuest:'Укажите имя и фамилию на английском',eContact:'Укажите номер или ник для связи',eSend:'Не отправилось. Попробуйте ещё раз или напишите нам в WhatsApp.',
      today:'Онлайн — со следующего дня. На сегодня — через оператора в WhatsApp / Telegram.',gap:'Между забором и следующей доставкой одной коляски нужно 2 часа.',more:'дольше 7 дней — +130 000 ₫ за каждый день, максимум 30 дней',max:'Максимум 30 дней'},
    en:{mon:['January','February','March','April','May','June','July','August','September','October','November','December'],wd:['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],
      title:'Free dates & online booking',step:'1) Tick one or more strollers · 2) tap the delivery day · 3) tap the pick-up day',
      col:'Stroller',free:'free',busy:'booked',part:'booked part of the day',sel:'your dates',loading:'Loading calendar…',err:'Calendar failed to load. Message us on WhatsApp or Telegram.',
      pickEnd:'Now tap the pick-up day',pickItem:'Tick a stroller',sum:'Total',days:'days',perOne:'per stroller',deliv:'Delivery',pick:'Pick-up',time:'Time',
      hotel:'Hotel',room:'Room number',guest:'First and last name (as at check-in)',chan:'How to contact you',contact:'Number / username',email:'Email (optional)',note:'Comment',
      btn:'Book now',sending:'Sending…',reset:'Reset',ok1:'Request #',ok2:'received! Our operator will message you to confirm. Pay 100% on delivery, no deposit.',
      eHotel:'Enter the hotel',eRoom:'Enter the room number',eGuest:'Enter your first and last name',eContact:'Enter a number or username',eSend:'Not sent. Please try again or message us on WhatsApp.',
      today:'Online booking starts from tomorrow. For today — message our operator.',gap:'One stroller needs 2 hours between pick-up and the next delivery.',more:'over 7 days — +130,000 ₫ per day, 30 days max',max:'30 days maximum'},
    ko:{mon:['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'],wd:['일','월','화','수','목','금','토'],
      title:'예약 가능 날짜 · 온라인 예약',step:'1) 유모차를 선택하세요(여러 대 가능) · 2) 배달 날짜 · 3) 회수 날짜를 누르세요',
      col:'유모차',free:'예약 가능',busy:'예약됨',part:'일부 시간 예약됨',sel:'선택한 날짜',loading:'달력을 불러오는 중…',err:'달력을 불러오지 못했습니다. 카카오톡으로 문의해 주세요.',
      pickEnd:'이제 회수 날짜를 누르세요',pickItem:'유모차를 선택하세요',sum:'합계',days:'일',perOne:'유모차 1대',deliv:'배달',pick:'회수',time:'시간',
      hotel:'호텔',room:'객실 번호',guest:'영문 이름 (체크인 시 이름)',chan:'연락 방법',contact:'번호 / 아이디',email:'이메일 (선택)',note:'요청 사항',
      btn:'예약하기',sending:'보내는 중…',reset:'초기화',ok1:'예약 요청 #',ok2:'접수되었습니다! 담당자가 연락드려 확정합니다. 배달 시 100% 현장결제, 보증금 없음.',
      eHotel:'호텔을 입력하세요',eRoom:'객실 번호를 입력하세요',eGuest:'영문 이름을 입력하세요',eContact:'연락처를 입력하세요',eSend:'전송되지 않았습니다. 다시 시도하거나 카카오톡으로 문의해 주세요.',
      today:'온라인 예약은 내일부터 가능합니다. 오늘은 담당자에게 문의해 주세요.',gap:'같은 유모차는 회수 후 다음 배달까지 2시간이 필요합니다.',more:'7일 초과 시 하루 +130,000 ₫, 최대 30일',max:'최대 30일'}
  }[L]||null; if(!T) return;
  var CH=L==='ko'?['KakaoTalk','WhatsApp','Instagram','Telegram']:['WhatsApp','Telegram','Instagram','KakaoTalk'];
  var css='.rq{max-width:64rem;margin:0 auto;font-family:Montserrat,sans-serif;color:#1a1a1a}.rq-step{text-align:center;font-size:13px;color:#57534e;margin:0 0 12px}'+
    '.rq-nav{display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:10px}.rq-nav b{font-size:17px;min-width:150px;text-align:center}.rq-nav button{width:38px;height:38px;border-radius:50%;border:1.5px solid #c0687a;background:#fff;color:#c0687a;font-size:20px;cursor:pointer}'+
    '.rq-box{background:#fff;border:1px solid #f0d0d8;border-radius:16px;overflow:hidden}.rq-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}'+
    '.rq-t{border-collapse:separate;border-spacing:0;font-size:12px}.rq-t th{font-weight:600;color:#a8a29e;padding:6px 0 4px;min-width:30px;text-align:center;line-height:1.1}.rq-t th small{display:block;font-weight:400;font-size:9px}.rq-t th.we{color:#c0687a}'+
    '.rq-t td{height:52px;min-width:30px;border-left:1px solid #f5ecee;border-top:1px solid #f5ecee;padding:0;cursor:pointer}.rq-t td.past{background:repeating-linear-gradient(45deg,#fafaf9,#fafaf9 4px,#f2f0ee 4px,#f2f0ee 8px);cursor:default}'+
    '.rq-t td.now,.rq-t th.now{box-shadow:inset 0 0 0 2px #c0687a}.rq-t td.sel{outline:2px solid #c0687a;outline-offset:-2px}.rq-t td.selr{background-color:#fce8ee}'+
    '.rq-t .it{position:sticky;left:0;z-index:2;background:#fff;min-width:170px;max-width:200px;text-align:left;padding:6px 8px 6px 10px;border-left:none;box-shadow:2px 0 5px rgba(0,0,0,.04);cursor:pointer}'+
    '@media(max-width:600px){.rq-t .it{min-width:132px;max-width:150px}.rq-in img{width:32px;height:32px;flex-basis:32px}}'+
    '.rq-in{display:flex;gap:8px;align-items:center}.rq-in input{width:18px;height:18px;accent-color:#c0687a;flex:0 0 18px}.rq-in img{width:40px;height:40px;object-fit:cover;border-radius:9px;flex:0 0 40px}.rq-in b{display:block;font-size:12px;line-height:1.25}.rq-in small{display:block;color:#a8a29e;font-size:10px;line-height:1.2;margin-top:2px}'+
    '.rq-leg{display:flex;flex-wrap:wrap;gap:6px 14px;justify-content:center;font-size:11px;color:#78716c;padding:10px}.rq-leg i{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-2px;margin-right:5px;border:1px solid #e7e5e4}'+
    '.rq-note{text-align:center;font-size:12px;color:#a8566a;margin:10px 0 0}.rq-f{max-width:34rem;margin:16px auto 0;background:#fff;border:1px solid #f0d0d8;border-radius:16px;padding:16px}'+
    '.rq-f label{display:block;font-size:12px;color:#78716c;margin:10px 0 4px}.rq-f input,.rq-f select,.rq-f textarea{width:100%;box-sizing:border-box;padding:10px 12px;border:1px solid #e7d6dc;border-radius:10px;font-size:15px;font-family:inherit;background:#fff}'+
    '.rq-2{display:grid;grid-template-columns:1fr 1fr;gap:8px}.rq-sum{background:#fdf4f7;border-radius:12px;padding:10px 12px;font-size:14px;line-height:1.5}.rq-sum b{color:#a8566a}'+
    '.rq-btn{display:block;width:100%;margin-top:14px;padding:13px;border:none;border-radius:12px;background:#c0687a;color:#fff;font-weight:700;font-size:16px;cursor:pointer}.rq-btn:disabled{opacity:.6}.rq-lnk{display:block;text-align:center;margin-top:8px;font-size:13px;color:#a8566a;cursor:pointer;background:none;border:none;width:100%}'+
    '.rq-err{color:#b91c1c;font-size:13px;text-align:center;margin-top:8px;min-height:16px}.rq-ok{background:#ecfdf5;border:1px solid #a7f3d0;border-radius:14px;padding:16px;text-align:center;font-size:15px;line-height:1.5;color:#065f46}.rq-hp{position:absolute;left:-9999px}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);
  var S={mon:null,data:null,sel:[],s:null,e:null,today:null};
  function two(n){ return (n<10?'0':'')+n; }
  function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function mn(t){ var m=String(t||'').match(/^(\d{1,2}):(\d{2})$/); return m?(+m[1]*60+ +m[2]):null; }
  function dnum(s){ var p=s.split('-'); return Math.round(Date.UTC(+p[0],+p[1]-1,+p[2])/864e5); }
  function days(a,b){ return dnum(b)-dnum(a)+1; }
  function dm(s){ var p=s.split('-'); return p[2]+'.'+p[1]; }
  function price(d){ var P=(S.data&&S.data.prices)||[300000,400000,500000,650000,750000,900000,1000000], X=(S.data&&S.data.extra)||130000; d=Math.max(1,Math.min(30,d)); return d<=7?P[d-1]:P[6]+(d-7)*X; }
  function vnd(n){ return Math.round(n).toLocaleString(L==='ru'?'ru-RU':'en-US').replace(/,/g,L==='ru'?' ':',')+' ₫'; }
  function money(n){ var s=vnd(n)+' · $'+Math.round(n/25000); if(L==='ru') s+=' · '+(Math.ceil(n/280/100)*100).toLocaleString('ru-RU')+' ₽'; return s; }
  function itemName(it){ return L==='en'?(it.name_en||it.name):(L==='ko'?(it.name_ko||it.name):it.name); }
  function itemDescr(it){ return L==='en'?(it.descr_en||it.descr):(L==='ko'?(it.descr_ko||it.descr):it.descr); }
  function post(u,b,form){ return fetch(u,form?{method:'POST',body:new URLSearchParams(b)}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}).then(function(r){ return r.json(); }); }
  function load(mon){
    root.innerHTML='<div class="rq"><p class="rq-step">'+T.loading+'</p></div>';
    post(API,{action:'rentPublic',month:mon||''}).then(function(r){ if(!r||!r.ok) throw 0; S.data=r; S.mon=r.month; S.today=r.today; if(!S.sel.length && r.items.length===1) S.sel=[r.items[0].id]; draw(); })
      .catch(function(){ root.innerHTML='<div class="rq"><p class="rq-step">'+T.err+'</p></div>'; });
  }
  function busyFor(id){ return (S.data.busy||[]).filter(function(b){ return b.item_id===id; }); }
  // занятость дня: доли [0..1] рабочего дня 07–21, с учётом 2 ч до/после брони
  function segs(id, ds){ var out=[], T0=420, T1=1260, G=(S.data.gap||120);
    busyFor(id).forEach(function(b){ var s0=dnum(b.sdate)*1440+mn(b.stime)-G, e0=dnum(b.edate)*1440+mn(b.etime)+G, d0=dnum(ds)*1440;
      var a=Math.max(s0,d0+T0), z=Math.min(e0,d0+T1); if(z>a) out.push([(a-d0-T0)/(T1-T0),(z-d0-T0)/(T1-T0)]); });
    return out; }
  function full(sg){ var c=0; sg.forEach(function(x){ c+=x[1]-x[0]; }); return c>=.98; }
  function grad(sg, base){ if(!sg.length) return base||''; sg.sort(function(a,b){return a[0]-b[0];}); var st=[],p=0,bc=base||'transparent';
    sg.forEach(function(x){ var a=Math.round(x[0]*100), b=Math.round(x[1]*100); if(a>p) st.push(bc+' '+p+'%',bc+' '+a+'%'); st.push('#d6d3d1 '+a+'%','#d6d3d1 '+b+'%'); p=Math.max(p,b); });
    if(p<100) st.push(bc+' '+p+'%',bc+' 100%'); return 'linear-gradient(90deg,'+st.join(',')+')'; }
  function draw(){
    var d=S.data, p=S.mon.split('-'), y=+p[0], m=+p[1], nd=new Date(Date.UTC(y,m,0)).getUTCDate();
    var h='<div class="rq"><p class="rq-step">'+T.step+'</p><div class="rq-nav"><button type="button" data-nav="-1" aria-label="‹">‹</button><b>'+T.mon[m-1]+' '+y+'</b><button type="button" data-nav="1" aria-label="›">›</button></div>';
    h+='<div class="rq-box"><div class="rq-wrap"><table class="rq-t"><thead><tr><th class="it">'+T.col+'</th>';
    for(var i=1;i<=nd;i++){ var ds=S.mon+'-'+two(i), w=new Date(Date.UTC(y,m-1,i)).getUTCDay(); h+='<th class="'+(ds===S.today?'now':'')+(w===0||w===6?' we':'')+'">'+i+'<small>'+T.wd[w]+'</small></th>'; }
    h+='</tr></thead><tbody>';
    d.items.forEach(function(it){ var on=S.sel.indexOf(it.id)>=0;
      h+='<tr><td class="it" data-item="'+it.id+'"><div class="rq-in"><input type="checkbox" '+(on?'checked':'')+' tabindex="-1" aria-label="'+esc(itemName(it))+'">'+(it.photo?'<img src="'+esc(it.photo)+'" alt="" loading="lazy">':'')+'<div><b>№'+it.num+' '+esc(itemName(it))+'</b>'+(itemDescr(it)?'<small>'+esc(itemDescr(it))+'</small>':'')+(it.url&&L==='ru'?'<small><a href="'+esc(it.url)+'" style="color:#c0687a">фото →</a></small>':'')+'</div></div></td>';
      for(var i=1;i<=nd;i++){ var ds=S.mon+'-'+two(i), past=ds<=S.today, sg=segs(it.id,ds);
        var inR=on&&S.s&&ds>=S.s&&ds<=(S.e||S.s), cls=(past?'past':'')+(ds===S.today?' now':'')+(inR?' selr':'')+(on&&(ds===S.s||ds===S.e)?' sel':'');
        var bg=past?'':grad(sg, inR?'#fce8ee':'');
        h+='<td class="'+cls+'" data-day="'+ds+'" data-it="'+it.id+'" title="'+(sg.length?(full(sg)?T.busy:T.part):T.free)+'"'+(bg?' style="background:'+bg+'"':'')+'></td>'; }
      h+='</tr>'; });
    h+='</tbody></table></div><div class="rq-leg"><span><i></i>'+T.free+'</span><span><i style="background:#d6d3d1"></i>'+T.busy+'</span><span><i style="background:linear-gradient(90deg,#fff 50%,#d6d3d1 50%)"></i>'+T.part+'</span><span><i style="background:#fce8ee;border-color:#c0687a"></i>'+T.sel+'</span></div></div>';
    h+='<p class="rq-note">'+T.today+' '+T.gap+'</p>';
    h+='<div id="rqForm"></div></div>';
    root.innerHTML=h; form();
    // прокрутить календарь так, чтобы первым был сегодняшний день (на телефоне видно ближайшие даты)
    try{ var w=root.querySelector('.rq-wrap'), th=root.querySelector('.rq-t th.now'), it=root.querySelector('.rq-t th.it'); if(w&&th&&it) w.scrollLeft=Math.max(0,th.offsetLeft-it.offsetWidth); }catch(_){}
  }
  function form(){
    var box=document.getElementById('rqForm'); if(!box) return;
    if(!S.sel.length){ box.innerHTML=''; return; }
    if(!S.s){ box.innerHTML=''; return; }
    if(!S.e){ box.innerHTML='<div class="rq-f"><div class="rq-sum">'+T.deliv+': <b>'+dm(S.s)+'</b><br>'+T.pickEnd+'</div><button type="button" class="rq-lnk" data-reset="1">'+T.reset+'</button></div>'; return; }
    var n=days(S.s,S.e), per=price(n), tot=per*S.sel.length;
    var names=S.data.items.filter(function(x){ return S.sel.indexOf(x.id)>=0; }).map(function(x){ return '№'+x.num+' '+esc(itemName(x)); }).join(', ');
    var topt=function(v){ var o=''; for(var t=420;t<=1260;t+=30){ var hh=two(Math.floor(t/60))+':'+two(t%60); o+='<option'+(hh===v?' selected':'')+'>'+hh+'</option>'; } return o; };
    var keep=function(id){ var el=document.getElementById(id); return el?el.value:''; };
    var v={st:keep('rq_st')||'10:00',et:keep('rq_et')||'18:00',h:keep('rq_h'),r:keep('rq_r'),g:keep('rq_g'),c:keep('rq_c'),ch:keep('rq_ch')||CH[0],e:keep('rq_e'),n:keep('rq_n')};
    box.innerHTML='<div class="rq-f"><div class="rq-sum">👶 '+names+'<br>'+T.deliv+': <b>'+dm(S.s)+'</b> → '+T.pick+': <b>'+dm(S.e)+'</b> · '+n+' '+T.days+(n>30?' — <b>'+T.max+'</b>':'')+'<br>'+T.sum+': <b>'+money(tot)+'</b>'+(S.sel.length>1?' ('+money(per)+' '+T.perOne+')':'')+(n>7?'<br><small>'+T.more+'</small>':'')+'</div>'+
      '<div class="rq-2"><div><label>'+T.deliv+' · '+T.time+'</label><select id="rq_st">'+topt(v.st)+'</select></div><div><label>'+T.pick+' · '+T.time+'</label><select id="rq_et">'+topt(v.et)+'</select></div></div>'+
      '<label>'+T.hotel+'</label><input id="rq_h" value="'+esc(v.h)+'" autocomplete="off">'+
      '<div class="rq-2"><div><label>'+T.room+'</label><input id="rq_r" value="'+esc(v.r)+'"></div><div><label>'+T.chan+'</label><select id="rq_ch">'+CH.map(function(c){ return '<option'+(c===v.ch?' selected':'')+'>'+c+'</option>'; }).join('')+'</select></div></div>'+
      '<label>'+T.guest+'</label><input id="rq_g" value="'+esc(v.g)+'" autocomplete="name">'+
      '<label>'+T.contact+'</label><input id="rq_c" value="'+esc(v.c)+'" autocomplete="tel">'+
      '<label>'+T.email+'</label><input id="rq_e" type="email" value="'+esc(v.e)+'" autocomplete="email">'+
      '<label>'+T.note+'</label><textarea id="rq_n" rows="2">'+esc(v.n)+'</textarea>'+
      '<input class="rq-hp" id="rq_hp" tabindex="-1" autocomplete="off" aria-hidden="true">'+
      '<button type="button" class="rq-btn" id="rqGo"'+(n>30?' disabled':'')+'>'+T.btn+'</button><div class="rq-err" id="rqErr"></div><button type="button" class="rq-lnk" data-reset="1">'+T.reset+'</button></div>';
  }
  root.addEventListener('click',function(ev){
    var t=ev.target; if(!S.data) return;
    var nav=t.closest&&t.closest('[data-nav]'); if(nav){ var p=S.mon.split('-'), y=+p[0], m=+p[1]-1+(+nav.getAttribute('data-nav')); y+=Math.floor(m/12); m=((m%12)+12)%12; load(y+'-'+two(m+1)); return; }
    if(t.closest&&t.closest('[data-reset]')){ S.s=null; S.e=null; draw(); return; }
    if(t.tagName==='A') return;
    var it=t.closest&&t.closest('td.it'); if(it){ var id=+it.getAttribute('data-item'), k=S.sel.indexOf(id); if(k>=0) S.sel.splice(k,1); else S.sel.push(id); draw(); return; }
    var c=t.closest&&t.closest('td[data-day]'); if(c){ var ds=c.getAttribute('data-day'), iid=+c.getAttribute('data-it'); if(ds<=S.today) return;
      if(S.sel.indexOf(iid)<0) S.sel.push(iid);
      if(!S.s||S.e||ds<S.s){ S.s=ds; S.e=null; } else { S.e=ds; }
      draw(); var f=document.getElementById('rqForm'); if(f&&S.e) f.scrollIntoView({behavior:'smooth',block:'nearest'}); return; }
    if(t.id==='rqGo') send();
  });
  root.addEventListener('change',function(ev){ if(ev.target&&ev.target.tagName==='INPUT'&&ev.target.type==='checkbox'){ ev.preventDefault(); } });
  function send(){
    var err=document.getElementById('rqErr'), btn=document.getElementById('rqGo'); err.textContent='';
    var g=function(id){ return (document.getElementById(id).value||'').trim(); };
    if(!S.sel.length){ err.textContent=T.pickItem; return; }
    if(!g('rq_h')){ err.textContent=T.eHotel; return; } if(!g('rq_r')){ err.textContent=T.eRoom; return; }
    if(!g('rq_g')){ err.textContent=T.eGuest; return; } if(!g('rq_c')){ err.textContent=T.eContact; return; }
    var q={items:S.sel.slice(), sdate:S.s, stime:g('rq_st'), edate:S.e, etime:g('rq_et')};
    btn.disabled=true; var old=btn.textContent; btn.textContent=T.sending;
    var fail=function(m){ err.textContent=m||T.eSend; btn.disabled=false; btn.textContent=old; };
    post(API,Object.assign({action:'rentCheck'},q)).then(function(c){
      if(!c||!c.ok) return fail(c&&c.error);
      var ru=function(s){ var p=s.split('-'); return p[2]+'.'+p[1]+'.'+p[0].slice(2); };
      var data={action:'new', items:c.text, amount:vnd(c.total), pay:'Наличными при получении', delivery:ru(S.s)+', '+q.stime,
        address:'🏨 '+g('rq_h')+', номер '+g('rq_r')+' · забор '+ru(S.e)+' '+q.etime, hotel:g('rq_h'), contact:g('rq_ch')+': '+g('rq_c'),
        recipient:g('rq_g'), email:g('rq_e'), card:g('rq_n'), lang:L, source:'site', hp:g('rq_hp'), zone:'', ddate:'', arrive:''};
      return post(ZAYAVKI,data,true).then(function(r){
        if(!r||!r.ok||!r.orderId) return fail();
        if(r.orderId==='—'){ root.innerHTML='<div class="rq-ok">OK</div>'; return; }
        return post(API,Object.assign({action:'rentHold',order_key:r.orderId,hotel:g('rq_h'),room:g('rq_r'),guest:g('rq_g'),contact:g('rq_ch')+': '+g('rq_c'),email:g('rq_e'),note:g('rq_n'),lang:L},q)).catch(function(){}).then(function(){
          try{ if(window.gtag) gtag('event','conversion',{'send_to':'AW-17946655007/L0hfCM-bs40dEJ_y0O1C','value':1.0,'currency':'USD','transaction_id':String(r.orderId)}); }catch(_){}
          root.innerHTML='<div class="rq"><div class="rq-ok">✅ '+T.ok1+esc(r.orderId)+' '+T.ok2+'<br><br>👶 '+S.data.items.filter(function(x){ return q.items.indexOf(x.id)>=0; }).map(function(x){ return '№'+x.num+' '+esc(itemName(x)); }).join(', ')+'<br>'+T.deliv+': '+dm(q.sdate)+' '+q.stime+' → '+T.pick+': '+dm(q.edate)+' '+q.etime+' · '+c.days+' '+T.days+'<br><b>'+money(c.total)+'</b></div></div>';
        });
      });
    }).catch(function(){ fail(); });
  }
  load('');
})();

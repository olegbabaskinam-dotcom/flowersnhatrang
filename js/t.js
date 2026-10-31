/* Surprise Service — своя аналитика сайта (31.10.2026). Анонимно: номер посетителя без имени/телефона.
   Пишет: вход на страницу (источник, utm, язык, устройство), время на странице и глубину прокрутки,
   клики WhatsApp/Telegram/звонок/Instagram/Kakao, добавление в корзину, заявку, оплату/наличные.
   Данные → buhproxy (Cloudflare D1) → «📊 Аналитика» в бухгалтерии. Связь с Microsoft Clarity по vid. */
(function(){
  try{
    if(window.__sst) return; window.__sst=1;
    var API='https://buhproxy.olegbabaskin-am.workers.dev';
    if(/bot|crawl|spider|headless|lighthouse|preview/i.test(navigator.userAgent||'')) return;
    var LS=window.localStorage, SS=window.sessionStorage;
    function rid(){ return Date.now().toString(36)+Math.random().toString(36).slice(2,8); }
    function g(s,k){ try{ return s.getItem(k); }catch(e){ return null; } }
    function p(s,k,v){ try{ s.setItem(k,v); }catch(e){} }
    var vid=g(LS,'sst_vid'), isNew=0; if(!vid){ vid=rid(); p(LS,'sst_vid',vid); p(LS,'sst_first',new Date().toISOString().slice(0,10)); isNew=1; }
    var now=Date.now(), last=+(g(LS,'sst_last')||0), sid=g(SS,'sst_sid');
    if(!sid || now-last>30*60*1000){ sid=rid(); p(SS,'sst_sid',sid); p(SS,'sst_pn','0');
      var q=new URLSearchParams(location.search), ut={};
      ['utm_source','utm_medium','utm_campaign','utm_term','utm_content','gclid','fbclid','yclid'].forEach(function(k){ if(q.get(k)) ut[k]=q.get(k).slice(0,100); });
      p(SS,'sst_land',JSON.stringify({ref:document.referrer||'',utm:ut,land:location.pathname})); }
    p(LS,'sst_last',String(now));
    var pn=+(g(SS,'sst_pn')||0)+1; p(SS,'sst_pn',String(pn));
    var land={}; try{ land=JSON.parse(g(SS,'sst_land')||'{}'); }catch(e){}
    var lang=(document.documentElement.lang||'').slice(0,2)||'ru';
    var dev=/iPad|Tablet/i.test(navigator.userAgent)?'tablet':(/Mobi|Android|iPhone/i.test(navigator.userAgent)?'mobile':'desktop');
    var t0=Date.now(), active=0, lastVis=Date.now(), vis=!document.hidden, maxScroll=0, sentLeave=0;
    function send(ev){ ev.vid=vid; ev.sid=sid; ev.path=location.pathname; var body=JSON.stringify({action:'t',e:[ev]});
      try{ if(navigator.sendBeacon && navigator.sendBeacon(API,new Blob([body],{type:'text/plain'}))) return; }catch(e){}
      try{ fetch(API,{method:'POST',body:body,keepalive:true,headers:{'Content-Type':'text/plain'}}); }catch(e){} }
    try{ if(window.clarity){ clarity('identify',vid); clarity('set','vid',vid); } }catch(e){}
    send({t:'pv',n:isNew,pn:pn,ref:pn===1?(land.ref||''):'',utm:pn===1?(land.utm||{}):{},title:(document.title||'').slice(0,120),lang:lang,dev:dev,sw:screen.width||0});
    function scr(){ var h=document.documentElement, s=(window.scrollY+window.innerHeight)/Math.max(h.scrollHeight,1); if(s>maxScroll) maxScroll=Math.min(1,s); }
    window.addEventListener('scroll',scr,{passive:true}); scr();
    document.addEventListener('visibilitychange',function(){ if(document.hidden){ if(vis) active+=Date.now()-lastVis; vis=false; leave(); } else { vis=true; lastVis=Date.now(); sentLeave=0; } });
    window.addEventListener('pagehide',leave);
    function leave(){ if(sentLeave) return; sentLeave=1; var a=active+(vis?Date.now()-lastVis:0); active=a; lastVis=Date.now();
      send({t:'leave',dur:Math.round(a/1000),sc:Math.round(maxScroll*100)}); }
    document.addEventListener('click',function(e){ var a=e.target&&e.target.closest?e.target.closest('a'):null; if(!a) return; var h=a.getAttribute('href')||'', k='';
      if(/wa\.me|whatsapp/i.test(h)) k='whatsapp'; else if(/t\.me\/|telegram/i.test(h)) k='telegram'; else if(/^tel:/i.test(h)) k='phone';
      else if(/instagram\.com/i.test(h)) k='instagram'; else if(/kakao/i.test(h)) k='kakao'; else if(/zalo/i.test(h)) k='zalo';
      if(k) send({t:'click',k:k}); },true);
    // корзина: добавление товара (flw_cart в localStorage)
    try{ var cnt=function(v){ try{ var x=JSON.parse(v||'[]'); return Array.isArray(x)?x.length:Object.keys(x||{}).length; }catch(e){ return 0; } };
      var os=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ var before=(k==='flw_cart')?cnt(this.getItem(k)):0; os.apply(this,arguments); if(k==='flw_cart'&&cnt(v)>before) send({t:'cart'}); }; }catch(e){}
    // заявка / чек / наличные: перехват отправки формы в Apps Script
    try{ var of=window.fetch; window.fetch=function(u,o){ var pr=of.apply(this,arguments); try{ var url=String(u&&u.url||u||''), b=o&&o.body, act='';
        if(url.indexOf('script.google.com')>=0 && b){ act=(b.get?b.get('action'):((String(b).match(/action[=":]+"?(\w+)/)||[])[1]))||''; }
        if(act==='new'||act==='receipt'||act==='cash'){ var amt=b.get?(b.get('amount')||''):''; pr.then(function(r){ return r.clone().json(); }).then(function(j){ if(j&&j.ok) send({t:act==='new'?'lead':(act==='receipt'?'paid':'cash'),oid:String(j.orderId||(b.get&&b.get('orderId'))||'').slice(0,12),amt:String(amt).slice(0,40)}); }).catch(function(){}); }
      }catch(e){} return pr; }; }catch(e){}
  }catch(e){}
})();

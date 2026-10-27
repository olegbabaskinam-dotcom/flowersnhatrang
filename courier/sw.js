// Service worker Карты заказов. НИЧЕГО НЕ КЭШИРУЕМ — данные живые.
// Нужен только чтобы Android предлагал «Установить приложение» со своей иконкой.
self.addEventListener('install',  function(e){ self.skipWaiting(); });
self.addEventListener('activate', function(e){ e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch',    function(e){ /* passthrough */ });

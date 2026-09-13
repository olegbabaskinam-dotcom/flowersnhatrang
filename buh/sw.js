// Service worker бухгалтерии.
// НИЧЕГО НЕ КЭШИРУЕМ — данные живые, кэш = залипшая старая версия.
// Он нужен только чтобы Android предлагал «Установить приложение».
self.addEventListener('install',  function(e){ self.skipWaiting(); });
self.addEventListener('activate', function(e){ e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch',    function(e){ /* passthrough: браузер грузит сам */ });

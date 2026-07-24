# -*- coding: utf-8 -*-
import re, html

MAPS = "https://maps.app.goo.gl/3H4ngJ1UoLrMDkiS7?g_st=ic"

# name, color, initial, date{ru,en,ko}, text{ru,en,ko}
R = [
 ("Артем Пушкин","#EF6C00","А",
   {"ru":"2 дня назад","en":"2 days ago","ko":"2일 전"},
   {"ru":"Спасибо большое! Уровень на высоте, цветы прекрасны. Доставили всё быстро и вовремя.",
    "en":"Thank you so much! Top-level service, the flowers are beautiful. Everything was delivered fast and on time.",
    "ko":"정말 감사합니다! 서비스 수준이 최고이고 꽃도 아름다워요. 모든 것을 빠르고 제시간에 배달해 주었어요."}),
 ("ll B","#3949AB","B",
   {"ru":"5 дней назад","en":"5 days ago","ko":"5일 전"},
   {"ru":"Цветы отличные! Доставили быстро. В 9:15 написал, в 10:00 уже привезли в отель! Удобно, что можно оплатить переводом рублями.",
    "en":"Great flowers! Fast delivery. I messaged at 9:15 and by 10:00 they were already at the hotel! Handy that you can pay by transfer in rubles.",
    "ko":"꽃이 훌륭해요! 배달도 빨라요. 9시 15분에 연락했는데 10시에 벌써 호텔에 도착했어요! 루블 송금으로 결제할 수 있어서 편리해요."}),
 ("Юлия Медунова","#43A047","Ю",
   {"ru":"5 дней назад","en":"5 days ago","ko":"5일 전"},
   {"ru":"Красивые, свежие, ароматные цветы доставили в отель чётко ко времени! Большое спасибо и пожелание как можно больше благодарных клиентов!",
    "en":"Beautiful, fresh, fragrant flowers delivered to the hotel right on time! Big thanks, and I wish you as many grateful clients as possible!",
    "ko":"예쁘고 신선하고 향기로운 꽃을 호텔로 정확히 제시간에 배달해 주었어요! 정말 감사하고, 감사하는 고객이 더 많아지길 바랍니다!"}),
 ("Надежда Никифорова","#C2185B","Н",
   {"ru":"5 дней назад","en":"5 days ago","ko":"5일 전"},
   {"ru":"Невероятный букет! Мгновенное оформление заказа и быстрая доставка. Удобная оплата рублями. Спасибо!",
    "en":"An incredible bouquet! Instant order processing and fast delivery. Convenient payment in rubles. Thank you!",
    "ko":"믿을 수 없는 부케예요! 주문 처리도 즉각적이고 배달도 빨라요. 루블 결제도 편리해요. 감사합니다!"}),
 ("Semper In Motu","#6D4C41","S",
   {"ru":"6 дней назад","en":"6 days ago","ko":"6일 전"},
   {"ru":"Заказали цветы — всё понравилось, особенно пунктуальность при доставке.",
    "en":"We ordered flowers — we liked everything, especially the punctuality of the delivery.",
    "ko":"꽃을 주문했는데 모든 것이 마음에 들었어요, 특히 배달 시간을 정확히 지켜서 좋았어요."}),
 ("Александр Пономарев","#2E7D32","А",
   {"ru":"неделю назад","en":"a week ago","ko":"1주 전"},
   {"ru":"Списался, ответили мигом, всё чётко и быстро решили, цена хорошая, советую всем.",
    "en":"I got in touch, they replied instantly, sorted everything out quickly and clearly, good price — I recommend it to everyone.",
    "ko":"연락하니 즉시 답장이 왔고, 모든 것을 빠르고 명확하게 해결해 주었어요. 가격도 좋아서 모두에게 추천해요."}),
 ("lavvvrenova","#8E24AA","L",
   {"ru":"неделю назад","en":"a week ago","ko":"1주 전"},
   {"ru":"Быстро собрали, учли все пожелания, доставили до отеля ровно ко времени! Очень красивые цветы.",
    "en":"They put it together quickly, took all my wishes into account, and delivered to the hotel exactly on time! Very beautiful flowers.",
    "ko":"빠르게 준비하고 모든 요청을 반영해서 호텔까지 정확히 제시간에 배달해 주었어요! 꽃이 아주 예뻐요."}),
 ("Лина Зверева","#7E57C2","Л",
   {"ru":"4 дня назад","en":"4 days ago","ko":"4일 전"},
   {"ru":"Было бы 10 звёзд — все бы поставили! Организованно, максимально быстро, вежливо! Спасибо огромное, счастливый ребёнок получил свой сюрприз! Шары очень качественные и красивые — написала в 7:40, и уже через 1,5 часа они были у нас дома!",
    "en":"If there were 10 stars I'd give them all! Well organised, super fast and polite! Thank you so much, my happy child got the surprise. The balloons are great quality — I messaged at 7:40 and they were at our home within 1.5 hours!",
    "ko":"별 10개가 있다면 다 드리고 싶어요! 체계적이고 정말 빠르고 친절해요! 아이가 깜짝 선물을 받고 너무 좋아했어요. 풍선 퀄리티도 훌륭하고, 7시 40분에 연락했는데 1시간 반 만에 집에 도착했어요!"}),
 ("Anna D.","#26A69A","A",
   {"ru":"2 недели назад","en":"2 weeks ago","ko":"2주 전"},
   {"ru":"Доченьке сегодня 15. Написала в WhatsApp, заказала букет. К назначенному времени прислали фото букета и быстро доставили. Всё чётко, качественно, своевременно и недорого. Доченька осталась очень довольна. Рекомендую!",
    "en":"My daughter turned 15 today. I messaged on WhatsApp and ordered a bouquet. They sent a photo of it at the agreed time and delivered quickly. Everything was precise, high quality, on time and affordable. My daughter was delighted. Highly recommend!",
    "ko":"오늘 딸이 15살이 되었어요. WhatsApp으로 부케를 주문했어요. 약속한 시간에 부케 사진을 보내주고 빠르게 배달해 주었어요. 모든 것이 정확하고, 품질도 좋고, 시간도 잘 지키고 가격도 합리적이에요. 딸이 정말 좋아했어요. 강력 추천합니다!"}),
 ("Wonjin Seo","#EF5350","W",
   {"ru":"3 недели назад","en":"3 weeks ago","ko":"3주 전"},
   {"ru":"Впервые дарил цветы во Вьетнаме. Искал по разным местам и заказал у русского владельца. Цветы качественнее, чем в местных магазинах, а главное — девушке очень понравилось. В следующий день рождения снова закажу здесь!",
    "en":"My first time giving flowers in Vietnam. After looking around I ordered from this Russian owner. The flowers were better quality than local shops, and most importantly my girlfriend loved them. I'll order here again for her next birthday!",
    "ko":"베트남에서 처음 꽃을 선물해보는데 여기저기 알아보다가 러시아 사장님 가게에 주문했어요. 베트남 가게들보다 꽃이 더 퀄리티 있고, 무엇보다 여자친구가 너무 좋아하더라구요. 다음 여자친구 생일에도 이용할게요~"}),
 ("harrys kalaigidis","#5C6BC0","H",
   {"ru":"2 месяца назад","en":"2 months ago","ko":"2개월 전"},
   {"ru":"Очень профессиональный человек, всё сделал с вниманием к деталям. Держал меня в курсе на каждом шаге. Быстро и легко общаться. И очень хорошие цены.",
    "en":"Very professional guy, he did everything with detail. Informed me on every step he did. Quick and easy to communicate. Very good prices also.",
    "ko":"정말 전문적인 분이에요. 모든 것을 세심하게 처리해 주었어요. 단계마다 알려주었고, 소통이 빠르고 쉬웠어요. 가격도 아주 좋아요."}),
 ("Павел К","#EC407A","П",
   {"ru":"2 недели назад","en":"2 weeks ago","ko":"2주 전"},
   {"ru":"Отличный сервис, быстро договорились, прислали фото вариантов цветов и упаковки, привезли в назначенное время к отелю. Очень приятный и позитивный человек. Успехов и проЦВЕТания бизнесу!",
    "en":"Excellent service. We agreed quickly, they sent photos of flower and wrapping options and delivered to the hotel right on time. A very pleasant and positive person. Wishing the business success and growth!",
    "ko":"훌륭한 서비스예요. 빠르게 협의하고, 꽃과 포장 옵션 사진을 보내주고, 약속한 시간에 호텔로 배달해 주었어요. 아주 친절하고 긍정적인 분이에요. 사업 번창을 기원합니다!"}),
 ("Iskhak Dzhanov","#FF7043","I",
   {"ru":"2 месяца назад","en":"2 months ago","ko":"2개월 전"},
   {"ru":"Отличный сервис, заказал 3 букета и шарики — всё красиво упаковали, добавили открытки, цветы свежие. Бесплатная доставка в нужное место и время.",
    "en":"Great service, I ordered 3 bouquets and balloons — everything was beautifully wrapped, with cards added, and the flowers were fresh. Free delivery to the right place and time.",
    "ko":"훌륭한 서비스예요. 부케 3개와 풍선을 주문했는데 모두 예쁘게 포장하고 카드도 넣어주고 꽃도 신선했어요. 원하는 장소와 시간에 무료 배달해 주었어요."}),
 ("Юля Певлина","#AB47BC","Ю",
   {"ru":"3 месяца назад","en":"3 months ago","ko":"3개월 전"},
   {"ru":"Быстрая и чёткая доставка самых свежих цветов в Нячанге. Заказывали 51 розовую розу. Отвечают быстро: утром написали — через 40 минут прислали фото с выбором, и через 30 минут доставили в отель недалеко от Камрани.",
    "en":"Fast and precise delivery of the freshest flowers in Nha Trang. We ordered 51 pink roses. They reply quickly: we messaged in the morning, got photos to choose from within 40 minutes, and 30 minutes later it was delivered to our hotel near Cam Ranh.",
    "ko":"냐짱에서 가장 신선한 꽃을 빠르고 정확하게 배달해 줘요. 핑크 장미 51송이를 주문했어요. 답장이 빨라요 — 아침에 연락하니 40분 만에 고를 수 있는 사진을 보내주고, 30분 뒤 깜라인 근처 호텔로 배달됐어요."}),
 ("Марина Бахметьева","#D81B60","М",
   {"ru":"2 месяца назад","en":"2 months ago","ko":"2개월 전"},
   {"ru":"Спасибо большое! Букет шикарный! Жена в восторге!",
    "en":"Thank you so much! The bouquet is gorgeous! My wife is thrilled!",
    "ko":"정말 감사합니다! 부케가 너무 멋져요! 아내가 아주 좋아해요!"}),
 ("Vitas Grishov","#42A5F5","V",
   {"ru":"3 месяца назад","en":"3 months ago","ko":"3개월 전"},
   {"ru":"Спасибо большое ребятам — помогли сделать мою девочку счастливой! Доставили в номер к 6 утра. Ещё раз спасибо, вы молодцы!",
    "en":"Big thanks to the team — they helped make my girl happy! Delivered to the room by 6 a.m. Thanks again, you're amazing!",
    "ko":"팀에게 정말 감사해요 — 제 여자친구를 행복하게 해줬어요! 새벽 6시까지 객실로 배달해 주었어요. 다시 한번 감사합니다, 정말 최고예요!"}),
 ("Artem Yurin","#66BB6A","A",
   {"ru":"2 месяца назад","en":"2 months ago","ko":"2개월 전"},
   {"ru":"Лучшие. Большое спасибо!",
    "en":"The best one. Many thanks!",
    "ko":"최고예요. 정말 감사합니다!"}),
 ("Амелия Емельянова","#8D6E63","А",
   {"ru":"2 месяца назад","en":"2 months ago","ko":"2개월 전"},
   {"ru":"Заказывали два букета — красные розы и белые лилии — на день рождения мамы. Хорошо проконсультировали, много разных цветов. Цветы свежие и красивые. Очень понравилось!",
    "en":"We ordered two bouquets — red roses and white lilies — for mum's birthday. They advised us well, lots of different flowers. The flowers were fresh and beautiful. We loved it!",
    "ko":"엄마 생신을 위해 빨간 장미와 흰 백합 두 부케를 주문했어요. 상담도 잘 해주고 꽃 종류도 다양했어요. 꽃이 신선하고 예뻤어요. 정말 마음에 들었어요!"}),
 ("Андрей Рудиков","#7E57C2","А",
   {"ru":"неделю назад","en":"a week ago","ko":"1주 전"},
   {"ru":"Отличный сервис. Никак не мог найти цветочный в Нячанге — недалеко и с хорошим ассортиментом. Неожиданно нашёл доставку с хорошим описанием, фото букетов и даже гелиевыми шарами. Заказал в обед — всё супер!",
    "en":"Excellent service. I just couldn't find a flower shop in Nha Trang that was nearby with a good range. Then I found this delivery with great descriptions, bouquet photos and even helium balloons. Ordered at lunch — everything was great!",
    "ko":"훌륭한 서비스예요. 냐짱에서 가깝고 종류 많은 꽃집을 못 찾고 있었는데, 설명도 잘 되어 있고 부케 사진에 헬륨 풍선까지 있는 이 배달 서비스를 발견했어요. 점심에 주문했는데 모든 게 완벽했어요!"}),
 ("Mad Mike","#FFA726","M",
   {"ru":"3 месяца назад","en":"3 months ago","ko":"3개월 전"},
   {"ru":"Потрясающая работа! В 9 утра в отель доставили красивейший и свежий букет!",
    "en":"Amazing work! By 9 a.m. a gorgeous, fresh bouquet was delivered to the hotel!",
    "ko":"환상적이에요! 아침 9시에 가장 예쁘고 신선한 부케를 호텔로 배달해 주었어요!"}),
 ("Оксана Герасимова","#26C6DA","О",
   {"ru":"3 недели назад","en":"3 weeks ago","ko":"3주 전"},
   {"ru":"Букет красивый, розы свежие! Сервис отличный! Спасибо вам большое!",
    "en":"Beautiful bouquet, fresh roses! Excellent service! Thank you so much!",
    "ko":"부케가 예쁘고 장미가 신선해요! 서비스도 훌륭해요! 정말 감사합니다!"}),
 ("Iskander Gera","#5C6BC0","I",
   {"ru":"вчера","en":"yesterday","ko":"어제"},
   {"ru":"Всё прекрасно: букет, сервис, обратная связь. Когда пришлось немного скорректировать заказ — всё было решено. Рекомендую!",
    "en":"Everything was perfect: the bouquet, the service, the communication. When I needed to tweak the order a little, it was all sorted out. Recommend!",
    "ko":"모든 것이 완벽했어요: 부케, 서비스, 소통까지. 주문을 조금 수정해야 했을 때도 다 해결해 주었어요. 추천합니다!"}),
]

# Отзывы с фото (Google Maps). Идут ПЕРВЫМИ. Формат: name,color,ini,date{},text{},photo
IMG = [
 ("Дмитрий К","#757575","Д",
   {"ru":"вчера","en":"yesterday","ko":"어제"},
   {"ru":"Отличные цветы! Хороший сервис, быстрая доставка!",
    "en":"Great flowers! Good service, fast delivery!",
    "ko":"꽃이 훌륭해요! 서비스도 좋고 배달도 빨라요!"},
   "dmitriy"),
 ("Диана Новикова","#1565C0","Д",
   {"ru":"2 дня назад","en":"2 days ago","ko":"2일 전"},
   {"ru":"Шикарный букет!!! Молодцы!!! Огромное спасибо!!!",
    "en":"Gorgeous bouquet!!! Well done!!! Huge thanks!!!",
    "ko":"너무 멋진 부케예요!!! 최고예요!!! 정말 감사합니다!!!"},
   "diana-n"),
 ("Жанылай Акбаева","#E53935","Ж",
   {"ru":"3 дня назад","en":"3 days ago","ko":"3일 전"},
   {"ru":"Даже не думала, что есть возможность заказать цветы у русскоязычного цветочного в Нячанге! Это круто! Доставили свежие розы имениннице оперативно! Спасибо за это вам большое!",
    "en":"I never imagined I could order flowers from a Russian-speaking florist in Nha Trang! That's awesome! They delivered fresh roses to the birthday girl super fast! Thank you so much!",
    "ko":"냐짱에서 러시아어를 쓰는 꽃집에 주문할 수 있을 거라곤 생각도 못했어요! 정말 멋져요! 생일 맞은 친구에게 신선한 장미를 신속하게 배달해 주었어요! 정말 감사합니다!"},
   "zhanylai"),
 ("Виталий Олегович","#1E88E5","В",
   {"ru":"4 дня назад","en":"4 days ago","ko":"4일 전"},
   {"ru":"Заказ выполнили очень быстро, учитывая, что я поздно спохватился) Жена счастлива получить корзину цветов на юбилей)",
    "en":"They completed the order very fast, considering I remembered late) My wife was happy to get a basket of flowers for her anniversary)",
    "ko":"제가 늦게 생각났는데도 주문을 아주 빠르게 처리해 주었어요) 아내가 기념일에 꽃바구니를 받고 행복해했어요)"},
   "vitaliy"),
 ("Аламеда","#00897B","А",
   {"ru":"5 дней назад","en":"5 days ago","ko":"5일 전"},
   {"ru":"Курьер приехал во время, я осталась очень довольна цветами в корзине, 101 роза 🌹",
    "en":"The courier arrived on time, I was very happy with the flowers in the basket — 101 roses 🌹",
    "ko":"택배 기사님이 제시간에 도착했고, 바구니에 담긴 101송이 장미에 아주 만족했어요 🌹"},
   "alameda"),
 ("Марина Мерзлякова","#F4511E","М",
   {"ru":"6 дней назад","en":"6 days ago","ko":"6일 전"},
   {"ru":"Спасибо за доставку! Очень быстро с момента заказа до получения. Привезли к отелю. Розы свежие и красивые! Поздравили дочь с Днём рождения! Была приятно удивлена. Удачи вам в вашем красивом деле!",
    "en":"Thank you for the delivery! Very fast from order to receipt. Brought it to the hotel. The roses are fresh and beautiful! We wished our daughter a happy birthday! She was pleasantly surprised. Good luck with your beautiful business!",
    "ko":"배달 감사합니다! 주문부터 수령까지 아주 빨랐어요. 호텔로 가져다 주었어요. 장미가 신선하고 예뻐요! 딸 생일을 축하해 주었어요! 딸이 기분 좋게 놀랐어요. 이 멋진 사업 번창하시길 바랍니다!"},
   "marina"),
 ("Диана Сатаева","#90A4AE","Д",
   {"ru":"неделю назад","en":"a week ago","ko":"1주 전"},
   {"ru":"Очень красивые и свежие цветочки, имениннице понравилось очень😍 Быстро и оперативно оформили всё, очень рада что нашла этот цветочный магазин. Пусть расцветает бизнес🥰",
    "en":"Very beautiful and fresh flowers, the birthday girl loved them so much 😍 Everything was arranged quickly and efficiently, I'm so glad I found this flower shop. May your business blossom 🥰",
    "ko":"정말 예쁘고 신선한 꽃이에요, 생일 맞은 친구가 너무 좋아했어요 😍 모든 걸 빠르고 신속하게 준비해 주었어요. 이 꽃집을 찾아서 정말 기뻐요. 사업이 활짝 피어나길 바라요 🥰"},
   "diana-s"),
 ("Евгений Минин","#6D4C41","Е",
   {"ru":"неделю назад","en":"a week ago","ko":"1주 전"},
   {"ru":"Заказывал цветы на день рождения жене, всё очень быстро и качественно, через 2 часа цветы уже привезли на ресепшен в отель :) Жене очень понравилось",
    "en":"I ordered flowers for my wife's birthday, everything was very fast and high quality — within 2 hours the flowers were already at the hotel reception :) My wife loved them",
    "ko":"아내 생일 꽃을 주문했는데 모든 게 아주 빠르고 품질도 좋았어요. 2시간 만에 호텔 리셉션으로 배달됐어요 :) 아내가 아주 좋아했어요"},
   "evgeniy-m"),
 ("Владимир Потапов","#3949AB","В",
   {"ru":"неделю назад","en":"a week ago","ko":"1주 전"},
   {"ru":"Брал небольшой букет и шарики сердечки. Обговорили всё минут за 10. Я не мог определиться по времени доставки, тк на отдыхе график ненормированный, в итоге договорились по факту по команде. От команды до доставки около часа.",
    "en":"I got a small bouquet and heart balloons. We sorted everything out in about 10 minutes. I couldn't pin down a delivery time since my holiday schedule was unpredictable, so we agreed to do it on demand. From my go-ahead to delivery was about an hour.",
    "ko":"작은 부케와 하트 풍선을 주문했어요. 10분 만에 모든 걸 정했어요. 휴가 일정이 불규칙해서 배달 시간을 정하기 어려웠는데, 요청하는 대로 해주기로 했어요. 요청부터 배달까지 약 1시간 걸렸어요."},
   "vladimir"),
]

STAR = '★★★★★'
GLOGO = ('<svg viewBox="0 0 48 48" width="18" height="18" style="flex:0 0 auto" aria-hidden="true">'
 '<path fill="#4285F4" d="M24 9.5c3.5 0 6.6 1.2 9 3.6l6.7-6.7C35.6 2.5 30.1 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.8 6.1C12.2 13.3 17.6 9.5 24 9.5z"/>'
 '<path fill="#34A853" d="M46.1 24.6c0-1.6-.1-3.1-.4-4.6H24v9.1h12.4c-.5 2.9-2.2 5.3-4.6 7l7.1 5.5c4.2-3.9 6.6-9.6 6.6-16.4z"/>'
 '<path fill="#FBBC05" d="M10.4 28.7c-.5-1.4-.7-2.9-.7-4.7s.3-3.3.7-4.7l-7.8-6.1C1 16.3 0 20 0 24s1 7.7 2.6 10.8l7.8-6.1z"/>'
 '<path fill="#EA4335" d="M24 48c6.1 0 11.3-2 15-5.5l-7.1-5.5c-2 1.3-4.6 2.1-7.9 2.1-6.4 0-11.8-3.8-13.6-9.3l-7.8 6.1C6.5 42.6 14.6 48 24 48z"/></svg>')

L = {
 "ru":{"title":"Отзывы на Google","sub":"Настоящие отзывы наших клиентов","btn":"Смотреть все отзывы на Google","prev":"Предыдущий","next":"Следующий","of":"136 отзывов · 5,0"},
 "en":{"title":"Google reviews","sub":"Real reviews from our customers","btn":"See all reviews on Google","prev":"Previous","next":"Next","of":"136 reviews · 5.0"},
 "ko":{"title":"구글 리뷰","sub":"실제 고객들의 후기","btn":"구글에서 모든 리뷰 보기","prev":"이전","next":"다음","of":"리뷰 136개 · 5.0"},
}

def card(r, lang, base=""):
    name, color, ini, date, text = r[0], r[1], r[2], r[3], r[4]
    photo = r[5] if len(r) > 5 else None
    img = ""
    txtcls = "rv-text"
    cardcls = "rv-card"
    if photo:
        cardcls = "rv-card rv-card--img"
        txtcls = "rv-text rv-text--full"
        img = (f'\n<img class="rv-photo" src="{base}img/site/reviews/{photo}.webp" '
               f'alt="{html.escape(name)} — отзыв с фото букета, доставка цветов Нячанг" '
               f'loading="lazy" decoding="async" width="700">')
    return f'''<article class="{cardcls}">
<header class="rv-head">
<div class="rv-ava" style="background:{color}">{html.escape(ini)}</div>
<div class="rv-meta"><div class="rv-name">{html.escape(name)}</div><div class="rv-date">{html.escape(date[lang])}</div></div>
{GLOGO}
</header>
<div class="rv-stars" aria-label="5 / 5">{STAR}</div>
<p class="{txtcls}">{html.escape(text[lang])}</p>{img}
</article>'''

STYLE = '''<style>
.rv-wrap{position:relative;max-width:72rem;margin:0 auto}
.rv-top{display:flex;align-items:center;justify-content:center;gap:.5rem;margin-bottom:.25rem}
.rv-top .rv-g{font-weight:600;color:#1a1a1a}
.rv-rate{display:flex;align-items:center;justify-content:center;gap:.4rem;color:#9c9490;font-size:.82rem;margin-bottom:1.25rem}
.rv-rate .s{color:#fbbc04;letter-spacing:1px}
.rv-track{display:flex;gap:1rem;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;padding:4px 2px 14px;scrollbar-width:none}
.rv-track::-webkit-scrollbar{display:none}
.rv-card{scroll-snap-align:start;flex:0 0 300px;max-width:300px;background:#fff;border:1px solid #efeae7;border-radius:1rem;padding:1.15rem 1.2rem;display:flex;flex-direction:column;gap:.65rem;box-shadow:0 1px 3px rgba(0,0,0,.03)}
@media(min-width:640px){.rv-card{flex-basis:332px;max-width:332px}}
.rv-head{display:flex;align-items:center;gap:.65rem}
.rv-ava{width:42px;height:42px;border-radius:50%;color:#fff;font-weight:600;display:flex;align-items:center;justify-content:center;font-size:1.05rem;flex:0 0 auto}
.rv-meta{flex:1 1 auto;min-width:0}
.rv-name{font-weight:600;color:#1a1a1a;font-size:.92rem;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rv-date{color:#9c9490;font-size:.75rem;margin-top:2px}
.rv-stars{color:#fbbc04;font-size:.98rem;letter-spacing:1.5px}
.rv-text{color:#57514e;font-size:.88rem;line-height:1.55;margin:0;display:-webkit-box;-webkit-line-clamp:9;-webkit-box-orient:vertical;overflow:hidden}
.rv-text--full{display:block;-webkit-line-clamp:none;overflow:visible}
.rv-photo{width:100%;height:200px;object-fit:cover;border-radius:.7rem;margin-top:.15rem;display:block;background:#f3efec}
.rv-nav{position:absolute;top:48%;transform:translateY(-50%);width:42px;height:42px;border-radius:50%;background:#fff;border:1px solid #e7e1de;box-shadow:0 2px 8px rgba(0,0,0,.08);display:flex;align-items:center;justify-content:center;cursor:pointer;color:#80757a;z-index:5;transition:.2s}
.rv-nav:hover{color:#c0687a;border-color:#e7c3cd}
.rv-prev{left:-6px}.rv-next{right:-6px}
@media(max-width:680px){.rv-nav{display:none}}
.rv-cta{text-align:center;margin-top:.5rem}
</style>'''

def carousel_section(lang, base=""):
    t = L[lang]
    cards = "\n".join(card(r, lang, base) for r in IMG) + "\n" + "\n".join(card(r, lang) for r in R)
    return f'''<!--REVIEWS-START-->
    <section class="reveal py-10 px-4 border-b border-stone-100">
        <div class="max-w-6xl mx-auto">
            <h3 class="font-serif text-2xl font-bold text-center mb-1" style="color:#1a1a1a;">{t["title"]}</h3>
            <p class="text-center text-stone-400 text-sm mb-2">{t["sub"]}</p>
            <div class="rv-rate"><span class="s">{STAR}</span><span>{t["of"]}</span></div>
            {STYLE}
            <div class="rv-wrap">
                <button class="rv-nav rv-prev" id="rvPrev-{lang}" aria-label="{t['prev']}" type="button"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg></button>
                <div class="rv-track" id="rvTrack-{lang}">
{cards}
                </div>
                <button class="rv-nav rv-next" id="rvNext-{lang}" aria-label="{t['next']}" type="button"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg></button>
            </div>
            <div class="rv-cta">
                <a href="{MAPS}" target="_blank" rel="noopener" class="inline-flex items-center gap-2 font-medium text-xs hover:underline transition" style="color:#c0687a;">
                    {GLOGO}{t["btn"]}
                </a>
            </div>
        </div>
        <script>
        (function(){{
          var t=document.getElementById('rvTrack-{lang}');if(!t)return;
          function step(d){{var c=t.querySelector('.rv-card');if(!c)return;t.scrollBy({{left:d*(c.offsetWidth+16),behavior:'smooth'}});}}
          var p=document.getElementById('rvPrev-{lang}'),n=document.getElementById('rvNext-{lang}');
          if(p)p.addEventListener('click',function(){{step(-1)}});
          if(n)n.addEventListener('click',function(){{step(1)}});
        }})();
        </script>
    </section>'''

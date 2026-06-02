# -*- coding: utf-8 -*-
import csv, datetime, re, itertools

def slugify(s):
    tr={'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z',
        'и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r',
        'с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'c','ч':'ch','ш':'sh','щ':'sch',
        'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',' ':'-'}
    s=s.lower(); out=''.join(tr.get(c,c) for c in s)
    out=re.sub(r'[^a-z0-9\-]','',out); out=re.sub(r'\-+','-',out).strip('-')
    return out[:65]

T=[]  # (category,title,keyword,photo_query)

occasions=[("на день рождения","birthday flowers bouquet"),("на годовщину свадьбы","anniversary roses"),
 ("на 8 марта","tulips spring"),("на день матери","flowers mother"),("на свадьбу","wedding flowers"),
 ("на помолвку","engagement flowers"),("в знак извинения","apology roses"),("на выписку из роддома","newborn flowers"),
 ("на первое свидание","romantic date flowers"),("для признания в любви","red roses love"),("на юбилей","celebration bouquet"),
 ("на новоселье","housewarming flowers"),("для выздоровления","get well flowers"),("на выпускной","graduation bouquet"),
 ("на день учителя","teacher flowers"),("на 14 февраля","valentine roses"),("в честь рождения ребёнка","baby flowers"),
 ("на корпоратив","office flowers"),("деловому партнёру","elegant business flowers"),("просто так","fresh surprise flowers")]
for o,pq in occasions:
    T.append(("Повод",f"Какие цветы подарить {o} в Нячанге",f"цветы {o}",pq))
    T.append(("Повод",f"Идеи букетов {o}: гид для туриста в Нячанге",f"букет {o}",pq))

recipients=[("жене","wife"),("девушке","girlfriend"),("маме","mom"),("подруге","friend"),
 ("коллеге","colleague"),("начальнице","boss elegant"),("сестре","sister"),("бабушке","grandmother"),
 ("любимой","romantic roses"),("учительнице","teacher")]
for r,pq in recipients:
    T.append(("Получатель",f"Какие цветы выбрать {r} — гид по букетам в Нячанге",f"цветы {r}",pq))

flowers=[("Розы","розы","red roses"),("Пионы","пионы","peonies"),("Тюльпаны","тюльпаны","tulips"),
 ("Орхидеи","орхидеи","orchids"),("Лилии","лилии","lilies"),("Подсолнухи","подсолнухи","sunflowers"),
 ("Хризантемы","хризантемы","chrysanthemums"),("Герберы","герберы","gerbera"),("Гортензии","гортензии","hydrangea"),
 ("Эустома","эустома","eustoma"),("Ромашки","ромашки","daisies"),("Каллы","каллы","calla lily")]
for f,fl,pq in flowers:
    T.append(("Цветок",f"{f} в Нячанге: значение, уход и кому дарить",f"{fl} нячанг",pq))
    T.append(("Цветок",f"Сколько стоят {fl} в Нячанге и как заказать доставку",f"купить {fl} нячанг",pq))

geo=[("Доставка цветов в отели Нячанга — как это работает","доставка цветов в отель нячанг","hotel flower delivery"),
 ("Доставка цветов в Камрань: сроки и зоны","доставка цветов камрань","resort flowers delivery"),
 ("Цветы в номер отеля: сюрприз для второй половинки","цветы в номер отеля","hotel room flowers"),
 ("Романтический сюрприз в Нячанге: цветы и шары","романтический сюрприз нячанг","romantic surprise balloons"),
 ("Предложение руки на пляже Нячанга: оформление цветами","предложение на пляже нячанг","beach proposal flowers"),
 ("Цветы в аэропорт Камрань: встреча с букетом","цветы аэропорт камрань","airport welcome flowers"),
 ("Украшение номера лепестками роз в Нячанге","украшение номера лепестками роз","rose petals room"),
 ("Доставка цветов 24/7 в Нячанге: ночные заказы","доставка цветов круглосуточно нячанг","night flower delivery"),
 ("Свежие цветы в Нячанге день в день","доставка цветов день в день нячанг","same day delivery flowers"),
 ("Где купить цветы в Нячанге туристу","купить цветы нячанг турист","tourist buying flowers")]
for t,kw,pq in geo: T.append(("Гео",t,kw,pq))

guides=[("Как сохранить букет свежим в жарком климате Вьетнама","как сохранить букет свежим","flowers vase care"),
 ("Значение цвета роз: что означает каждый оттенок","значение цвета роз","colorful roses"),
 ("Язык цветов: что сказать букетом","язык цветов значение","flower language"),
 ("Сколько роз дарить: значение количества","сколько роз дарить","roses bunch"),
 ("Как заказать доставку цветов через WhatsApp","заказать цветы whatsapp","ordering flowers phone"),
 ("Оплата цветов рублями, донгами и долларами в Нячанге","оплата цветов нячанг","flowers payment cash"),
 ("Бюджетные букеты в Нячанге: красиво и недорого","недорогие цветы нячанг","budget bouquet"),
 ("Премиум-букеты в Нячанге: люксовые композиции","премиум букеты нячанг","luxury arrangement"),
 ("Цветы и воздушные шары: идеальный подарок-сюрприз","цветы и шары нячанг","flowers helium balloons"),
 ("Как выбрать букет, который не завянет в дороге","стойкий букет жара","durable flowers heat"),
 ("Топ-10 популярных букетов в Нячанге","популярные букеты нячанг","popular bouquets"),
 ("Сезонные цветы во Вьетнаме по месяцам","сезонные цветы вьетнам","seasonal flowers vietnam")]
for t,kw,pq in guides: T.append(("Гид",t,kw,pq))

culture=[("Традиции дарения цветов во Вьетнаме","традиции цветов вьетнам","vietnam flower tradition"),
 ("Какие цветы любят корейцы: гид для подарка","цветы для корейцев","korean flower gift"),
 ("Цветочный этикет для туристов в Азии","цветочный этикет азия","flower etiquette"),
 ("Какие цветы не дарят во Вьетнаме","какие цветы не дарят вьетнам","white flowers"),
 ("Корейские праздники и цветы: Соллаль, Чхусок","корейские праздники цветы","korean holiday flowers"),
 ("День 'Пепперо' и другие корейские поводы","пепперо день цветы","pepero day korea"),
 ("White Day в Корее: что подарить","white day подарок","white day gift"),
 ("Цветы на годовщину 100 дней отношений","годовщина 100 дней","couple 100 days flowers")]
for t,kw,pq in culture: T.append(("Культура",t,kw,pq))

for m in ["январе","феврале","марте","апреле","мае","июне","июле","августе","сентябре","октябре","ноябре","декабре"]:
    T.append(("Сезон",f"Какие цветы дарить в {m} в Нячанге",f"цветы в {m} нячанг","seasonal bouquet"))

# повод×цветок
co=[("день рождения","birthday"),("годовщину","anniversary"),("8 марта","spring"),("свидание","romantic"),
    ("извинение","apology"),("признание","love"),("юбилей","celebration"),("свадьбу","wedding")]
cf=[("из роз","roses"),("из пионов","peonies"),("из тюльпанов","tulips"),("из орхидей","orchids"),
    ("из лилий","lilies"),("из гербер","gerbera"),("из хризантем","chrysanthemums"),("микс","mixed bouquet")]
for (o,oe),(f,fe) in itertools.product(co,cf):
    T.append(("Комбо",f"Букет {f} на {o}: идеи и доставка в Нячанге",f"букет {f} на {o}",f"{fe} {oe} bouquet"))

# получатель×повод
rc=[("жене","wife"),("девушке","girlfriend"),("маме","mom"),("подруге","friend"),("коллеге","colleague"),("сестре","sister"),("любимой","beloved")]
oc=[("на день рождения","birthday"),("на годовщину","anniversary"),("на 8 марта","spring"),("на юбилей","celebration"),("без повода","surprise")]
for (r,re_),(o,oe) in itertools.product(rc,oc):
    T.append(("Связка",f"Что подарить {r} {o} в Нячанге: цветы и идеи",f"что подарить {r} {o}",f"{re_} {oe} flowers"))

# отели
hotels=["Muong Thanh","Sheraton","InterContinental","Novotel","Mercure","Sunrise","Havana","Diamond Bay",
 "Liberty Central","Premier Havana","Galina","Ariyana","Potique","Selectum Noa","Movenpick","Radisson Blu",
 "Alma Resort","The Anam","Fusion Resort","Duyen Ha"]
for h in hotels:
    T.append(("Отель",f"Доставка цветов в отель {h} (Нячанг / Камрань)",f"доставка цветов {h}","hotel flowers luxury"))

# цветок×получатель
fl2=[("Розы","roses"),("Пионы","peonies"),("Тюльпаны","tulips"),("Орхидеи","orchids"),("Лилии","lilies"),("Подсолнухи","sunflowers")]
rec2=[("жене","wife"),("маме","mom"),("девушке","girlfriend"),("коллеге","colleague")]
for (f,fe),(r,re_) in itertools.product(fl2,rec2):
    T.append(("Связка",f"{f} {r}: когда уместно и как заказать в Нячанге",f"{f.lower()} {r}",f"{fe} for {re_}"))

more=[("Как сделать сюрприз туристу в отеле Нячанга","сюрприз в отеле нячанг","hotel surprise"),
 ("Романтический ужин в Нячанге с цветами","романтический ужин нячанг","romantic dinner flowers"),
 ("Цветы любимым на расстоянии в Нячанге","цветы на расстоянии","long distance flowers"),
 ("Корзина цветов vs букет: что выбрать","корзина цветов или букет","flower basket"),
 ("Монобукет: стильный минимализм","монобукет нячанг","mono bouquet"),
 ("Авторские букеты ручной работы в Нячанге","авторский букет нячанг","handmade bouquet"),
 ("Цветы в шляпной коробке в Нячанге","цветы в коробке нячанг","flowers in box"),
 ("Сухоцветы и стабилизированные цветы","сухоцветы стабилизированные","dried flowers"),
 ("Свадебный букет невесты в Нячанге","свадебный букет невесты","bridal bouquet"),
 ("Цветы для фотосессии в Нячанге","цветы для фотосессии","flowers photoshoot"),
 ("Композиции для свадьбы на пляже Нячанга","свадьба на пляже цветы","beach wedding flowers"),
 ("Букет-комплимент: маленький знак внимания","букет комплимент","small bouquet"),
 ("Цветы на день влюблённых заранее","день влюблённых цветы заказ","valentine flowers"),
 ("Топ ошибок при выборе букета","ошибки выбор букета","choosing bouquet"),
 ("Как удивить корейскую девушку цветами","удивить корейскую девушку","korean girl flowers"),
 ("Цветы и сладости: комбо-подарки в Нячанге","цветы и сладости подарок","flowers chocolate"),
 ("Букет на рабочий стол: цветы в офис Нячанга","цветы в офис нячанг","office desk flowers"),
 ("Цветы на крестины и для малыша","цветы на крестины","baby christening flowers")]
for t,kw,pq in more: T.append(("Гид",t,kw,pq))

price=[("Сколько стоит букет роз в Нячанге","цена букета роз нячанг","roses price"),
 ("Доставка цветов в Нячанге: цены и тарифы","цены доставки цветов нячанг","delivery price flowers"),
 ("Дешёвые цветы в Нячанге без потери качества","дешёвые цветы нячанг","affordable flowers"),
 ("Подарок до 1000 рублей: цветы в Нячанге","подарок до 1000 рублей цветы","budget gift flowers")]
for t,kw,pq in price: T.append(("Цена",t,kw,pq))


# ШАРЫ
balloons=[("Гелиевые шары в Нячанге: доставка и оформление","гелиевые шары нячанг","helium balloons party"),
 ("Шары на день рождения в Нячанге","шары на день рождения нячанг","birthday balloons"),
 ("Фотозона из шаров для праздника","фотозона из шаров","balloon photo arch"),
 ("Шары-цифры на юбилей","шары цифры юбилей","number balloons"),
 ("Букет из шаров: альтернатива цветам","букет из шаров","balloon bouquet"),
 ("Шары с гелием в номер отеля Нячанга","шары в отель нячанг","balloons hotel room"),
 ("Сюрприз с шарами на годовщину","шары на годовщину","anniversary balloons"),
 ("Шары и цветы вместе: комбо-подарок","шары и цветы нячанг","balloons and flowers"),
 ("Шары для гендер-пати в Нячанге","шары гендер пати","gender reveal balloons"),
 ("Светящиеся шары LED в Нячанге","светящиеся шары led","led balloons night")]
for t,kw,pq in balloons: T.append(("Шары",t,kw,pq))

# УХОД за каждым цветком
care=[("Розы","розами","roses care vase"),("Пионы","пионами","peonies care"),("Тюльпаны","тюльпанами","tulips care"),
 ("Орхидеи","орхидеями","orchids care"),("Лилии","лилиями","lilies care"),("Гортензии","гортензиями","hydrangea care"),
 ("Хризантемы","хризантемами","chrysanthemums care"),("Герберы","герберами","gerbera care")]
for f,fi,pq in care:
    T.append(("Уход",f"Как ухаживать за {fi} в жару Нячанга",f"уход за {fi}",pq))

# ЗНАЧЕНИЕ ЧИСЛА РОЗ
for n in ["1","3","5","7","9","11","15","21","25","51","101"]:
    T.append(("Гид",f"Что означает букет из {n} роз",f"{n} роз значение","red roses bunch"))

# КОРЕЙСКИЕ темы (для KO-охвата)
kor=[("Какие цветы подарить корейцу на день рождения","цветы корейцу день рождения","korean birthday flowers"),
 ("Цветы для корейской свадьбы: традиции","корейская свадьба цветы","korean wedding flowers"),
 ("Coming of Age Day: цветы для корейцев","coming of age day цветы","korean coming of age roses"),
 ("Чхусок: подарки и цветы","чхусок цветы подарок","chuseok korean holiday"),
 ("Соллаль (корейский новый год) и цветы","соллаль цветы","seollal korean new year"),
 ("Цветы для корейских туристов в Нячанге","цветы корейские туристы нячанг","korean tourists flowers"),
 ("Как заказать цветы через KakaoTalk","заказать цветы kakaotalk","ordering flowers app"),
 ("Розы на 100/200/300 дней отношений по-корейски","розы 100 дней корея","couple anniversary roses")]
for t,kw,pq in kor: T.append(("Культура",t,kw,pq))

# ДОП ПОВОД×ЦВЕТОК добивка (новые цветы)
co2=[("день рождения","birthday"),("годовщину","anniversary"),("свидание","romantic"),("юбилей","celebration")]
cf2=[("из подсолнухов","sunflowers"),("из гортензий","hydrangea"),("из эустомы","eustoma"),
     ("из ромашек","daisies"),("из калл","calla lily"),("из гербер","gerbera")]
import itertools as _it
for (o,oe),(f,fe) in _it.product(co2,cf2):
    T.append(("Комбо",f"Букет {f} на {o}: идеи и доставка в Нячанге",f"букет {f} на {o}",f"{fe} {oe}"))

# ДОП ГИДЫ
mg=[("Как выбрать цветы по знаку зодиака","цветы по знаку зодиака","zodiac flowers"),
 ("Цветы по цвету: как собрать гармоничный букет","цветы по цвету букет","color palette bouquet"),
 ("Что подарить вместо цветов в Нячанге","альтернатива цветам подарок","gift alternative flowers"),
 ("Открытка к букету: что написать","что написать в открытке","gift card note flowers"),
 ("Доставка цветов анонимно в Нячанге","анонимная доставка цветов","secret flowers delivery"),
 ("Подписка на цветы: букет каждую неделю","подписка на цветы","flower subscription weekly"),
 ("Цветы на работу любимому в Нячанге","цветы мужчине нячанг","flowers for him men"),
 ("Можно ли дарить цветы в горшке","цветы в горшке подарок","potted plant gift"),
 ("Самые стойкие цветы для жаркого климата","стойкие цветы жара","heat resistant flowers"),
 ("Свежесть букета: как проверить при получении","свежесть букета проверить","fresh flowers check")]

for t,kw,pq in mg: T.append(("Гид",t,kw,pq))


final=[("Цветы на Новый год в Нячанге","цветы на новый год нячанг","new year flowers"),
 ("Цветы на Рождество для туристов","цветы на рождество","christmas flowers"),
 ("Букет на день святого Валентина для неё","валентинка букет для неё","valentine bouquet her"),
 ("Букет на день святого Валентина для него","валентинка букет для него","valentine flowers him"),
 ("Цветы на Международный женский день в офис","цветы 8 марта офис","womens day office flowers"),
 ("Цветы маме на день рождения: топ идей","цветы маме день рождения","mom birthday flowers"),
 ("Свадебная арка из живых цветов в Нячанге","свадебная арка цветы","wedding flower arch"),
 ("Бутоньерка жениху и гостям","бутоньерка жениху","groom boutonniere"),
 ("Лепестки роз для брачной ночи","лепестки роз брачная ночь","rose petals romance"),
 ("Цветы на выписку: мальчик или девочка","цветы на выписку малыша","newborn welcome flowers"),
 ("Большой букет 101 роза в Нячанге","101 роза нячанг","101 roses big bouquet"),
 ("Маленький милый букетик в подарок","маленький букет подарок","small cute bouquet"),
 ("Цветы и торт: двойной сюрприз в Нячанге","цветы и торт нячанг","flowers and cake"),
 ("Доставка цветов на виллу в Нячанге","доставка цветов на виллу","villa flowers delivery"),
 ("Цветы для годовщины 1 год (бумажная свадьба)","годовщина 1 год цветы","first anniversary flowers"),
 ("Цветы на серебряную свадьбу 25 лет","серебряная свадьба цветы","silver anniversary flowers"),
 ("Букет преподавателю на защиту диплома","букет на защиту диплома","graduation defense flowers"),
 ("Цветы для бизнес-открытия в Нячанге","цветы на открытие бизнеса","grand opening flowers"),
 ("Траурные цветы и венки в Нячанге","траурные цветы нячанг","funeral flowers wreath"),
 ("Цветы для извинения перед девушкой","цветы извинение девушке","apology flowers girlfriend"),
 ("Сезон пионов в Нячанге: когда заказывать","сезон пионов нячанг","peonies season"),
 ("Экзотические тропические цветы Вьетнама","тропические цветы вьетнам","tropical flowers exotic")]
for t,kw,pq in final: T.append(("Повод",t,kw,pq))

# дедуп
seen=set(); U=[]
for t in T:
    if t[1] not in seen: seen.add(t[1]); U.append(t)
print("Уникальных тем сгенерировано:",len(U))
U=U[:365]
print("Записываем:",len(U))

start=datetime.date(2026,6,3)
with open("registry.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh)
    w.writerow(["id","date","type","category","keyword_ru","title_ru","slug","photo_query_en","status_ru","status_en","status_ko"])
    for i,t in enumerate(U,1):
        d=start+datetime.timedelta(days=i-1)
        cat,title,kw,pq=t
        w.writerow([i,d.isoformat(),"article",cat,kw,title,slugify(title),pq,"todo","todo","todo"])
print("registry.csv готов")
# статистика по категориям
from collections import Counter
print(dict(Counter(t[0] for t in U)))

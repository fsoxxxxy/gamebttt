"""
Scenario Manager - Handles game scenarios and situations
"""

import random
from typing import List

class ScenarioManager:
    """Manages game scenarios and situations"""
    
    def __init__(self):
        self.scenarios = [
            self._scenario_walk_after_high,
            self._scenario_police_trap,
            self._scenario_missing_stash,
            self._scenario_bad_batch,
            self._scenario_security_cameras,
            self._scenario_balcony_whisper,
            self._scenario_suspicious_meeting,
            self._scenario_missing_delivery,
            self._scenario_informant_leak,
            self._scenario_territory_dispute
        ]
    
    def get_random_scenario(self) -> str:
        """Get a random scenario"""
        scenario_func = random.choice(self.scenarios)
        return scenario_func()
    
    def _scenario_walk_after_high(self) -> str:
        """Scenario 1: Walk after getting high"""
        return (
            "🌙 Ситуация: Прогулка после кайфа\n\n"
            "Вечер прошел прекрасно, вся компания осталась довольна, на столе была куча кайфов. "
            "Мы пошли на прогулку, провожали друг друга по очереди. Вернулся назад я сам — а товар пропал.\n\n"
            "❓ Кто по-твоему был крысой?"
        )
    
    def _scenario_police_trap(self) -> str:
        """Scenario 2: Police trap"""
        return (
            "🚔 Ситуация: Засада ментов\n\n"
            "Я созвонился с братками и договорился встретиться с каждым с разницей в полчаса. "
            "Никто не знал, кто придет первым. На месте уже ждали копы.\n\n"
            "❓ Кто слил инфу? Кто крыса?"
        )
    
    def _scenario_missing_stash(self) -> str:
        """Scenario 3: Missing stash"""
        return (
            "📦 Ситуация: Пропажа с кладом\n\n"
            "Мы решили сделать общий клад. Все сложили туда по чуть-чуть, даже самые осторожные участвовали. "
            "Через пару часов клад исчез, и следы вели в никуда. Только один из нас знал точку.\n\n"
            "❓ Кто украл общак?"
        )
    
    def _scenario_bad_batch(self) -> str:
        """Scenario 4: Bad batch test"""
        return (
            "💊 Ситуация: Плохая закладка\n\n"
            "Новый барыга предложил тестовую партию. Один из вас должен был проверить. "
            "Проверил — и улетел, как Прометей. Утром его нашли на балконе у соседа с хлебом в зубах. "
            "Товар не вернулся.\n\n"
            "❓ Кто тестер? Кто не вернул товар?"
        )
    
    def _scenario_security_cameras(self) -> str:
        """Scenario 5: Security cameras"""
        return (
            "📹 Ситуация: Камеры наблюдения\n\n"
            "На районе установили камеры. Один из вас накосячил, и теперь на видосе мы все в кадре. "
            "Но только у одного из вас был маршрут через этот двор.\n\n"
            "❓ Кто попал в объектив и засветил всех?"
        )
    
    def _scenario_balcony_whisper(self) -> str:
        """Scenario 6: Balcony whisper"""
        return (
            "🌃 Ситуация: Шептун с балкона\n\n"
            "В 3 ночи был слышен шёпот с балкона. Утром — минус товар. "
            "Кто из вас любит ночами вести философские беседы с фольгой и пепельницей?\n\n"
            "❓ Кто ночной философ и вор?"
        )
    
    def _scenario_suspicious_meeting(self) -> str:
        """Scenario 7: Suspicious meeting"""
        return (
            "🤝 Ситуация: Подозрительная встреча\n\n"
            "Вчера кто-то из наших встречался с незнакомцем возле старого завода. "
            "Сегодня половина товара исчезла, а в кармане у кого-то нашлись лишние деньги.\n\n"
            "❓ Кто торговал втихаря?"
        )
    
    def _scenario_missing_delivery(self) -> str:
        """Scenario 8: Missing delivery"""
        return (
            "🚗 Ситуация: Пропавшая доставка\n\n"
            "Курьер должен был привезти партию к 6 вечера. Но кто-то из вас "
            "перехватил его по дороге и забрал товар себе. Курьер найден, товара нет.\n\n"
            "❓ Кто перехватил доставку?"
        )
    
    def _scenario_informant_leak(self) -> str:
        """Scenario 9: Informant leak"""
        return (
            "📞 Ситуация: Слив информатора\n\n"
            "Наш человек в отделе предупредил о рейде, но кто-то из вас "
            "не послушался и остался на точке. Теперь мент знает всех в лицо.\n\n"
            "❓ Кто не слушает советы и подставил всех?"
        )
    
    def _scenario_territory_dispute(self) -> str:
        """Scenario 10: Territory dispute"""
        return (
            "🏠 Ситуация: Территориальный спор\n\n"
            "Чужие начали торговать на нашей территории. Но они знали "
            "где и когда мы работаем. Кто-то из наших дал им информацию.\n\n"
            "❓ Кто сдал наши точки конкурентам?"
        )

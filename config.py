"""
Configuration settings for the game
"""

# Game configuration
GAME_CONFIG = {
    "min_players": 3,
    "max_players": 10,
    "registration_time": 120,  # 2 minutes in seconds
    "discussion_time": 120,    # 2 minutes in seconds
    "voting_time": 120,        # 2 minutes in seconds
    "enable_taunts": True,     # Enable character taunts during game
    "taunt_frequency": 30,     # Seconds between taunts
}

# Character roles
ROLES = [
    "Хитрый Барыга",
    "Ебальник Пояльник", 
    "Чайка Виноватая",
    "Джин Солёной Лампы",
    "ПросящийХапку",
    "Охотник за Бледным",
    "Бакопор Внезапный",
    "Собака, Съевшая Товар"
]

# Bot messages
BOT_MESSAGES = {
    "game_started": (
        "🎮 Начинаем новую игру! Нужны торчки! Жми /join чтобы вступить.\n"
        "⏰ Осталось времени: {time_left}\n"
        "👥 Игроков: {player_count}"
    ),
    "player_joined": "✅ {username} присоединился к игре! Игроков: {player_count}",
    "registration_ending": "⏰ Регистрация заканчивается через {time_left}! Игроков: {player_count}",
    "game_starting": "✅ Игра начинается! Роли выданы.",
    "discussion_started": "💬 Обсуждение началось! У вас 2 минуты.",
    "voting_started": "🗳️ Голосование! Кто по-твоему крыса? У тебя 2 минуты.",
    "player_eliminated": "🔪 Большинство решило — закопать @{username}.",
    "rat_found": "🎯 Крыса была угадана! Молодцы.",
    "rat_not_found": "🐀 Это была не крыса... Крыса среди нас.",
    "rat_wins": "🏆 Крыса победила! Слишком мало игроков осталось.",
}

# Character taunts for entertainment during game
CHARACTER_TAUNTS = {
    "Хитрый Барыга": [
        "Эй Барыга, не забудь проверить карманы - там твоя честность осталась!",
        "Барыга, товар не продашь, если сам весь употребишь!",
        "Хитрый говоришь? А выглядишь как пойманный с поличным!"
    ],
    "Ебальник Пояльник": [
        "Ебальник, может хватит трепаться и дело делать пора?",
        "Пояльник, язык твой работает быстрее мозга!",
        "Эй болтун, слова на ветер не бросай - могут вернуться бумерангом!"
    ],
    "Чайка Виноватая": [
        "Чайка, ты и правда виноватая или просто так называешься?",
        "Виноватая Чайка всегда найдет, в чем покаяться!",
        "Чайка, не кружи над головой - садись и отвечай!"
    ],
    "Джин Солёной Лампы": [
        "Алладин, не пора ли тебе лампу протирать?",
        "Джин, три желания есть, а четвертое - не попасться!",
        "Солёная лампа? А что, сладкую уже обыскали?"
    ],
    "ПросящийХапку": [
        "Эй, Просящий, может сам заработаешь на хапку?",
        "Хапку просишь? А совесть дома не забыл?",
        "Всегда просишь, а когда давать будешь?"
    ],
    "Охотник за Бледным": [
        "Охотник, на себя в зеркало смотрел? Сам бледный как мел!",
        "За бледным охотишься? Так ты его уже поймал - в зеркале!",
        "Охотник говоришь? А выглядишь как добыча!"
    ],
    "Бакопор Внезапный": [
        "Бакопор, твоя внезапность предсказуема как рассвет!",
        "Внезапный? Да ты как телеграмма - всегда с опозданием!",
        "Бакопор, порхаешь как бабочка, а жалишь как комар!"
    ],
    "Собака, Съевшая Товар": [
        "Эй Собака, за пятку шмали дашь лапу?",
        "Собака, товар съела или просто так лаешь?",
        "Хороший мальчик! А теперь отрыгни товар обратно!"
    ]
}

# Admin user IDs (hidden cheats)
ADMIN_USERS = []  # Add admin user IDs here

# Admin cheat commands (hidden)
ADMIN_CHEATS = {
    "reveal_rat": True,      # Show who is the rat
    "skip_phases": True,     # Skip time limits
    "force_end": True,       # Force end game
    "god_mode": True,        # Immunity from voting
}

# Error messages
ERROR_MESSAGES = {
    "no_game": "❌ Нет активной игры в этом чате",
    "game_exists": "❌ Игра уже идет в этом чате!",
    "registration_ended": "❌ Регистрация уже закончилась!",
    "already_joined": "❌ Вы уже в игре!",
    "game_full": "❌ Максимум {max_players} игроков!",
    "not_enough_players": "❌ Недостаточно игроков для начала игры! Нужно минимум {min_players}",
    "not_voting_phase": "❌ Сейчас не время для голосования",
    "cannot_vote": "❌ Вы не можете голосовать",
    "invalid_target": "❌ Неверная цель для голосования",
}

#!/usr/bin/env python3
"""
Telegram bot for "Who's the Rat?" social deduction game
Main bot entry point with command handlers
"""

import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from game_manager import GameManager
from config import BOT_MESSAGES, GAME_CONFIG, ADMIN_USERS, CHARACTER_TAUNTS

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize game manager
game_manager = GameManager()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🎮 Добро пожаловать в игру 'Кто Крыса?'\n\n"
        "Команды:\n"
        "/startgame - начать новую игру\n"
        "/join - присоединиться к игре\n"
        "/status - показать статус игры\n"
        "/roles - описание ролей\n"
        "/help - показать эту справку"
    )

async def startgame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /startgame command"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username or f"user_{user_id}"
    
    try:
        success, message = await game_manager.start_game(chat_id, user_id, username, context)
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        await update.message.reply_text("❌ Ошибка при создании игры. Попробуйте позже.")

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /join command"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username or f"user_{user_id}"
    
    try:
        success, message = game_manager.join_game(chat_id, user_id, username)
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error joining game: {e}")
        await update.message.reply_text("❌ Ошибка при присоединении к игре.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    chat_id = update.effective_chat.id
    
    try:
        status_message = game_manager.get_game_status(chat_id)
        await update.message.reply_text(status_message)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        await update.message.reply_text("❌ Ошибка при получении статуса игры.")

async def roles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /roles command"""
    roles_text = (
        "🎭 Роли персонажей:\n\n"
        "• Хитрый Барыга\n"
        "• Ебальник Пояльник\n"
        "• Чайка Виноватая\n"
        "• Джин Солёной Лампы\n"
        "• ПросящийХапку\n"
        "• Охотник за Бледным\n"
        "• Бакопор Внезапный\n"
        "• Собака, Съевшая Товар\n\n"
        "Один из игроков тайно назначается Крысой 🐀"
    )
    await update.message.reply_text(roles_text)

async def vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voting callback queries"""
    query = update.callback_query
    chat_id = query.message.chat_id
    voter_id = query.from_user.id
    
    try:
        data = query.data.split('_')
        if len(data) != 2 or data[0] != 'vote':
            await query.answer("❌ Неверный формат голоса")
            return
            
        target_id = int(data[1])
        success, message = await game_manager.cast_vote(chat_id, voter_id, target_id, context)
        
        await query.answer(message)
        
        # Check if voting is complete
        if success:
            game = game_manager.get_game(chat_id)
            if game and game.phase == "voting" and game.all_votes_cast():
                await game_manager.process_votes(chat_id, context)
                
    except Exception as e:
        logger.error(f"Error processing vote: {e}")
        await query.answer("❌ Ошибка при голосовании")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🎮 Игра 'Кто Крыса?' - социальная игра на выживание\n\n"
        "📋 Как играть:\n"
        "1. Создайте игру командой /startgame\n"
        "2. Игроки присоединяются командой /join\n"
        "3. Через 2 минуты начинается игра\n"
        "4. Читайте ситуацию и обсуждайте\n"
        "5. Голосуйте за подозрительного\n"
        "6. Выясните, кто крыса!\n\n"
        "🎯 Цель: Обычные игроки должны найти крысу, крыса должна остаться незамеченной\n\n"
        "⚡ Команды:\n"
        "/startgame - начать игру\n"
        "/join - присоединиться\n"
        "/status - статус игры\n"
        "/roles - список ролей\n"
        "/settings - настройки игры\n"
        "/closeregistration - закрыть регистрацию вручную"
    )
    await update.message.reply_text(help_text)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if chat_id not in game_manager.games:
        await update.message.reply_text("❌ Нет активной игры для настройки")
        return
        
    game = game_manager.games[chat_id]
    if game.creator_id != user_id:
        await update.message.reply_text("❌ Только создатель игры может менять настройки")
        return
        
    if game.phase != "registration":
        await update.message.reply_text("❌ Настройки можно менять только во время регистрации")
        return
    
    # Show current settings with inline keyboard
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton(f"⏰ Время регистрации: {GAME_CONFIG['registration_time']}с", callback_data="set_reg_time")],
        [InlineKeyboardButton(f"👥 Мин. игроков: {GAME_CONFIG['min_players']}", callback_data="set_min_players")],
        [InlineKeyboardButton(f"👥 Макс. игроков: {GAME_CONFIG['max_players']}", callback_data="set_max_players")],
        [InlineKeyboardButton(f"🎭 Подколы: {'Вкл' if GAME_CONFIG['enable_taunts'] else 'Выкл'}", callback_data="toggle_taunts")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ Настройки игры:",
        reply_markup=reply_markup
    )

async def close_registration_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /closeregistration command"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if chat_id not in game_manager.games:
        await update.message.reply_text("❌ Нет активной игры")
        return
        
    game = game_manager.games[chat_id]
    if game.creator_id != user_id:
        await update.message.reply_text("❌ Только создатель игры может закрыть регистрацию")
        return
        
    if game.phase != "registration":
        await update.message.reply_text("❌ Регистрация уже закончена")
        return
        
    if len(game.players) < GAME_CONFIG["min_players"]:
        await update.message.reply_text(f"❌ Недостаточно игроков! Нужно минимум {GAME_CONFIG['min_players']}")
        return
    
    await update.message.reply_text("✅ Регистрация закрыта досрочно! Игра начинается...")
    await game_manager._start_game_phase(chat_id, context)

# Admin cheat commands (hidden)
async def admin_reveal_rat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin cheat: reveal the rat"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_USERS:
        return
        
    chat_id = update.effective_chat.id
    if chat_id not in game_manager.games:
        await update.message.reply_text("❌ Нет активной игры")
        return
        
    game = game_manager.games[chat_id]
    rat_player = game.get_rat_player()
    if rat_player:
        await update.message.reply_text(f"🐀 Крыса: @{rat_player.username}")
    else:
        await update.message.reply_text("❌ Крыса не назначена")

async def admin_skip_phase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin cheat: skip current phase"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_USERS:
        return
        
    chat_id = update.effective_chat.id
    if chat_id not in game_manager.games:
        await update.message.reply_text("❌ Нет активной игры")
        return
        
    game = game_manager.games[chat_id]
    if game.phase == "discussion":
        await game_manager._start_voting_phase(chat_id, context)
        await update.message.reply_text("⏭️ Фаза пропущена")
    elif game.phase == "voting":
        await game_manager.process_votes(chat_id, context)
        await update.message.reply_text("⏭️ Голосование завершено")

async def admin_end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin cheat: force end game"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_USERS:
        return
        
    chat_id = update.effective_chat.id
    if chat_id not in game_manager.games:
        await update.message.reply_text("❌ Нет активной игры")
        return
        
    game = game_manager.games[chat_id]
    game.end_game()
    await update.message.reply_text("🛑 Игра принудительно завершена админом")

def main():
    """Main function to run the bot"""
    # Get bot token from environment variable
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("startgame", startgame_command))
    application.add_handler(CommandHandler("join", join_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("roles", roles_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("closeregistration", close_registration_command))
    
    # Admin cheat commands (hidden)
    application.add_handler(CommandHandler("adminrat", admin_reveal_rat))
    application.add_handler(CommandHandler("adminskip", admin_skip_phase))
    application.add_handler(CommandHandler("adminend", admin_end_game))
    
    # Add callback query handler for voting
    application.add_handler(CallbackQueryHandler(vote_callback))
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

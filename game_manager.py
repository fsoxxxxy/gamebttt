"""
Game Manager - Handles multiple game instances and their lifecycle
"""

import asyncio
import logging
import random
from typing import Dict, Tuple, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from game_state import GameState
from scenarios import ScenarioManager
from config import GAME_CONFIG, BOT_MESSAGES, CHARACTER_TAUNTS

logger = logging.getLogger(__name__)

class GameManager:
    """Manages multiple game instances across different chats"""
    
    def __init__(self):
        self.games: Dict[int, GameState] = {}
        self.scenario_manager = ScenarioManager()
        self.taunt_tasks: Dict[int, asyncio.Task] = {}  # Track taunt tasks for each game
    
    async def start_game(self, chat_id: int, creator_id: int, creator_username: str, context: ContextTypes.DEFAULT_TYPE) -> Tuple[bool, str]:
        """Start a new game in the specified chat"""
        if chat_id in self.games:
            game = self.games[chat_id]
            if game.phase != "ended":
                return False, "❌ Игра уже идет в этом чате! Используйте /status для информации."
        
        # Create new game instance
        self.games[chat_id] = GameState(chat_id, creator_id, creator_username)
        
        # Schedule registration timer
        asyncio.create_task(self._registration_timer(chat_id, context))
        
        return True, BOT_MESSAGES["game_started"].format(
            time_left="2:00",
            player_count=1
        )
    
    def join_game(self, chat_id: int, user_id: int, username: str) -> Tuple[bool, str]:
        """Add a player to the game"""
        if chat_id not in self.games:
            return False, "❌ Нет активной игры в этом чате. Создайте игру командой /startgame"
        
        game = self.games[chat_id]
        
        if game.phase != "registration":
            return False, "❌ Регистрация уже закончилась!"
        
        if user_id in game.players:
            return False, "❌ Вы уже в игре!"
        
        if len(game.players) >= GAME_CONFIG["max_players"]:
            return False, f"❌ Максимум {GAME_CONFIG['max_players']} игроков!"
        
        success = game.add_player(user_id, username)
        if success:
            return True, f"✅ @{username} присоединился к игре! Игроков: {len(game.players)}"
        else:
            return False, "❌ Ошибка при добавлении игрока"
    
    def get_game_status(self, chat_id: int) -> str:
        """Get current game status"""
        if chat_id not in self.games:
            return "❌ Нет активной игры в этом чате"
        
        game = self.games[chat_id]
        
        if game.phase == "registration":
            return f"📝 Регистрация игроков ({len(game.players)}/{GAME_CONFIG['max_players']})\n" + \
                   f"Игроки: {', '.join([f'@{p.username}' for p in game.players.values()])}"
        
        elif game.phase == "discussion":
            return f"💬 Фаза обсуждения\n" + \
                   f"Игроков: {len([p for p in game.players.values() if p.alive])}\n" + \
                   f"Сценарий активен"
        
        elif game.phase == "voting":
            votes_cast = len(game.votes)
            total_players = len([p for p in game.players.values() if p.alive])
            return f"🗳️ Голосование ({votes_cast}/{total_players})\n" + \
                   f"Проголосовали: {votes_cast} из {total_players}"
        
        elif game.phase == "ended":
            return "🏁 Игра завершена"
        
        else:
            return "❓ Неизвестное состояние игры"
    
    def get_game(self, chat_id: int) -> Optional[GameState]:
        """Get game instance for chat"""
        return self.games.get(chat_id)
    
    async def cast_vote(self, chat_id: int, voter_id: int, target_id: int, context: ContextTypes.DEFAULT_TYPE) -> Tuple[bool, str]:
        """Cast a vote for elimination"""
        if chat_id not in self.games:
            return False, "❌ Нет активной игры"
        
        game = self.games[chat_id]
        
        if game.phase != "voting":
            return False, "❌ Сейчас не время для голосования"
        
        if voter_id not in game.players or not game.players[voter_id].alive:
            return False, "❌ Вы не можете голосовать"
        
        if target_id not in game.players or not game.players[target_id].alive:
            return False, "❌ Неверная цель для голосования"
        
        # Cast the vote
        game.votes[voter_id] = target_id
        target_username = game.players[target_id].username
        
        return True, f"✅ Вы проголосовали против @{target_username}"
    
    async def process_votes(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Process voting results and determine elimination"""
        if chat_id not in self.games:
            return
        
        game = self.games[chat_id]
        
        # Count votes
        vote_counts = {}
        for target_id in game.votes.values():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1
        
        # Find player with most votes
        if not vote_counts:
            await context.bot.send_message(
                chat_id,
                "❌ Никто не проголосовал! Игра завершается."
            )
            game.end_game()
            return
        
        eliminated_id = max(vote_counts.keys(), key=lambda x: vote_counts[x])
        eliminated_player = game.players[eliminated_id]
        
        # Eliminate player
        eliminated_player.alive = False
        
        # Check if eliminated player was the rat
        result_message = f"🔪 Большинство решило — закопать @{eliminated_player.username}.\n\n"
        
        if eliminated_player.is_rat:
            result_message += "🎯 Крыса была угадана! Молодцы, торчки победили!"
            game.end_game()
            self.stop_taunts(chat_id)
        else:
            result_message += "🐀 Это была не крыса... Крыса среди нас.\n"
            
            # Check if only rat remains
            alive_players = [p for p in game.players.values() if p.alive]
            if len(alive_players) <= 2:  # Only rat and one other player
                result_message += "\n🏆 Крыса победила! Слишком мало игроков осталось."
                game.end_game()
                self.stop_taunts(chat_id)
            else:
                result_message += f"\nОсталось игроков: {len(alive_players)}"
                # Start new round
                asyncio.create_task(self._start_discussion_phase(chat_id, context))
        
        await context.bot.send_message(chat_id, result_message)
    
    async def _registration_timer(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Handle registration phase timer"""
        registration_time = GAME_CONFIG["registration_time"]
        
        # Send periodic updates
        for remaining in [90, 60, 30]:
            await asyncio.sleep(registration_time - remaining)
            if chat_id not in self.games or self.games[chat_id].phase != "registration":
                return
            
            game = self.games[chat_id]
            minutes = remaining // 60
            seconds = remaining % 60
            time_str = f"{minutes}:{seconds:02d}" if minutes > 0 else f"{seconds}"
            
            await context.bot.send_message(
                chat_id,
                f"⏰ Регистрация заканчивается через {time_str}! Игроков: {len(game.players)}"
            )
        
        # Wait for remaining time
        await asyncio.sleep(30)
        
        if chat_id not in self.games or self.games[chat_id].phase != "registration":
            return
        
        game = self.games[chat_id]
        
        if len(game.players) < GAME_CONFIG["min_players"]:
            await context.bot.send_message(
                chat_id,
                f"❌ Недостаточно игроков для начала игры! Нужно минимум {GAME_CONFIG['min_players']}"
            )
            del self.games[chat_id]
            return
        
        # Start the game
        await self._start_game_phase(chat_id, context)
    
    async def _start_game_phase(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Start the main game phase"""
        game = self.games[chat_id]
        
        # Assign roles
        game.assign_roles()
        
        # Notify players of their roles
        for player in game.players.values():
            try:
                if player.is_rat:
                    await context.bot.send_message(
                        player.user_id,
                        "🤫 Ты крыса. Будь осторожен и не попадись!"
                    )
                else:
                    await context.bot.send_message(
                        player.user_id,
                        f"👤 Твоя роль: {player.role}\nТы не крыса. Найди настоящую крысу!"
                    )
            except Exception as e:
                logger.error(f"Could not send role message to user {player.user_id}: {e}")
        
        await context.bot.send_message(chat_id, "✅ Игра начинается! Роли выданы.")
        
        # Start discussion phase
        await self._start_discussion_phase(chat_id, context)
        
        # Start character taunts if enabled
        if GAME_CONFIG["enable_taunts"]:
            self.taunt_tasks[chat_id] = asyncio.create_task(self._taunt_loop(chat_id, context))
    
    async def _start_discussion_phase(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Start discussion phase with scenario"""
        game = self.games[chat_id]
        game.start_discussion()
        
        # Get random scenario
        scenario = self.scenario_manager.get_random_scenario()
        player_names = [p.role for p in game.players.values() if p.alive]
        scenario_text = scenario.format(player_names)
        
        message = f"🎭 {scenario_text}\n\n💬 Обсуждение началось! У вас 2 минуты."
        await context.bot.send_message(chat_id, message)
        
        # Start discussion timer
        asyncio.create_task(self._discussion_timer(chat_id, context))
    
    async def _discussion_timer(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Handle discussion phase timer"""
        await asyncio.sleep(GAME_CONFIG["discussion_time"])
        
        if chat_id not in self.games or self.games[chat_id].phase != "discussion":
            return
        
        # Start voting phase
        await self._start_voting_phase(chat_id, context)
    
    async def _start_voting_phase(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Start voting phase"""
        game = self.games[chat_id]
        game.start_voting()
        
        # Create voting keyboard
        alive_players = [p for p in game.players.values() if p.alive]
        keyboard = []
        
        for player in alive_players:
            keyboard.append([InlineKeyboardButton(
                f"🗳️ @{player.username}",
                callback_data=f"vote_{player.user_id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id,
            "🗳️ Голосование началось! Кто по-твоему крыса? У вас 2 минуты.",
            reply_markup=reply_markup
        )
        
        # Start voting timer
        asyncio.create_task(self._voting_timer(chat_id, context))
    
    async def _voting_timer(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Handle voting phase timer"""
        await asyncio.sleep(GAME_CONFIG["voting_time"])
        
        if chat_id not in self.games or self.games[chat_id].phase != "voting":
            return
        
        # Process votes even if not everyone voted
        await self.process_votes(chat_id, context)
    
    async def _taunt_loop(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Send random character taunts during the game"""
        try:
            while chat_id in self.games and self.games[chat_id].phase in ["discussion", "voting"]:
                await asyncio.sleep(GAME_CONFIG["taunt_frequency"])
                
                if chat_id not in self.games or self.games[chat_id].phase not in ["discussion", "voting"]:
                    break
                
                game = self.games[chat_id]
                alive_players = [p for p in game.players.values() if p.alive]
                
                if alive_players:
                    # Pick random player and their character
                    target_player = random.choice(alive_players)
                    character_name = target_player.role
                    
                    if character_name in CHARACTER_TAUNTS:
                        taunt = random.choice(CHARACTER_TAUNTS[character_name])
                        taunt_message = f"🎭 {taunt}"
                        
                        await context.bot.send_message(chat_id, taunt_message)
                        
        except Exception as e:
            logger.error(f"Error in taunt loop: {e}")
        finally:
            # Clean up task reference
            if chat_id in self.taunt_tasks:
                del self.taunt_tasks[chat_id]
    
    def stop_taunts(self, chat_id: int):
        """Stop character taunts for a game"""
        if chat_id in self.taunt_tasks:
            self.taunt_tasks[chat_id].cancel()
            del self.taunt_tasks[chat_id]

import discord
from discord import app_commands
from discord.ext import commands
import os
import random

# Game imports
import game
import player

intents = discord.Intents.default()
intents.message_content = True

# The bot
bot = commands.Bot(command_prefix="/", intents=intents)

# The cricket game
the_game: game.Game = None


# Callbacks
@bot.event
async def on_ready():
  print(f"{bot.user} is ready.")
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)


@bot.event
async def on_message(message):
  pass


@bot.event
async def on_reaction_add(reaction, user):
  global the_game
  try:
    if the_game:
      # When response to a challenge is given by the user who was challenged (player2)
      if reaction.message == the_game.challenge_response_message and the_game.challenge_accepted == False and user.id == the_game.player2.id:

        # Player2 accepts the challenge
        if reaction.emoji == '✅':
          the_game.challenge_accepted = True
          await the_game.toss_start()

        # Player2 rejects the challenge
        elif reaction.emoji == '❌':
          the_game.challenge_accepted = False
          the_game = None  # Garbage collected the object

        await the_game.edit_challenge_response_message()

      # Toss response by either user
      if the_game.challenge_accepted == True and the_game.toss == None and reaction.message == the_game.toss_message and (
          user.id == the_game.player1.id or user.id == the_game.player2.id):
        # Set the toss pick for both players
        toss_responder = None
        if user.id == the_game.player1.id:
          toss_responder = the_game.player1
          the_game.player1.toss_pick = reaction.emoji
          the_game.player2.toss_pick = 0 if game.TOSS_CHOICES.index(
            reaction.emoji) == 1 else 1
        else:
          toss_responder = the_game.player2
          the_game.player2.toss_pick = reaction.emoji
          the_game.player1.toss_pick = 0 if game.TOSS_CHOICES.index(
            reaction.emoji) == 1 else 1

        await the_game.edit_toss_message(toss_responder=toss_responder)
        the_game.toss = random.choice(game.TOSS_CHOICES)
        await the_game.toss_result()
        await the_game.start_game()
  except AttributeError as e:
    print(e)


# App commands
@bot.tree.command(name="challenge",
                  description="Challenges the user for cricket game")
@app_commands.describe(user="User to challenge")
async def challenge(interaction: discord.Interaction, user: discord.User):
  global the_game

  if the_game:
    await interaction.response.send_message(
      content="**Error:** There's already a challenge waiting for response.",
      ephemeral=True)
  else:
    # Players
    player1 = await player.Player(user=interaction.user)
    player2 = await player.Player(user=user)

    # Initialize Game between these 2 players
    the_game = await game.Game(interaction=interaction,
                               player1=player1,
                               player2=player2)

    await the_game.send_challenge_response()


@bot.tree.command(name="p", description="Plays the turn")
@app_commands.describe(option="Options to choose")
async def p(interaction: discord.Interaction, option: str):

  player = the_game.player1 if interaction.user.id == the_game.player1.id else (
    the_game.player2 if interaction.user.id == the_game.player2.id else None)

  if the_game and the_game.game_started and player:
    if len(option) != 2 or option[0] not in game.SPEEDS or option[
        1] not in game.POSITIONS:
      await interaction.response.send_message(
        content="**Error:** Incorrect option. Usage: `/p a1`, `/p s8`, `/p b4`",
        ephemeral=True)

    if (the_game.turn == "Baller"
        and player == the_game.batsman) or (the_game.turn == "Batsman"
                                            and player == the_game.baller):
      await interaction.response.send_message(
        content="**Error:** Wait for your turn.", ephemeral=True)
    else:
      await the_game.continue_game(played_by=player, option=option)
      await interaction.response.send_message(
        content=
        f"**Game**: You successfully played your turn. \n> **Your speed:** {option[0]}\n> **Your position:** {option[1]}",
        ephemeral=True)

  else:
    await interaction.response.send_message(
      content="**Error:** You are not in the game.", ephemeral=True)


# Start the bot
bot.run(os.getenv('token'))

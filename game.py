import discord
from async_class import AsyncClass
import random

import player

# Constants
TOSS_CHOICES = ('🥎', '🏏')
SPEEDS = ['s', 'a', 'b', 'c', 'd']
POSITIONS = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
TURN_STATUSES = ["NIL", "RUN", "FOUR", "SIX", "OUT"]


class Game(AsyncClass):

  # Message references
  challenge_response_message: discord.Message = None
  toss_message: discord.Message = None
  toss_result_message: discord.Message = None
  game_message: discord.Message = None
  turn_message: discord.Message = None

  async def __ainit__(self, interaction: discord.Interaction,
                      player1: player.Player, player2: player.Player):
    self.interaction = interaction
    self.player1 = player1
    self.player2 = player2
    # Game
    self.overs = 1
    self.curr_round = 0
    self.curr_over = 0
    self.curr_ball = 0
    self.turn = "Baller"
    self.target = None
    self.winner = None
    # Flags and results
    self.challenge_accepted = False
    self.game_started = False
    self.toss = None
    self.batsman = None
    self.baller = None

  async def send_challenge_response(self):
    await self.interaction.response.send_message(
      f"**Challenge:** {self.player1.mention} challenges {self.player2.mention} for a cricket game."
    )
    # Stores challenge interaction response message and add reactions to the message
    self.challenge_response_message = await self.interaction.original_response(
    )
    await self.challenge_response_message.add_reaction('✅')
    await self.challenge_response_message.add_reaction('❌')

  async def edit_challenge_response_message(self):
    if self.challenge_accepted:
      await self.challenge_response_message.edit(
        content=
        f"{self.challenge_response_message.content}\n\n*- {self.player2.display_name} accepted the challenge.*"
      )
    else:
      await self.challenge_response_message.edit(
        content=
        f"{self.challenge_response_message.content}\n\n*- {self.player2.display_name} rejected the challenge.*"
      )

  async def toss_start(self):
    self.toss_message = await self.interaction.channel.send(
      content="**Toss:** Heads or Tails?\n\n> 🥎 - for heads.\n> 🏏 - for Tails."
    )
    await self.toss_message.add_reaction('🥎')
    await self.toss_message.add_reaction('🏏')

  async def edit_toss_message(self, toss_responder: player.Player):
    await self.toss_message.edit(
      content=
      f"{self.toss_message.content}\n\n*- {toss_responder.display_name} selected {toss_responder.toss_pick}.*"
    )

  # Toss Result
  async def toss_result(self):

    if self.player1.toss_pick == self.toss:
      self.player1.toss_winner = True
      self.player1.batsman = True
      self.player2.baller = True
      self.batsman = self.player1
      self.baller = self.player2
    else:
      self.player2.toss_winner = True
      self.player2.batsman = True
      self.player1.baller = True
      self.batsman = self.player2
      self.baller = self.player1

    self.toss_result_message = await self.interaction.channel.send(
      content=
      f"**Toss Result:** {self.toss} and the winner is {self.batsman.display_name}\n\n- *Batsman is {self.batsman.display_name} \n- Baller is {self.baller.display_name}*"
    )

  async def start_game(self):
    self.game_started = True
    self.curr_round += 1
    self.game_message = await self.interaction.channel.send(
      content=
      f"**Game Started:** Overs and Balls {self.curr_over}.{self.curr_ball}({self.overs})\n\n**Please choose the following options:**\n> **Speed:** {' '.join(SPEEDS)}\n> **Position:** {' '.join(POSITIONS)}\n> **Example:** `/p a1`, `/p s8`\n\n{self.turn} {''.join([self.baller.mention if self.turn == 'Baller' else self.batsman.mention])}'s turn"
    )

  async def continue_game(self, played_by, option):
    if self.turn_message:
      await self.turn_message.delete()
    self.turn_message = await self.interaction.channel.send(
      content=f"**Game:** {played_by.display_name} played their turn.")

    played_by.curr_option = option

    await self.switch_turn()

    curr_turn_status = 'NIL'
    if self.turn == "Baller":
      curr_turn_status = await self.find_result()
      self.curr_ball += 1
    if self.curr_ball > 5:
      self.curr_over += 1
      self.curr_ball = 0

    if curr_turn_status == "RUN":
      runs = self.batsman.runs[-1]
      await self.interaction.channel.send(
        content=
        f"**Game:** Nice, {self.batsman.mention} made {runs} run{'s' if runs < 1 or runs > 1 else ''}."
      )
    elif curr_turn_status == "FOUR":
      await self.interaction.channel.send(
        content=f"**Game:** Great, {self.batsman.mention} made a 4.")
    elif curr_turn_status == "SIX":
      await self.interaction.channel.send(
        content=f"**Game:** Awesome, {self.batsman.mention} made a 6.")
    elif curr_turn_status == "OUT":
      await self.interaction.channel.send(
        content=
        f"**Game:** Amazing, clean bold by {self.baller.mention}.\n\n{self.batsman.mention} go home bro.",
        file=discord.File('./images/empire_out.png'))
      self.curr_round += 1
    if self.curr_over == self.overs:
      await self.interaction.channel.send(content="**Game:** All over.")
      self.curr_round += 1

    if self.curr_round == 2:
      await self.end_round()
    elif self.curr_round == 3:
      await self.finish_game()
      return

    if self.game_message:
      await self.game_message.delete()
    self.game_message = await self.interaction.channel.send(
      content=
      f"**Game:** Balls n Overs: {self.curr_over}.{self.curr_ball}({self.overs}), Score: {self.batsman.score}{', TARGET: ' + str(self.target) if self.target else ''}\n\n**Please choose the following options:**\n> **Speed:** {' '.join(SPEEDS)}\n> **Position:** {' '.join(POSITIONS)}\n> **Example:** `/p a1`, `/p s8`\n\n{self.turn} {''.join([self.baller.mention if self.turn == 'Baller' else self.batsman.mention])}'s turn"
    )

  async def switch_turn(self):
    if self.turn == "Baller":
      self.turn = "Batsman"
    else:
      self.turn = "Baller"

  async def end_round(self):
    self.target = self.batsman.score + 1

    # Switch batting and balling
    if self.batsman == self.player1:
      self.baller = self.player1
      self.batsman = self.player2

      self.player1.batsman = False
      self.player1.baller = True
      self.player2.batsman = True
      self.player2.baller = False
    else:
      self.batsman = self.player1
      self.baller = self.player2

      self.player1.batsman = True
      self.player1.baller = False
      self.player2.batsman = False
      self.player2.baller = True

    await self.reset_game()

    await self.interaction.channel.send(
      content=
      f"**Game:** \n\n- *Batsman is {self.batsman.display_name} \n- Baller is {self.baller.display_name}*"
    )

  async def find_result(self):
    status = "NIL"

    if self.batsman.curr_option == self.baller.curr_option:
      status = "OUT"
      return status

    # Score System Logic will be implemented here
    status = "RUN"
    await self.batsman.make_runs(random.choice([0, 1, 2, 3]))
    return status

  async def find_winner(self):
    self.winner = self.player1 if self.player1.score > self.player2.score else (
      self.player2 if self.player2.score > self.player1.score else None)

  async def reset_game(self):
    self.overs = 1
    self.curr_over = 0
    self.curr_ball = 0
    self.turn = "Baller"

  async def finish_game(self):
    await self.find_winner()
    await self.interaction.channel.send(
      content=
      f"**Game:** Game finished. {self.player1.mention}'s score is {self.player1.score} and {self.player2.mention}'s score is {self.player2.score}\n\n{''.join(['And the **winner** is ' + self.winner.mention if self.winner else 'Its a **draw**'])}"
    )

  # End the game
  async def end(self):
    await self.__adel__()

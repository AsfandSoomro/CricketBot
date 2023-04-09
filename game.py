import discord
from async_class import AsyncClass

import player

# Constants
TOSS_CHOICES = ('🥎', '🏏')
SPEEDS = ['s', 'a', 'b', 'c', 'd']
POSITIONS = ['1', '2', '3', '4', '5', '6', '7', '8', '9']


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
    self.curr_over = 0
    self.curr_ball = 0
    self.turn = "Baller"
    self.curr_turn_result = None
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
    print(self.turn)
    if self.turn == "Baller":
      self.curr_turn_result = await self.find_result()
      self.curr_ball += 1
    if self.curr_ball > 5:
      self.curr_over += 1
      self.curr_ball = 0

    if self.curr_over == self.overs:
      await self.interaction.channel.send(content="**Game:** All over.")

    if self.game_message:
      await self.game_message.delete()
    self.game_message = await self.interaction.channel.send(
      content=
      f"**Game:** Overs and Balls {self.curr_over}.{self.curr_ball}({self.overs})\n\n**Please choose the following options:**\n> **Speed:** {' '.join(SPEEDS)}\n> **Position:** {' '.join(POSITIONS)}\n> **Example:** `/p a1`, `/p s8`\n\n{self.turn} {''.join([self.baller.mention if self.turn == 'Baller' else self.batsman.mention])}'s turn"
    )

  async def switch_turn(self):
    if self.turn == "Baller":
      self.turn = "Batsman"
    else:
      self.turn = "Baller"

  async def find_result(self):
    result = {
      "Score": 0,
      "Status" "NILL"
    }
    
    if self.batsman.curr_option == self.baller.curr_option:
      result["Status"] = "OUT"
      return result
    
    result["Score"] = 2
    result["STATUS"] = RUN
    return result

  # End the game
  async def end(self):
    await self.__adel__()

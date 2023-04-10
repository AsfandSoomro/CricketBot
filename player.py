import discord
from async_class import AsyncClass


class Player(AsyncClass):

  async def __ainit__(self, user: discord.User):
    # User attributes
    self.id = user.id
    self.name = user.name
    self.display_name = user.display_name
    self.display_avatar = user.display_avatar
    self.mention = user.mention
    # Player Attributes
    self.toss_pick = None
    self.toss_winner = False
    self.batsman = False
    self.baller = False
    self.curr_option = None
    self.runs = []
    self.fours = 0
    self.sixes = 0
    self.score = 0

  async def make_runs(self, runs):
    self.runs.append(runs)
    await self.update_score()

  async def make_four(self):
    self.fours += 1
    await self.update_score()

  async def make_six(self):
    self.sixes += 1
    await self.update_score()

  async def update_score(self):
    self.score = sum(self.runs) + (self.fours * 4) + (self.sixes * 6)

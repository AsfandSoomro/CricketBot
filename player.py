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
    self.score = 0

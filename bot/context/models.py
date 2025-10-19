from discord import Guild
from discord.channel import TextChannel as Channel


class ServerContext():
    server: Guild
    logs: Channel
    debug: Channel
    zigzagoon: Channel
    bot_chat: Channel
    def __init__(self,
            server: Guild,
            logs: Channel,
            debug: Channel,
            zigzagoon: Channel,
            bot_chat: Channel
            ) -> None:
        self.server = server
        self.logs = logs
        self.debug = debug
        self.zigzagoon = zigzagoon
        self.bot_chat = bot_chat


class GlobalContext():
    doodledoo: ServerContext
    pif: ServerContext
    def __init__(self,
                 doodledoo: ServerContext,
                 pif: ServerContext
                 ) -> None:
        self.doodledoo = doodledoo
        self.pif = pif

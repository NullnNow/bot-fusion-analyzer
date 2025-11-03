from discord import Client, Guild, TextChannel

from .models import ServerContext, GlobalContext

# Doodledoo test server
id_server_doodledoo          = 446241769462562827
id_channel_gallery_doodledoo = 1360964111718158498
id_channel_assets_doodledoo  = 1363610399064330480
id_channel_logs_doodledoo    = 1360969318296322328
id_channel_debug_doodledoo   = 1360964178927554680

bot_environment = "local"

# Pokémon Infinite Fusion
if bot_environment == "local":
    id_server_pif           = id_server_doodledoo
    id_channel_gallery_pif  = id_channel_gallery_doodledoo
    id_channel_assets_pif   = id_channel_assets_doodledoo
    id_channel_logs_pif     = id_channel_logs_doodledoo
    id_channel_debug_pif    = id_channel_debug_doodledoo
    id_spriter_apps_pif     = 1365804567127916655
    id_channel_zigzagoon    = id_channel_debug_doodledoo
    id_spritework           = 1374857028509503538
    id_bot_chat             = id_channel_logs_doodledoo
elif bot_environment == "pif":
    id_server_pif           = 302153478556352513
    id_channel_gallery_pif  = 543958354377179176
    id_channel_assets_pif   = 1094790320891371640
    id_channel_logs_pif     = 999653562202214450
    id_channel_debug_pif    = 703351286019653762
    id_spriter_apps_pif     = 1134483288703119361
    id_channel_zigzagoon    = 1234176742957121607
    id_spritework           = 1050404143807873157
    id_bot_chat             = 700790080175996938
else:
    id_server_pif           = 756264475102937199
    id_channel_gallery_pif  = 1185991301645209610
    id_channel_assets_pif   = 1226648126375596145
    id_channel_logs_pif     = 1367184071389614091
    id_channel_debug_pif    = 1367184071389614091
    id_spriter_apps_pif     = 1193291636457865266 # sprite-errors
    id_channel_zigzagoon    = 1332162874931413104 # zigzag-chatter
    id_spritework           = 1185685268133593118
    id_bot_chat             = 1367184071389614091


class BotContext:
    def __init__(self, client: Client):
        server_doodledoo        = get_server_from_id(client, id_server_doodledoo)
        channel_log_doodledoo   = get_channel_from_id(server_doodledoo, id_channel_logs_doodledoo)
        channel_debug_doodledoo = get_channel_from_id(server_doodledoo, id_channel_debug_doodledoo)

        doodledoo_context = ServerContext(
            server    = server_doodledoo,
            sprite    = channel_log_doodledoo,
            assets    = channel_log_doodledoo,
            logs      = channel_log_doodledoo,
            debug     = channel_debug_doodledoo,
            zigzagoon = channel_log_doodledoo,
            bot_chat  = channel_log_doodledoo
        )

        server_pif        = get_server_from_id(client, id_server_pif)
        sprite_gallery    = get_channel_from_id(server_pif, id_channel_gallery_pif)
        assets_gallery    = get_channel_from_id(server_pif, id_channel_assets_pif)
        channel_log_pif   = get_channel_from_id(server_pif, id_channel_logs_pif)
        channel_debug_pif = get_channel_from_id(server_pif, id_channel_debug_pif)
        channel_zigzagoon = get_channel_from_id(server_pif, id_channel_zigzagoon)
        channel_bot_chat  = get_channel_from_id(server_pif, id_bot_chat)

        pif_context = ServerContext(
            server    = server_pif,
            sprite    = sprite_gallery,
            assets    = assets_gallery,
            logs      = channel_log_pif,
            debug     = channel_debug_pif,
            zigzagoon = channel_zigzagoon,
            bot_chat  = channel_bot_chat
        )

        self.context = GlobalContext(
            doodledoo=doodledoo_context,
            pif=pif_context
        )


def get_channel_from_id(server: Guild, channel_id) -> TextChannel:
    channel = server.get_channel(channel_id)
    if channel is None:
        raise KeyError(channel_id)
    if not isinstance(channel, TextChannel):
        raise TypeError(channel)
    return channel


def get_server_from_id(client: Client, server_id) -> Guild:
    server = client.get_guild(server_id)
    if server is None:
        raise KeyError(server_id)
    return server

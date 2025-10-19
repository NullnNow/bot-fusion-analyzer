import json
import os

import discord
from discord import Member, ButtonStyle, Interaction, User, Message, HTTPException, Forbidden, NotFound
from discord.ui import View, Button

from bot.misc.utils import fancy_print

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OPT_OUT_FILE = os.path.join(CURRENT_DIR, "..", "..", "data", "OptedOutUsers.json")


class HideAutoAnalysis(View):
    message: Message

    def __init__(self, caller: Member|User):
        self.original_caller = caller
        super().__init__(timeout=600)   # After 10 mins it won't show the remove/opt out buttons anymore

    @discord.ui.button(label="Hide core", style=ButtonStyle.secondary)
    async def hide_auto_analysis(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.message.delete()
            self.stop()
        else:
            await different_user_response(interaction, self.original_caller)

    @discord.ui.button(label="Opt out", style=ButtonStyle.secondary)
    async def auto_analysis_opt_out(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.message.edit(view=None)
            opt_out_view = OptOutConfirmation(self.original_caller)
            await interaction.response.send_message(
                content="Do you want to permanently opt out of automatic Fusion Bot core on new spritework posts?",
                view=opt_out_view,delete_after=60
            )
        else:
            await different_user_response(interaction, self.original_caller)

    async def on_timeout(self) -> None:
        if not self.message:
            return
        if not self.message.embeds:
            return
        try:
            await self.message.edit(view=None)
        except (HTTPException, Forbidden, NotFound, TypeError) as error:
            error_log = f"Exception {error} while trying to timeout auto core"
            if self.message.thread:
                error_log = error_log + f" in {self.message.thread.name}"
            elif self.message.channel:
                error_log = error_log + f" in {self.message.channel.name}"
            print(error_log)
        self.stop()



class OptOutConfirmation(View):

    def __init__(self, caller: Member|User):
        self.original_caller = caller
        super().__init__()

    @discord.ui.button(label="Confirm opt out", style=ButtonStyle.danger)
    async def opt_user_out(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            await add_to_opt_out_list(interaction.user)
            fancy_print("Opt Out >",interaction.user.name,interaction.channel.name,"")
            await interaction.response.edit_message(content="Opted out successfully.", view=None, delete_after=20)
        else:
            await different_user_response(interaction, self.original_caller)

    @discord.ui.button(label="Cancel (keep automatic core)", style=ButtonStyle.secondary)
    async def cancel_opt_out(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.original_caller.id:
            await interaction.message.delete()
        else:
            await different_user_response(interaction, self.original_caller)



# View-related functions

async def different_user_response(interaction: Interaction, og_user: Member):
    response_text = f"Hi {interaction.user.mention}! That's meant for {og_user.name}."
    await interaction.response.send_message(content=response_text, ephemeral=True, delete_after=60)


async def is_opted_out_user(user: Member|User) -> bool:
    user_list = await grab_user_list()
    return user.id in user_list


async def add_to_opt_out_list(user: Member|User):
    user_list = await grab_user_list()
    user_list.append(user.id)
    with open(OPT_OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_list, f)


async def grab_user_list() -> list:
    with open(OPT_OUT_FILE, 'r', encoding='utf-8') as f:
        user_list = json.load(f)
        if not isinstance(user_list, list):
            return []
        return user_list

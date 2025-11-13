import os
from typing import Any

import discord
from discord import (Member, User, Thread, TextChannel, DMChannel, SelectOption,
                     File, Message, HTTPException, Forbidden, NotFound)
from discord.ui import View, Button, Select, Item
from discord import ButtonStyle, Interaction

from bot.context.setup import ctx
from bot.misc.utils import fancy_print
from .tutorial_sections import sections

SPRITER_ROLE_ID = 392803830900850688
APPLICANT_ID    = 1136806607469150380
MANAGER_ROLE_ID = 900867033175040101
WATCHOG_ROLE_ID = 1100903960476385350
MOD_ROLE_ID     = 306953740651462656
UNOWN_ROLE_ID   = 1210701164426039366
NO_GALPOST_ID   = 1191178850713993236
NO_HARVEST_ID   = 1191179006578532372
NON_TUTORIAL_ROLES = [SPRITER_ROLE_ID, MANAGER_ROLE_ID, WATCHOG_ROLE_ID, MOD_ROLE_ID,
                      UNOWN_ROLE_ID, NO_GALPOST_ID, NO_HARVEST_ID, APPLICANT_ID]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_PATH = os.path.join(CURRENT_DIR, "..", "..", "resources")
FINISH_TUTORIAL = "Thanks for using Tutorial Mode!\nIf you'd like to use it again, use the /help command."
TUTORIAL_LOG_DECORATOR = "TutMode >"


def user_is_potential_spriter(user: User|Member) -> bool:
    if not isinstance(user, Member):
        return False
    for role in user.roles:
        if role.id in NON_TUTORIAL_ROLES:
            return False
    return True


async def send_tutorial_mode_prompt(user: Member, channel: TextChannel|Thread|DMChannel):
    prompt_text = (f"**Hi {user.display_name}!** If you're unsure what some of that means (for instance, "
                   f"similarity is probably not what you think!), press the **Tutorial Mode** button below.\n"
                   f"Also, make sure that if you edit your sprite, post updates in this same thread, don't "
                   f"create a new one please! Even if the analysis says 'controversial' or 'invalid', you can "
                   f"just edit it to make it valid.")
    prompt_view = PromptButtonsView(user)
    view_message = await channel.send(content=prompt_text, view=prompt_view)
    prompt_view.message = view_message


# Views

class PromptButtonsView(View):
    message: Message

    def __init__(self, caller: Member):
        self.original_caller = caller
        super().__init__(timeout=3600)   # Prompt gets disabled after an hour

    @discord.ui.button(label="Tutorial Mode", style=ButtonStyle.primary, emoji="✏")
    async def engage_tutorial_mode(self, interaction: Interaction, _button: Button):
        if interaction.user.id == self.original_caller.id:
            fancy_print(TUTORIAL_LOG_DECORATOR, interaction.user.name, interaction.channel.name,
                        "Tutorial Mode engaged")
            tutorial_mode = TutorialMode(self.original_caller)
            await interaction.response.edit_message(
                content="**Tutorial Mode**\nSelect a tutorial section from the dropdown below.",
                view=tutorial_mode)
            tutorial_mode.message = await interaction.original_response()
            self.stop()
        else:
            await different_user_response(interaction, self.original_caller)

    @discord.ui.button(label="Discard", style=ButtonStyle.secondary)
    async def discard_tutorial_prompt(self, interaction: Interaction, _button: Button):
        if interaction.user.id == self.original_caller.id:
            self.stop()
            await interaction.message.delete()
        else:
            await different_user_response(interaction, self.original_caller)

    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any], /) -> None:
        await view_error(interaction, error)

    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
        og_message = self.message
        if og_message:
            try:
                extra_msg = "\nButtons disabled. If you still want to use Tutorial Mode, you can do so with /help"
                await og_message.edit(content=og_message.content + extra_msg, view=self)
            except (HTTPException, Forbidden, NotFound, TypeError) as error:
                error_log = f"Exception {error} while trying to timeout Tutorial prompt"
                if self.message.thread:
                    error_log = error_log + f" in {self.message.thread.name}"
                elif self.message.channel:
                    error_log = error_log + f" in {self.message.channel.name}"
                print(error_log)
        self.stop()


class TutorialMode(View):
    message: Message

    def __init__(self, caller: Member):
        self.original_caller = caller
        super().__init__(timeout=36000)  # Tutorial auto-finishes after 10 hours
        self.add_item(TutorialSelect(self.original_caller))

    @discord.ui.button(label="Exit Tutorial Mode", style=ButtonStyle.secondary)
    async def exit_tutorial_mode(self, interaction: Interaction, _button: Button):
        if interaction.user.id == self.original_caller.id:
            fancy_print(TUTORIAL_LOG_DECORATOR, interaction.user.name,
                        interaction.channel.name, "Tutorial Mode finished")
            await interaction.response.edit_message(content=FINISH_TUTORIAL, view=None, attachments=[])
            self.stop()
        else:
            await different_user_response(interaction, self.original_caller)

    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any], /) -> None:
        await view_error(interaction, error)

    async def on_timeout(self) -> None:
        if self.message:
            try:
                await self.message.edit(content=FINISH_TUTORIAL, view=None, attachments=[])
            except (HTTPException, Forbidden, NotFound, TypeError) as error:
                error_log = f"Exception {error} while trying to timeout Tutorial Mode"
                if self.message.thread:
                    error_log = error_log +  f" in {self.message.thread.name}"
                elif self.message.channel:
                    error_log = error_log +  f" in {self.message.channel.name}"
                print(error_log)

        self.stop()


class TutorialSelect(Select):
    def __init__(self, caller: Member):
        self.original_caller = caller
        options = []
        for section_name in sections:
            section = sections[section_name]
            option = SelectOption(label=section.title, description=section.description, value=section_name)
            options.append(option)
        super().__init__(placeholder="Choose a tutorial section", options=options)

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.original_caller.id:
            await different_user_response(interaction, self.original_caller)
            return

        section = sections[self.values[0]]
        if not section:
            print(f"ERROR: No section found for element: {self.values[0]}")
        fancy_print(TUTORIAL_LOG_DECORATOR, interaction.user.name, interaction.channel.name,
                    f"Section: {section.title}")
        full_section = f"**Tutorial Mode: {section.title}**\n\n{section.content}"
        attachments = []
        section_image = section.image
        if section_image:
            attachment_file = File(os.path.join(IMAGES_PATH, section_image))
            attachments.append(attachment_file)
        await interaction.response.edit_message(content=full_section, attachments=attachments)



# View-related functions

async def different_user_response(interaction: Interaction, og_user: Member):
    response_text = (f"Hi {interaction.user.mention}! That's meant for {og_user.name}, but if you want to use "
                     f"the Tutorial Mode yourself, you can use /help in a channel such as "
                     f"<#1031005766359982190> to do so.")
    await interaction.response.send_message(content=response_text, ephemeral=True, delete_after=60)

async def view_error(interaction: Interaction, error: Exception):
    await ctx().doodledoo.debug.send(f"VIEW ERROR in {interaction.channel} ({interaction.channel.jump_url})\n")
    raise RuntimeError from error



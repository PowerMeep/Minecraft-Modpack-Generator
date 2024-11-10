import logging
import os

from models.modpack import generate

import disnake
from disnake.ext import commands
from disnake import SelectOption, ButtonStyle, Embed
from disnake.ui import StringSelect, ActionRow, Button

logger = logging.getLogger()
intents = disnake.Intents.default()
intents.members = True
client = commands.InteractionBot(intents=intents)

id_member_select = 'member-select'
id_do_generate = 'build-modpack'
id_send_it = 'send-it'

btn_generate = Button(
    style=ButtonStyle.green,
    label='Generate',
    custom_id=id_do_generate
)
btn_regenerate = Button(
    style=ButtonStyle.green,
    label='Regenerate',
    custom_id=id_do_generate
)
btn_send_it = Button(
    style=ButtonStyle.blurple,
    label='Send It',
    custom_id=id_send_it
)
btn_report = Button(
    style=ButtonStyle.url,
    label='Report Issue',
    url='https://github.com/PowerMeep/Minecraft-Modpack-Generator/issues'
)



def add_author(embed, author):
    avatar_url = author.avatar.url if author.avatar else None
    embed.set_author(
        name=author.display_name,
        icon_url=avatar_url
    )


class BuilderState:
    def __init__(self,
                 author: disnake.User):
        self.author = author
        self.members_by_id = {}
        self.selected_members_by_name = {}
        self.modpack = None
        self.message: disnake.Message = None

    def to_embed(self):
        desc = [
            f'# {self.modpack.get_name()}',
            self.modpack.challenge.description
        ]
        if self.modpack.scenario:
            desc.append(f'\n_{self.modpack.scenario.description}_')
        desc.append(f'\n**Duration:** {self.modpack.challenge.duration}')
        if len(self.selected_members_by_name) > 0:
            desc.append('### Players')
            for player in self.selected_members_by_name.values():
                desc.append(f'- <@{player.id}>')

        desc.append(f'### Mods ({self.modpack.version})')
        for mod in self.modpack.sources_by_mod.keys():
            desc.append(f'- [{mod.curseforge_meta.display_name}]({mod.curseforge_meta.website_url})')

        if len(self.modpack.meta_by_sidequest) > 0:
            desc.append('### Sidequests')

        embed = Embed(
            description='\n'.join(desc)
        )

        add_author(embed, self.author)

        for sq, meta in self.modpack.meta_by_sidequest.items():
            desc = sq.description
            if not sq.per_player and meta:
                desc = f'{desc}\nTarget: **{meta}**'
            embed.add_field(
                name=sq.name,
                value=desc
            )
        return embed


states_by_user = {}


@client.slash_command(
    description='Generate a Minecraft Modpack'
)
async def build_modpack(inter):
    await inter.response.defer(
        with_message=True,
        ephemeral=True
    )

    state: BuilderState
    if state := states_by_user.get(inter.author.id):
        try:
            await state.message.delete()
        except:
            # We don't really care if this was successful or not
            pass
    state = BuilderState(inter.author)
    states_by_user[inter.author.id] = state

    try:
        await show_player_prompt(inter, state)
    except:
        # If we couldn't get the player list and show the prompt, just skip right to generating.
        await regenerate(inter, state)


@client.listen('on_button_click')
async def on_button_click(inter: disnake.MessageInteraction):
    await inter.response.defer(
        with_message=True,
        ephemeral=True
    )

    state = states_by_user.get(inter.author.id)
    if state is None:
        await inter.response.send_message(
            content='There was an error processing this request. Please try again.',
            ephemeral=True
        )
        return

    if inter.component.custom_id == id_do_generate:
        await regenerate(inter, state)
        return
    elif inter.component.custom_id == id_send_it:
        await send(inter, state)
        return

    await inter.response.send_message(
        content='oops'
    )


@client.listen('on_dropdown')
async def on_dropdown(inter: disnake.MessageInteraction):
    await inter.response.defer(
        with_message=True,
        ephemeral=True
    )

    state: BuilderState = states_by_user.get(inter.author.id)
    if state is None:
        await inter.response.send_message(
            content='There was an error processing this request. Please try again.',
            ephemeral=True
        )
        return
    for pid in inter.resolved_values:
        member = state.members_by_id.get(pid)
        state.selected_members_by_name[member.display_name] = member
    await regenerate(inter, state)


async def show_player_prompt(inter: disnake.ApplicationCommandInteraction,
                             state: BuilderState):
    members = inter.guild.fetch_members(limit=25)
    # An error should be thrown here if we weren't able to retrieve any members.

    options = []
    async for member in members:
        if member.id == client.user.id:
            continue
        state.members_by_id[str(member.id)] = member
        options.append(
            SelectOption(
                label=member.display_name,
                value=str(member.id)
            )
        )

    components = [
        StringSelect(
            placeholder='Participating members',
            custom_id=id_member_select,
            min_values=0,
            max_values=len(options),
            options=options
        ),
        ActionRow(btn_generate, btn_report)
    ]

    embed = Embed(
        title='Build Modpack',
        description=(
            '**Select any players that will be joining.**\n\n'
            '_Please be patient. Building can take a while._'
        )
    )
    add_author(embed, inter.author)

    state.message = await inter.edit_original_response(
        embed=embed,
        components=components
    )


async def regenerate(inter: disnake.MessageInteraction,
                     state: BuilderState):
    logger.info(f'{inter.author.display_name} is generating a modpack')
    state.modpack = generate(list(state.selected_members_by_name.keys()))
    components = ActionRow(btn_regenerate, btn_send_it, btn_report)

    if state.message:
        # If this interaction has already been responded to
        try:
            await inter.delete_original_response()
        except:
            pass

        await state.message.edit(
            embed=state.to_embed(),
            components=components
        )
    else:
        # If this interaction has been deferred, but not responded to
        state.message = await inter.edit_original_response(
        embed=state.to_embed(),
        components=components
    )


async def send(inter: disnake.MessageInteraction,
               state: BuilderState):
    await state.message.delete()
    filepath = state.modpack.generate_modpack_zip()

    try:
        await inter.delete_original_response()
    except:
        pass

    channel: disnake.TextChannel = inter.channel
    await channel.send(
        embed=state.to_embed(),
        file=disnake.File(filepath)
    )
    desc_by_name = {}
    for sq, meta in state.modpack.meta_by_sidequest.items():
        if sq.per_player:
            for name, target in meta.get('assignments').items():
                desc_by_name.setdefault(name, []).append(f'{sq.name}: **{target}**')
    for name, desc in desc_by_name.items():
        embed = Embed(
            description='\n'.join(desc)
        )

        add_author(embed, state.author)

        member: disnake.Member = state.selected_members_by_name.get(name)
        dm_channel = member.dm_channel
        if dm_channel is None:
            dm_channel = await member.create_dm()

        await dm_channel.send(
            embed=embed
        )


@client.event
async def on_ready():
    logger.info('Successfully connected to Discord')
    import api
    await api.app.run_task(
        '0.0.0.0',
        8000
    )
    client.loop.call_soon_threadsafe(client.loop.stop)


def start():
    client.run(os.environ.get('DISCORD_BOT_TOKEN'))


if __name__ == '__main__':
    import main
    main.load()
    start()

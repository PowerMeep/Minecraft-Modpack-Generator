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


class BuilderState:
    def __init__(self):
        self.members_by_id = {}
        self.selected_members_by_name = {}
        self.modpack = None
        self.message: disnake.Message = None

    def to_embed(self):
        desc = [
            f'# {self.modpack.get_name()}',
            self.modpack.challenge.description,
            f'\n**Duration:** {self.modpack.challenge.duration}'
        ]
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
async def build_modpack(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer(
        with_message=False,
        ephemeral=True
    )

    state: BuilderState
    if state := states_by_user.get(inter.author.id):
        try:
            await state.message.delete()
        except:
            pass
    state = BuilderState()
    states_by_user[inter.author.id] = state

    options = []
    async for member in inter.guild.fetch_members(limit=25):
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
        Button(
            style=ButtonStyle.green,
            label='Build',
            custom_id=id_do_generate
        )
    ]

    embed = Embed(
        title='Build Modpack'
    )

    state.message = await inter.edit_original_response(
        embed=embed,
        components=components
    )


@client.listen('on_button_click')
async def on_button_click(inter: disnake.MessageInteraction):
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


async def regenerate(inter: disnake.MessageInteraction,
                     state: BuilderState):
    await inter.response.defer(
        with_message=False,
        ephemeral=True
    )
    logger.info(f'{inter.author.display_name} is generating a modpack')
    state.modpack = generate(list(state.selected_members_by_name.keys()))
    await state.message.edit(
        embed=state.to_embed(),
        components=ActionRow(
            Button(
                label='Regenerate',
                style=ButtonStyle.green,
                custom_id=id_do_generate
            ),
            Button(
                label='Send it',
                style=ButtonStyle.green,
                custom_id=id_send_it
            ),
        )
    )


async def send(inter: disnake.MessageInteraction,
               state: BuilderState):
    await state.message.delete()
    filepath = state.modpack.generate_modpack_zip()
    await inter.response.send_message(
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

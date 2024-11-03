import logging
logger = logging.getLogger()


def dict_to_x_list(d) -> list:
    out = []
    for v in d.values():
        out .append('x' if v else ' ')
    return out


class Mod:
    def __init__(self,
                 name,
                 configs=None,
                 curseforge_id: int = None,
                 modrinth_slug: str = None):
        self.name = name
        self.curseforge_id = curseforge_id
        self.modrinth_slug = modrinth_slug

        # file id
        # required (enabled?)
        self.configs = configs or []

    def get_alt_configuration(self, configs):
        mod = Mod(
            name=self.name,
            configs=configs
        )
        return mod

    def __str__(self):
        return self.name


mods_by_name = {
    'Vanilla': Mod('Vanilla')
}


def from_json(obj: dict):
    m = Mod(
        name=obj.get('name'),
        curseforge_id=obj.get('curseforge_id'),
        modrinth_slug=obj.get('modrinth_slug')
    )
    logger.info(f'Loaded mod: {m.name}')
    mods_by_name[m.name] = m


def load_mods():
    from models.load_util import load_named_items
    load_named_items('configs/mods.json', from_json)

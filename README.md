# Minecraft Modpack Generator

This project generates goal-oriented modpacks for Minecraft.

For the moment, this only supports the Curseforge API and Forge mods.

## How it works
### It's All About the Layers
**Layers** are a collection of mods that and configurations that have a high compatibility and serve a specific theme.
They are applied one at a time to create the final output.

Each layer on its own should result in a valid "modpack", even if that pack only ends up being one mod.

### Generation
First, a **Challenge** is chosen. The challenge represents the goal that the players will try to achieve
over the duration of this modpack.

Several challenges support a number of **Scenarios**. These function as the setting that the challenge takes place in.

Once the **Challenge** and **Scenario** are chosen, there is enough information to select the most compatible version of
Minecraft and the mod loader. Any layers that are not compatible with this selection are dropped.

Now that the core is in place, we can randomly add up to 3 supported **Sidequests**. These are like a little extra spice
to add some more flavor to the overall experience. Some sidequests can generate player-specific configurations if a
list of players is provided before the pack generation.

Lastly, one final pass is made for **Compats**, which are extra layers that are applied if the conditions are met.
These just serve to create better integration between other things that are present.

## Roadmap

### General TODO:
- Add gravity sidequest (Fabric or 1.12 Forge)
- Add lifelink sidequest (Bukkit)
- Seed the randomness
- Figure out modrinth multiple project scrape
- Test ALL layers to make sure they work independently
  - Implement some method of creating a modpack with arbitrary layers
- Rather than challenges also having terrain and villages, use one-off scenarios with no names? Less duplicate code.

### Milestone 1
**The builder consistently assembles sensible configurations.**

### Milestone 2
**The builder describes the configuration in the Discord server.**
- [x] REST API
  - [x] Pass in players
  - [x] Per-player sidequests
  - [x] Players in params
  - [x] Players in request body
- [x] Dockerfile
- [x] Discord
  - [x] Generate and post a configuration
  - [x] DM players their specific configurations
  - [x] Discord post uses better links
  - [x] Other configs
- [ ] A short description (< 100 chars) for Discord dropdowns

### Milestone 3
**The builder is able to assemble zip files that can be imported by clients.**
- [x] Ability to choose a loader and minecraft version
- [x] Ability to choose a version for the loader
- [x] Account for mod dependencies
- [x] Generate manifest.json
- [x] Generate modlist.html
- [x] Generate overrides from layers
- [x] Generate final zip file
- [x] Attach client zip file to Discord message
- [ ] Zip file can be downloaded from a url
  - Is this necessary?
  - Every page refresh would have to generate a zip and attach a link to it
- [ ] Delete old files from temp and build
- [ ] Generated thumbnails

### Milestone 4
**The builder is able to automatically start a Minecraft server.**
- [ ] Overrides for server.properties file
  - [ ] Hardcore
  - [ ] Generate structures
- [ ] Some kind of local "registry" to copy already-downloaded files from
- [ ] Ability to generate a Docker Compose for the itzg image
- [ ] Ability to create / stop / restart / destroy images using that compose

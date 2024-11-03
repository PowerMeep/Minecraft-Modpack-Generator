# Minecraft Modpack Generator

This project generates goal-oriented modpacks for Minecraft.

This version is a very early iteration. It's basically a proof of concept.

## How it works
### Challenges
First, a **Challenge** is chosen. A challenge is composed of **Layers** and **Sidequests**.
The challenge dictates how the modpack will be constructed and what the goal of the pack will be.

The final modpack will have a name, description, a modloader, a version, and a list of mods.

Noteably, there will only ever be one village or terrain mod.

### Layers
**Layers** are a collection of mods that and configurations that have a high compatibility and serve a specific theme.

### Sidequests
**Sidequests** are smaller goals that players will try to complete alongside the main **Challenge** goal.
They may provide **Layers** of their own.

Some **Sidequests** require to know the list of players beforehand.
This is needed to generate player-specific configurations.

### Compats
**Compats** are extra mods or configs that are activated by the presence of two other mods.

## Roadmap

### General TODO:
- [x] Ability to look up mod metadata from a url
- [ ] Mods w/ multiple configs
- [ ] Figure out modrinth multiple project scrape
- [x] Get loaders and versions from responses
- [ ] Make the pretty version table
- [x] Auto choose the configuration that gets the most mods
- [x] Cache api calls
- [x] Validate JSON files when reading them in

### Milestone 1
**The builder consistently assembles sensible configurations.**

### Milestone 2
**The builder describes the configuration in the Discord server.**
- [ ] REST API
  - [x] Pass in players
  - [x] Per-player sidequests
  - [ ] Pass configs in body
- [ ] Dockerfile
- [ ] Discord integration

### Milestone 3
**The builder is able to assemble zip files that can be imported by clients.**
- [x] Ability to choose a loader and version
- [ ] Some kind of local "registry" to copy already-downloaded files from
- [ ] Account for mod dependencies (?)
- [ ] Attach client zip file to Discord message

### Milestone 4
**The builder is able to automatically start a Minecraft server.**
- [ ] Ability to generate a Docker Compose for the itzg image
- [ ] Ability to create / stop / restart / destroy images using that compose

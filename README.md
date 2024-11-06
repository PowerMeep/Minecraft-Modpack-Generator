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
- [ ] Add gravity sidequest
- [ ] Add skyblock theme
- [ ] Dawn Era
- [ ] Rename "roughin it"
- [ ] Implement compats
- [ ] Seed the randomness
- [ ] Figure out modrinth multiple project scrape
- [ ] Make the pretty version table
- [ ] Include hardcore in json
- [x] Show the scenario names, not just the challenge types
- [x] Ability to look up mod metadata from a url
- [x] Get loaders and versions from responses
- [x] Auto choose the configuration that gets the most mods
- [x] Cache api calls
- [x] Validate JSON files when reading them in
- [x] Remove sidequests when all of their mods have been removed
- [x] Retrieve and store more CF data
  - [x] Official name
  - [x] Friendly url
  - [x] File Id
  - [x] Dependencies
  - [ ] Modloader data


### Milestone 1
**The builder consistently assembles sensible configurations.**

### Milestone 2
**The builder describes the configuration in the Discord server.**
- [x] REST API
  - [x] Pass in players
  - [x] Per-player sidequests
  - [x] Players in params
  - [x] Players in request body
  - [ ] Other configs
- [x] Dockerfile
- [x] Discord
  - [x] Generate and post a configuration
  - [x] DM players their specific configurations
  - [x] Discord post uses better links

### Milestone 3
**The builder is able to assemble zip files that can be imported by clients.**
- [x] Ability to choose a loader and minecraft version
- [ ] Ability to choose a version for the loader
- [ ] Account for mod dependencies (?)
  - Determine whether CF can do this automatically
- [x] Generate manifest.json
- [x] Generate modlist.html
- [x] Generate overrides from layers
- [x] Generate final zip file
- [x] Attach client zip file to Discord message
- [ ] Zip file can be downloaded from a url
  - Is this necessary?
  - Every page refresh would have to generate a zip and attach a link to it
- [ ] Delete old files from temp and build

### Milestone 4
**The builder is able to automatically start a Minecraft server.**
- [ ] Some kind of local "registry" to copy already-downloaded files from
- [ ] Ability to generate a Docker Compose for the itzg image
- [ ] Ability to create / stop / restart / destroy images using that compose

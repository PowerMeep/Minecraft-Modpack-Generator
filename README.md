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
- [ ] Layer-Mod link has more data
  - [ ] Requiredness
  - [ ] Mod Configs
  - [ ] Layer Configs?
- [x] Remove sidequests when all of their mods have been removed
- [x] Retrieve and store more CF data
  - [x] Official name
  - [x] Friendly url
  - [x] File Id
  - [x] Dependencies
  - [ ] Modloader data





Multiple mod configs:
- Configs need to be aware of which versions they support (with wildcards)
- A mod may have multiple configs, a config may have multiple versions


**Option 1: Mods with different configs are defined as different mods**

Pros
+ Layers just reference which mod they want
+ Layers are able to reuse the same configs
+ Mods that are dropped before the final result will also drop their configs

Cons
- Duplicates mod definitions

**Option 2: Mods define their own configs**

Pros
+ Layers are able to reuse the same configs
+ Mods that are dropped before the final result will also drop their configs
+ No duplication

Cons
- Layers reference mods and their configs

**Option 3: Layers define configs (mod level)**

Pros
+ More cohesive configs, knowing what other mods will be included (?)
+ Mods that are dropped before the final result will also drop their configs

Cons
- Some configs may be duplicated with other layers'


**Option 4: Layers define configs (layer level)**

Pros
+ More cohesive configs, knowing what other mods will be included

Cons
- Some configs may be duplicated with other layers'
- Some mods may be dropped from the final result, but the configs would be kept

--

**Option: Mods had different entries for each config**
- Layers reference the mod-config they want
- Layers also define their own configs
- Layer configs are applied on top of mod configs

**Option:**
- Configs are defined separately
- Layers... ??
- This one might just be too complicated






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
- [ ] Zip file can be downloaded from a url
- [ ] Attach client zip file to Discord message

### Milestone 4
**The builder is able to automatically start a Minecraft server.**
- [ ] Some kind of local "registry" to copy already-downloaded files from
- [ ] Ability to generate a Docker Compose for the itzg image
- [ ] Ability to create / stop / restart / destroy images using that compose

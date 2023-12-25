# Modpack Builder

This project generates goal-oriented modpacks.

This version is a very early iteration. It's basically a proof of concept.

## Roadmap

### General TODO:
- [ ] Ability to look up mod metadata from a url
- [ ] Separation of code and configuration data
- [x] Use logging instead of print statements

### Milestone 1
**The builder consistently assembles sensible configurations.**

### Milestone 2
**The builder describes the configuration in the Discord server.**
- [ ] Discord integration
- [ ] Dockerfile (?)

### Milestone 3
**The builder is able to assemble zip files that can be imported by clients.**
- [ ] Ability to choose a loader and version
- [ ] Some kind of local "registry" to copy already-downloaded files from
- [ ] Account for mod dependencies (?)
- [ ] Attach client zip file to Discord message

### Milestone 4
**The builder is able to automatically start a Minecraft server.**
- [ ] Ability to generate a Docker Compose for the itzg image
- [ ] Ability to create / stop / restart / destroy images using that compose

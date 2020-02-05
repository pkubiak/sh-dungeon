# sh-dungeon

Simple dungeon crawler in terminal using RayTracing engine. 
Project use python reimplementation of my previous [raytracer](https://github.com/pkubiak/raytracer). 

## Features ##
- FullColor 24bit display in terminal
- No external package dependencies
- Low res pixelated graphics

<a href="https://asciinema.org/a/297924" class="float:right">
<img src="https://asciinema.org/a/297924.svg" width="500" alt="asciicast">
</a>


## Implementation status ##
- [x] Keyboard handling in terminal ([keyboard.py](https://github.com/pkubiak/sh-dungeon/blob/master/keyboard.py))
- [x] Full color image display in terminal (using ANSI escape sequences: [screen.py](https://github.com/pkubiak/sh-dungeon/blob/master/screen.py))
- [x] PNM image loading ([image.png](https://github.com/pkubiak/sh-dungeon/blob/master/rt/image.py))
- [ ] RayTracer system
  - [x] Cameras
    - [x] Ortographic
    - [x] Perspectivic
  - [ ] Scene
    - [x] Simple solids collection
    - [ ] BHV structure for fast scene intersecting
  - [ ] Solids
    - [x] Triangles
    - [x] Quads
    - [ ] Sprites (Quad always parallel to camera)
  - [ ] Textures
    - [x] ConstantTexture (RGB color)
    - [x] ImageTexture
  - [ ] Materials
    - [x] Dummy Material
    - [x] Flat Material
    - [x] Phong Material
    - ...
  - [ ] Lights
    - [x] Point Light
    - [ ] Directional Light
  - [ ] Integrators
    - [x] RayCasting
    - [x] RayTracing
    - ... (PathTracer, RecRayTracer)
  - [ ] Speedups (to provide realtime rendering)
  
- [ ] Dungeon Crawler mechanics
  - [x] Simple maze demo
  - [x] Simple turn based animations
  - [ ] Level stored in files
  - [ ] Many activities system (via [State Pattern](http://gameprogrammingpatterns.com/state.html))
    - [ ] Main Menu
    - [ ] Game
    - [ ] Inventory 
    - [ ] ...
  - [ ] Sprites rendering (npc, enemies, torches, ...)
  - [ ] Interaction with environment (opening doors, using staircase)
  - [ ] User handled items (sword, magic staff, ...)
  - [ ] NPC / enemies
    - [ ] movements
    - [ ] dialogs
  - [ ] Fight system
  

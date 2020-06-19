# sh-dungeon

Simple dungeon crawler in terminal using RayTracing engine. 
Project use python reimplementation of my previous [raytracer](https://github.com/pkubiak/raytracer). 

Pypy3 is recommended python runtime.

## Features ##
- FullColor 24bit display in terminal
- No external package dependencies
- Low res (63x63) pixelated graphics

<a href="https://asciinema.org/a/298860" class="float:right">
<img src="https://asciinema.org/a/298860.png" width="300" alt="asciicast">
</a>


## Implementation status ##
- [x] Keyboard handling in terminal ([keyboard.py](https://github.com/pkubiak/sh-dungeon/blob/master/engine/keyboard.py))
- [x] Full color image display in terminal (using ANSI escape sequences: [screen.py](https://github.com/pkubiak/sh-dungeon/blob/master/engine/screen.py))
- [x] PNM/PAM image loading ([image.py](https://github.com/pkubiak/sh-dungeon/blob/master/engine/rt/image.py))
- [x] Many activities system (via [State Pattern](http://gameprogrammingpatterns.com/state.html)): [activity.py](https://github.com/pkubiak/sh-dungeon/blob/master/engine/activity.py)
  - [x] Main Menu
  - [x] Game
  - [ ] Inventory 
  - [ ] ...
- [ ] GUI
  - [ ] Inputs
  - [ ] Radio/Check button
  - [ ] Select box
  - [ ] Scrollarea
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
    - [ ] ...
  - [ ] Lights
    - [x] Point Light
    - [ ] Directional Light
  - [ ] Integrators
    - [x] RayCasting
    - [x] RayTracing
    - [ ] ... (PathTracer, RecRayTracer)
  - [ ] Speedups (to provide realtime rendering)
  
- [ ] Dungeon Crawler mechanics
  - [x] Simple maze demo
  - [x] Simple turn based animations
  - [ ] Level stored in files

  - [x] Sprites rendering (npc, enemies, torches, ...)
  - [ ] Interaction with environment (opening doors, using staircase)
  - [x] User handled items (sword, magic staff, ...)
  - [ ] NPC / enemies
    - [ ] movements
    - [ ] dialogs
  - [ ] Fight system
  - [ ] Collisions
  

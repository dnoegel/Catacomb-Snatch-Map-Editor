Catacomb Snacht Map Editor
--------------------------
Create your own Maps for Catacomb Snatch.

Features
========
 * Load and save levels directly from the .jar-files
 * Load and save levels to .bmp files to share them with other people

Multi level support
===================
The original version of CS does only support one level - level1.bmp.
Several forks of the game try to implement multi level support. Right now these forks (e.g. Maescool's or Borsty's) seem to hardcode additional levels. For this reason it is not possible for the level editor, to add additional levels to the game.

Anyhow it is possible to deal with those multi-level-forks:

 * The level editor support reading those levels. When opening a multi-level .jar file, you will be prompted to select the level, you want to edit.
 * When writing to a multi-level .jar file, level1.bmp (the default level) will be overwriten. 
 
If you do know how to compile the source, you are also able to add you levels to the LevelList (./src/com/mojang/mojam/level/LevelList.java).

Warning
=======
 * backup your mojam.jar file, befor you edit it. This script won't do it for you
 * there are no save-before-quit and overwrite-warnings

Dependencies
===========
 * Python2
 * PIL (python-imaging)
 * PyGTK

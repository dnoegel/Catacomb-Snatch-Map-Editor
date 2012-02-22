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

The perhaps most frequently used fork by Maescool and Borsty does support multi levels. In order to use it, you have to store your level-bitmaps to ~/.mojam/levels. The game will look there for levels.

If you want to store a new level into the game's .jar file, this level editor will overwrite the existing level1.bmp. Right now there is now way around this, as the levels in the .jar-file are hardcoded. So in most cases, you want to store your levels in ~/.mojam/levels.

Warning
=======
 * backup your mojam.jar file, befor you edit it. This script won't do it for you
 * there are no save-before-quit and overwrite-warnings

Dependencies
===========
 * Python2
 * PIL (python-imaging)
 * PyGTK

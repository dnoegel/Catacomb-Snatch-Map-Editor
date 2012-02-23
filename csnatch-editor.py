#!/usr/bin/env python
# coding: utf-8

import gtk

import csnatch_editor_modules.main_window

class App(object):
    def __init__(self):
        self.window = csnatch_editor_modules.main_window.GUI()



if __name__ == "__main__":
    App()
    gtk.main()

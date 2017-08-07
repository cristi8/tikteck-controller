#!/usr/bin/env python

import os
import cherrypy

COLOR_FILE = '/dev/shm/lightbulbs_color'


class App(object):
    @cherrypy.expose
    def index(self):
        index_html_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'index.html')
        return cherrypy.lib.static.serve_file(index_html_path)

    @cherrypy.expose
    def set_color(self, r, g, b, bright):
        with open(COLOR_FILE, 'w') as f:
            f.write('%d %d %d %d\n' % (int(r), int(g), int(b), int(bright)))


conf = {
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': '',
        'tools.staticdir.root': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    }
}
cherrypy.quickstart(App(), config=conf)

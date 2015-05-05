__author__ = 'roberto'
import os

class Files(object):

    def __init__(self, filename):
        self.load_video(filename)
        #self.filename_video = filename



    def load_video(self, filename):
        self.filename_video = filename
        self.id = os.path.splitext(filename)[0]

    def exists_reel(self, exists):
        self.exists_reel=exists


import random

class Queue():
    def __init__(self):
        self.songs = []
        self.current_song = None
    def add(self, song):
        self.songs.append(song)
    def next(self):
        if self.songs:
            return self.songs.pop(0)
        return None
    def is_empty(self):
        return len(self.songs) == 0
    def set_current(self, song):
        self.current_song = song
    def show(self, page=0):
        songs = []
        if self.current_song is not None:
            songs.append(self.current_song)
        songs.extend(self.songs)
        start = page * 20
        end = start + 20
        result = ''
        for index, song in enumerate(songs[start:end], start=start + 1):
            result += f'{index}. **{song["title"]}**\n'
        if not result:
            return '❌ The queue is empty!'
        return result
    def shuffle(self):
        random.shuffle(self.songs)
    def push(self, index):
        song = self.songs.pop(index-2)
        self.songs.insert(0, song)
    def repeat_current(self):
        song = self.current_song
        self.songs.insert(0, song)
    def insert(self, index, song):
        self.songs.insert(index, song)
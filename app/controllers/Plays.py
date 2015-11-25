from system.core.controller import *
from flask import redirect, request, flash

class Plays(Controller):
    def __init__(self,action):
        super(Plays, self).__init__(action)
        self.load_model('Play')

    def index(self):
        return self.load_view('/Plays/index.html')

    def create(self):
        register_info = request.form
        register = self.models['Play'].create(register_info)
        if register['status'] == False:
            for message in register['errors']:
                flash(message)
                return redirect('/')
        else:
            flash("You have succesfully registered!")
            return redirect('/')

    def login(self):
        login_info = request.form
        login = self.models['Play'].login(login_info)
        if login['status'] == True:
            session['id'] = login['login']['id']
            session['first_name'] = login['login']['first_name']
            return redirect('/home')
        else:
            return redirect('/')

    def home(self):
        hub_info = self.models['Play'].hub_info()
        return self.load_view('/Plays/home.html', hub_info=hub_info)

    def add_song(self):
        song_info = request.form
        add_song = self.models['Play'].add_song(song_info)
        if add_song['status'] == False:
            for message in add_song['errors']:
                flash(message)
                return redirect('/home')
        else:
            flash("You have succesfully added a song!")
            return redirect('/home')

    def playlist(self, id):
        user_id = id
        playlist = self.models['Play'].list_playlist(user_id)
        user = self.models['Play'].user(user_id)
        return self.load_view('/Plays/playlist.html', playlist =playlist, user=user)

    def add_playlist(self):
        user_id = session['id']
        name = session['first_name']
        playlist_info = request.form
        add_playlist = self.models['Play'].add_playlist(user_id, name, playlist_info)
        return redirect('/home')

    def song(self, id):
        song_id = id
        song_info = self.models['Play'].song(song_id)
        others_added = self.models['Play'].others_added(song_id)
        return self.load_view('/Plays/song.html', song_info=song_info, others_added = others_added)
    def logout(self):
        session.pop = ['id']
        session.pop = ['first_name']
        return redirect('/')

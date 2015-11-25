from system.core.model import Model
import re

class Play(Model):
    def __init__(self):
        super(Play, self).__init__()
    def create(self, info):
        EMAIL_REGEX = re.compile(r'^[a-za-z0-9\.\+_-]+@[a-za-z0-9\._-]+\.[a-za-z]*$')
        errors = []
        
        if len(info['first_name']) < 2:
            errors.append('Name needs to be at least 2 characters long')
        if len(info['last_name']) < 2:
            errors.append('Last name needs to be at least 2 characters long')
        if not info['email']:
            errors.append('Email can\'t be blank')
        elif not EMAIL_REGEX.match(info['email']):
            errors.append('Email must be in valid format')
        if len(info['password']) < 3:
            errors.append('Password must be longer than 3 characters')
        if info['password'] != info['confirm_password']:
            errors.appened('Password doesn\'t match')
        
        if errors:
            return {"status" :False, 'errors' :errors}
        else:
            pw_hash = self.bcrypt.generate_password_hash(info['password'])
            create_user_query = "INSERT INTO users (first_name, last_name, email, password,created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', NOW(), NOW())".format(info['first_name'], info['last_name'], info['email'],pw_hash)
            self.db.query_db(create_user_query)
            return{"status":True}
    def login(self,info):

        login_user_query = "SELECT * FROM users WHERE email = '{}'".format(info['login_email'])
        login = self.db.query_db(login_user_query)
        if login[0]:
            if self.bcrypt.check_password_hash(login[0]['password'], info['login_password']):
                return {'status':True, 'login':login[0]}
            else:
                return {'status':False}
    def add_song(self, info):
        errors = []

        if len(info['artist']) < 2:
            errors.append('Artist name needs to be more than 2 characters long')
        if len(info['title']) < 2:
            errors.append('Song title needs to be longer than 2 characters')
        if errors:
            return{"status": False, 'errors':errors}
        else:
            add_artist_query = "INSERT INTO artists (name, created_at, updated_at) VALUES ('{}', NOW(), NOW())".format(info['artist'])
            self.db.query_db(add_artist_query)

            artist_id_query = "SELECT * FROM artists ORDER BY created_at DESC"
            artist_id = self.db.query_db(artist_id_query)
            print artist_id[0]['id']

            add_song_query = "INSERT INTO songs (title, artist_id, created_at, updated_at) VALUES ('{}','{}',NOW(),NOW())".format(info['title'], artist_id[0]['id'])
            self.db.query_db(add_song_query)
            return{"status": True}
    def hub_info(self):
        hub_info_query = "SELECT songs.id,playlists.user_id,songs_in_playlist.playlist_id, songs.title, artists.name, count(songs_in_playlist.song_id) AS count FROM artists JOIN songs ON artists.id = songs.artist_id Left JOIN songs_in_playlist ON songs.id = songs_in_playlist.song_id LEFT JOIN playlists ON playlists.id = songs_in_playlist.playlist_id GROUP BY songs.id"
        hub_info = self.db.query_db(hub_info_query)
        print hub_info
        return hub_info
    def add_playlist(self, id, name, info):
        song_info_query = "SELECT songs.id, artists.name, songs.title FROM artists JOIN songs on artists.id = songs.artist_id WHERE songs.id = {}".format(info['song_id'])
        song_info = self.db.query_db(song_info_query)
        
        check_playlist_query = "SELECT * FROM playlists WHERE user_id = '{}'".format(id)
        check_playlist = self.db.query_db(check_playlist_query)
        
        if not check_playlist:
            new_playlist_query = "INSERT INTO playlists (name, created_at,updated_at,user_id) VALUES ('{}', NOW(),NOW(),'{}')".format(name, id)
            self.db.query_db(new_playlist_query)
        which_playlist_query = "SELECT playlists.id FROM playlists WHERE user_id = '{}'".format(id)
        playlist_id = self.db.query_db(which_playlist_query)
        print playlist_id
        playlist_id = playlist_id[0]
        
        add_playlist_query = "INSERT INTO songs_in_playlist (playlist_id, song_id) VALUES ('{}','{}')".format(playlist_id['id'], info['song_id'])
        self.db.query_db(add_playlist_query)

    def list_playlist(self, user_id):
        list_playlist_query = "SELECT playlists.user_id,songs_in_playlist.playlist_id, songs.title, artists.name, count(songs_in_playlist.song_id) AS count FROM artists JOIN songs ON artists.id = songs.artist_id Left JOIN songs_in_playlist ON songs.id = songs_in_playlist.song_id LEFT JOIN playlists ON playlists.id = songs_in_playlist.playlist_id WHERE playlists.user_id = '{}' GROUP BY songs.id".format(user_id)
        playlist = self.db.query_db(list_playlist_query)
        return playlist

    def user(self, user_id):
        user_query = "SELECT * FROM users WHERE id = {}".format(user_id)
        user = self.db.query_db(user_query)
        return user[0]

    def song(self, song_id):
        song_info_query = "SELECT * FROM songs JOIN artists ON artists.id = songs.artist_id WHERE songs.id = '{}'".format(song_id)
        song_info = self.db.query_db(song_info_query)
        return song_info[0]

    def others_added(self, song_id):
        others_added_query = "SELECT concat(users.first_name, ' ',users.last_name) AS name, count(songs_in_playlist.song_id) AS count,users.id as user_id FROM users JOIN playlists ON users.id = playlists.user_id LEFT JOIN songs_in_playlist ON playlists.id = songs_in_playlist.playlist_id LEFT JOIN songs ON songs_in_playlist.song_id = songs.id WHERE songs.id = '{}' GROUP BY users.id".format(song_id)
        others_added = self.db.query_db(others_added_query)
        return others_added
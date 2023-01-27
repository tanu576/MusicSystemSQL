from ast import Str
import sqlite3
from getpass import getpass
from datetime import date, datetime
import math
import os

connection = None
cursor = None

def connect(path):

    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return

def startSession(userid):

    global connection, cursor
    print("New session has started now.")
    startdate = datetime.now()
    finalstartdate = startdate.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''SELECT max(sno) FROM sessions s''')
    temp =  cursor.fetchone() 
    sno = temp[0] +1
    data = (userid, sno, finalstartdate, None)
    cursor.execute ('INSERT INTO sessions (uid, sno, start, end) VALUES (?,?,?,?);', data)
    connection.commit()
    return sno


def getUserActions(userid):
    sessionNo = 0
    exit = False
    while (not exit):
        userTaskId = input("Select 1 to start a session, 2 to search for songs and playlists, 3 to search for artists, 4 to end the session, 5 to Logout, 6 to exit: ")
        if userTaskId == '1':
            sno = startSession(userid)
            sessionNo = sno
        elif userTaskId == '2':
            search(userid)
        elif userTaskId == '3':
            searchArtist(userid)
        elif userTaskId == '4':
            if sessionNo != 0:
                endSession(sessionNo)
            else:
                print("No session started")            
        elif userTaskId == '5':
            # endSession(sessionNo)
            main()
        elif userTaskId == '6': 
            exit = True
        else:
            print("Invalid option selected")

def searchArtist(userid):
    kword = input("Enter keywords separated by space: ")
    kwords_arr = kword.split(" ")
    count = len(kwords_arr)
    counter = 0
    query = "SELECT result.name, result.nationality, count(p3.sid) FROM  "
    query += "(SELECT aps.name, aps.nationality, aps.cnt, count(aps.name) as num FROM ( "
    for kw in kwords_arr:
        if counter < count-1:
            query += '''SELECT a.name, a.nationality, count(p.sid) as cnt
                        FROM artists a, songs s, perform p 
                        WHERE (a.aid = p.aid AND p.sid = s.sid ) 
                        AND (a.name like '%{}%' OR s.title like '%{}%')
                        GROUP BY a.name, a.nationality
                        UNION ALL
                        '''.format(kw,kw)
        else:
            query += '''SELECT a2.name, a2.nationality, count(p2.sid) as cnt
                        FROM artists a2, songs s2, perform p2 
                        WHERE (a2.aid = p2.aid AND p2.sid = s2.sid ) 
                        AND (a2.name like '%{}%' OR s2.title like '%{}%')
                        GROUP BY a2.name, a2.nationality
                        ORDER BY a2.name,a2.nationality ) as aps GROUP BY aps.name ORDER BY num DESC) as result, perform p3, artists a3 
                        WHERE (result.name = a3.name and a3.aid = p3.aid)
                        GROUP BY result.name, result.nationality
                        ORDER BY num DESC;
                        '''.format(kw,kw)
        counter += 1

    cursor.execute(query)
    row = cursor.fetchall()
    num_results = len(row)
    num_pages = math.ceil(num_results/5)
    i = 0
    page_count  = 1
    for  each in row:
        if i <5:
            print(each)
            if i == 4:
                print("Page 1/{}".format(num_pages))
                page_count += 1
        else:
            option_selected = input("Press 1 for selecting an artist or 2 for viewing more information: ")
            os.system('clear')
            while page_count <= num_pages:
                if option_selected == '1':
                    artist_info = get_artist_info()
                    selection_option = input("Press 1 to select a song or 2 to exit: ")
                    if selection_option == '1':
                        get_song_actions(userid,artist_info)
                    elif selection_option == '2':
                        return
                        
                elif option_selected == '2':
                    for j in range(i+1,i+6):
                        if (j < num_results):
                            print(row[j])
                        if j == i+5:
                            print("Page {}/{}".format(page_count,num_pages)) 
                            page_count += 1
                if page_count == num_pages+1:
                    break
                option_selected = input("Press 1 for selecting an artist or 2 for viewing more information: ")
                i += 5
            break
        i += 1
    option_select2 = input("Select 1 for artist details or 2 for exit: ")
    if option_select2 == 1:
        artist_info = get_artist_info()
        selection_option = input("Press 1 to select a song or 2 to exit: ")
        if selection_option == '1':
            get_song_actions(userid,artist_info)
    elif option_select2 == 2:
        return

def search(userid):
    kword = input("Enter keywords separated by space: ")
    kwords_arr = kword.split(" ")
    count = len(kwords_arr)
    counter = 0
    # query = "SELECT result.sid, result.title, result.duration FROM "
    query = "SELECT t1.sid, t1.title, t1.duration, count(t1.sid) as num FROM ( "
    for kw in kwords_arr:
        if counter < count-1:
            query += '''SELECT s.sid, s.title, s.duration
                        FROM songs s
                        WHERE s.title like '%{}%'
                        UNION ALL
                        '''.format(kw)
        else:
            query += '''SELECT s2.sid, s2.title, s2.duration
                        FROM  songs s2 
                        WHERE s2.title like '%{}%'
                        ORDER BY s2.sid ) as t1 GROUP BY t1.sid ORDER BY num DESC  ;
                        '''.format(kw)

        counter += 1

    cursor.execute(query)
    row = cursor.fetchall()
    songs = []
    x = ['Song']
    for each in row:
        songs.append(each + tuple(x))
    


    counter2 = 0
    # query2 = "SELECT result.pid, result.title, result.total FROM "
    query2 = "SELECT t1.pid, t1.title, t1.total, count(t1.pid) as num FROM ( "    
    for kw in kwords_arr:
        if counter2 < count-1:
            query2 += '''SELECT p.pid, p.title, sum(s.duration) as total
                    FROM playlists p, songs s, plinclude pl
                    WHERE (pl.pid = p.pid AND pl.sid = s.sid) AND p.title like '%{}%'
                    GROUP BY p.pid, p.title
                    UNION ALL
                    '''.format(kw)

        else:
            query2 += '''SELECT p2.pid, p2.title, sum(s2.duration) as total
                        FROM  playlists p2 , songs s2, plinclude pl2
                        WHERE (pl2.pid = p2.pid AND pl2.sid = s2.sid) AND p2.title like '%{}%'
                        GROUP BY p2.pid, p2.title
                        ) as t1 GROUP BY t1.pid ORDER BY num DESC;
                        '''.format(kw)

        counter2 += 1

    cursor.execute(query2)
    row2 = cursor.fetchall()
    playlist = []
    y = ['Playlist']
    for each in row2:
        playlist.append(each + tuple(y))
    row3 = songs + playlist
    row3.sort(key= lambda tup: tup[3], reverse=True)


    num_results = len(row3)
    num_pages = math.ceil(num_results/5)
    i = 0
    page_count  = 1
    for  each in row3:
        if i <5:
            print(each)
            if i == 4:
                print("Page 1/{}".format(num_pages))
                page_count += 1
        else:
            option_selected = input("Press 1 for selecting an Song/Playlist or 2 for viewing more information: ")
            #os.system('clear')
            while page_count <= num_pages:
                if option_selected == '1':
                    selection_option = input("Enter Song ID / Playlist ID: ")
                    for i in row3:
                        if i[4] == 'Song':
                            song_actions(userid, selection_option)
                        elif i[4] == 'Playlist':
                            playlist_action(selection_option, userid)
                elif option_selected == '2':
                    for j in range(i+1,i+6):
                        if (j < num_results):
                            print(row3[j])
                        if j == i+5:
                            print("Page {}/{}".format(page_count,num_pages)) 
                            page_count += 1
                if page_count == num_pages+1:
                    break
                option_selected = input("Press 1 for selecting an Song/Playlist or 2 for viewing more information: ")
                i += 5
            break
        i += 1
    option_select2 = input("Press 1 for selecting an Song/Playlist or 2 for exit: ")
    if option_select2 == '1':
        song_playlist = input("Enter 1 for selecting Song 2 for selection Playlist id: ")
        if song_playlist == '1':
            selection_option = input("Enter Song ID: ")
            song_actions(userid, selection_option)
        elif song_playlist == '2':
            selection_option = input("Enter Playlist ID: ")
            playlist_action(selection_option, userid)
    elif option_select2 == '2':
        return

def song_actions(userid, selected_song):
    exit = False
    while not exit:
        song_option = input("Press 1 to listen to a song, Press 2 to see more information, Press 3 to add to playlist, Press 4 to exit: ")
        data = (userid,None)
        if song_option == '1':
            cursor.execute('''
                SELECT s.sno FROM sessions s
                WHERE s.uid = ? AND s.end is ?
            ''', data)
            exists = cursor.fetchone()
            data2 = ( selected_song,userid, exists)
            if exists is not None:
                cursor.execute('''
                    SELECT * FROM listen l
                    WHERE l.sid = ? AND l.uid = ? AND l.sno = ?
                ''', data2)
                listening_event_exists = cursor.fetchone()
                if listening_event_exists is not None:
                    cursor.execute('UPDATE listen SET cnt = :new_cnt where sid = :s_sid AND uid = :u_uid AND sno = :s_sno', {'new_cnt': listening_event_exists[3] + 1,'s_sid': selected_song, 'u_uid': userid, 's_sno': exists})
                    connection.commit()
                else:
                    new_event = (userid,exists,selected_song,1)
                    cursor.execute('INSERT into listen VALUES (?,?,?,?)', new_event)
                    connection.commit()
            else:
                print("New session Started")
                startSession(userid)


        elif song_option == '2':
            cursor.execute('''
                SELECT s.sid, s.title, s.duration
                FROM songs s
                WHERE s.sid = :s_sid
            ''', {'s_sid': selected_song})
            song_deets = cursor.fetchall()
            for each in song_deets:
                print(each)
            print("Artists who have performed this song are: ")
            cursor.execute('''
                SELECT a.name
                FROM perform p, artists a
                WHERE p.aid = a.aid AND p.sid = :s_sid 
            ''', {'s_sid': selected_song})
            artists_performed = cursor.fetchall()
            for each in artists_performed:
                print(each)
            print("This song is a part of the following playlists: ")
            cursor.execute('''
                SELECT pl.title
                FROM plinclude p, playlists pl
                WHERE pl.pid = p.pid AND p.sid = :s_sid 
            ''', {'s_sid': selected_song})
            playlists_include = cursor.fetchall()
            for each in playlists_include:
                print(each)

        elif song_option == '3':
            add_selection = input("Press 1 to add song to an existing playlist or 2 to create a new playlist and add to it: ")
            data = (userid,)
            if add_selection == '1':
                cursor.execute('''
                    SELECT * FROM playlists p
                    WHERE p.uid = ?
                ''',data)
                playlist_exists = cursor.fetchall()
                if len(playlist_exists) == 0:
                    print("Sorry there is no existing playlist, try again !")
                elif len(playlist_exists) > 0:
                    for p_list in playlist_exists:
                        print(p_list)
                    p_id = input("Select id for the playlist from the above options: ")
                    cursor.execute('''SELECT max(pl.sorder) FROM plinclude pl WHERE pl.pid = :pl_id''', {'pl_id': p_id})
                    s_order = cursor.fetchone()[0]
                    new_sorder = s_order +1
                    new_playlist_song = (p_id,selected_song,new_sorder)
                    cursor.execute('INSERT into plinclude VALUES (?,?,?)', new_playlist_song)
                    connection.commit()

            elif add_selection == '2':
                playlist_name = input("Enter a title for the playlist: ")

                cursor.execute('''SELECT max(p.pid) FROM playlists p''')
                playlist_id = cursor.fetchone()[0]
                new_pid = playlist_id +1
                new_playlist = (new_pid,playlist_name,userid)
                cursor.execute('INSERT into playlists VALUES (?,?,?)', new_playlist)
                connection.commit()
                new_playlist_song = (new_pid,selected_song,1)
                cursor.execute('INSERT into plinclude VALUES (?,?,?)', new_playlist_song)
                connection.commit()
        elif song_option == '4':
            return

def get_artist_info():

    artist_name = input("Enter the full artist name to select an artist: ")
    cursor.execute('''
        SELECT s.sid, s.title, s.duration
        FROM artists a, songs s, perform p
        WHERE (s.sid = p.sid AND p.aid = a.aid) AND a.name = :aname COLLATE NOCASE
    ''', {'aname': artist_name})
    artist_info = cursor.fetchall()
    for val in artist_info:
        print(val)
    return artist_info

def playlist_action(playlistID, userid):
    print("Playlist contains the following Song")
    cursor.execute('''SELECT s.sid, s.title, s.duration FROM playlists p, songs s, plinclude pl
                    WHERE p.pid = :ppid and (p.pid = pl.pid and pl.sid = s.sid)''', {'ppid': playlistID})
    row = cursor.fetchall()
    for val in row:
        print(val)
    selection_option = input("Press 1 to select a song or 2 to exit: ")
    if selection_option == '1':
        selected_song = input("Enter song Id: ")
        song_actions(userid,selected_song)
    elif selection_option == '2':
        return


def get_song_actions(userid, artist_info):
    data = (userid, None)
    exit = False
    check_song = False
    selected_song = input("Enter song id: ")
    for each in artist_info:
        if each[0] == int(selected_song):
            check_song = True
            break
    if check_song:
        while not exit:
            song_option = input("Press 1 to listen to a song, Press 2 to see more information, Press 3 to add to playlist, Press 4 to exit: ")
            if song_option == '1':
                cursor.execute('''
                    SELECT s.sno FROM sessions s
                    WHERE s.uid = ? AND s.end is ?
                ''', data)
                exists = cursor.fetchone()[0]
                data2 = ( selected_song,userid, exists)
                if exists is not None:
                    cursor.execute('''
                        SELECT * FROM listen l
                        WHERE l.sid = ? AND l.uid = ? AND l.sno = ?
                    ''', data2)
                    listening_event_exists = cursor.fetchone()
                    if listening_event_exists is not None:
                        cursor.execute('UPDATE listen SET cnt = :new_cnt where sid = :s_sid AND uid = :u_uid AND sno = :s_sno', {'new_cnt': listening_event_exists[3] + 1,'s_sid': selected_song, 'u_uid': userid, 's_sno': exists})
                        connection.commit()
                    else:
                        new_event = (userid,exists,selected_song,1)
                        cursor.execute('INSERT into listen VALUES (?,?,?,?)', new_event)
                        connection.commit()
                else:
                    print("New session Started")
                    startSession(userid)


            elif song_option == '2':
                cursor.execute('''
                    SELECT s.sid, s.title, s.duration
                    FROM songs s
                    WHERE s.sid = :s_sid
                ''', {'s_sid': selected_song})
                song_deets = cursor.fetchall()
                for each in song_deets:
                    print(each)
                print("Artists who have performed this song are: ")
                cursor.execute('''
                    SELECT a.name
                    FROM perform p, artists a
                    WHERE p.aid = a.aid AND p.sid = :s_sid 
                ''', {'s_sid': selected_song})
                artists_performed = cursor.fetchall()
                for each in artists_performed:
                    print(each)
                print("This song is a part of the following playlists: ")
                cursor.execute('''
                    SELECT pl.title
                    FROM plinclude p, playlists pl
                    WHERE pl.pid = p.pid AND p.sid = :s_sid 
                ''', {'s_sid': selected_song})
                playlists_include = cursor.fetchall()
                for each in playlists_include:
                    print(each)

            elif song_option == '3':
                add_selection = input("Press 1 to add song to an existing playlist or 2 to create a new playlist and add to it: ")
                data = (userid,)
                if add_selection == '1':
                    cursor.execute('''
                        SELECT * FROM playlists p
                        WHERE p.uid = ?
                    ''',data)
                    playlist_exists = cursor.fetchall()
                    if len(playlist_exists) == 0:
                        print("Sorry there is no existing playlist, try again !")
                    elif len(playlist_exists) > 0:
                        for p_list in playlist_exists:
                            print(p_list)
                        p_id = input("Select id for the playlist from the above options: ")
                        cursor.execute('''SELECT max(pl.sorder) FROM plinclude pl WHERE pl.pid = :pl_id''', {'pl_id': p_id})
                        s_order = cursor.fetchone()[0]
                        new_sorder = s_order +1
                        new_playlist_song = (p_id,selected_song,new_sorder)
                        cursor.execute('INSERT into plinclude VALUES (?,?,?)', new_playlist_song)
                        connection.commit()

                elif add_selection == '2':
                    playlist_name = input("Enter a title for the playlist: ")

                    cursor.execute('''SELECT max(p.pid) FROM playlists p''')
                    playlist_id = cursor.fetchone()[0]
                    new_pid = playlist_id +1
                    new_playlist = (new_pid,playlist_name,userid)
                    cursor.execute('INSERT into playlists VALUES (?,?,?)', new_playlist)
                    connection.commit()
                    new_playlist_song = (new_pid,selected_song,1)
                    cursor.execute('INSERT into plinclude VALUES (?,?,?)', new_playlist_song)
                    connection.commit()
            elif song_option == '4':
                return

    else:
        print("Invalid song id selected, Try again !")
        get_song_actions(userid,artist_info)

def getArtistActions(userid):
    
    exit  = False
    while not exit:
        artistTaskId = input("Select 1 to add a song, select 2 to find top fans and playlists or 3 to logout, 4 to exit: ")
        if artistTaskId == '1':
            addSong(userid)
        elif artistTaskId == '2':
            findTopFansArtists(userid)
        elif artistTaskId == '3':
            print("Logging out")
            main()
        elif artistTaskId == '4':
            exit = True
        else:
            print("Invalid Option Selected")   
       
def addSong(aid):
    entered_title = input("Enter song title to add: ")
    entered_duration = input("Enter song duration: ")
    sid = cursor.execute('''SELECT max(sid) from songs''')
    row = cursor.fetchone()
    sid_val = row[0]+1
    data = (sid_val, entered_title, entered_duration)
    perform_data = (aid, sid_val)
    check_data = (entered_title, entered_duration)

    
    cursor.execute("SELECT * FROM songs WHERE title = ? COLLATE NOCASE AND duration = ?", check_data)
    rows = cursor.fetchone()
    if rows is None:
        cursor.execute('''INSERT  INTO songs (sid, title, duration) VALUES (?, ?, ?);''', data)
        cursor.execute('''INSERT INTO perform (aid, sid) VALUES (?,?);''',
                    perform_data)

        new_artist = input("Any other artist who performs this song? (yes/no) ")
        while (new_artist == "yes"):
            
            new_aid = input("Enter artist id: ")
            new_artist_data = (new_aid, sid_val)
            cursor.execute('''INSERT INTO perform (aid, sid) VALUES (?,?);''',
                            new_artist_data)
            new_artist = input("Any other artist who performs this song? (yes/no) ")
        connection.commit()
    else:
        print("Song already exists in the table")
   

def endSession(sno):
    snumber = sno
    enddate = datetime.now()
    finalenddate = enddate.strftime("%Y-%m-%d %H:%M:%S")
    data = (finalenddate, snumber)
    cursor.execute('UPDATE sessions SET end = ? WHERE sno = ?;', data)
    connection.commit()

def findTopFansArtists(aid):

    cursor.execute('''
        SELECT u.uid, u.name
        FROM users u,  listen l, perform p
        WHERE u.uid = l.uid AND l.sid = p.sid AND p.aid = :artistid
        GROUP BY l.uid
        ORDER BY count(l.cnt) DESC
        LIMIT 3
    ''', {'artistid':aid})

    top_fans = cursor.fetchall()
    
    cursor.execute('''
        SELECT p.pid, p.title
        FROM playlists p, plinclude pl, perform pf
        WHERE p.pid = pl.pid AND pl.sid = pf.sid AND pf.aid = :artistid
        GROUP BY p.pid
        ORDER BY count(pl.sid) DESC
        LIMIT 3
    ''', {'artistid': aid})

    top_playlists = cursor.fetchall()

    print('Top Fans:')
    for fan in top_fans:
        print(fan)
    print('Top Playlists:')
    for playlist in top_playlists:
        print(playlist)    

def main():
    global connection, cursor
    path = "/Users/tanugoyal/Desktop/FALL_2022/CMPUT_291/project1/p1.db"
    #path = input("Enter db path: ")
    connect(path)
    
    userid = input("Enter your userid ")
    password = getpass()
    userNum = 0
    artistNum = 0
    cursor.execute('''
        SELECT Count(uid) FROM users u
        WHERE uid = :uname COLLATE NOCASE AND pwd = :pw
    ''', {'uname': userid, 'pw': password},)

    numUsers = cursor.fetchone()
    cursor.execute('''
        SELECT Count(aid) FROM artists a
        WHERE aid = :uname COLLATE NOCASE AND pwd = :pw
    ''', {'uname': userid, 'pw': password},)
    numArtists = cursor.fetchone()

    if numUsers[0] == 0 and numArtists[0] == 0:
        cursor.execute('''SELECT u.pwd FROM users u WHERE u.uid = :u_id COLLATE NOCASE''',{'u_id': userid})
        checkuser = cursor.fetchone()
        cursor.execute('''SELECT a.pwd FROM artists a WHERE a.aid = :a_aid COLLATE NOCASE''', {'a_aid': userid})
        checkartist = cursor.fetchone()
        if checkuser is None and checkartist is None:
            newusername = input("Enter username: ")
            new_password = getpass()
            data = (userid, newusername, new_password)
            cursor.execute("INSERT INTO users VALUES (?,?,?)", data)
            connection.commit()
            userNum = 1
            artistNum = 0
        elif checkuser is not None:
            if password !=  checkuser[0]:
                print("Incorrect password Entered, Try Again")
                main()
        elif checkartist is not None:
            if password !=  checkartist[0]:
                print("Incorrect password Entered, Try Again")
                main()          

    elif numUsers[0] == 1 and numArtists[0] == 1:
        usertype = input("Press U for user or A for artist: ")
        if usertype == 'U':
            userNum = 1
        elif usertype == 'A':
            artistNum = 0

    elif numUsers[0] == 1 and numArtists[0]== 0:
        userNum = 1
    elif numUsers[0] == 0 and numArtists[0]== 1:
        artistNum = 1
    
    if userNum == 1 and artistNum == 0:
        getUserActions(userid)
    elif artistNum == 1 and userNum == 0:
        getArtistActions(userid)
         
    connection.close()
    return

if __name__ == "__main__":
    main()



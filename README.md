# MusicSystemSQL

This project has been coded using python and provides an extensive implementation of
an interactive music application. The program begins by logging the user or artist into
the application. To make the code readable and efficient, we have used structural programming and created several functions each of which are called throughout the program as required.
"USER GUIDE"
The user (user or artist) is prompted to enter the username and password (ie perform login activity) and is then shown a list of all options available to them based on their account type: ie users can start a session, search for songs and playlists, search for artists and end the session while artists can add a song and find top fans and playlists. The program outputs options to choose from which can be selected using hints given in the form of prompts for example "Press 1 to listen to a song, Press 2 to see more information or Press 3 to add to playlist"
Within the specific user and artist menus, the user can navigate to any of the available options using numbers (each attributing to a different selection) as outputted in the prompt. Once a user is finished with their work on the application, they can either logout - which would allow another user to log in or exit from the application which works primarily as a shut down.
Please find a basic flowchart for this application at the end of this document. (page 4)
"MAIN FUNCTIONS"
1. getArtistActions and getUserActions
These two functions are only used to navigate through the program. They prompt the user to select one of the available options based on their account type (artist or user) and call the relevant functions as appropriate
2. startSession(uid)
If the user selects "start a session", the program creates a new row in the sessions table with the user id entered during login, current date/time as the start_date and end_date as null.
3. search()
The search function is implemented to handle the user request to search for a song or playlist. The function uses the keywords entered by the user to find the closest matching playlists and songs. This list is then listed in a paginated form with each line mentioning whether it is a song or a playlist. From here, the user also has the option to choose any particular song by entering the song id (listed from the search) or a playlist by entering the playlist id. On selecting a playlist, all songs within that playlist are displayed and the user can now select any song using the song id. This leads the user to a new menu where they can perform multiple song actions.
1
4. searchArtist()
The user can also search for artists using the keywords to list all the songs with matching keywordsinorderoftheclosestmatch.Thisstillliststhesongsintheformor pages with each page containing 5 closest song matches. The user can then also navigate to the song menu and perform song actions by selected a song
5. endsession(sno)
To end a session, the user can select 4 and that will add a date to the originally null end_date column in the sessions table.
6. addSong(aid)
This function implements the functionality that allows the artist to enter a new song using their initially entered aid at the time of login. To add a song, the program checks if the song exists and then creates a new row in the songs table and performs table if needed. It also prompts the user to mention if any other artists have performed the same song.
7. findtopFansandPlaylists()
This function is called when the artist selects option 2 from their menu. It finds the top fans and playlists based on the number of times users have listened to their songs
8. songactions()
This function uses if--else statements to input the user's choice among listening to a song, getting more information or adding the song to any playlist. It then directs the application to the appropriate function

import os

avatars = os.listdir('static/images')

def testt():
    playersqlid = 1
    avatarFound = False
    for avatar in avatars:
        a,b = avatar.split(".")
        if int(a) == int(playersqlid):
            print(avatar)
            avatarFound = True
            break
    if avatarFound == False:
        print('false')
        

testt()

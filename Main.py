import random
import time
import os
witch_good=True
witch_bad=True
with open("log.txt","w") as log:
    log.write("Game start. "+time.strftime("%Y-%m-%d %H:%M:%S")+'\n')
def werewolf():
    with open("log.txt","a") as log:
        global player,tonight_died
        if("Werewolf" in player):
            time.sleep(3)
            killed_player=int(input('Who are you going to kill?(use serial number)'))
            while killed_player<1 or killed_player>6:
                killed_player=int(input("Please type again."))
            log.write("Player "+str(killed_player)+" was killed by the Werewolves.\n")
            os.system("cls")
            tonight_died.append(killed_player)
            time.sleep(3)
            if(player.count("Werewolf")==2):
                killed_player = int(input('Who are you going to kill?(use serial number)'))
                while killed_player < 1 or killed_player > 6:
                    killed_player = int(input("Please type again."))
                log.write("Player " + str(killed_player) + " was killed by the Werewolves.\n")
                os.system("cls")
                tonight_died.append(killed_player)
                time.sleep(3)
def witch():
    global player
    if("Witch" in player):
        time.sleep(3)
        with open("log.txt","a") as log:
            global witch_good,witch_bad
            print("This night, Player"+str(tonight_died[0])+" and Player"+str(tonight_died[1])+" was killed.")
            if witch_good:
                a=input("Do you want to use the good potion? y/n ")
                while a!="y" and a!="n":
                    a=input("Please type again. ")
                if a=="y":
                    a=int(input("Which player do you want to save?(use serial number) "))
                    while a < 1 or a > 6 or a not in tonight_died:
                        a=input("Please type again. ")
                    tonight_died.remove(a)
                    log.write("Player"+str(a)+" was saved by the Witch. \n")
                    witch_good=False
            if witch_bad:
                a=input("Do you want to use the another potion? y/n ")
                while a != "y" and a != "n":
                    a = input("Please type again. ")
                if a == "y":
                    a = int(input("Which player do you want to kill?(use serial number) "))
                    while a < 1 or a > 6 or a in tonight_died:
                        a = input("Please type again.")
                    tonight_died.append(a)
                    log.write("Player" + str(a) + " was killed by the Witch. \n")
                    witch_bad=False
            os.system("cls")
def prophet():
    global player
    if("Prophet" in player):
        time.sleep(3)
        with open("log.txt", "a") as log:
            a = int(input("Who will you prophesy about?(use serial number) "))
            while a < 1 or a > 6:
                a = int(input("Please type again. "))
            print(player[a - 1])
            log.write("Player" + str(a) + " was prophesyed by the Prophet.\n")
            time.sleep(3)
            os.system("cls")
def vote():
    votes=[0,0,0,0,0,0]
    with open("log.txt","a") as log:
        i=0
        while i<6:
            if player[i]!='':
                a=int(input("Who will you vote for?(use serial number) "))
                while a < 1 or a > 6 or player[a-1]=='':
                    a = int(input("Please type again. " ))
                votes[a-1]+=1
            os.system("cls")
            time.sleep(3)
            i+=1
        player[votes.index(max(votes))]=''
        died.append(votes.index(max(votes)))
        print("Player"+str(votes.index(max(votes)))+" was out.")
        log.write("Player"+str(votes.index(max(votes)))+" was out.\n")
player=[]
died=[]
character=["Civilian",'Civilian','Werewolf','Werewolf','Witch','Prophet']
i=0
n=0
with open("log.txt","a") as log:
    while i<6:
        n=character.pop(random.randint(0,len(character)-1))
        player.append(n)
        print("Player"+str(i+1)+", you\'re "+player[i]+'.')
        log.write("Player"+str(i+1)+" is "+player[i]+'.\n')
        time.sleep(3)
        os.system("cls")
        time.sleep(3)
        i += 1
while ("Civilian" in player) and ("Werewolf" in player) and (("Witch" in player) or ("Prophet" in player)) :
    tonight_died = []
    werewolf()
    witch()
    prophet()
    died.append(tonight_died)
    for i in tonight_died:
        print("Tonight, Player"+str(i-1)+" was killed.")
        player[i-1]=''
    vote()
with open("log.txt","a") as log:
    if(("Civilian" not in player) or (("Witch" not in player) or ("Prophet" not in player))):
        print("The Werewolves is win.")
        log.write("The Werewolves is win.")
    else:
        print("The Civilians is win.")
        log.write("The Civilians is win.")
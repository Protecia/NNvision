# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""
import random
import sys
from threading import Thread, Lock, Event
import time

verrou = Lock()


class Afficheur(Thread):

    """Thread chargé simplement d'afficher un mot dans la console."""

    def __init__(self, mot, event_list, cam_id, nb_cam,sleep):
        Thread.__init__(self)
        self.mot = mot
        self.event_list = event_list
        self.cam_id = cam_id
        self.nb_cam = nb_cam
        self.sleep = sleep 


    def run(self):
        """Code à exécuter pendant l'exécution du thread."""
        i = 0
        time.sleep(self.sleep)
        while i < 5:
            self.event_list[self.cam_id].wait()
            #print('cam {} alive'.format(self.cam_id))
            self.event_list[(self.cam_id-1)%self.nb_cam].clear()
            #print('cam {} clear\n'.format((self.cam_id-1)%self.nb_cam))
            
            with verrou:
                for lettre in self.mot:
                    sys.stdout.write(lettre)
                    sys.stdout.flush()
                    attente = 0.1
                    attente += random.randint(1, 10) / 200
                    time.sleep(attente)
            
            for j in range(self.nb_cam):
                self.event_list[((self.cam_id)+1+j)%self.nb_cam].set()
                time.sleep(0.02)
                #print('cam {} set\n'.format((self.cam_id+1+j)%self.nb_cam))
                if not self.event_list[self.cam_id].isSet(): break
            
        
                
                
                
                
                
                
            
            i += 1
            

# Création des threads
nb_cam =3
thread_list = []

#for i in nb_cam:
#    thread_list.append([Event(),Afficheur()])
    
event_list = [Event(),Event(),Event()] 

thread_1 = Afficheur("canard", event_list,0,3,0)

thread_2 = Afficheur("TORTUE", event_list,1,3,5)

thread_3 = Afficheur("*****", event_list,2,3,2)


# Lancement des threads
thread_1.start()
thread_2.start()
thread_3.start()


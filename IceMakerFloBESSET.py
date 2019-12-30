# coding: utf-8
#!/usr/bin/env python

#voici le programme de gestion de ma machine à glacons DIY
# cette machine fait automatiquement des glacons en utilisant l'eau du reseau domestique 
# elle a un bac amovible qui récupère les glacons et qui est accessible via une porte 
# elle dispose d'un bac de récuperation d'eau usée qui est automatiquement vidangé vers l'évacuation d'eau domestique comme pour une machine à laver
# elle dispose d'un bac d'eau fraiche qui est raffraichie par un module peltier et qui est automatiquement remplie via l'arrivée d'eau du reseau domestique 
# le materiel utilisé pour faire les glacons est le matériel présent dans uen machine à glacons pour particulers (compresseur, condenseur, evaporateur)
# le bac dans lequel se forment les glacons est fixé sur un moteur synchrone qui le fait pivoter dans un sens ou dans un autre
# le moteur syncrone est fait pour tourner dans un sens unique mais celui-ci part dans l'autre sens si au demmarage il est bloqué
# des contacteurs de fin de courses sont en places pour qu'on connaisse la position du bac 
# il y a une sonde de temperature au dessus du bac qui permets de verifier si celui-ci est plein car lorsque les glacons arrivent à son niveau, il indiquera une temperature de 0 degrés


# importation des librairies 
import RPi.GPIO as GPIO
import threading
import time
import board
import Adafruit_DHT as dht

moteur = 2 #relais1
electrovanne_arrivee_eau = 3 #relais2
compresseur = 4 #relais3
ventilateur = 5 #relais4
electrovanne_gaz_chaud = 6 #relais5 
pompe_evacuation_eau = 7 #relais6
electrovanne_distributeur_eau = 8 #relais7
pompe_distributeur_eau = 9 #relais8

#declaration des gpios des contacteurs ou capteurs
contacteur_moteur_1 = 10
contacteur_moteur_2 = 11
contacteur_bac_glacons = 12
debitmetre = 13
bouton_start_stop = 14
ledR = 15
ledG = 16
ledB = 17
bouton_distributeur_eau = 18
capteur_niveau_eau = 19
capteur_temperature = 20

compteur_cycle = 0 # incrementation a chaque cycle de fabrique de glacons
valeur_contacteurs_moteur = 0 # defini quel contacteur est enclenche
contact1 = 1 #contacteur 1 enclenché
contact2 = 1 #contacteur 2 enclenché 
start = 0 #variable utilisée pour le demmarrage ou l'arret des cycles
stop = 1 #variable utilisée pour le demmarrage ou l'arret des cycles
nombre_distribution_eau = 0 # incremantation a chaque service d'eau fraiche et remise à 0 au bout de 60 et vidange du bac de recup d'eau


# definition des types de GPIO entrees ou sorties
GPIO.setwarnings(False) # on desactive les erreur si le GPIO est utilise
GPIO.setmode(GPIO.BCM) # on utilise le numero de GPIO et pas le numero de la broche
GPIO.setup(moteur, GPIO.OUT) # OUT car on envoi un information au relais
GPIO.output(moteur, GPIO.HIGH) # par defaut le relais est ferme donc eteint
GPIO.setup(electrovanne_arrivee_eau, GPIO.OUT)
GPIO.output(electrovanne_arrivee_eau, GPIO.HIGH)
GPIO.setup(compresseur, GPIO.OUT)
GPIO.output(compresseur, GPIO.HIGH)
GPIO.setup(ventilateur, GPIO.OUT)
GPIO.output(ventilateur, GPIO.HIGH)
GPIO.setup(electrovanne_gaz_chaud, GPIO.OUT)
GPIO.output(electrovanne_gaz_chaud, GPIO.HIGH)
GPIO.setup(pompe_evacuation_eau, GPIO.OUT)
GPIO.output(pompe_evacuation_eau, GPIO.HIGH)
GPIO.setup(contacteur_moteur_1, GPIO.IN, pull_up_down = GPIO.PUD_UP) #bouton pressoir
GPIO.setup(contacteur_moteur_2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(contacteur_bac_glacons, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(debitmetre, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(bouton_start_stop, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ledR, GPIO.OUT)
GPIO.output(ledR, GPIO.LOW)
GPIO.setup(ledG, GPIO.OUT)
GPIO.output(ledG, GPIO.LOW)
GPIO.setup(ledB, GPIO.OUT)
GPIO.output(ledB, GPIO.LOW)
GPIO.setup(bouton_distributeur_eau, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(capteur_niveau_eau, GPIO.IN)
GPIO.setup(pompe_distributeur_eau, GPIO.OUT)
GPIO.output(pompe_distributeur_eau, GPIO.HIGH)
GPIO.setup(electrovanne_distributeur_eau, GPIO.OUT)
GPIO.setup(electrovanne_distributeur_eau, GPIO.HIGH)

def led_blanche_ON(): #allumage de toutes les couleurs de la leg RGB pour eclairer le verre en blanc lors du service d'eau fraiche
      GPIO.output(ledR, GPIO.HIGH) # on allume la led rouge
      GPIO.output(ledG, GPIO.HIGH) # on allume la led verte
      GPIO.output(ledB, GPIO.HIGH) # on allume la led bleue

def led_blanche_OFF(): #extinction de toutes les couleurs de la leg RGB pour eclairer le verre en blanc lors du service d'eau fraiche
      GPIO.output(ledR, GPIO.LOW) # on eteint la led rouge
      GPIO.output(ledG, GPIO.LOW)  # on eteint la led verte
      GPIO.output(ledB, GPIO.LOW)  # on eteint la led bleue

       


def valeur_contacteurs(): # on donne la position du bac 
      global valeur_contacteurs_moteur
      global contact1
      global contact2
      while True:
          contact1 = GPIO.input(contacteur_moteur_1) #contacteur 1 enclenché ou non
          contact2 = GPIO.input(contacteur_moteur_2) #contacteur 2 enclenché ou non         
          if contact1 == 0:
              valeur_contacteurs_moteur = 1 # le contacteur 1 est enclenché
          elif contact2 == 0:
              valeur_contacteurs_moteur = 2 # le contacteur 2 est enclenché
          else:
              valeur_contacteurs_moteur = 0 # le moteur est en mouvement

def demarrer(objet): #commande pour demmarer un organe electrique
      GPIO.output(objet, GPIO.LOW)

def arreter(objet): #commande pour arreter un organe electrique
      GPIO.output(objet, GPIO.HIGH)
             
def debit_metre(): #lors de la vidange du bac de recuperation d'eau, cette vanne va verifier quand il y n'y a plus d'eau dans le bac pour arreter la pompe
      while True:
          valeur = 0
          capteur = GPIO.input(debitmetre)
          if capteur == 0:
              valeur = 1  #il y a de l'eau qui passe dedans
          elif capteur == 1:
              valeur = 0  # il n'y a plus d'eau
          return valeur

def vidange(): # on vidange le bac de recuperation d'eau usée
      presence_eau = 1
      demarrer(pompe_evacuation_eau)
      while presence_eau == 1: 
          presence_eau = debit_metre() # tant qu'il y a de l'eau on pompe et on arrete dès qu'il n'y a plus d'eau
      arreter(pompe_evacuation_eau)

def vidange_auto(): # tous les 60 services d'eau fraiche, on vide le bac de récuperation d'eau usée (si on tombe de l'eau a coté du verre) pour eviter que l'eau stagne
      global nombre_distribution_eau
      while True:
          if nombre_distribution_eau = 60 :
              vidange()
              nombre_distribution_eau = 0 # on remets le compteur à 0 
                   
                  
def start_stop(): # verification du bouton de marche / arret
      global start
      global stop
      allume = 0
      GPIO.remove_event_detect(bouton_start_stop)
      GPIO.add_event_detect(bouton_start_stop, GPIO.BOTH)
      while True:
          
          if GPIO.event_detected(bouton_start_stop): # lorsque la machine est eteinte, si on appuie sur le bouton, on demarrer le cycle
              if start == 0:
                  start = 1
                  stop = 0
                  allume = 1
              elif start == 1: # si elle est allumée, si on appuie sur le bouton, on l'éteint.
                 start = 0
                 stop = 1
                 allume = 0
          return allume

def distributeur(): # distributeur d'eau fraiche, si on appuie sur le bouton avec le verre, la pompe recupere l'eau fraiche et l'envoie dans le verre d'eau tant qu'on reste appuyé sur le bouton
      while True:
          arreter(pompe_distributeur_eau) #par defaut la pompe est eteinte
          led_blanche_OFF() # la led aussi
          
          bouton = GPIO.input(bouton_distributeur_eau)
          
          while bouton == 0:
              demarrer(pompe_distributeur_eau) #on appuie sur le bouton, on demarre la pompe pour remplir le verre
              led_blanche_ON() # on allume toutes les leds pour eclairer le verre en blanc pour voir le niveau d'eau dans le verre
              bouton = GPIO.input(bouton_distributeur_eau) #on remplit tant que le bouton n'est pas relaché
              nombre_distribution_eau = nombre_distribution_eau + 1 #on alimente le compteur de service pour que la vidange du bac de recup d'eau usée se fasse au bout de 60 services
              
def ouverture_bac(): #a modifier lors du montage final (valeurs inversées pour les tests et leds à inverser egalement)
      bac = 0
      valeur = 0 # une fois la machine montée, ce bouton sera tout le temps enclenché par la porte qui donne accès au bac de glacons
      # lorsque la porte est ouverte, celà bloquera la verse des glacons dans le bac au cas où on ait retiré le bac pour récuperer les glacons
      while True:
          bac = GPIO.input(contacteur_bac_glacons)
          
          if bac == 1: #pour pouvoir faire mes tests j'ai inversé les valeurs pour qu'on ait pas à laisser le bouton enclenché 
              
              
              valeur = 1
              
          elif bac == 0:
              valeur = 0
              
                            
          return valeur

def remplissage_auto_bac_eau(): #lorsque on va se servir de l'eau fraiche, cette fonction va remplir automatiquement le bac d'eau quand son niveau est dessendu en dessous d'un capteur
    while True:
          eau = GPIO.input(capteur_niveau_eau)
          arreter(electrovanne_distributeur_eau) #de base l'electrovanne de remplissage est fermée
          while eau == 1 #valeur a inverser une fois le bac d'eau est en place pour que dès que le niveau d'eau est dessendu en dessous du capteur, on remplisse à nouveau le bac d'eau
              demarrer(electrovanne_distributeur_eau) 
              eau = GPIO.input(capteur_niveau_eau)
              
def temperature(): #cette sonde de temperature sera au dessus du bac des glacons et va calculer la temperature 0 quand le bac sera rempli de glacons
# en effet lorsque le bac va se remplir, quand les glacons seront assez proche du capteur, il va capter une temperature de 0 degrés donc on va mettre en pause la production de glacons
      while True:
          h,t = dht.read_retry(dht.DHT22, capteur_temperature)
          temp = t
          return temp

def pause():  # cette pause se base sur la fonction du dessus et va mettre en pause la fabrication de glacons si le bac est plein 
      demarrer(moteur)
      while valeur_contacteurs_moteur == 0:
          break
      arreter(moteur)
      demmarer(electrovanne_gaz_chaud)
      time.sleep(10)
      arreter(electrovanne_gaz_chaud) # on vide les derniers glacons avant la pause
      while ouverture_bac() == 1: #si la porte du bac a glacons est ouverte on fait une pause pour pas vider les glacons dans le vide si on a recuperé le bac
      demarrer(moteur)
      while valeur_contacteurs_moteur == 0:
          break
      arreter(moteur) # on a remis le moteur en position 1
      arreter(compresseur) # on arrete le compresseur et le ventilateur
      arreter(ventilateur)      
                

          
          
              
def premier_menu():
      while True: #boucle sans fin
          initialisation() #fonction qui remets le moteur sur le bon contacteur
          lancement_programme() #lancement du programme machine a glacons

def initialisation() : #on va si besoin replacer moteur a la position initiale 1
      global valeur_contacteurs_moteur #on appelle la variable necessaire
      if valeur_contacteurs_moteur == 0: #la position du moteur est perdue
          demarrer(moteur) # on demarre le moteur
          if valeur_contacteurs_moteur == 1: #contacteur 1 atteint
              arreter(moteur) #on arrete le moteur
              return;
          elif valeur_contacteurs_moteur == 2: #contacteur 2 atteint
              arreter(moteur) #on arrete le moteur
              time.sleep(2) #on fait une pause de 2 secondes 
              demarrer(moteur) #on relance le moteur
              while valeur_contacteurs_moteur == 0:
                  break
              # dans la ligne du dessus on attends le declenchement du contacteur 1
              arreter(moteur) # contact 1 atteint on arrete le moteur
              return; #on retourne au premier menu
      elif valeur_contacteurs_moteur = 2: #on est pas au bon contacteur
          demarrer(moteur) # on demarre le moteur
          while valeur_contacteurs_moteur == 0:
                  break
          # dans la ligne du dessus on attends le declenchement du contacteur 1
          arreter(moteur) #on arrete le moteur
          return; #on retourne au premier menu
      elif valeurs_contacteurs_moteur = 1: #on est au bon contacteur
          return; #on retourne au premier menu 


def arret_machine(): #cette fonction se declanchera quand on appuyera sur le bouton ON/OFF pour arrêter la machine qui est en route
      global valeur_contacteurs_moteur #on declare les variables dont on a besoin
        
      if valeur_contacteurs_moteur == 0: #moteur en mouvement
          demarrer(moteur) #on demarrer le moteur meme si il est déja démarré
          while valeur_contacteurs_moteur == 0:
              break
          arreter(moteur)    
          if valeur_contacteurs_moteur == 1:
              time.sleep(1)
              demarrer(moteur)
              while valeur_contacteurs_moteur == 0:
                  break
              arreter(moteur)
              demarrer(electrovanne_gaz_chaud) # on vide les derniers glacons au cas où ils avaient commencé à se former 
              time.sleep(10)
              arreter(electrovanne_gaz_chaud)
              while ouverture_bac() == 1: #on verifie que le bac soit bien en place avant de vider les glacons
                  break
              demmarer(moteur)
              while valeur_contacteurs_moteur == 0:
                  break
              arreter(moteur)
      elif valeur_contacteurs_moteur == 1 : #si le contacteur 1 est activé
          time.sleep(1)
          demarrer(moteur)
          while valeur_contacteurs_moteur == 0:
              break
          arreter(moteur)
          demarrer(electrovanne_gaz_chaud)
          time.sleep(10)
          arreter(electrovanne_gaz_chaud)
          while ouverture_bac() == 1:
              break
          demmarer(moteur)
          while valeur_contacteurs_moteur == 0:
              break
          arreter(moteur)
      elif valeur_contacteurs_moteur == 2 : #si le contacteur 2 est active
          demarrer(electrovanne_gaz_chaud)
          time.sleep(10)
          arreter(electrovanne_gaz_chaud)
          while ouverture_bac() == 1:
              break
          demmarer(moteur)
          while valeur_contacteurs_moteur == 0:
              break
          arreter(moteur) #on eteint le moteur
      arreter(compresseur) #on arrete le compresseur
      arreter(ventilateur) #on arrete le ventilateur
      vidange()
      lancement_programme()


def lancement_programme(): # application generale
      while start_stop() == 0:
          break      #on attend le demarrage 
      fabrique() #bouton start a ete appuye on lance la fabrication des glacons
      arret_machine() #le bouton stop a ete appuye on arrête la fabrication
      return; #on retourne donc dans la boucle sans fin qui va revenir ici

    
      
def fabrique():  # cycle fabrication des glacons
      global valeur_contacteurs_moteur #on appelle la variable necessaire
      global compteur_cycle # variable qui definie le nombre de cycles de glaçons realisé
      while start_stop() == 1:  #tant qu'on appuie pas sur le bouton stop, la machine fonctionne
          while valeur_contacteurs_moteur != 1:
              break
          arreter(moteur) # on eteint le moteur meme si il est logiquement eteint
          compteur_cycle = compteur_cycle + 1 # on incremente le nombre de cycle de fabrication
          demarrer(electrovanne_arrivee_eau) #on ouvre l'electrovanne d'eau pour remplir le bac
          time.sleep(5) #on laisse couler pendant 5 secondes
          arreter(electrovanne_arrivee_eau) #on ferme l'electrovanne
          demarrer(electrovanne_arrivee_eau) #on demarre le compresseur
          demarrer(ventilateur) # on demarre le ventilo
          if compteur_cycle <= 1:  #si on est au premier cycle
              time.sleep(900) # on laisse tourner le compresseur pendant 15 min car il faut le temps que çà refroidisse
          else:
              time.sleep(720) # quand on passe au deuxième cycle, on raccourcit et on laisse 12 minutes
          if temperature() <= 0:
              while temperature() <= 0 :
               #si le bac est plein on mets en pause la fabrique en utilisant la fonction pause
           
                  pause()
                  break
              GPIO.output(ledG, GPIO.LOW)
            
          else:
              demarrer(moteur) #on demarre le moteur pour faire tourner le bac car les glacons sont formés
              while valeur_contacteurs_moteur == 0:
                  break          #on attends de toucher le contacteur 2
              arreter(moteur) # on eteint le moteur
              demarrer(electrovanne_gaz_chaud) #on ouvre l'electrovanne de gaz chaud qui va degivrer l'evaporateur et liberer les glacons
              time.sleep(10) #on laisse ouvert la vanne pendant 10 secondes
              arreter(electrovanne_gaz_chaud) #on ferme l'electrovanne de gaz chaud, les glacons sont tombés
              while ouverture_bac() == 1: #si le contacteur de bac n'est pas enfonce c'est que le recipient à glacons est ouvert alors on fait une pause pour pas que les glacons tombent dans le vide
                  break
              demarrer(moteur) #on demarre le moteur pour qu'il remette le bac à l'horizontale pour refaire des glacons et qu'il balance les glacons dans le recipient à glacons.
          
      return; #on est sorti de la boucle car on a appuyé sur stop donc on revient au menu precedent.



if __name__ == '__main__':     # Demarrage du programme  
      
      premier_menu() # on lance le menu principale qui lancera les fonctions dans l'ordre souhaité
      threading.Thread(target=valeur_contacteurs).start() #les thread sont des fonctions qui tournent en tache de fond en permanence
      threading.Thread(target=distributeur).start() #les thread sont des fonctions qui tournent en tache de fond en permanence
      threading.Thread(target=start_stop).start() #les thread sont des fonctions qui tournent en tache de fond en permanence
      threading.Thread(target=vidange_auto).start() #les thread sont des fonctions qui tournent en tache de fond en permanence
      threading.Thread(target=ouverture_bac).start() #les thread sont des fonctions qui tournent en tache de fond en permanence
      threading.Thread(target=remplissage_auto_bac_eau).start() #les thread sont des fonctions qui tournent en tache de fond en permanence
      threading.Thread(target=temperature).start() #les thread sont des fonctions qui tournent en tache de fond en permanence
      treadind.Thread(target=detecteur).start() # S'il existe un obstacle au cours de son processus 


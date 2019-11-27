                              [[[PROJET MACHINE A GLACONS / DISTRIBUTEUR D'EAU FRAICHE]]]

Bonjour à tous,

je travaille acutellement sur un projet d'une machine à glacons DIY avec un distributeur d'eau fraiche.
La machine est reliée à l'arrivée d'eau et l'evacuation d'eau domestique (comme pour une machine à laver ou un lave vaisselle)
La partie electronique sera gérée par un raspberry pi avec une carte relais qui pilotera tous les organes électriques et récupèrera les 
valeurs de divers capteurs.

1) DISTRIBUTEUR D'EAU FRAICHE

La machine dispose d'un bac de 3 litres remplie automatiquement par une electrovanne qui réceptionne l'eau du reseau domestique
Il y a un capteur de presence d'eau fixé sur le bac qui envoi l'info à l'electrovanne quand le niveau d'eau descends en dessous de celui-ci
Pour se servir de l'eau fraiche, il y a une ouverture dans la machine où on place le verre dedans et lorsqu'on appuie sur un bouton avec le 
verre, ca enclenche une pompe qui récupère l'eau du bac et l'envoi dans le verre via un tuyeau.
Il y aussi une led RGB qui s'allume en blanc et éclaire le verre
L'eau du bac est raffraichie par une module peltier (utilisée dans les glacières electriques par exemple) 

2) FABRICATION DES GLACONS

le matériel utilisé est celui présent dans une machine à glacons classique (un condensateur, un compresseur, un ventilateur, un evaporateur,
une electrovanne pour libérer des gaz chaud
Je vous décrit un cycle de creation de glacons :
  1- Un bac pivotant grâce à un moteur syncrone se mets en position sous l'evaporateur (pour rappel, un evaporateur de machine à glacons se
  composent de tiges autour desquelles le glacons va se former car les tiges atteignent la temperature de -16 degrés)
  2- le bac pivotant se remplit d'eau grâce à l'electrovanne qui récupère l'eau du reseau domestique 
  si le bac deborde, elle va dans un bac de récuperation d'eau qui sera vidangé automatiquement
  3- le compresseur, le condenseur et un ventilateur se mettent en route et vont former les glacons autour des tiges de l'evaporateur
  4- au bout d'un certain temps (15 min pour le premier cycle et 12 pour les autres) le bac pivote a nouveau et va faire tombeau le surplus
  d'eau et les glacons restent accrochés au tiges de l'evaporateur
  5- l'electrovanne gaz chaud s'ouvre et libère du gaz chaud qui va aller jusqu'aux tiges de l'evaporateur pour degivrer et faire tomber les 
  glacons 
  6- le bac repivote et une plage fixée au bac va entrainer les glacons pour les faire tomber dans un bac où on peut les récuperer
  7- à partir de ce moment là on refait un cycle et on en fait le nombre qu'il faut jusqu'à que le bac des glacons soit plein
  
 3) BAC DE GLACONS
 
 Le bac de glaçons est amovible et accessible via une porte d'accès qui contient un capteur (si celle-ci est ouverte, on mets en pause 
 pour eviter de faire tomber les glacons si le bac n'est pas présent
 Une sonde de temperature est positionnée au dessus du bac et si celle-ci atteinds 0 degrés, on mets en pause la fabrication car celà veut
 dire que le bac est rempli de glacons (les glaçons sont proches du capteur donc celui-ci relève une temperature de 0 degrés minimum)
 
 4) BAC RECUPERATION EAUX USEES
 
 Tout le surplus d'eau est récupéré dans ce bac qui est vidangé automatiquement pour pas que l'eau stagne
 Lorsqu'on arrete la fabrication des glacons celui-ci se vidange 
 A l'emplacement où on remplit le verre d'eau, en dessous, il y a aussi un tuyeau qui ramene l'eau qu'on peut renverser avec le verre dans 
 ce bac pour qu'elle soit aussi vidangée (au bout de 60 service d'eau, on vidange le bac de recuperation d'eaux usées)
 Pour vidanger, on a une pompe qui est relié à un tuyeau qui va vers l'evacuation de la maison et il y a aussi un debimetre qui va arrêter
 la pompe lorsqu'il n'y a plus d'eau qui passe dans le tuyeau (le bac est vide) pour eviter de la faire forcer dans le vide.

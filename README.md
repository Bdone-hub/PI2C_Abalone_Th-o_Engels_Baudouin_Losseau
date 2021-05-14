Engels Théo 195367 
Losseau Baudouin 195093

Pour lancer l'Ia il faut mettre dans la ligne de commande le port suivi du nom de l'ia, sinon le port et le nom par defaut son utilisé (5214 et 'l'IA super intelligente de Baudouin et Théo')           exemple: py /chemin/projet/abalone 4500 Paul

Stratégie de l'IA:

Recherche du "meilleur move" par la méthode de la version cache de la méthode negamax limitée en temps

La statégie utilisée est: 

	-rester en bloc et au centre du plateau (de moins en moins important au fur et à mesure que la partie avance).
	-empêcher les adversaire d'etre en bloc et au centre du plateau (de moins en moins important au fur et à mesure que la partie avance).
	-Éviter de ce faire tuer.
	-Avoir plus de billes que l'adversaire.
	-Apres 100 rounds, le 'centre' visé bouge aleatoirement au case adjacente au vrai centre du plateau et ce, tout les 10 tours (pour eviter de boucler).
	-Éviter au maximum de perdre une cinqueme bille.
	-Essayer au maximum de tué une cinquime bille à l'adversaire.

Bibliothèques nécessaires:

	socket, pour etablir la liaison TCP avec le serveur.
	json, pour transcrire la requete du serveur qui est en format json en python.
	jsonNetwork, import de fonction pour recevoir la requete du serveur  (fichier fournis par Monsieur Lurkin).                              
	choice in random, pour envoyer des messages de facon aléatoire dans une liste et pour modifier la position centrale visée par les billes. 
	defaultdict in collections, pour créer un dictionnaire avec zero comme valeur si la clef est non utilisée. 
	time, pour calculer le temps pris par la fonction recursive et la stopper afin de rester dans le temps imparti. 
	copy, pour copier des dictionnaires et pouvoir les modifier sans modifier l'original. 
	numpy, pour faire des calculs de matrice de facon plus efficace. 
	sys, pour recuper les parametres donné dans le terminal. 


Engels Théo 195367 
Losseau Baudouin 195093

Pour lancer l'Ia il faut mettre dans la ligne de commande le port suivi du nom de l'ia, sinon le port est 5214 par défault           exemple: py /chemin/projet/abalone 4500 Paul

Stratégie de l'IA:

Recherche du "meilleur move" par la méthode de la version cache de la méthode negamax limitée en temps

Le score associé à chaque état vise à :

	-Prendre possession du centre (poids donné diminue lors de l'avancement de la partie)
	
	-Rester en bloc
	
	-Kill dès que l'on a l'occasion

Bibliothèques nécessaires:

	socket, pour etablir la liaison TCP avec le serveur
	threading pour gerer à la fois les demandes de pings et les requetes de jeux en meme temps
	json, pour transcrire la requete du serveur qui est en format json en python.
	jsonNetwork, import de fonction pour recevoir la requete du serveur                                
	choice in random, pour envoyer des messages de facon aléatoire dans une liste et pour modifier la position centrale visée par les billes ( pts 1 de la stratégie). 
	defaultdict in collections, pour créer un dictionnaire avec zero comme valeur si la clef est non utilisée 
	time, pour calculer le temps pris par la fonction recursive et la stopper afin de rester dans le temps imparti 
	copy, pour copier des dictionnaires et pouvoir les modifier sans modifier l'original 
	numpy, pour faire des calculs de matrice de facon plus efficace 
	sys, pour recuper les parametres donné dans le terminal 


import socket
import json
import sys
import jsonNetwork
from random import choice
from collections import defaultdict
import time
import copy
import numpy

class abaloneAI:
    def __init__(self,name, targetIP="localHost", port=5201):
        #initie la premiere connexion et crée certaine variables
        s = socket.socket()
        s.connect((targetIP,3000))
        self.__s = s
        self.port = port
        self.name = name
        self.round = 1
        self.numJoueur=2
        self.numbW = 14
        self.numbB = 14
        self.messages = ("Counter this you casual","un bon jambon est fait avec amour","Si tu joue comme ca, ca va aller vite","Nerf this","Attend c'est toi random ou tu es juste nul?","better jungler wins","better boulier wins","https://www.youtube.com/watch?v=dQw4w9WgXcQ","https://www.youtube.com/watch?v=wXMD6wmcwvE&t=11344s","https://www.amazon.fr/Python-pour-Nuls-John-MUELLER/dp/2754083219","Honnetement je me serais pas inscrit si j'était toi","Bine joué,...","De toute façon c'est de la faute de mes mates","https://youtu.be/uuXxBWoSOU4","En raison des conditions sanitaire actuelles, nous devons vous eliminez du tournoi")
        self.directions={
        'NE': (-1,  0),
        'SW': ( 1,  0),
        'NW': (-1, -1),
        'SE': ( 1,  1),
        'E': ( 0,  1),
        'W': ( 0, -1)
    }


    def run(self):
        '''Lance les differents threads, un pour gerer les demande de ping et un autre pour gerer le reste'''
        self.__running=True
        res = json.dumps({"request": "subscribe","port": self.port,"name": self.name,"matricules": ["195367", "195093"]})
        self.__s.send(res.encode('utf8'))
        self.handlePing()
        

    def handlePing(self):
        '''repond aux request play et ping
        Crée un nouveau socket car le prof lance une connexion tcp
        voir le fichier jsonNetwork pour les fonctions'''
        while self.__running:
            pingSocket = socket.socket()
            pingSocket.bind(("localhost", self.port))
            pingSocket.listen()
            try:
                pingS, pingAdd = pingSocket.accept()
                data = ''
                ended =  False
                while not ended:
                    data += pingS.recv(4096).decode('utf8')
                    if data != '':
                        if data[0]=='{' and data[-1] == '}':
                            ended = True
                            data = json.loads(data)
                if data == {"request": "ping"}:
                    jsonNetwork.sendJSON(pingS,{"response":"pong"})
                if "request" in data.keys():
                    if data["request"] == "play":
                        if data["state"]["players"].index(self.name)==0:
                            self.numJoueur=1 #1 = black                 (self,state, player, timeout=2.5))
                        else:
                            self.numJoueur = 2
                        _, self.numbB, self.numbW = self.gameOver((data["state"]["board"]))
                        if (data["state"]["board"]) == [
                                    ["W", "W", "W", "W", "W", "X", "X", "X", "X"],
                                    ["W", "W", "W", "W", "W", "W", "X", "X", "X"],
                                    ["E", "E", "W", "W", "W", "E", "E", "X", "X"],
                                    ["E", "E", "E", "E", "E", "E", "E", "E", "X"],
                                    ["E", "E", "E", "E", "E", "E", "E", "E", "E"],
                                    ["X", "E", "E", "E", "E", "E", "E", "E", "E"],
                                    ["X", "X", "E", "E", "B", "B", "B", "E", "E"],
                                    ["X", "X", "X", "B", "B", "B", "B", "B", "B"],
                                    ["X", "X", "X", "X", "B", "B", "B", "B", "B"]]:
                            self.round = 1
                        else:
                            self.round+=1
                        move = self.negamaxWithPruningIterativeDeepening(data["state"]["board"],self.numJoueur)
                        jsonNetwork.sendJSON(pingS,{"response": "move","move": move,"message": choice(self.messages)})
                pingS.close()
            except EOFError as error:
                print(error)

    def get_play(self,board,player):
        # renvoie un mouvement "legal" pour ce faire appelle get_plays et analyse le status de la game pour savoir qui on est 
        if player==1:
            self.us = "B"
            self.enemy = "W"
        else:
            self.us = "W"
            self.enemy = "B"
        return self.get_plays(board)
        

    def get_plays(self, board):
        #crée un dictionaire avec tout les move legaux possible selon la structure {bille de base:[([bille a bouger], direction)]}
        Xline = ["X", "X", "X", "X", "X", "X", "X", "X", "X","X", "X"]
        possible_moves_move = {}
        possible_moves_kill = {}
        board = copy.deepcopy(board)
        for line in board:
            line.insert(0,"X")
            line.append("X")
        board.insert(0,Xline)
        board.append(Xline)
        for line in range(len(board)):
            for row in range(len(board[line])):
                if board[line][row] == self.us:
                    for dire in ["NE", "NW", "E", "SE", "SW", "W"]:
                        temp_move, name = self.test_move(board, [line, row], dire)
                        if name == 'move':
                            if len(temp_move[0]) !=0:
                                if (line-1,row-1) in possible_moves_move.keys():
                                    possible_moves_move[(line-1,row-1)].append(temp_move)
                                else:
                                    possible_moves_move[(line-1,row-1)]=[temp_move]
                        else:
                            if len(temp_move[0]) !=0:
                                if (line-1,row-1) in possible_moves_kill.keys():
                                    possible_moves_kill[(line-1,row-1)].append(temp_move)
                                else:
                                    possible_moves_kill[(line-1,row-1)]=[temp_move]
        if possible_moves_kill != {}:
            possible_moves = possible_moves_kill
        else:
            possible_moves = possible_moves_move
        l=[]
        for x in possible_moves:
            for i in possible_moves[x]:
                l.append(i)
        return l

    def move_dire(self, board, marble, dire, num = 1):
        #calcule les index de la case suivante dans la direction spécifiée
        line =  marble[0]
        row = marble[1]
        if dire == "NE":
            line = line-num
        if dire == "NW":
            line = line-num
            row = row-num
        if dire == "E":
            row = row+num
        if dire == "SE":
            line = line+num
            row = row+num
        if dire == "SW":
            line = line+num
        if dire == "W":
            row = row-num
        if line ==-1 or board==-1:
            raise IndexError
        return board[line][row], line, row


    def test_move(self, board, marble, dire):
        #vérifie si la direction indiquée pour la bille indiquée permet de faire un mouvement
        marbles = []
        kill = []
        chain_lenght = 1
        try:
            next_marble_1, next_marble_1_l, next_marble_1_r = self.move_dire(board, marble, dire)
            chain_lenght+=1
            next_marble_2, next_marble_2_l, next_marble_2_r = self.move_dire(board, marble, dire, num=2)
            chain_lenght+=1
            next_marble_3, next_marble_3_l, next_marble_3_r = self.move_dire(board, marble, dire, num=3)
            chain_lenght+=1
            next_marble_4, next_marble_4_l, next_marble_4_r = self.move_dire(board, marble, dire, num=4)
            chain_lenght+=1
            next_marble_5, next_marble_5_l, next_marble_5_r = self.move_dire(board, marble, dire, num=5)
            chain_lenght+=1
        except IndexError:
            pass
        if chain_lenght>=2:
            if next_marble_1 == "E":
                marbles.append([marble[0]-1,marble[1]-1])
        if chain_lenght>=3:
            if next_marble_1 == self.us and next_marble_2=="E":
                marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1]))
        if chain_lenght>=4:
            if next_marble_1 == self.us and next_marble_2==self.us and next_marble_3=="E":
                marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1], [next_marble_2_l-1, next_marble_2_r-1]))
            elif next_marble_1 == self.us and next_marble_2 == self.enemy:
                if next_marble_3=="E":
                    marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1,next_marble_1_r-1]))
                elif next_marble_3=="X": 
                    kill.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1,next_marble_1_r-1]))
        if chain_lenght>=5:
            if next_marble_1 == self.us and next_marble_2 == self.us and next_marble_3==self.enemy:
                if next_marble_4=="E":
                    marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1], [next_marble_2_l-1, next_marble_2_r-1]))
                elif next_marble_4=="X":
                    kill.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1], [next_marble_2_l-1, next_marble_2_r-1]))
        if chain_lenght >= 6:
            if next_marble_1 == self.us and next_marble_2 == self.us and next_marble_3==self.enemy and next_marble_4==self.enemy:
                if next_marble_5=="E":
                    marbles.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1], [next_marble_2_l-1, next_marble_2_r-1]))
                elif next_marble_5=="X":
                    kill.extend(([marble[0]-1,marble[1]-1], [next_marble_1_l-1, next_marble_1_r-1], [next_marble_2_l-1, next_marble_2_r-1]))
        if len(kill) != 0:
            return (kill, dire), 'kill'
        return (marbles, dire), 'move'
                 


    def negamaxWithPruningIterativeDeepening(self,board, player, timeout=2.5):
        '''Renvoie un move selon la stratégie dans le ReadMe via la methode Negamax '''
        cache = defaultdict(lambda : 0)
        def cachedNegamaxWithPruningLimitedDepth(board, player, depth, alpha=float('-inf'), beta=float('inf')):
            over= self.gameOver(board)[0]
            if over or depth == 0:
                res = (-self.heuristic(board, player), None, over)

            else:
                theValue, theMove, theOver = float('-inf'), None, True
                possibilities = [(move, self.apply(board,move)) for move in self.get_play(board,player)]   # Fonction Apply, renvoie le nouvel etat du jeu     
                possibilities.sort(key=lambda poss: cache[self.tupleTuple(poss[1])])
                for move, NewsBoard in reversed(possibilities):
                    value, _, over = cachedNegamaxWithPruningLimitedDepth(NewsBoard, player%2+1, depth-1, -beta, -alpha)
                    theOver = theOver and over
                    if value > theValue:
                        theValue, theMove = value, move
                    alpha = max(alpha, theValue)
                    if alpha >= beta:
                        break
                res = (-theValue, theMove, theOver)
            cache[self.tupleTuple(board)] = res[0]
            return res

        value, move = 0, None
        depth = 1                     
        start = time.time()
        over = False
        while value > -500 and time.time() - start < timeout and not over and depth<3:
            value, move, over = cachedNegamaxWithPruningLimitedDepth(board, player, depth)
            depth += 1
        return {'marbles':move[0], 'direction': move[1]}

    def tupleTuple(self,listeListe):
        tempL = []
        for list in listeListe:
            tempL.append(tuple(list))
        return tuple(tempL)

    def gameOver(self,boardx):
        '''Return True si la patie est finie'''
        count_B=0
        count_W=0
        
        for line in boardx:
            for case in line:
                if case=="W":
                    count_W+=1
                if case=="B":
                    count_B+=1
        
        return(not((not(count_B<9) and not(count_W<9))),count_B,count_W)

    def addDirection(self,pos, direction):
        D = self.directions[direction]
        return (pos[0] + D[0], pos[1] + D[1])

    def isOnBoard(self,pos):
        l, c = pos
        if min(pos) < 0:
            return False
        if max(pos) > 8:
            return False
        if abs(c-l) >= 5:
            return False
        return True

    def isEmpty(self,board, pos):
        return self.getStatus(board, pos) == 'E'

    def isFree(self,board, pos):
        if self.isOnBoard(pos):
            return self.isEmpty(board, pos)
        else:
            return True

    def moveOneMarble(self,board, pos, direction):
        li, ci = pos
        ld, cd = self.addDirection(pos, direction)
        color = self.getColor(board, pos)
        try:
            destStatus = self.getStatus(board, (ld, cd))
        except:
            destStatus = 'X'
        res = copy.copy(board)
        res[li] = copy.copy(res[li])
        res[li][ci] = 'E'

        if destStatus == 'E':
            res[ld] = copy.copy(res[ld])
            res[ld][cd] = color

        return res

    def moveMarblesTrain(self,board, marbles, direction):
        if direction in ['E', 'SE', 'SW']:
            marbles = sorted(marbles, key=lambda L: -(L[0]*9+L[1]))
        else:
            marbles = sorted(marbles, key=lambda L: L[0]*9+L[1])

        color = self.getColor(board, marbles[0])
        pos = self.addDirection(marbles[0], direction)
        toPush = []
        while not self.isFree(board, pos):
            if self.getColor(board, pos) == color:
                pass
            toPush.append(pos)
            pos = self.addDirection(pos, direction)

        if len(toPush) >= len(marbles):
            pass
        board = self.moveMarbles(board, list(reversed(toPush)) + marbles, direction)
        return board

    def getStatus(self,board, pos):
        return board[pos[0]][pos[1]]


    def getColor(self,board, pos):
        status = self.getStatus(board, pos)
        if status == 'W' or status == 'B':
            return status
        

    def moveMarbles(self,board, marbles, direction):
        for pos in marbles:
            board = self.moveOneMarble(board, pos, direction)
        return board

    def apply(self,board,move):
        pos=move[0]
        direction=move[1]
        if len (pos)==1:
            return (self.moveMarbles(board,pos,direction))
        if len (pos) >1:
            return(self.moveMarblesTrain(board,pos,direction))

    
    def heuristic(self,state, player):
        ''' Attribue un score à l'etat en fonction du joueur et de la stratégie (voir ReadMe) '''
        if player==1:
            self.us = "B"
            self.enemy = "W"
            nbrBilleEne = self.numbW
            nbrBilleUs = self.numbB
        else:
            self.us = "W"
            self.enemy = "B"
            nbrBilleEne = self.numbB
            nbrBilleUs = self.numbW
        
        game = self.gameOver(state)
        if game[0]:
            if game[1] <9:
                theWinner = 1
            elif game[2] <9:
                theWinner =2
            if theWinner is None:
                return 0
            if theWinner == player:
                return 400
            return -400

        res = 0
        it  = 0
        tot_dist = 0
        tot_dist_enemy = 0
        posx = []
        posy = []
        posxE = []
        posyE = []
        center  = [4,4]

        if self.round >=100 and self.round%10 == 0:
            center  = choice(((3,3),(3,4),(4,3),(4,5),(5,4),(5,5)))
        for line in range(len(state)):
                for row in range(len(state[line])):
                    if state[line][row] == self.us:
                        it+=1
                        tot_dist += numpy.sqrt(numpy.square(line-center[0])+numpy.square(row-center[1]))
                        posx.append(row)
                        posy.append(line)
                    elif state[line][row] == self.enemy:
                        tot_dist_enemy+=numpy.sqrt(numpy.square(line-4)+numpy.square(row-4))
                        posxE.append(row)
                        posyE.append(line)
        std = numpy.std(posx)+ numpy.std(posy)
        stdE = numpy.std(posxE)+ numpy.std(posyE)

        tot_dist = tot_dist/it
        tot_dist_enemy= tot_dist_enemy/it
        if self.round > 100:
            roundInt = 100
        else:
            roundInt = self.round
        res = (game[player]-game[player%2+1])*roundInt*7-(tot_dist+std-tot_dist_enemy-stdE)*(3/roundInt)-(nbrBilleUs-game[player])*100
        if game[player%2+1] == 9 and nbrBilleEne != game[player%2+1]:
            res+=200
        if game[player] == 9 and nbrBilleUs != game[player]:
            res-=200
        return res

    







if len(sys.argv)==1:
    abaloneAI(port=5214,name = "l'IA super intelligente de Baudouin et Théo").run()
elif len(sys.argv)==3:
    abaloneAI(port = int(sys.argv[1]), name = str(sys.argv[2])).run()
else:
    print('Erreur: veillez preciser le port et le nom souhaiter')

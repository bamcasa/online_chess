import pygame
import pprint
import sys
import numpy as np
import socket
import pickle
import threading

pygame.init()

class chessgame:
    def __init__(self):
        HOST = socket.gethostbyname(socket.gethostname())
        PORT = 9999
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))

        t = threading.Thread(target=self.recv)
        t.start()

        self.FPS = 30
        self.screen = pygame.display.set_mode((600, 600))
        self.font = pygame.font.SysFont("notosanscjkkr", 30)
        self.clicked = False
        self.click_x,self.click_y = 0,0
        self.turn = 1 #짝수 : 검은색 홀수 :하얀색
        self.white_promotion = False
        self.black_promotion = False
        self.pos = 0
        self.En_passant = [0,0]

        #self.background_image = [pygame.image.load("image/green.png"), pygame.image.load("image/white.png")]

        self.black_bishop = pygame.image.load("image/black_bishop.png")
        self.black_king = pygame.image.load("image/black_king.png")
        self.black_knight = pygame.image.load("image/black_knight.png")
        self.black_pawn = pygame.image.load("image/black_pawn.png")
        self.black_rook = pygame.image.load("image/black_Rook.png")
        self.black_queen = pygame.image.load("image/black_queen.png")

        self.white_bishop = pygame.image.load("image/white_bishop.png")
        self.white_king = pygame.image.load("image/white_king.png")
        self.white_knight = pygame.image.load("image/white_knight.png")
        self.white_pawn = pygame.image.load("image/white_pawn.png")
        self.white_rook = pygame.image.load("image/white_Rook.png")
        self.white_queen = pygame.image.load("image/white_queen.png")

        self.board = np.zeros((8,8))
        # 1 : 폰 2 : 룩 3 : 나이트 4: 비숍 5: 퀸 6 : 킹
        # 음수 : 화이트

        #폰
        for i in range(8):
            self.board[1][i] = 1
            self.board[6][i] = -1
        #black_pawns = np.array([False, False, False, False, False, False, False, False])
        #white_pawns = np.array([False, False, False, False, False, False, False, False])

        #룩
        self.board[0][0] = 2
        self.board[0][7] = 2
        self.board[7][0] = -2
        self.board[7][7] = -2

        #나이트
        self.board[0][1] = 3
        self.board[0][6] = 3
        self.board[7][1] = -3
        self.board[7][6] = -3

        #비숍
        self.board[0][2] = 4
        self.board[0][5] = 4
        self.board[7][2] = -4
        self.board[7][5] = -4

        #퀸
        self.board[0][3] = 5
        self.board[7][3] = -5

        #킹
        self.board[0][4] = 6
        self.board[7][4] = -6

        self.location = [[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0]]

        self.canmove = np.zeros((8,8))

        background_x = 0
        background_y = 0
        color1 = [(0, 0, 0), (255, 255, 255)]
        color = 1
        for i in range(8):
            for j in range(8):
                self.location[i][j] = pygame.draw.rect(self.screen, color1[color], (background_x, background_y, 75, 75))
                background_x += 75
                if color == 1:
                    color -= 1
                else:
                    color += 1
            if color == 1:
                color -= 1
            else:
                color += 1
            background_x = 0
            background_y += 75

    def backgroud(self):
        background_x = 0
        background_y = 0
        color1 = [(0,0,0),(255,255,255)]
        color = 1
        for i in range(8):
            for j in range(8):
                pygame.draw.rect(self.screen, color1[color],(background_x, background_y, 75, 75))
                background_x += 75
                if color == 1:
                    color -= 1
                else:
                    color += 1
            if color == 1:
                color -= 1
            else:
                color += 1
            background_x = 0
            background_y += 75
        #print(len(self.location))

    def chesspiece(self):
        for x in range(8):
            for y in range(8):
                self.show(x, y)

    def click(self,pos):# 1 : 폰   2 : 룩    3 : 나이트     4: 비숍     6: 킹     5 : 퀸
        if self.white_promotion or self.black_promotion:
            return
        for i in range(8):
            for j in range(8):
                if self.location[i][j].collidepoint(pos):
                    print(f"[{i},{j}]")
                    if self.board[i][j] == 0 and not(self.clicked):
                        print("공백")
                        return
                    if self.clicked:
                        if self.board[self.click_x][self.click_y] > 0 and not (self.turn % 2 == 0) or self.board[self.click_x][self.click_y] < 0 and self.turn % 2 == 0:
                            print("자신의 턴이 아님")
                            return
                    elif self.board[i][j] > 0 and not(self.turn % 2 == 0) or self.board[i][j] < 0 and self.turn % 2 == 0:
                        print("자신의 턴이 아님")
                        return
                    if not(self.clicked):
                        self.click_x,self.click_y = i,j
                    x,y = i,j
        # turn True = 검은색 Fasle = 하얀색  양수 = 블랙  음수 = 화이트
        if self.clicked:
            if self.click_x == x and self.click_y == y:
                print("똑같은 곳 클릭")
                return
            #pprint.pprint(self.canmove)
            if self.canmove[x][y] == 0:
                print("움직일 수 없는 곳임")
                return
            self.move(self.click_x,self.click_y,x,y)
            if self.En_passant[0] == x and self.En_passant[1] == y:
                if x>=3:
                    print("앙파상")
                    self.board[self.En_passant[0]-1][self.En_passant[1]] = 0
                elif x<=4:
                    print("앙파상")
                    self.board[self.En_passant[0]+1][self.En_passant[1]] = 0
            self.clicked = False
            self.click_x = 0
            self.click_y = 0
        else:
            self.clicked = True
            self.movemake(self.click_x, self.click_y)

    def show(self,x,y):# 1 : 폰 2 : 룩 3 : 나이트 4: 비숍 6: 킹 5 : 퀸
        if self.board[x][y] == 0:
            return
        elif self.board[x][y] > 0:
            if self.board[x][y] == 1:
                self.screen.blit(self.black_pawn,(y*75,x*75))
            elif self.board[x][y] == 2:
                self.screen.blit(self.black_rook, (y * 75, x * 75))
            elif self.board[x][y] == 3:
                self.screen.blit(self.black_knight, (y * 75, x * 75))
            elif self.board[x][y] == 4:
                self.screen.blit(self.black_bishop, (y * 75, x * 75))
            elif self.board[x][y] == 5:
                self.screen.blit(self.black_king,(y*75,x*75))
            elif self.board[x][y] == 6:
                self.screen.blit(self.black_queen, (y * 75, x * 75))
        else :
            if self.board[x][y]*-1 == 1:
                self.screen.blit(self.white_pawn, (y * 75, x * 75))
            elif self.board[x][y]*-1 == 2:
                self.screen.blit(self.white_rook, (y * 75, x * 75))
            elif self.board[x][y]*-1 == 3:
                self.screen.blit(self.white_knight, (y * 75, x * 75))
            elif self.board[x][y]*-1 == 4:
                self.screen.blit(self.white_bishop, (y * 75, x * 75))
            elif self.board[x][y]*-1 == 5:
                self.screen.blit(self.white_king, (y * 75, x * 75))
            elif self.board[x][y]*-1 == 6:
                self.screen.blit(self.white_queen, (y * 75, x * 75))

    def movemake(self,x,y):
        if abs(self.board[x][y]) == 1: #폰
            if x == 1 and self.board[x][y] > 0:
                self.canmove[x+1][y] = 1
                self.canmove[x+2][y] = 1
            elif self.board[x][y] > 0:
                if self.board[x][y-1] == -1 and x<=4:
                    self.canmove[x+1][y-1] = 1
                    self.En_passant[0] = x+1
                    self.En_passant[1] = y-1
                    #print("앙파상")
                if self.board[x][y+1] == -1 and x<=4:
                    self.canmove[x+1][y+1] = 1
                    self.En_passant[0] = x+1
                    self.En_passant[1] = y+1
                    #print("앙파상")
                if self.board[x+1][y+1] != 0:
                    self.canmove[x+1][y+1] = 1
                if self.board[x+1][y-1] != 0:
                    self.canmove[x+1][y-1] = 1
                if self.board[x+1][y] != 0:
                    return
                self.canmove[x+1][y] = 1
            if x == 6 and self.board[x][y] < 0:
                self.canmove[x-1][y] = 1
                self.canmove[x-2][y] = 1
            elif self.board[x][y] < 0:
                if self.board[x][y-1] == 1 and x>=3:
                    self.canmove[x-1][y-1] = 1
                    self.En_passant[0] = x-1
                    self.En_passant[1] = y-1
                    #print("앙파상")
                if self.board[x][y+1] == 1 and x>=3:
                    self.canmove[x-1][y+1] = 1
                    self.En_passant[0] = x-1
                    self.En_passant[1] = y+1
                    #print("앙파상")
                if self.board[x-1][y+1] != 0:
                    self.canmove[x-1][y+1] = 1
                if self.board[x-1][y-1] != 0:
                    self.canmove[x-1][y-1] = 1
                if self.board[x-1][y] != 0:
                    return
                self.canmove[x-1][y] = 1
        if abs(self.board[x][y]) == 2: #룩
            for i in range(1,8):
                self.canmove[x-i][y] = 1
                self.canmove[x][y-i] = 1

        if abs(self.board[x][y]) == 3: #나이트
            if y-1 >= 0:
                if x-2 >= 0:
                    self.canmove[x - 2][y - 1] = 1
                if x+2 <= 7:
                    self.canmove[x + 2][y - 1] = 1
            if y+1 <= 7:
                if x-2 >= -1:
                    self.canmove[x - 2][y + 1] = 1
                if x+2 <= 7:
                    self.canmove[x + 2][y + 1] = 1

            if y-2 >= 0:
                if x-1 >= 0:
                    self.canmove[x - 1][y - 2] = 1
                if x+1 <= 7:
                    self.canmove[x + 1][y - 2] = 1
            if y+2 <= 7:
                if x-1 >= 0:
                    self.canmove[x - 1][y + 2] = 1
                if x+1 <= 7:
                    self.canmove[x + 1][y + 2] = 1
        if abs(self.board[x][y]) == 4: #비숍
            for i in range(1,8):
                if x-i <= -1 or y-i <= -1:
                    break
                self.canmove[x-i][y-i] = 1
            for i in range(1,8):
                if x+i >=8 or y+i >=8:
                    break
                self.canmove[x+i][y+i] = 1
            for i in range(1,8):
                if x-i <= -1 or y+i >=8:
                    break
                self.canmove[x-i][y+i] = 1
            for i in range(1,8):
                if x+i >= 8 or y-i <= -1:
                    break
                self.canmove[x+i][y-i] = 1

        if abs(self.board[x][y]) == 5: #퀸
            for i in range(1,8):
                if x-i <= -1 or y-i <= -1:
                    break
                self.canmove[x-i][y-i] = 1
            for i in range(1,8):
                if x+i >=8 or y+i >=8:
                    break
                self.canmove[x+i][y+i] = 1
            for i in range(1,8):
                if x-i <= -1 or y+i >=8:
                    break
                self.canmove[x-i][y+i] = 1
            for i in range(1,8):
                if x+i >= 8 or y-i <= -1:
                    break
                self.canmove[x+i][y-i] = 1
            for i in range(1,8):
                self.canmove[x-i][y] = 1
                self.canmove[x][y-i] = 1


        if abs(self.board[x][y]) == 6: #킹
            if x+1 <= 7:
                self.canmove[x + 1][y] = 1
                if y+1 <= 7:
                    self.canmove[x + 1][y + 1] = 1
                if y-1 >=0:
                    self.canmove[x + 1][y - 1] = 1
            if x-1 >=0:
                self.canmove[x - 1][y] = 1
                if y+1 <= 7:
                    self.canmove[x - 1][y + 1] = 1
                if y-1 >=0:
                    self.canmove[x - 1][y - 1] = 1
            if y + 1 <= 7:
                self.canmove[x][y + 1] = 1
            if y - 1 >= 0:
                self.canmove[x][y - 1] = 1
    def showmove(self):
        for i in range(8):
            for j in range(8):
                if self.canmove[i][j] == 1:
                    pygame.draw.circle(self.screen, (190, 190, 190),
                                       (j * 75 + 37, i * 75 + 37), 10)


    def move(self,x,y,new_x,new_y):
        self.board[new_x][new_y] = self.board[x][y]
        self.board[x][y] = 0
        self.canmove = np.zeros((8, 8))
        self.send()

    def choice(self,pos,x,y):
        if self.white_promotion:
            if self.clicked_rook.collidepoint(pos):
                self.board[x, y] = -2
                self.white_promotion = False
            elif self.clicked_knight.collidepoint(pos):
                self.board[x, y] = -3
                self.white_promotion = False
            elif self.clicked_bishop.collidepoint(pos):
                self.board[x, y] = -4
                self.white_promotion = False
            elif self.clicked_queen.collidepoint(pos):
                self.board[x, y] = -5
                self.white_promotion = False
        elif self.black_promotion:
            if self.clicked_rook.collidepoint(pos):
                self.board[x, y] = 2
                self.black_promotion = False
            elif self.clicked_knight.collidepoint(pos):
                self.board[x, y] = 3
                self.black_promotion = False
            elif self.clicked_bishop.collidepoint(pos):
                self.board[x, y] = 4
                self.black_promotion = False
            elif self.clicked_queen.collidepoint(pos):
                self.board[x, y] = 5
                self.black_promotion = False

    def game(self):
        self.screen.blit(self.font.render(str(self.turn), True, (50, 255, 255)), (20, 20))
        if self.turn % 2 == 0: #검은색
            self.screen.blit(self.font.render("BLACK TURN", True, (50, 255, 255)), (250, 20))
        else: #하얀색
            self.screen.blit(self.font.render("WHITE TURN", True, (50, 255, 255)), (250, 20))
        for i in range(8):
            if self.board[0][i] == -1:
                #print("흰 폰이 끝에 다임")
                pygame.draw.rect(self.screen, (190,190,190), [100, 200, 400, 200])
                pygame.draw.rect(self.screen, (255,255,255), [100, 200, 400, 200], 5)
                self.clicked_rook = self.screen.blit(self.white_rook,(115,235))
                self.clicked_bishop = self.screen.blit(self.white_bishop,(215,235))
                self.clicked_knight = self.screen.blit(self.white_knight,(315,235))
                self.clicked_queen = self.screen.blit(self.white_king,(415,235))
                self.screen.blit(self.font.render("ROOK", True, (0, 0, 0)), (115, 335))
                self.screen.blit(self.font.render("BISHOP", True, (0, 0, 0)), (215, 335))
                self.screen.blit(self.font.render("KNIGHT", True, (0, 0, 0)), (315, 335))
                self.screen.blit(self.font.render("QUEEN", True, (0, 0, 0)), (415, 335))
                self.white_promotion = True
                self.choice(self.pos,0,i)
            if self.board[7][i] == 1:
                #print("검은 폰이 끝에 다임")
                pygame.draw.rect(self.screen, (190,190,190), [100, 200, 400, 200])
                pygame.draw.rect(self.screen, (255,255,255), [100, 200, 400, 200], 5)
                self.clicked_rook = self.screen.blit(self.black_rook,(115,235))
                self.clicked_bishop = self.screen.blit(self.black_bishop,(215,235))
                self.clicked_knight = self.screen.blit(self.black_knight,(315,235))
                self.clicked_queen = self.screen.blit(self.black_king,(415,235))
                self.screen.blit(self.font.render("ROOK", True, (0, 0, 0)), (115, 335))
                self.screen.blit(self.font.render("BISHOP", True, (0, 0, 0)), (215, 335))
                self.screen.blit(self.font.render("KNIGHT", True, (0, 0, 0)), (315, 335))
                self.screen.blit(self.font.render("QUEEN", True, (0, 0, 0)), (415, 335))
                self.black_promotion = True
                self.choice(self.pos,7,i)

        black = 0
        white = 0
        for i in range(8):
            for j in range(8):
                if self.board[i][j] > 0:
                    black += 1
                elif self.board[i][j] < 0:
                    white += 1
        if 6 in self.board:
            pass
            #print("검은 퀸 살아있음")
        else:
            self.screen.blit(self.font.render("WHITE WIN", True, (50, 255, 255)), (300, 250))
            #print("검은 퀸 죽음 흰색 이김")
        if -6 in self.board:
            pass
            #print("하얀 퀸 살아있음")
        else:
            self.screen.blit(self.font.render("BLACK WIN", True, (50, 255, 255)), (300, 250))
            #print("하얀 퀸 죽음 검은색 이김")
        #print(black,white)\\\\
    def send(self):
        y = self.board.flatten().tolist()
        msg = pickle.dumps(y)
        #print(msg)
        self.client_socket.send(msg)
    def recv(self):
        data = self.client_socket.recv(1024)
        print(np.array(pickle.loads(data)).reshape(8, 8))
        self.board = np.array(pickle.loads(data)).reshape(8, 8)
        t = threading.Thread(target=self.recv)
        t.start()
        self.turn += 1


    def main(self):
        clock = pygame.time.Clock()
        while True:
            #self.recv()
            #print(self.white_promotion)
            clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.pos = pygame.mouse.get_pos()
                    self.click(self.pos)
            self.backgroud()
            self.chesspiece()
            self.showmove()
            self.game()

            pygame.display.update()

if __name__ == "__main__":
    chessgame().main()
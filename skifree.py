#!/usr/bin/env python
"""A simple mod of SkiFree"""

# Source code taken from Warren Sande at
# http://www.manning-source.com/books/sande/All_Files_By_Chapter/hw_ch10_code/skiing_game.py
# Released under the MIT license http://www.opensource.org/licenses/mit-license.php

import pygame
import sys
import os
import random
import urllib
import urllib2

skier_images = ["images/skier_down.png",
                "images/skier_right1.png",
                "images/skier_right2.png",
                "images/skier_left2.png",
                "images/skier_left1.png"]

try:
    if os.environ["USER"]:
        player = os.environ["USER"]
    else:
        player = os.environ["LOGNAME"]
except KeyError:
    player = os.environ["LOGNAME"]


class SkierClass(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/skier_down.png")
        self.rect = self.image.get_rect()
        self.rect.center = [320, 100]
        self.angle = 0
        
    def turn(self, direction):
        self.angle = self.angle + direction
        if self.angle < -2: self.angle = -2
        if self.angle >  2: self.angle =  2
        center = self.rect.center
        self.image = pygame.image.load(skier_images[self.angle])
        self.rect = self.image.get_rect()
        self.rect.center = center
        speed = [self.angle, 6 - abs(self.angle) * 2]
        return speed
    
    def move(self, speed):
        self.rect.centerx = self.rect.centerx + speed[0]
        if self.rect.centerx < 20:  self.rect.centerx = 20
        if self.rect.centerx > 620: self.rect.centerx = 620
        
class ObstacleClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location, type):
        pygame.sprite.Sprite.__init__(self)
        self.image_file = image_file
        self.image = pygame.image.load(image_file)
        self.location = location
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.type = type
        self.passed = False

    def scroll(self, terrainPos):
        self.rect.centery = self.location[1] - terrainPos

def create_map(start, end):
    obstacles = pygame.sprite.Group()
    gates = pygame.sprite.Group()
    locations = []
    for i in range(10):
        row = random.randint(start, end)
        col = random.randint(0, 9)
        location = [col * 64 + 20, row * 64 + 20]
        if not (location in locations):
            locations.append(location)
            type = random.choice(["tree", "flag"])
            if type == "tree": img = "images/skier_tree.png"
            elif type == "flag": img = "images/skier_flag.png"
            obstacle = ObstacleClass(img, location, type)
            obstacles.add(obstacle)
    return obstacles

def animate():
    screen.fill([255, 255, 255])
    pygame.display.update(obstacles.draw(screen))
    screen.blit(skier.image, skier.rect)
    screen.blit(score_text, [10, 10])
    pygame.display.flip()

def updateObstacleGroup(map0, map1):
    obstacles = pygame.sprite.Group()
    for ob in map0: obstacles.add(ob)
    for ob in map1: obstacles.add(ob)
    return obstacles

def main():    
    global screen
    global obstacles
    global skier
    global score_text
    pygame.init()
    screen = pygame.display.set_mode([640, 640])
    clock = pygame.time.Clock()
    skier = SkierClass()
    speed = [0, 6]
    map_position = 0
    points = 0
    map0 = create_map(20, 29)
    map1 = create_map(10, 19)
    activeMap = 0
    
    obstacles = updateObstacleGroup(map0, map1)
    
    font = pygame.font.Font(None, 50)
    
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    speed = skier.turn(-1)
                elif event.key == pygame.K_RIGHT:
                    speed = skier.turn(1)
        skier.move(speed)
        map_position += speed[1]
        
        if map_position >= 640 and activeMap == 0:
            activeMap = 1
            map0 = create_map(20, 29)
            obstacles = updateObstacleGroup(map0, map1)
        if map_position >= 1280 and activeMap == 1:
            activeMap = 0
            for ob in map0:
                ob.location[1] = ob.location[1] - 1280
            map_position = map_position - 1280
            map1 = create_map(10, 19)
            obstacles = updateObstacleGroup(map0, map1)
            
        for obstacle in obstacles:
            obstacle.scroll(map_position)
            
        hit = pygame.sprite.spritecollide(skier, obstacles, False)
        if hit:
            if hit[0].type == "tree":
                skier.image = pygame.image.load("images/skier_crash.png")
                animate()
                pygame.time.delay(1000)
                screen.fill([255, 255, 255])
                game_over = font.render("Game Over!", 1, (0, 0, 0))
                params = urllib.urlencode(dict(player=player, score=points))
                req = urllib2.Request(url="http://www.thefirstmimzy.com/skifree.php", data=params)
                f = urllib2.urlopen(req)
                scores_page = f.read()
                scores_rows = scores_page.strip("<br>").split("<br><br>")
                scores_table = []
                for row in scores_rows:
                    scores_table.append(row.split("<br>"))
                for i in range(len(scores_table)):
                    high_player = "{:.<100}".format(scores_table[i][0][7:])
                    high_score = "{}  ".format(scores_table[i][1][6:])
                    high_player_surf = font.render(high_player, 1, (0, 0, 0))
                    high_score_surf = font.render(high_score, 1, (0, 0, 0), (255, 255, 255))
                    screen.blit(high_player_surf, [20, 250 + 50 * i])
                    screen.blit(high_score_surf, [640 - high_score_surf.get_width(), 250 + 50 * i])
                table_header = font.render("High Scores:", 1, (0, 0, 0))
                screen.blit(table_header, [20, 170])    
                screen.blit(score_text, [20, 70])
                screen.blit(game_over, [20, 20])
                pygame.display.flip()
                while True:
                    clock.tick(20)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: sys.exit()
            elif hit[0].type == "flag":
                points += 10
                hit[0].kill()
        
        score_text = font.render("Score: " + str(points), 1, (0, 0, 0))
        animate()

if __name__ == "__main__":
    main()
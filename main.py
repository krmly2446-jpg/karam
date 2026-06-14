"""alien_shooter_full.py
لعبة تصويب فضائيين 2D بسيطة باستخدام Pygame
التثبيت: pip install pygame
التشغيل: python موقع.py
"""

import sys
import random
import pygame

# ---------------- إعدادات ----------------
WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (20, 20, 30)
GREEN = (0, 220, 120)
RED   = (220, 70, 70)
YELLOW= (240, 220, 0)
CYAN  = (0, 210, 210)
PURPLE= (180, 0, 200)

# ---------------- الأصوات ----------------
def load_sounds():
    class _Dummy:
        def __init__(self): self._vol = 1.0
        def play(self): pass
        def set_volume(self, v): self._vol = v

    try:
        shoot = pygame.mixer.Sound('shoot.wav')
        explode = pygame.mixer.Sound('explode.wav')
        shoot.set_volume(0.3)
        explode.set_volume(0.4)
    except Exception:
        shoot = _Dummy()
        explode = _Dummy()
    return shoot, explode

# ---------------- اللاعب ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.w, self.h = 50, 28
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(0,self.h),(self.w//2,0),(self.w,self.h)])
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.bottom = WIDTH//2, HEIGHT-20
        self.speed, self.lives = 6, 3
        self.last_shot, self.shoot_cool = 0, 300
        self.invincible = 0

    def update(self, keys, dt):
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.rect.x += dx * self.speed
        self.rect.x = max(10, min(WIDTH-60, self.rect.x))
        if self.invincible>0:
            self.invincible -= dt

    def shoot(self, bullets, sound):
        if pygame.time.get_ticks()-self.last_shot >= self.shoot_cool:
            bullets.add(Bullet(self.rect.centerx, self.rect.top-5, -9, "player"))
            self.last_shot = pygame.time.get_ticks()
            try:
                sound.play()
            except Exception:
                pass

    def hit(self):
        if self.invincible<=0:
            self.lives -= 1
            self.invincible = 1500

# ---------------- الرصاص ----------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,vy,owner):
        super().__init__()
        self.image = pygame.Surface((4,12))
        self.image.fill(YELLOW if owner=="player" else RED)
        self.rect = self.image.get_rect(center=(x,y))
        self.vy, self.owner = vy, owner

    def update(self,dt=None):
        self.rect.y += self.vy
        if self.rect.bottom<0 or self.rect.top>HEIGHT:
            self.kill()

# ---------------- الفضائي ----------------
class Alien(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((40,30),pygame.SRCALPHA)
        pygame.draw.ellipse(self.image,PURPLE,(0,5,40,20))
        pygame.draw.circle(self.image,WHITE,(12,15),3)
        pygame.draw.circle(self.image,WHITE,(28,15),3)
        self.rect = self.image.get_rect(topleft=(x,y))

# ---------------- جيش الفضائيين ----------------
class AlienArmy:
    def __init__(self,rows,cols):
        self.group = pygame.sprite.Group()
        for r in range(rows):
            for c in range(cols):
                self.group.add(Alien(80+c*60, 60+r*50))
        self.dir, self.speed, self.drop = 1, 1.0, 20
        self.last_shot, self.cool = 0, 1000

    def update(self,dt=None):
        move = self.dir*self.speed
        hit_edge=False
        for alien in self.group:
            alien.rect.x+=move
            if alien.rect.right>WIDTH-40 or alien.rect.left<40:
                hit_edge=True
        if hit_edge:
            self.dir*=-1
            for alien in self.group:
                alien.rect.y+=self.drop
            self.speed = min(self.speed+0.2,4)

    def maybe_shoot(self,bullets):
        if pygame.time.get_ticks()-self.last_shot>self.cool and self.group:
            alien=random.choice(self.group.sprites())
            bullets.add(Bullet(alien.rect.centerx,alien.rect.bottom,6,"alien"))
            self.last_shot=pygame.time.get_ticks()
            self.cool=max(400,self.cool-20)

# ---------------- رسم النص ----------------
def draw_text(surf,text,size,x,y,color=WHITE,center=False):
    font=pygame.font.SysFont("consolas",size,True)
    img=font.render(text,True,color)
    if center:
        rect=img.get_rect(center=(x,y))
    else:
        rect=img.get_rect(topleft=(x,y))
    surf.blit(img,rect)

# ---------------- الشاشة الرئيسية ----------------
def start_screen(screen):
    screen.fill(BLACK)
    draw_text(screen,"🚀 Alien Shooter 2D 🚀",48,WIDTH//2,HEIGHT//2-60,YELLOW,True)
    draw_text(screen,"اضغط أي مفتاح للبدء",28,WIDTH//2,HEIGHT//2+20,WHITE,True)
    pygame.display.flip()
    wait=True
    while wait:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()
            if e.type==pygame.KEYDOWN:
                wait=False

# ---------------- الرئيسية ----------------
def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    screen=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Alien Shooter 2D")
    clock=pygame.time.Clock()

    # محاولة تشغيل موسيقى خلفية (اختياري)
    try:
        pygame.mixer.music.load('background.ogg')
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    shoot_snd, explode_snd = load_sounds()

    start_screen(screen)

    player=Player(); players=pygame.sprite.Group(player)
    bullets=pygame.sprite.Group(); alien_bullets=pygame.sprite.Group()
    army=AlienArmy(4,8)

    score,wave=0,1
    bg_stars=[(random.randint(0,WIDTH),random.randint(0,HEIGHT),random.randint(1,3)) for _ in range(120)]
    running,game_over,win=True,False,False

    while running:
        dt=clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                running=False
        keys=pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running=False
        if not game_over and keys[pygame.K_SPACE]:
            player.shoot(bullets,shoot_snd)

        if not game_over:
            player.update(keys,dt)
            bullets.update(dt); alien_bullets.update(dt); army.update(dt); army.maybe_shoot(alien_bullets)

            hits=pygame.sprite.groupcollide(army.group,bullets,True,True)
            for h in hits:
                score+=10
                try:
                    explode_snd.play()
                except Exception:
                    pass
            if pygame.sprite.spritecollide(player,alien_bullets,True):
                player.hit()
            if pygame.sprite.spritecollide(player,army.group,False):
                player.lives=0
            if player.lives<=0:
                game_over=True; win=False
            if not army.group:
                wave+=1; army=AlienArmy(min(6,4+wave//2),min(12,8+wave))
                player.lives=min(5,player.lives+1)
            if wave>5:
                game_over=True; win=True

        screen.fill(GRAY)
        for i,(x,y,s) in enumerate(bg_stars):
            y=(y+s)%HEIGHT
            pygame.draw.circle(screen,(200,200,255),(x,y),s)
            bg_stars[i]=(x,y,s)
        players.draw(screen); army.group.draw(screen); bullets.draw(screen); alien_bullets.draw(screen)
        draw_text(screen,f"النقاط: {score}",22,10,10)
        draw_text(screen,f"الحياة: {player.lives}",22,10,40)
        draw_text(screen,f"الموجة: {wave}",22,10,70)

        if game_over:
            msg="فزت 🎉" if win else "خسرت 💥"
            draw_text(screen,msg,48,WIDTH//2,HEIGHT//2-20,YELLOW,True)
            draw_text(screen,"اضغط أي مفتاح للخروج",28,WIDTH//2,HEIGHT//2+40,WHITE,True)
            pygame.display.flip()
            wait=True
            while wait:
                for e in pygame.event.get():
                    if e.type==pygame.QUIT:
                        wait=False;running=False
                    if e.type==pygame.KEYDOWN:
                        wait=False;running=False
        pygame.display.flip()
    pygame.quit()

if __name__=="__main__":
    main()



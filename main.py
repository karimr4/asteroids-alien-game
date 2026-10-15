
import pygame, math, random
import asyncio

height = 600
width = 800

pygame.init()

background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (width, height))

pygame.display.set_caption("Alien Invasion Asteroids")

clock = pygame.time.Clock()
window = pygame.display.set_mode((width, height))
font = pygame.font.SysFont("Arial", 18)

gameover = False
score = 0
lives = 3


class player(object):
    def __init__(self):
        self.position = pygame.Vector2(width/2, height/2)
        self.angle = 0
        self.velocity = pygame.Vector2(0, 0)

    def draw(self, window):
        points = [
            pygame.Vector2(0, -22),
            pygame.Vector2(-16, 18),
            pygame.Vector2(0, 10),
            pygame.Vector2(16, 18)
        ]

        points = [
            p.rotate(-self.angle) + self.position
            for p in points
        ]

        pygame.draw.polygon(window, (80, 255, 150), points, 2)

    def move(self):
        self.position += self.velocity
        self.position.x %= width
        self.position.y %= height

    def accelerate(self):
        direction = pygame.Vector2(0, -1).rotate(-self.angle)
        self.velocity += direction * 0.25

    def slowDown(self):
        if self.velocity.length() > 0:
            self.velocity -= self.velocity.normalize() * 0.25

            if self.velocity.length() < 0.25:
                self.velocity = pygame.Vector2(0, 0)


class asteroid(object):
    def __init__(self):
        self.position = pygame.Vector2(random.randrange(width), random.randrange(height))
        self.velocity = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.radius = random.randint(18, 30)
        self.mass = self.radius * self.radius

    def move(self):
        self.position += self.velocity
        self.position.x %= width
        self.position.y %= height

    def draw(self, window):
        pygame.draw.circle(window, (150, 150, 150), self.position, self.radius, 2)


class missile(object):
    def __init__(self):
        direction = pygame.Vector2(0, -1).rotate(-player1.angle)
        self.position = player1.position + direction * 28
        self.velocity = direction * 7

    def move(self):
        self.position += self.velocity

    def draw(self, window):
        pygame.draw.circle(window, (255, 220, 50), self.position, 4)


class enemyMissile(object):
    def __init__(self):
        direction = player1.position - enemyPosition

        if direction.length() > 0:
            direction = direction.normalize()

        self.position = pygame.Vector2(enemyPosition)
        self.velocity = direction * 5

    def move(self):
        self.position += self.velocity

    def draw(self, window):
        pygame.draw.circle(window, (255, 0, 0), self.position, 4)

player1 = player()
asteroids = [asteroid() for i in range(6)]
missiles = []
enemyMissiles = []

enemyPosition = pygame.Vector2(width/4, height/2)
enemyAngle = 0
enemyCooldown = 0
detected = False
distance = 0
dot = 0


def redrawGameWindow():
    window.blit(background, (0, 0))
    pygame.draw.circle(window, (100, 100, 100), enemyPosition, 300, 1)

    direction = pygame.Vector2(
        math.cos(math.radians(enemyAngle)),
        -math.sin(math.radians(enemyAngle))
    )

    pygame.draw.line(window, (255, 0, 0), enemyPosition, enemyPosition + direction * 40, 3)
    pygame.draw.circle(window, (255, 0, 0) if detected else (255, 255, 255), enemyPosition, 12)

    player1.draw(window)

    for a in asteroids:
        a.draw(window)

    for m in missiles:
        m.draw(window)

    for m in enemyMissiles:
        m.draw(window)

    window.blit(font.render("score: " + str(score), True, (255, 255, 255)), (10, 10))
    window.blit(font.render("lives: " + str(lives), True, (255, 255, 255)), (10, 30))
    window.blit(font.render("distance: " + str(round(distance)), True, (255, 255, 255)), (10, 50))
    window.blit(font.render("dot product: " + str(round(dot, 2)), True, (255, 255, 255)), (10, 70))
    window.blit(font.render("enemy: " + ("attack" if detected else "patrol"), True, (255, 255, 255)), (10, 90))

    if gameover:
        window.blit(font.render("game over - press r to restart", True, (255, 0, 0)), (width/2 - 120, height/2))


run = True


async def main():
    global run, gameover, score, lives
    global player1, asteroids, missiles, enemyMissiles
    global enemyCooldown, enemyAngle, detected, distance, dot

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not gameover:
                    missiles.append(missile())

                if event.key == pygame.K_r and gameover:
                    player1 = player()
                    asteroids = [asteroid() for i in range(6)]
                    missiles = []
                    enemyMissiles = []
                    score = 0
                    lives = 3
                    enemyCooldown = 0
                    gameover = False

        if not gameover:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player1.angle += 3

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player1.angle -= 3

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player1.accelerate()
            else:
                player1.slowDown()

            player1.move()

            for a in asteroids:
                a.move()

            for i in range(len(asteroids)):
                for j in range(i + 1, len(asteroids)):
                    a = asteroids[i]
                    b = asteroids[j]
                    direction = b.position - a.position
                    d = direction.length()

                    if d < a.radius + b.radius:
                        if d == 0:
                            direction = pygame.Vector2(1, 0)
                        else:
                            direction = direction.normalize()

                        relativeVelocity = b.velocity - a.velocity
                        speed = relativeVelocity.dot(direction)

                        if speed < 0:
                            impulse = -2 * speed / (1/a.mass + 1/b.mass)
                            a.velocity -= direction * impulse/a.mass
                            b.velocity += direction * impulse/b.mass

                        a.position -= direction * 2
                        b.position += direction * 2

            for m in missiles[:]:
                m.move()

                if not (0 <= m.position.x <= width and 0 <= m.position.y <= height):
                    missiles.remove(m)
                    continue

                for a in asteroids[:]:
                    if m.position.distance_to(a.position) < a.radius:
                        asteroids.remove(a)
                        missiles.remove(m)
                        asteroids.append(asteroid())
                        score += 10
                        break

            for a in asteroids:
                if player1.position.distance_to(a.position) < a.radius + 20:
                    lives -= 1
                    player1.position = pygame.Vector2(width/2, height/2)
                    player1.velocity = pygame.Vector2(0, 0)

                    if lives <= 0:
                        gameover = True
                    break

            enemyAngle = (enemyAngle + 0.5) % 360

            direction = pygame.Vector2(
                math.cos(math.radians(enemyAngle)),
                -math.sin(math.radians(enemyAngle))
            )

            toPlayer = player1.position - enemyPosition
            distance = enemyPosition.distance_to(player1.position)

            if toPlayer.length() > 0:
                toPlayer = toPlayer.normalize()
                dot = direction.dot(toPlayer)
            else:
                dot = 1

            detected = distance < 300 and dot > 0.7

            if enemyCooldown > 0:
                enemyCooldown -= 1

            if detected and enemyCooldown == 0:
                enemyMissiles.append(enemyMissile())
                enemyCooldown = 60

            for m in enemyMissiles[:]:
                m.move()

                if not (0 <= m.position.x <= width and 0 <= m.position.y <= height):
                    enemyMissiles.remove(m)
                    continue
                if m.position.distance_to(player1.position) < 15:
                    enemyMissiles.remove(m)
                    lives -= 1
                    player1.position = pygame.Vector2(width/2, height/2)
                    player1.velocity = pygame.Vector2(0, 0)

                    if lives <= 0:
                        gameover = True

        redrawGameWindow()
        pygame.display.update()

        await asyncio.sleep(0)
    pygame.quit()
asyncio.run(main())

import pygame
class FloatingText:
    def __init__(self, text, x, y, color=(136, 0, 21), duration=2000):  # משך במילישניות
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

    def is_expired(self):
        return pygame.time.get_ticks() - self.start_time > self.duration

    def draw(self, surface):
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, self.color)
        surface.blit(text_surface, (self.x, self.y))
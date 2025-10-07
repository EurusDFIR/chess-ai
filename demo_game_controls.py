"""
Demo Game Controls - Test UI mới
Chạy file này để xem các nút mới: Resign, Draw, Rematch, Home
"""
import os
import sys
import pygame
import pygame_gui

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.gui.game_controls import get_game_controls

def main():
    pygame.init()
    
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Controls Demo - Eury Engine")
    
    clock = pygame.time.Clock()
    theme_path = os.path.join("src", "gui", "theme.json")
    manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path)
    
    # Create game controls
    controls = get_game_controls(manager, WIDTH, HEIGHT)
    controls.create_game_buttons()
    controls.show_game_buttons(game_active=True)
    
    # Demo state
    game_result = None
    show_result = False
    
    # Info text
    font = pygame.font.Font(None, 24)
    
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == controls.resign_button:
                        print("🏳️ Player resigned!")
                        game_result = 'black_win'
                        show_result = True
                        controls.show_game_buttons(game_active=False)
                    
                    elif event.ui_element == controls.draw_button:
                        print("🤝 Draw offered/accepted!")
                        game_result = 'draw'
                        show_result = True
                        controls.show_game_buttons(game_active=False)
                    
                    elif event.ui_element == controls.rematch_button:
                        print("🔄 Rematch! Starting new game...")
                        game_result = None
                        show_result = False
                        controls.show_game_buttons(game_active=True)
                    
                    elif event.ui_element == controls.home_button:
                        print("🏠 Going home...")
                        running = False
            
            manager.process_events(event)
        
        manager.update(time_delta)
        
        # Draw
        screen.fill((50, 55, 60))
        
        # Draw fake chessboard
        board_size = 512
        board_x = 20
        board_y = (HEIGHT - board_size) // 2
        for row in range(8):
            for col in range(8):
                color = (220, 230, 240) if (row + col) % 2 == 0 else (150, 170, 190)
                pygame.draw.rect(screen, color, (board_x + col * 64, board_y + row * 64, 64, 64))
        
        # Draw info
        info_texts = [
            "Game Controls Demo",
            "",
            "Click buttons to test:",
            "⚔ Resign - End game (you lose)",
            "🤝 Draw - Offer/accept draw",
            "🔄 Rematch - Start new game",
            "🏠 Home - Return to menu",
            "",
            f"Selected Time: {controls.get_selected_time_control()['name']}",
            f"Selected AI: {controls.get_selected_ai_level()['name']}",
        ]
        
        y = 50
        for text in info_texts:
            if text:
                rendered = font.render(text, True, (220, 220, 220))
                screen.blit(rendered, (560, y))
            y += 30
        
        manager.draw_ui(screen)
        
        # Draw game result overlay if needed
        if show_result:
            controls.draw_game_status(screen, game_result)
        
        pygame.display.flip()
    
    pygame.quit()
    print("✅ Demo ended")

if __name__ == "__main__":
    main()

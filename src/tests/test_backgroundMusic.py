import pygame
import os

# Initialize pygame and the mixer
pygame.init()
pygame.mixer.init()

# Construct the correct path to the music file in the 'gui/assets/music' folder
music_path = os.path.join(os.path.dirname(__file__), "..", "gui", "assets", "music", "background_music.mp3")

# Normalize the path for cross-platform compatibility
music_path = os.path.normpath(music_path)

# Check if the file exists before trying to load it
if not os.path.exists(music_path):
    print(f"Error: Music file not found at '{music_path}'. Please ensure the file exists.")
else:
    try:
        # Load and play the music
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # Play music in a loop
        pygame.mixer.music.set_volume(1.0)
        print("Playing music...")
    except pygame.error as e:
        print(f"Error loading music file: {e}")

# Keep the program running for 10 seconds to hear the music
pygame.time.delay(1000000)

# Quit pygame once the program is done
pygame.quit()

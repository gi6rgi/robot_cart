import threading
import time
import pygame
import cv2
import numpy as np

from src import servo
from src.camera import Camera

WINDOW_SIZE = (800, 600)
FPS = 30


class RobotController:
    def __init__(self):
        # Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Robot Control - Use Arrow Keys")
        self.clock = pygame.time.Clock()
        
        # Robot Camera
        self.camera = Camera()
        self.camera.start()
        
        # Shared variables for camera thread
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.running = True

        # Start camera capture thread
        self.camera_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.camera_thread.start()
        
        # Motor state
        self.current_action = None
    
    def _capture_loop(self):
        """Background thread that continuously captures frames"""
        while self.running:
            try:
                frame = self.camera.picam2.capture_array()
                # Convert RGB to BGR for consistency with OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                with self.frame_lock:
                    self.latest_frame = frame
                    
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"Camera error: {e}")
                time.sleep(0.1)

    def _get_latest_frame(self):
        """Get the latest frame from camera thread"""
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None
    
    def _frame_to_surface(self, frame):
        """Convert OpenCV frame to Pygame surface"""
        # Resize to window size
        frame = cv2.resize(frame, WINDOW_SIZE)
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Rotate for Pygame (OpenCV uses different coordinate system)
        frame = np.rot90(frame)
        frame = np.flipud(frame)
        # Convert to Pygame surface
        return pygame.surfarray.make_surface(frame)
    
    def _handle_controls(self):
        """Handle keyboard input for motor control"""
        keys = pygame.key.get_pressed()
        
        # Determine action based on keys
        new_action = None
        
        # Check for combination keys first
        if keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            new_action = "forward_left"
        elif keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            new_action = "forward_right"
        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            new_action = "backward_left"
        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            new_action = "backward_right"
        elif keys[pygame.K_UP]:
            new_action = "forward"
        elif keys[pygame.K_DOWN]:
            new_action = "backward"
        elif keys[pygame.K_LEFT]:
            new_action = "left"
        elif keys[pygame.K_RIGHT]:
            new_action = "right"
        
        # Only send command if action changed
        if new_action != self.current_action:
            if new_action == "forward":
                servo.forward()
            elif new_action == "backward":
                servo.backward()
            elif new_action == "left":
                servo.turn_left()
            elif new_action == "right":
                servo.turn_right()
            elif new_action == "forward_left":
                # Move forward while turning left - one motor faster than the other
                servo.set_lr(servo.STOP + servo.SPD, servo.STOP - servo.SPD // 2)
            elif new_action == "forward_right":
                # Move forward while turning right
                servo.set_lr(servo.STOP + servo.SPD // 2, servo.STOP - servo.SPD)
            elif new_action == "backward_left":
                # Move backward while turning left
                servo.set_lr(servo.STOP - servo.SPD // 2, servo.STOP + servo.SPD)
            elif new_action == "backward_right":
                # Move backward while turning right
                servo.set_lr(servo.STOP - servo.SPD, servo.STOP + servo.SPD // 2)
            else:
                servo.stop()
            
            self.current_action = new_action

    def run(self):
        """Main control loop"""
        print("Robot Control Started!")
        print("Controls:")
        print("  ↑ : Forward")
        print("  ↓ : Backward")
        print("  ← : Turn Left")
        print("  → : Turn Right")
        print("  SPACE/ESC : Stop and Exit")
        
        try:
            while self.running:
                # Handle Pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
                            self.running = False
                
                # Get and display latest camera frame
                frame = self._get_latest_frame()
                if frame is not None:
                    surface = self._frame_to_surface(frame)
                    self.screen.blit(surface, (0, 0))
                
                # Handle motor controls
                self._handle_controls()
                
                # Draw control hints on screen
                font = pygame.font.Font(None, 36)
                text = font.render("Use Arrow Keys | ESC to Exit", True, (255, 255, 0))
                text_rect = text.get_rect(center=(WINDOW_SIZE[0]//2, 30))
                # Add background for better visibility
                background = pygame.Surface((text_rect.width + 20, text_rect.height + 10))
                background.set_alpha(128)
                background.fill((0, 0, 0))
                self.screen.blit(background, (text_rect.x - 10, text_rect.y - 5))
                self.screen.blit(text, text_rect)
                
                # Update display
                pygame.display.flip()
                self.clock.tick(FPS)
                
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nStopping robot...")
        self.running = False
        servo.stop()
        time.sleep(0.1)
        self.camera.stop()
        pygame.quit()
        print("Robot stopped. Goodbye!")

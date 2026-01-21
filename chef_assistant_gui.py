#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chef Assistant GUI - Interactive cooking assistant with camera feed and chat interface
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import cv2
from PIL import Image, ImageTk
import threading
import time
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chef_assistant import ChefAssistant, load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChefAssistantGUI:
    """GUI for Chef Assistant with camera feed and chat interface."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Chef Assistant - Interactive Cooking Helper")
        self.root.geometry("1280x720")
        self.root.configure(bg="#2C3E50")
        
        # Initialize variables
        self.assistant = None
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.recipe_loaded = False
        
        # Create UI components
        self.create_widgets()
        
        # Initialize Chef Assistant
        self.initialize_assistant()
        
        # Start camera feed
        self.start_camera()
        
    def create_widgets(self):
        """Create all UI widgets."""
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Camera Feed
        left_frame = tk.Frame(main_frame, bg="#34495E", relief=tk.RAISED, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Camera title
        camera_title = tk.Label(
            left_frame,
            text="📹 Camera Feed",
            font=("Arial", 16, "bold"),
            bg="#34495E",
            fg="white"
        )
        camera_title.pack(pady=10)
        
        # Camera display
        self.camera_label = tk.Label(left_frame, bg="black")
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Camera status
        self.camera_status = tk.Label(
            left_frame,
            text="Camera: Initializing...",
            font=("Arial", 10),
            bg="#34495E",
            fg="#ECF0F1"
        )
        self.camera_status.pack(pady=5)
        
        # Right panel - Chat Interface
        right_frame = tk.Frame(main_frame, bg="#34495E", relief=tk.RAISED, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Chat title
        chat_title = tk.Label(
            right_frame,
            text="💬 Chef Assistant",
            font=("Arial", 16, "bold"),
            bg="#34495E",
            fg="white"
        )
        chat_title.pack(pady=10)
        
        # Recipe info panel
        info_frame = tk.Frame(right_frame, bg="#2C3E50")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.recipe_name_label = tk.Label(
            info_frame,
            text="Recipe: Not loaded",
            font=("Arial", 12, "bold"),
            bg="#2C3E50",
            fg="#3498DB"
        )
        self.recipe_name_label.pack(anchor=tk.W)
        
        self.step_label = tk.Label(
            info_frame,
            text="Step: 0/0",
            font=("Arial", 10),
            bg="#2C3E50",
            fg="#ECF0F1"
        )
        self.step_label.pack(anchor=tk.W)
        
        # Chat history
        chat_frame = tk.Frame(right_frame, bg="#34495E")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#ECF0F1",
            fg="#2C3E50",
            state=tk.DISABLED,
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for different message types
        self.chat_display.tag_config("user", foreground="#2980B9", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("assistant", foreground="#27AE60", font=("Arial", 11))
        self.chat_display.tag_config("system", foreground="#E74C3C", font=("Arial", 10, "italic"))
        self.chat_display.tag_config("warning", foreground="#E67E22", font=("Arial", 11, "bold"))
        
        # Input frame
        input_frame = tk.Frame(right_frame, bg="#34495E")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Command entry
        self.command_entry = tk.Entry(
            input_frame,
            font=("Arial", 12),
            bg="#ECF0F1",
            fg="#2C3E50"
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.command_entry.bind("<Return>", lambda e: self.send_command())
        
        # Send button
        send_button = tk.Button(
            input_frame,
            text="Send",
            font=("Arial", 12, "bold"),
            bg="#27AE60",
            fg="white",
            command=self.send_command,
            cursor="hand2"
        )
        send_button.pack(side=tk.RIGHT)
        
        # Quick action buttons
        button_frame = tk.Frame(right_frame, bg="#34495E")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        buttons = [
            ("Next Step", "next", "#3498DB"),
            ("What is This?", "what is this", "#9B59B6"),
            ("How Much?", "how much", "#E67E22"),
            ("Repeat", "repeat", "#1ABC9C"),
            ("Help", "help", "#F39C12"),
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 10),
                bg=color,
                fg="white",
                command=lambda cmd=command: self.quick_command(cmd),
                cursor="hand2",
                width=12
            )
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Load Recipe button
        load_frame = tk.Frame(right_frame, bg="#34495E")
        load_frame.pack(fill=tk.X, padx=10, pady=10)
        
        load_button = tk.Button(
            load_frame,
            text="📖 Load Recipe (Poha)",
            font=("Arial", 12, "bold"),
            bg="#E74C3C",
            fg="white",
            command=self.load_recipe,
            cursor="hand2"
        )
        load_button.pack(fill=tk.X)
        
    def initialize_assistant(self):
        """Initialize the Chef Assistant."""
        try:
            self.add_message("Initializing Chef Assistant...", "system")
            config = load_config()
            self.assistant = ChefAssistant(config)
            self.add_message("✓ Chef Assistant initialized successfully!", "system")
            self.add_message("\nWelcome! Load a recipe to begin cooking.", "assistant")
        except Exception as e:
            self.add_message(f"✗ Error initializing: {e}", "system")
            logger.error(f"Initialization error: {e}")
    
    def start_camera(self):
        """Start the camera feed."""
        self.is_running = True
        self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
        self.camera_thread.start()
    
    def camera_loop(self):
        """Main camera loop (runs in separate thread)."""
        try:
            # Try to open camera
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                self.root.after(0, lambda: self.camera_status.config(
                    text="Camera: Not available (using placeholder)",
                    fg="#E74C3C"
                ))
                # Use placeholder image
                self.use_placeholder_camera()
                return
            
            self.root.after(0, lambda: self.camera_status.config(
                text="Camera: Connected ✓",
                fg="#27AE60"
            ))
            
            while self.is_running:
                ret, frame = self.camera.read()
                
                if ret:
                    # Store current frame for processing
                    self.current_frame = frame.copy()
                    
                    # Convert BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Resize to fit display
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Convert to PIL Image
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Update label
                    self.camera_label.imgtk = imgtk
                    self.camera_label.configure(image=imgtk)
                
                time.sleep(0.03)  # ~30 FPS
                
        except Exception as e:
            logger.error(f"Camera error: {e}")
            self.root.after(0, lambda: self.camera_status.config(
                text=f"Camera: Error - {e}",
                fg="#E74C3C"
            ))
            self.use_placeholder_camera()
    
    def use_placeholder_camera(self):
        """Display placeholder when camera is not available."""
        while self.is_running:
            # Create placeholder image
            placeholder = Image.new('RGB', (640, 480), color=(52, 73, 94))
            
            # Add text (you can use PIL.ImageDraw for better text)
            imgtk = ImageTk.PhotoImage(image=placeholder)
            
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
            
            time.sleep(1)
    
    def load_recipe(self):
        """Load a recipe."""
        try:
            recipe_path = "recipes/poha.json"
            
            if not Path(recipe_path).exists():
                self.add_message(f"✗ Recipe not found: {recipe_path}", "system")
                return
            
            self.add_message(f"Loading recipe: {recipe_path}", "system")
            self.assistant.start_session(recipe_path)
            
            # Update UI - session is a dict, access with keys
            if self.assistant.session and self.assistant.session.get('active'):
                recipe_name = self.assistant.session['recipe'].get("name", "Unknown")
                total_steps = len(self.assistant.session['recipe'].get("steps", []))
            
                self.recipe_name_label.config(text=f"Recipe: {recipe_name}")
                self.step_label.config(text=f"Step: 0/{total_steps}")
                self.recipe_loaded = True
                
                self.add_message(f"✓ Recipe loaded: {recipe_name}", "system")
                self.add_message(f"Total steps: {total_steps}", "system")
                self.add_message("\nReady to cook! Say 'next' to begin.", "assistant")
            else:
                self.add_message("✗ Error: Session not initialized", "system")

        except Exception as e:
            self.add_message(f"✗ Error loading recipe: {e}", "system")
            logger.error(f"Recipe load error: {e}")
            import traceback
            traceback.print_exc()
    
    def send_command(self):
        """Send user command to assistant."""
        command = self.command_entry.get().strip()
        
        if not command:
            return
        
        # Clear input
        self.command_entry.delete(0, tk.END)
        
        # Display user message
        self.add_message(f"You: {command}", "user")
        
        # Process command in background
        threading.Thread(target=self.process_command, args=(command,), daemon=True).start()
    
    def quick_command(self, command):
        """Execute quick command button."""
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, command)
        self.send_command()
    
    def process_command(self, command):
        """Process command with assistant."""
        try:
            if not self.recipe_loaded and command.lower() != "help":
                self.add_message("⚠ Please load a recipe first!", "warning")
                return
            
            # Process command
            response = self.assistant.process_voice_command(command)

            # Update step counter - session is a dict
            if self.assistant.session and self.assistant.session.get('active'):
                validator = self.assistant.session.get('validator')
                if validator:
                    current_step = validator.current_step
                    total_steps = len(self.assistant.session['recipe'].get("steps", []))
                self.root.after(0, lambda: self.step_label.config(
                    text=f"Step: {current_step}/{total_steps}"
                ))
            
            # Display response
            if response:
                self.add_message(f"Assistant: {response}", "assistant")
            
        except Exception as e:
            self.add_message(f"✗ Error: {e}", "system")
            logger.error(f"Command processing error: {e}")
            import traceback
            traceback.print_exc()
    
    def add_message(self, message, msg_type="assistant"):
        """Add message to chat display."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n\n", msg_type)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def cleanup(self):
        """Cleanup resources."""
        self.is_running = False
        
        if self.camera:
            self.camera.release()
        
        if self.assistant:
            self.assistant.cleanup()
        
        cv2.destroyAllWindows()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = ChefAssistantGUI(root)
    
    # Handle window close
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit Chef Assistant?"):
            app.cleanup()
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

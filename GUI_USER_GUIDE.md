# Chef Assistant GUI - User Guide

## 🎨 Overview

The Chef Assistant GUI provides a visual interface with:
- **Live camera feed** - See ingredients and cooking process
- **Interactive chat** - Text-based communication with the assistant
- **Recipe tracking** - Visual step counter and progress
- **Quick action buttons** - Fast access to common commands

---

## 🚀 Quick Start

### Launch the GUI

**Option 1: Using the batch file (Windows)**
```cmd
run_gui.bat
```

**Option 2: Using Python directly**
```cmd
python chef_assistant_gui.py
```

---

## 📋 GUI Layout

### Left Panel: Camera Feed (640x480)
- Shows live video from your webcam
- Used for ingredient identification and quantity checking
- If no camera is available, shows placeholder image
- Camera status indicator at bottom

### Right Panel: Chat Interface

#### 1. Recipe Information Bar
- **Recipe Name**: Currently loaded recipe
- **Step Counter**: Current step / Total steps

#### 2. Chat History
- **User messages** (Blue): Your commands
- **Assistant responses** (Green): Chef's guidance
- **System messages** (Red): Status updates
- **Warnings** (Orange): Important alerts

#### 3. Text Input Field
- Type your commands here
- Press **Enter** to send

#### 4. Quick Action Buttons
- **Next Step** - Move to next cooking step
- **What is This?** - Identify ingredient in camera
- **How Much?** - Check quantity measurement
- **Repeat** - Hear last instruction again
- **Help** - Show available commands

#### 5. Load Recipe Button
- Click to load the Poha recipe
- Required before starting cooking

---

## 💬 Available Commands

### Navigation Commands
- `next` or `next step` - Move to next cooking step
- `previous` or `back` - Go back one step
- `repeat` - Repeat current instruction

### Ingredient Commands
- `what is this` - Identify ingredient in camera
- `is this correct` - Verify ingredient matches recipe

### Quantity Commands
- `how much` - Check if quantity is correct
- `show measurement` - Display measurement guide

### Help & Control
- `help` - List all available commands
- `stop` - End cooking session
- `exit` - Close the application

---

## 🎯 How to Use

### Step-by-Step Cooking Session

1. **Launch the GUI**
   ```cmd
   run_gui.bat
   ```

2. **Wait for initialization**
   - GUI will display "Chef Assistant initialized successfully!"
   - Camera feed will start automatically

3. **Load a recipe**
   - Click the **"📖 Load Recipe (Poha)"** button
   - Recipe information will appear at the top
   - Chat will confirm recipe is loaded

4. **Start cooking**
   - Click **"Next Step"** or type `next`
   - Follow the instructions displayed in chat
   - Camera will show your cooking area

5. **Identify ingredients** (when prompted)
   - Hold ingredient in front of camera
   - Click **"What is This?"** button
   - Assistant will identify the ingredient

6. **Check quantities**
   - Hold measuring spoon/cup in front of camera
   - Click **"How Much?"** button
   - Assistant will verify the amount

7. **Navigate through recipe**
   - Use **"Next Step"** to advance
   - Use **"Repeat"** to hear instructions again
   - Progress tracked in step counter

8. **Complete cooking**
   - When done, click **"Stop"** or type `stop`
   - Session summary will be displayed

---

## 🔧 Features

### Camera Feed Features
- **Real-time video**: 30 FPS live feed
- **Ingredient recognition**: AI-powered identification
- **Quantity validation**: Check measurements
- **Fallback mode**: Works without camera (placeholder shown)

### Chat Interface Features
- **Color-coded messages**: Easy to distinguish message types
- **Auto-scroll**: Always shows latest message
- **Command history**: Scroll to see previous interactions
- **Quick buttons**: One-click common commands

### Recipe Features
- **Step-by-step guidance**: Clear instructions
- **Safety warnings**: Highlighted in orange
- **Progress tracking**: Visual step counter
- **Ingredient prompts**: Reminders to verify items

---

## ⚙️ Troubleshooting

### Camera Not Working
**Problem**: Camera shows "Not available" or black screen

**Solutions**:
1. Check if camera is connected
2. Close other apps using the camera (Zoom, Teams, etc.)
3. Try a different USB port
4. Restart the application
5. GUI works without camera (shows placeholder)

### Recipe Not Loading
**Problem**: "Recipe not found" error

**Solutions**:
1. Ensure `recipes/poha.json` exists
2. Check file path is correct
3. Verify JSON file is valid

### Commands Not Working
**Problem**: Assistant doesn't respond to commands

**Solutions**:
1. Load a recipe first (click Load Recipe button)
2. Check spelling of commands
3. Use Quick Action buttons instead
4. Check logs for errors

### GUI Won't Start
**Problem**: Application crashes on launch

**Solutions**:
1. Install dependencies:
   ```cmd
   pip install opencv-python pillow tkinter
   ```
2. Check Python version (3.8+ required)
3. Run from command line to see errors:
   ```cmd
   python chef_assistant_gui.py
   ```

---

## 🎨 Customization

### Change Window Size
Edit `chef_assistant_gui.py`:
```python
self.root.geometry("1280x720")  # Change to desired size
```

### Change Colors
Modify color codes in the `create_widgets` method:
- Background: `#2C3E50` (dark blue-gray)
- Panels: `#34495E` (lighter blue-gray)
- Buttons: Various colors for different actions

### Add More Recipes
1. Create new recipe JSON in `recipes/` folder
2. Modify `load_recipe` method to include recipe selection

---

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB
- **Camera**: Optional (works without)

### Recommended Requirements
- **OS**: Windows 11
- **Python**: 3.10+
- **RAM**: 8GB
- **Camera**: USB webcam or built-in (720p+)
- **Screen**: 1280x720 or higher

---

## 🔑 Keyboard Shortcuts

- **Enter** - Send command
- **Esc** - Clear input field (when focused)
- **Alt+F4** - Close application (Windows)

---

## 📝 Tips for Best Experience

### Camera Tips
1. **Good lighting**: Ensure ingredients are well-lit
2. **Stable position**: Keep camera steady
3. **Clear background**: Remove clutter from frame
4. **Close-up shots**: Hold items 6-12 inches from camera

### Interaction Tips
1. **Use Quick Buttons**: Faster than typing
2. **Read warnings**: Pay attention to orange safety alerts
3. **Check step counter**: Track your progress
4. **Repeat when needed**: Don't hesitate to ask for repeats

### Cooking Tips
1. **Prep ingredients**: Have everything ready before starting
2. **Follow safety warnings**: Especially for hot oil/surfaces
3. **Verify quantities**: Use "how much" feature frequently
4. **Take your time**: No rush, cook at your pace

---

## 🆘 Support

### Get Help
- Type `help` in chat for command list
- Check `TEST_RESULTS.md` for system status
- Review `SETUP_STATUS.md` for configuration

### Report Issues
- Check logs in `logs/chef_assistant.log`
- Note error messages from GUI
- Describe steps to reproduce problem

---

## 🎯 What's Next?

### Current Features
✅ Camera feed display
✅ Interactive chat
✅ Recipe loading and tracking
✅ Quick action buttons
✅ Command processing
✅ Safety warnings

### Future Enhancements
🔜 Voice input integration
🔜 Multiple recipe selection
🔜 Recipe history
🔜 Cooking timer
🔜 Shopping list generator
🔜 Nutritional information

---

**Enjoy cooking with Chef Assistant! 👨‍🍳**

*Last Updated: 2026-01-20*

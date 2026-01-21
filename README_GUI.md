# 🎨 Chef Assistant GUI - Quick Start

## Launch the GUI

### Windows
```cmd
run_gui.bat
```

### Linux/Mac
```bash
python3 chef_assistant_gui.py
```

---

## What You'll See

### GUI Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chef Assistant - Interactive Cooking Helper   │
├──────────────────────────┬──────────────────────────────────────┤
│                          │  💬 Chef Assistant                    │
│   📹 Camera Feed         │  ┌─────────────────────────────────┐  │
│                          │  │ Recipe: Poha                    │  │
│  ┌────────────────────┐  │  │ Step: 2/8                       │  │
│  │                    │  │  └─────────────────────────────────┘  │
│  │   Live Video       │  │                                       │
│  │   640 x 480        │  │  ┌─────────────────────────────────┐  │
│  │                    │  │  │ Chat History                    │  │
│  │                    │  │  │                                 │  │
│  │                    │  │  │ User: next                      │  │
│  │                    │  │  │                                 │  │
│  └────────────────────┘  │  │ Assistant: Heat 2 teaspoons...  │  │
│                          │  │                                 │  │
│  Camera: Connected ✓     │  │                                 │  │
│                          │  └─────────────────────────────────┘  │
│                          │                                       │
│                          │  ┌─────────────────────────────────┐  │
│                          │  │ Type command here...            │  │
│                          │  └─────────────────────────────────┘  │
│                          │                                       │
│                          │  [Next] [What is This?] [How Much?]  │
│                          │  [Repeat] [Help]                      │
│                          │                                       │
│                          │  [📖 Load Recipe (Poha)]              │
└──────────────────────────┴──────────────────────────────────────┘
```

---

## Step-by-Step Usage

### 1. Start the Application
Double-click `run_gui.bat` or run:
```cmd
python chef_assistant_gui.py
```

### 2. Load Recipe
- Click the **"📖 Load Recipe (Poha)"** button
- Wait for confirmation message

### 3. Start Cooking
- Click **"Next Step"** button to begin
- Follow instructions in chat window

### 4. Use Quick Actions
- **Next Step** - Move forward in recipe
- **What is This?** - Point camera at ingredient
- **How Much?** - Check quantity measurement
- **Repeat** - Hear last instruction again
- **Help** - Show all commands

### 5. Type Custom Commands
Type in the input box and press Enter:
- `next`
- `what is this`
- `how much`
- `repeat`
- `help`
- `stop`

---

## Features at a Glance

### ✅ Working Features
- ✓ Live camera feed (or placeholder if no camera)
- ✓ Interactive text chat
- ✓ Recipe step tracking
- ✓ Quick action buttons
- ✓ Safety warnings display
- ✓ Ingredient identification (simulated if no camera)
- ✓ Quantity checking (simulated if no camera)
- ✓ Color-coded messages

### ⚠️ Camera Required For
- Real-time ingredient recognition
- Actual quantity verification
- Visual cooking assistance

Without camera: GUI still works with text-based interaction and mock responses.

---

## Quick Tips

💡 **Click buttons** instead of typing for faster interaction  
💡 **Watch the step counter** to track your progress  
💡 **Read orange warnings** for safety alerts  
💡 **Use "Repeat"** if you missed an instruction  

---

## Troubleshooting

### GUI won't start?
```cmd
pip install opencv-python pillow
python chef_assistant_gui.py
```

### Camera not working?
- GUI works fine without camera (shows placeholder)
- Check if other apps are using camera
- Try unplugging/replugging USB camera

### Commands not responding?
- Make sure you clicked "Load Recipe" first
- Use Quick Action buttons
- Check chat window for error messages

---

## Full Documentation

📖 See `GUI_USER_GUIDE.md` for complete documentation

---

**Ready to cook? Launch the GUI and enjoy! 👨‍🍳**

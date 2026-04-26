# Spinemaniax


<img width="2559" height="1353" alt="image" src="https://github.com/user-attachments/assets/438e46b0-3051-48ac-ac2e-35f40ed890f1" />

<img width="2555" height="1348" alt="image" src="https://github.com/user-attachments/assets/5b781436-3ffd-4c51-9eed-b61b65447f91" />

<img width="432" height="694" alt="image" src="https://github.com/user-attachments/assets/646e0b30-c1c6-4de8-83e0-e2b983532842" />

Spinemaniax is a fully featured, interactive GUI application built with Python and Tkinter. It provides a customizable spinning wheel to randomly select options, making it perfect for giveaways, decision making, games, and more. 

The application offers smooth animations, a modern and responsive user interface, detailed win tracking across multiple rounds, and deep aesthetic customization. 

## ✨ Features

- **Dynamic Spinning Wheel:** A visually appealing wheel rendered dynamically using Python's `Pillow` library, complete with wobble effects, smooth acceleration, and deceleration.
- **Custom Options:** Easily add, remove, and rename options on the wheel.
- **Random Name Generation:** Don't know what to put? Use the "Random" button to generate funny "Adjective + Noun" combinations automatically.
- **Round Tracking:** Set the number of rounds you want to play. The application keeps track of each round's winner in a built-in results table and determines the overall winner at the end!
- **Deep Customization (Appearance Tab):**
  - **Themes:** Toggle between Light and Dark modes seamlessly.
  - **Button Colors:** Customize the UI button colors or randomize them for a fun look.
  - **Wheel Palettes:** Choose from preset color palettes for the wheel like *Vibrant*, *Pastel*, or *Neon*, or fully randomize the wheel's colors.
- **Responsive UI:** The application window is fully resizable. Fonts and the wheel canvas automatically scale to fit your screen perfectly.
- ** Secret Weighted Probabilities:** A hidden menu allows you to set custom winning probabilities for each option on the wheel!

## 🛠️ Prerequisites

To run this application, you need Python installed on your system along with the `Pillow` library for advanced image rendering.

```bash
pip install Pillow
```

## 🚀 How to Run (If you don't run the exe directly)

1. Clone or download this repository.
2. Navigate to the project directory.
3. Run the main script:

```bash
python main.py
```

## 📖 How to Use

### Basic Usage
1. When you launch the app, you will see default options.
2. Click **"Add Option"** to add more segments to the wheel, or **"Remove Option"** to delete them.
3. Type names into the text boxes or click **"Random"** to generate fun names.
4. Set the **"Number of Rounds"** using the `+` and `-` buttons at the bottom.
5. Click **"Spin the Wheel 🎡"** and watch it go! 
6. (Optional) If the spin is taking too long, click **"Stop"** to immediately jump to the result.

### Appearance Settings
Click on the **"Appearance"** tab at the top of the window to access aesthetic customizations.
- Use **"Toggle Dark/Light"** to switch the main theme.
- Customize button colors or pick a completely new color palette for your wheel segments.

###  The Hidden Menu (Weighted Probabilities)
Want to "rig" the wheel or give certain options a higher chance of winning?
1. In the main "Spin Chart" tab, press `Ctrl + Shift + P` on your keyboard.
2. A hidden **"Set Winning Probabilities"** menu will appear.
3. Here, you can define exact percentage chances (0-100%) for each option to win. The application will automatically balance them so they always sum up to exactly 100%.
4. Click **"Save"** and spin the wheel. The visual wheel remains the same, but the outcome will favor your custom odds!

## 📂 Project Structure

- `main.py` - The entry point of the application.
- `app.py` - Contains the main GUI logic, layout, and event handling (`SpinChartApp`).
- `wheel_renderer.py` - Handles the high-quality drawing and rotation of the wheel graphics using `Pillow`.
- `appearance_tab.py` - Contains the logic and UI for the appearance settings menu.
- `hidden_menu.py` - The logic for the secret probabilities dialog.
- `constants.py` - Stores theme colors, layout constants, and word lists for random generation.
- `utils.py` - Helper functions for text rendering, probability distribution, and random name generation.

---
*Enjoy spinning!* 🏆








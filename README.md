# 🇳🇵 Nepal Inflation Visualizer - Enhanced Edition

A beautiful, interactive visualization tool that demonstrates how inflation erodes purchasing power over time, specifically designed for Nepal's currency and economic context.

![Nepal Flag](https://img.shields.io/badge/🇳🇵-Nepal-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenGL](https://img.shields.io/badge/OpenGL-Graphics-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### 📊 Interactive Visualization
- **Real-time inflation simulation** with adjustable rates (0-25%)
- **Time period analysis** from 1 to 30 years
- **Multiple denominations** of Nepali currency (Rs. 5 to Rs. 1000)
- **Purchasing power timeline** showing year-by-year value erosion

### 💰 Economic Analysis
- **Visual money scaling** that shrinks as purchasing power decreases
- **Buying power comparison** showing what you can afford today vs. future
- **Color-coded indicators**: Green (healthy) → Yellow (moderate) → Red (severe)
- **Real-world examples** with common Nepali items and prices

### 🎨 Modern UI Design
- **Clean, professional interface** with smooth animations
- **Dark theme** optimized for long viewing sessions
- **Responsive controls** with sliders, buttons, and keyboard shortcuts
- **Ghost outlines** showing original vs. current purchasing power

### 🏗️ Technical Excellence
- **Modular architecture** with separated concerns
- **OpenGL graphics** for smooth, hardware-accelerated rendering
- **JSON configuration** for easy customization of data and text
- **Cross-platform compatibility** (Windows, macOS, Linux)

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/nischal0x01/inflation-visualizer.git
   cd inflation-visualizer
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

## 🎮 Controls

### 🖱️ Mouse/Touch
- **Drag sliders** to adjust inflation rate and time period
- **Click buttons** to select denominations or toggle features
- **Hover effects** for better user feedback

### ⌨️ Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `W` / `↑` | Increase inflation rate |
| `S` / `↓` | Decrease inflation rate |
| `A` / `←` | Decrease time period |
| `D` / `→` | Increase time period |
| `1-7` | Select denomination (Rs. 5, 10, 20, 50, 100, 500, 1000) |
| `SPACE` | Toggle auto-play mode |
| `R` | Reset to defaults |
| `ESC` | Exit application |

## 📁 Project Structure

```
inflation-visualizer/
├── src/
│   ├── main.py              # Main application entry point
│   ├── formulas.py          # Financial calculations and math functions
│   ├── ui_theme.py          # Color palette and styling constants
│   ├── graphics_utils.py    # OpenGL drawing primitives and utilities
│   ├── config.json          # Configuration data and localization
│   └── opengl.py           # Additional OpenGL utilities
├── assets/
│   └── fullmoneyasset.jpg   # Currency sprite sheet
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### 🏛️ Architecture Highlights

- **formulas.py**: Pure mathematical functions for inflation calculations
- **ui_theme.py**: Centralized theming and color management
- **graphics_utils.py**: Reusable OpenGL drawing components
- **config.json**: Data-driven configuration for easy localization

## 🎯 Use Cases

### 📚 Educational
- **Economics teachers** demonstrating inflation concepts
- **Students** learning about monetary policy and purchasing power
- **Financial literacy programs** in Nepal

### 💼 Professional
- **Financial advisors** explaining long-term investment importance
- **Policy makers** visualizing economic impact scenarios
- **Researchers** studying inflation effects on different income groups

### 🏠 Personal
- **Individuals** planning long-term finances
- **Families** understanding the importance of inflation-beating investments
- **Anyone** curious about economic concepts

## 🛠️ Technical Details

### Dependencies
- **glfw**: Modern OpenGL window management
- **PyOpenGL**: Python OpenGL bindings
- **Pillow**: Image processing and text rendering
- **numpy**: Numerical computations

### System Requirements
- **RAM**: 512 MB minimum
- **GPU**: Any modern graphics card with OpenGL 2.1+ support
- **Storage**: 50 MB free space
- **Display**: 1280x800 minimum resolution

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and ensure code quality
4. **Test thoroughly** across different scenarios
5. **Submit a pull request** with a clear description

### 🐛 Bug Reports
Please use GitHub Issues to report bugs, including:
- Operating system and Python version
- Steps to reproduce the issue
- Expected vs. actual behavior
- Screenshots if applicable

## 📈 Future Enhancements

- [ ] **Multi-currency support** for other South Asian countries
- [ ] **Historical data integration** with real inflation rates
- [ ] **Export functionality** for charts and reports
- [ ] **Mobile app version** for Android/iOS
- [ ] **Web version** using WebGL
- [ ] **Advanced scenarios** with variable inflation rates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Nepal Rastra Bank** for currency design inspiration
- **OpenGL community** for excellent graphics libraries
- **Python community** for robust development tools
- **Contributors** who help improve this project

## 📞 Contact

- **GitHub**: [@nischal0x01](https://github.com/nischal0x01)
- **Project Link**: [https://github.com/nischal0x01/inflation-visualizer](https://github.com/nischal0x01/inflation-visualizer)

---

**Made with ❤️ for financial education in Nepal**

*"Understanding inflation today, securing prosperity tomorrow"*

# Set Operations Visualizer / Визуализатор операций над множествами

An interactive Python application for visualizing set theory operations using Venn diagrams with drag-and-drop functionality.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

- **Interactive Venn Diagrams**: Drag and drop circles to reposition sets A, B, and C
- **Real-time Visualization**: See set operations results instantly as you type formulas
- **Multiple Operations**: Support for union, intersection, XOR, difference, and complement
- **Smart Display**: Automatically hides unused circles based on the formula
- **Safe Expression Parsing**: Secure recursive descent parser (no `eval()`)
- **Point Count Display**: Shows the number of points in the result set
- **Optimized Performance**: Efficient grid-based computation (100×100 points)

## 📸 Screenshots

The visualizer displays three interactive circles representing sets A, B, and C. Enter formulas to see the results highlighted in purple.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/EulerRings.git
cd EulerRings
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 📖 Usage

### Supported Operations

| Operation | Syntax | Description | Example |
|-----------|--------|-------------|---------|
| **Union** | `U` | Elements in A or B (OR) | `A U B` |
| **Intersection** | `&` | Elements in both A and B (AND) | `A & B` |
| **Symmetric Difference** | `^` | Elements in A or B but not both (XOR) | `A ^ B` |
| **Difference** | `-` | Elements in A but not in B | `A - B` |
| **Complement** | `.` | Elements not in A (NOT) | `A.` |

### Formula Examples

```
A U B          # Union of A and B
A & B          # Intersection of A and B
A - B          # Elements in A but not in B
A.             # Complement of A (everything except A)
(A U B).       # Complement of union
A & B & C      # Intersection of all three sets
(A U B) - C    # Union of A and B, minus C
A ^ B          # Symmetric difference (XOR)
```

### Operator Precedence

Operations are evaluated in the following order (highest to lowest):
1. **Parentheses** `( )`
2. **NOT** `.`
3. **AND** `&`
4. **XOR** `^`
5. **DIFF** `-`
6. **OR** `U`

### Interactive Features

- **Drag Circles**: Click and drag any circle to reposition it
- **Type Formulas**: Enter set expressions in the text box
- **Reset Button**: Click "Сброс" to restore original positions
- **Auto-Hide**: Unused circles automatically hide based on your formula

## 🐛 Troubleshooting

### Common Issues

**Issue**: Window doesn't appear
- **Solution**: Make sure you have a display environment (not running headless)

**Issue**: Slow performance
- **Solution**: Reduce `GRID_SIZE` in the code (e.g., from 100 to 50)

**Issue**: Import errors
- **Solution**: Install dependencies: `pip install -r requirements.txt`

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

- Add more set operations
- Implement save/load functionality for formulas
- Add keyboard shortcuts
- Export visualizations as images
- Add animation for transitions
- Support for more than 3 sets

## 📄 License

This project is licensed under the MIT License - feel free to use it for educational or commercial purposes.

## 🙏 Acknowledgments

- Built with [NumPy](https://numpy.org/) for efficient numerical computation
- Visualization powered by [Matplotlib](https://matplotlib.org/)
- Inspired by set theory and Venn diagram visualizations

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Note**: This is an educational tool for learning set theory operations. The visualizer uses point-based approximation and may not be mathematically precise for all edge cases.

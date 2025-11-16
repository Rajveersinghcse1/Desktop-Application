# 📊 Data Viewing Guide - OpenUP

## Supported Data Formats

OpenUP now supports viewing **all data files in table format**, making it easy to inspect and analyze structured data.

---

## 📁 Supported File Types

### ✅ Currently Supported

| Format | Extensions | Domain | Description |
|--------|-----------|--------|-------------|
| **CSV** | `.csv`, `.tsv` | Data | Comma/Tab-separated values |
| **Excel** | `.xlsx`, `.xls` | Data | Microsoft Excel spreadsheets |
| **LAS/LAZ** | `.las`, `.laz` | Geospatial | LiDAR point cloud data |
| **Text** | `.txt`, `.log` | Documents | Plain text files |
| **JSON** | `.json` | Data | JSON data structures |
| **Markdown** | `.md` | Documents | Markdown documents |
| **Images** | `.png`, `.jpg`, `.bmp`, `.gif` | Images | Raster images |

---

## 🎯 How to View Data Files

### Method 1: Double-Click
1. Navigate using the file browser (left panel)
2. Double-click any supported file
3. View data in the **Metadata/Table** and **Visualization** tabs

### Method 2: Menu
1. Click `File > Open File` (or press `Ctrl+O`)
2. Select your data file
3. Data appears automatically

### Method 3: Command Line
```bash
# Launch with specific file
launch.bat "path\to\your\file.las"

# Or
python main.py "C:\Data\myfile.csv"
```

---

## 📊 Table View Features

### CSV/Excel Files
- ✅ **Auto-preview**: First 1,000 rows displayed
- ✅ **Column statistics**: Min, max, mean for numeric columns
- ✅ **Memory usage**: Shows data size in memory
- ✅ **Sortable columns**: Click headers to sort
- ✅ **Searchable**: Filter data quickly

### LAS/LAZ Point Cloud Files
- ✅ **Point preview**: First 1,000 points shown
- ✅ **All dimensions**: X, Y, Z, Intensity, Classification, etc.
- ✅ **Metadata**: Point count, bounds, scale, version
- ✅ **File info**: Size, format, coordinate system

---

## 📈 Example: Viewing RealWorld_OpenPit_Mine.las

### What You'll See

**Metadata Tab:**
```
📊 LAS Point Cloud Metadata

File Name: RealWorld_OpenPit_Mine.las
File Size: 1.7 MB
Point Count: 50,234 points
Version: 1.2
X Min/Max: 123.456 / 789.012
Y Min/Max: 234.567 / 890.123
Z Min/Max: 345.678 / 901.234

📐 Available Dimensions:
   • X
   • Y
   • Z
   • Intensity
   • Classification
   • Return Number
   • Scan Angle
```

**Visualization Tab:**
```
┌─────────────────────────────────────────────────┐
│ 📍 Displaying first 1,000 of 50,234 points     │
├─────┬──────┬──────┬─────────┬──────────────────┤
│  X  │  Y   │  Z   │ Inten.  │ Classification   │
├─────┼──────┼──────┼─────────┼──────────────────┤
│ 123 │ 234  │ 345  │ 1250    │ Ground           │
│ 124 │ 235  │ 346  │ 1180    │ Vegetation       │
│ 125 │ 236  │ 347  │ 1420    │ Building         │
│ ... │ ...  │ ...  │ ...     │ ...              │
└─────┴──────┴──────┴─────────┴──────────────────┘
```

---

## 🔧 Performance Tips

### Large Files (> 100 MB)
- Only first 1,000 rows/points displayed for speed
- Full metadata always available
- Use domain filters to focus on specific file types

### CSV Files
- Auto-detects delimiter (comma, tab, semicolon)
- Handles UTF-8 and Latin-1 encoding
- Shows column types and statistics

### LAS/LAZ Files
- Compressed LAZ files supported (requires `lazrs`)
- All point dimensions available
- Bounding box and scale information shown

---

## 🚀 Quick Start

### View Your LAS File
```bash
# From OpenUP directory
launch.bat "C:\Data\RealWorld_OpenPit_Mine.las"
```

### View CSV Data
```bash
launch.bat "C:\Data\mydata.csv"
```

### Browse and Explore
```bash
# Launch without file to browse
launch.bat
```

---

## 📚 Additional Resources

- **Plugin Development**: `docs/PLUGIN_DEVELOPMENT.md`
- **User Guide**: `docs/QUICK_START.md`
- **Developer Guide**: `docs/DEVELOPMENT.md`

---

## ✨ Pro Tips

1. **Filter by Domain**: Use checkboxes (All, Data, Geospatial, Images) to filter visible files
2. **Recent Files**: Access recently opened files via `File > Recent Files`
3. **Table Sorting**: Click column headers in table view to sort data
4. **Metadata First**: Check Metadata tab for file statistics before viewing full data
5. **Keyboard Shortcuts**: 
   - `Ctrl+O`: Open file
   - `Ctrl+R`: Refresh view
   - `Ctrl+B`: Toggle file browser

---

## 🐛 Troubleshooting

### LAS Files Show "Unsupported"
```bash
# Install laspy library
.\venv\Scripts\pip.exe install laspy lazrs
```

### CSV Not Displaying
- Check file encoding (should be UTF-8 or Latin-1)
- Verify delimiter (comma, tab, semicolon auto-detected)
- File size limit: 100 MB for preview

### Application Won't Start
```bash
# Reinstall dependencies
.\venv\Scripts\pip.exe install -r requirements.txt
```

---

**Happy Data Viewing! 📊🚀**

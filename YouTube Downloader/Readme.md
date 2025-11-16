# YouTube Downloader - Setup & Troubleshooting Guide

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
```bash
pip install pytubefix PyQt6 requests
```

Or use the requirements file:
```bash
pip install -r requirements_youtube.txt
```

2. **Run the application:**
```bash
python Youtubedownloader.py
```

## ✅ PROBLEM SOLVED: "Bad Request" Error

### What was the issue?
The original `pytube` library has compatibility issues with YouTube's API changes, causing "400 Bad Request" errors.

### Solution
We switched to **`pytubefix`** - a maintained fork that fixes these issues!

### Your problematic URL now works perfectly:
```
https://www.youtube.com/watch?v=ntRx60An1fY&t=5s
✓ Tested and working!
```

## 🔧 Troubleshooting

### If you still encounter errors:

1. **Update pytubefix:**
```bash
pip install --upgrade pytubefix
```

2. **Clear cache and reinstall:**
```bash
pip uninstall pytube pytubefix -y
pip install pytubefix
```

3. **Check video restrictions:**
- Age-restricted videos may require authentication
- Private/unlisted videos won't work
- Some region-blocked videos may fail

### Error: "Module not found"
```bash
pip install pytubefix PyQt6 requests
```

### Error: "Bad Request" persists
The application now includes:
- ✓ Automatic URL cleaning (removes &t= and &list= parameters)
- ✓ Multiple retry attempts
- ✓ Detailed error messages
- ✓ Fallback strategies

## 📝 What We Fixed

### URL Cleaning
- Removes timestamp parameters (`&t=5s`)
- Removes playlist parameters (`&list=...`)
- Normalizes youtu.be short links
- Handles malformed URLs

### Error Handling
- Multiple retry attempts
- Detailed error messages
- Logging for debugging
- Graceful degradation

### Library Compatibility
- ✓ Uses pytubefix (best compatibility)
- ✓ Falls back to pytube if needed
- ✓ Auto-detection of available library
- ✓ Version-agnostic fixes

## 🎯 Features Working

✅ Single video downloads
✅ Playlist downloads
✅ Audio extraction (MP3)
✅ Multiple quality options
✅ Thumbnail preview
✅ Progress tracking
✅ Download history
✅ Queue management
✅ Dark/Light themes
✅ Clipboard monitoring

## 🧪 Testing

Test if a URL works:
```bash
python quick_test.py
```

Run comprehensive tests:
```bash
python test_youtube_url.py
```

Update pytube/pytubefix:
```bash
python update_pytube.py
```

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytubefix | ≥6.0.0 | YouTube download (RECOMMENDED) |
| PyQt6 | ≥6.6.0 | GUI framework |
| requests | ≥2.31.0 | HTTP requests (thumbnails) |

## 🎓 Usage Tips

1. **Best Quality:** Select the highest resolution from dropdown
2. **Audio Only:** Choose "Audio Only" radio button for MP3
3. **Playlists:** Use "Fetch Playlist" button for entire playlists
4. **Queue:** Add multiple videos before downloading
5. **History:** View all downloads in History tab

## 🐛 Known Issues

1. **Age-restricted videos:** Require YouTube authentication
2. **Live streams:** Not supported
3. **Premium content:** Requires premium account
4. **Some very new videos:** May need API to catch up

## 💡 Tips

- Enable clipboard monitoring in Settings
- Use dark theme for better visibility
- Check logs folder for detailed error information
- Videos with special characters in title are automatically sanitized

## 🔗 Useful Links

- pytubefix GitHub: https://github.com/JuanBindez/pytubefix
- Report issues: Check logs/ folder for details
- PyQt6 Docs: https://www.riverbankcomputing.com/static/Docs/PyQt6/

## ✨ Success!

Your URL that was failing:
```
https://www.youtube.com/watch?v=ntRx60An1fY&t=5s
```

Now downloads successfully as:
- **Title:** Intro to PowerShell: Investigating Windows Processes
- **Author:** The Cyber Mentor
- **Duration:** 22m 40s
- **Quality:** 360p (23.1 MB)
- **Audio:** Multiple bitrates available

**Enjoy your ultra-advanced YouTube downloader! 🎉**

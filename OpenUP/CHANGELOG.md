# Changelog

All notable changes to OpenUP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-14

### Added
- Initial release of OpenUP
- Core application architecture with plugin system
- Main window with menu bar, toolbar, and status bar
- File browser with search functionality
- Domain filter for categorizing files
- Dual-tab preview (Metadata + Visualization)
- Configuration management with persistent storage
- Structured logging with rotation
- Background worker pool for async operations
- Three-tier cache system (metadata, thumbnails, processed)
- Dark and light theme support
- Text file plugin (txt, md, log, json, yaml, etc.)
- Image file plugin (png, jpg, bmp, gif, tiff, webp)
- Data file plugin (csv, tsv, xlsx, xls)
- Drag-and-drop file support
- Recent files tracking
- Settings dialog for user preferences
- Plugin information dialog
- Comprehensive documentation
- Unit tests for core components
- PyInstaller specification for executable builds
- Cross-platform support (Windows, macOS, Linux)

### Features
- **Plugin System**: Extensible architecture for adding new file formats
- **Performance**: Background workers, caching, and streaming for large files
- **UI/UX**: Intuitive interface with keyboard shortcuts
- **Configuration**: Persistent settings with JSON storage
- **Logging**: Detailed logs for debugging and monitoring
- **Testing**: Unit test framework with pytest
- **Documentation**: User guides, developer guides, and API docs

### Security
- File size validation per plugin
- Safe path handling to prevent traversal attacks
- Process isolation for background workers
- Input validation for all file operations

### Documentation
- README.md - Project overview
- QUICK_START.md - 5-minute setup guide
- DEVELOPMENT.md - Developer guide
- PLUGIN_DEVELOPMENT.md - Plugin creation tutorial
- PROJECT_SUMMARY.md - Complete project overview

## [Unreleased]

### Planned Features
- Audio/video preview plugins
- 3D model viewer plugin (obj, stl, ply)
- Geospatial data plugin (las, laz, GeoTIFF)
- Medical imaging plugin (DICOM, NIfTI)
- PDF viewer plugin with page navigation
- Code editor plugin with syntax highlighting
- Archive viewer plugin (zip, tar, rar)
- Cloud file support (S3, Azure, Google Drive)
- Plugin marketplace
- Real-time file watching
- Batch file processing
- Export functionality
- Advanced 3D rendering with Open3D
- GPU-accelerated visualization
- Mobile companion app

### Future Improvements
- Hot plugin reloading
- Plugin dependency management
- Custom keyboard shortcut configuration
- Workspace/project management
- File comparison mode
- Annotation and markup tools
- Integration with version control
- REST API for remote access
- Telemetry and crash reporting (opt-in)

## Version History

### Version Numbering

OpenUP follows [Semantic Versioning](https://semver.org/):

- **Major version** (X.0.0): Breaking changes, major new features
- **Minor version** (1.X.0): New features, backward compatible
- **Patch version** (1.0.X): Bug fixes, minor improvements

### Support Policy

- **Current version** (1.x.x): Full support
- **Previous major version** (0.x.x): Security fixes only
- **Older versions**: No support

## Contributing

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**OpenUP Development Team**

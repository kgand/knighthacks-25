# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-25

### Added
- Initial release of Chess Vision Live
- Real-time chess piece detection from webcam
- YOLOv8 and InceptionV3 model implementations
- Web interface using Gradio
- Chess logic utilities and move validation
- Multi-source dataset support
- AMD GPU optimization with ROCm
- Comprehensive test suite
- Documentation and setup guides

### Features
- **Models**: YOLOv8 and InceptionV3 detectors
- **UI**: Modern web interface with Gradio
- **Logic**: Chess move validation and position analysis
- **Training**: Support for custom model training
- **GPU**: AMD ROCm and NVIDIA CUDA support
- **Testing**: Comprehensive test coverage

### Performance
- YOLOv8s: 91% mAP @ 42 FPS (AMD RX 7900 XTX)
- InceptionV3: 89% mAP @ 18 FPS (AMD RX 7900 XTX)

## [0.2.0] - 2024-10-25

### Added
- Board state prediction and validation
- Move detection from board changes
- Position analysis and evaluation
- Enhanced error handling and logging

### Changed
- Improved detection accuracy
- Better board corner detection
- Enhanced perspective correction

## [0.1.0] - 2024-10-25

### Added
- Core chess logic utilities
- Image processing functions
- Video processing utilities
- Logging system
- Basic model implementations

### Changed
- Initial project structure
- Package organization
- Development workflow

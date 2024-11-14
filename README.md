# Advanced Dixon MRI Viewer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://pypi.org/project/PyQt5/)

A sophisticated medical imaging application designed for processing and analyzing Dixon MRI sequences, with a focus on fat-water separation techniques. This tool provides researchers and clinicians with an intuitive interface for viewing and processing Dixon MRI data.

![Application Screenshot]()

## Table of Contents
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
  - [Loading Data](#loading-data)
  - [Processing Parameters](#processing-parameters)
  - [Export Options](#export-options)
- [Technical Details](#technical-details)
  - [Dixon Method Implementation](#dixon-method-implementation)
  - [Image Processing Pipeline](#image-processing-pipeline)
- [Contributing](#contributing)
  - [Testing](#testing)
  - [Pull Request Process](#pull-request-process)
- [Research Background](#research-background)
- [Citing This Software](#citing-this-software)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

### Core Functionality
- Advanced Dixon fat-water separation algorithm implementation
- Real-time image processing and visualization
- Support for DICOM format
- Customizable window/level adjustments
- Batch processing capabilities

### Image Processing
- Multiple noise reduction methods:
  - Gaussian filtering
  - Median filtering
  - Bilateral filtering
- Contrast enhancement
- Customizable fat threshold selection
- Phase correction for improved separation

### User Interface
- Dark mode optimized for clinical environments
- Quadrant view showing all processing stages
- Intuitive navigation between scans
- Comprehensive settings management

## Installation

### Prerequisites
```bash
# Required system packages
sudo apt-get update
sudo apt-get install python3.8-dev python3-pip

# Python dependencies
pip install -r requirements.txt
```

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/dixon-mri-viewer.git
cd dixon-mri-viewer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### Loading Data
The application expects these specific directory structures, dicom files should be paired in order, i.e. the first dicom image in the 'inphase' directory should be paired with the first dicom image in the 'outphase' directory, and so on and so forth. Dataset sample is already uploaded.
```
main_folder/
    any_name/
        any_other_name/
            inphase/
                *.dcm
            outphase/
                *.dcm

# or

main_folder/
    random_name/
        inphase/
            *.dcm
        outphase/
            *.dcm

# or even

main_folder/
    inphase/
        *.dcm
    outphase/
        *.dcm
```

### Processing an Visualization Parameters
Key parameters that affect fat-water separation and visualization:

| Parameter | Default | Range/Opptions | Description |
|-----------|---------|--------|-------------|
| Fat Threshold | 0.1 | 0.0-1.0 | Minimum fat signal intensity |
| Noise Reduction | None | Gaussian, Median, Bilateral | Smooting and denoising |
| Contrast and Brightness | 0 | -50 : 50 | Brightness and contrast control |

## Technical Details

### Dixon Method Implementation
The software implements both basic and advanced Dixon methods:

1. Basic Dixon:
```python
water = (in_phase + out_phase) / 2.0
fat = (in_phase - out_phase) / 2.0
```

2. Advanced Dixon with phase correction:
```python
phase = np.angle(in_phase + 1j * out_phase)
magnitude = np.abs(in_phase + 1j * out_phase)
corrected_phase = np.unwrap(phase)
```

### Image Processing Pipeline
1. DICOM loading and validation
2. Noise reduction (optional)
3. Fat-water separation
4. Post-processing and enhancement
5. Display optimization

## Contributing

### Development Setup
1. Fork the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Testing
- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Use pytest for testing:
```bash
pytest tests/
```

### Pull Request Process
1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Commit your changes:
```bash
git commit -m "add new feature"
```
3. Push to your fork and submit a pull request

4. Ensure your PR:
- Passes all tests
- Updates documentation
- Includes test coverage


## Research Background
This implementation is based on the Dixon method for fat-water separation in MRI, first proposed by Thomas Dixon in 1984. The advanced method includes improvements such as phase correction and multi-peak fat modeling.

## Key References

1. Dixon, W.T. (1984). Simple proton spectroscopic imaging. Radiology, 153(1), 189-194.
2. Elster, A.D. (2024). Dixon Method. In Questions and Answers in MRI. ELSTER LLC. Retrieved from https://mriquestions.com/dixon-method.html 
## Citing This Software
If you use this software in your research, please cite:
```bibtex
@software{dixon_mri_viewer,
  author       = {Yasmin ElGamal, Salma Ashraf, Rana Hany, Sarah Ibrahim, Nouran Khatab},
  title        = {Advanced Dixon MRI Viewer},
  year         = {2024},
  publisher    = {GitHub},
  url          = {https://github.com/nouran-19/Fat-and-Water-Suppression-Dixon-Technique}
}
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- PyQt5 team for the GUI framework
- pydicom contributors for DICOM handling
- NumPy community for numerical computing support
- Research community for Dixon method improvements

---
Made with ❤️ for the course: SBE4120 Medical Imaging, Fall 2024, Taught by Siemens Healthineers, Egypt.
<br>
Contributotrs:

import sys
import os
import io
import numpy as np
from PIL import Image
import pydicom
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, QGridLayout, 
                            QMessageBox, QFrame, QStatusBar, QProgressBar, QSplitter,
                            QDialog, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox,
                            QGroupBox, QTabWidget, QSlider, QFormLayout)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont
from PyQt5.QtCore import Qt, QSize, QSettings, QTimer, QBuffer
import qdarkstyle
from datetime import datetime
from pydicom.dataset import FileDataset, FileMetaDataset

class ImageFrame(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #2c2c2c;
                border-radius: 10px;
                background-color: #1e1e1e;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title label with custom styling
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #00a6d6;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("padding: 5px;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.image_label)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        # Initialize settings
        self.settings = QSettings('MRIViewer', 'DixonProcessor')
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_display_tab(), "Display")
        tabs.addTab(self.create_processing_tab(), "Processing")
        tabs.addTab(self.create_export_tab(), "Export")
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        apply_button = QPushButton("Apply")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(apply_button)
        buttons_layout.addWidget(cancel_button)
        
        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Connect buttons
        save_button.clicked.connect(self.accept_and_save)
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self.apply_settings)
        
        # Load saved settings
        self.load_settings()

    def create_display_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Image Display Group
        display_group = QGroupBox("Image Display")
        display_layout = QFormLayout()
        
        self.window_size = QComboBox()
        self.window_size.addItems(["400x400", "512x512", "600x600", "800x800"])
        
        self.play_speed = QComboBox()
        self.play_speed.addItems(["0.25x", "0.5x", "1x", "1.5x", "2x", "4x"])
        self.play_speed.setCurrentText("1x")
        
        # Add tooltips for clarity
        self.window_size.setToolTip("Set the default size for image display")
        self.play_speed.setToolTip("Set the playback speed for image sequences")
        
        display_layout.addRow("Default Window Size:", self.window_size)
        display_layout.addRow("Playback Speed:", self.play_speed)
        display_group.setLayout(display_layout)
        
        # Image Adjustment Group
        adjustment_group = QGroupBox("Image Adjustment")
        adjustment_layout = QVBoxLayout()
        
        # Contrast Control
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("Contrast:")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-50, 50)
        self.contrast_slider.setValue(0)
        self.contrast_slider.setTickPosition(QSlider.TicksBelow)
        self.contrast_slider.setTickInterval(10)
        self.contrast_value = QLabel("0")
        self.contrast_slider.valueChanged.connect(lambda v: self.contrast_value.setText(str(v)))
        self.contrast_slider.setToolTip("Adjust image contrast")
        
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_value)
        
        # Brightness Control
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("Brightness:")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-50, 50)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness_slider.setTickInterval(10)
        self.brightness_value = QLabel("0")
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_value.setText(str(v)))
        self.brightness_slider.setToolTip("Adjust image brightness")
        
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value)
        
        # Reset Button for adjustments
        reset_adjustments_btn = QPushButton("Reset Adjustments")
        reset_adjustments_btn.clicked.connect(self.reset_image_adjustments)
        reset_adjustments_btn.setToolTip("Reset contrast and brightness to default values")
        
        # Add all adjustment controls to the group
        adjustment_layout.addLayout(contrast_layout)
        adjustment_layout.addLayout(brightness_layout)
        adjustment_layout.addWidget(reset_adjustments_btn)
        adjustment_group.setLayout(adjustment_layout)
        
        self.auto_window = QCheckBox("Auto Window/Level")
        self.auto_window.setToolTip("Automatically adjust contrast and brightness")
        
        self.window_width = QSpinBox()
        self.window_width.setRange(1, 4000)
        self.window_width.setToolTip("Controls contrast - wider values show more grayscale range")
        
        self.window_center = QSpinBox()
        self.window_center.setRange(-2000, 2000)
        self.window_center.setToolTip("Controls brightness - higher values make image brighter")
        
        # Add all groups to main layout
        layout.addWidget(display_group)
        layout.addWidget(adjustment_group)
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def reset_image_adjustments(self):
        """Reset contrast and brightness sliders to default values"""
        self.contrast_slider.setValue(0)
        self.brightness_slider.setValue(0)
        self.contrast_value.setText("0")
        self.brightness_value.setText("0")

    def create_processing_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Dixon Processing Group
        dixon_group = QGroupBox("Dixon Processing")
        dixon_layout = QFormLayout()
        
        self.fat_threshold = QDoubleSpinBox()
        self.fat_threshold.setRange(0, 1)
        self.fat_threshold.setSingleStep(0.01)
        
        self.noise_reduction = QComboBox()
        self.noise_reduction.addItems(["None", "Gaussian", "Median", "Bilateral"])
        
        self.advanced_dixon = QCheckBox("Use Advanced Dixon Method")
        
        dixon_layout.addRow("Fat Threshold:", self.fat_threshold)
        dixon_layout.addRow("Noise Reduction:", self.noise_reduction)
        dixon_group.setLayout(dixon_layout)
           
        
        layout.addWidget(dixon_group)
        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_export_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Export Options Group
        export_group = QGroupBox("Export Options")
        export_layout = QFormLayout()
        
        self.export_format = QComboBox()
        self.export_format.addItems(["DICOM", "PNG", "JPEG", "TIFF", "GIF"])
        
        self.compression = QCheckBox("Use Compression")
        
        # Add GIF settings
        self.gif_settings = QGroupBox("GIF Settings")
        gif_layout = QFormLayout()
        
        self.gif_duration = QSpinBox()
        self.gif_duration.setRange(50, 1000)
        self.gif_duration.setValue(500)
        self.gif_duration.setSuffix(" ms")
        self.gif_duration.setToolTip("Duration for each frame in milliseconds")
        
        self.gif_loop = QCheckBox("Loop GIF")
        self.gif_loop.setChecked(True)
        
        gif_layout.addRow("Frame Duration:", self.gif_duration)
        gif_layout.addRow("Loop:", self.gif_loop)
        self.gif_settings.setLayout(gif_layout)
        
        export_layout.addRow("Export Format:", self.export_format)
        export_layout.addRow("Compression:", self.compression)
        export_layout.addWidget(self.gif_settings)
        export_group.setLayout(export_layout)
        
        layout.addWidget(export_group)
        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def load_settings(self):
        # Load Display settings
        self.window_size.setCurrentText(self.settings.value('display/window_size', '400x400'))
        self.play_speed.setCurrentText(self.settings.value('display/play_speed', '1x'))
        self.auto_window.setChecked(self.settings.value('display/auto_window', True, type=bool))
        self.window_width.setValue(self.settings.value('display/window_width', 2000, type=int))
        self.window_center.setValue(self.settings.value('display/window_center', 0, type=int))
        
        # Load Processing settings
        self.fat_threshold.setValue(self.settings.value('processing/fat_threshold', 0.1, type=float))
        self.noise_reduction.setCurrentText(self.settings.value('processing/noise_reduction', 'None'))

        # Load contrast and brightness settings
        self.contrast_slider.setValue(self.settings.value('display/contrast', 0, type=int))
        self.brightness_slider.setValue(self.settings.value('display/brightness', 0, type=int))
        
        
        # Load Export settings
        self.export_format.setCurrentText(self.settings.value('export/format', 'DICOM'))
        self.compression.setChecked(self.settings.value('export/compression', True, type=bool))
        self.gif_duration.setValue(self.settings.value('export/gif_duration', 500, type=int))
        self.gif_loop.setChecked(self.settings.value('export/gif_loop', True, type=bool))

    def save_settings(self):
        # Save Display settings
        self.settings.setValue('display/window_size', self.window_size.currentText())
        self.settings.setValue('display/play_speed', self.play_speed.currentText())
        self.settings.setValue('display/auto_window', self.auto_window.isChecked())
        self.settings.setValue('display/window_width', self.window_width.value())
        self.settings.setValue('display/window_center', self.window_center.value())
        
        # Save Processing settings
        self.settings.setValue('processing/fat_threshold', self.fat_threshold.value())
        self.settings.setValue('processing/noise_reduction', self.noise_reduction.currentText())

        # Save contrast and brightness settings
        self.settings.setValue('display/contrast', self.contrast_slider.value())
        self.settings.setValue('display/brightness', self.brightness_slider.value())
       
        
        # Save Export settings
        self.settings.setValue('export/format', self.export_format.currentText())
        self.settings.setValue('export/compression', self.compression.isChecked())
        self.settings.setValue('export/gif_duration', self.gif_duration.value())
        self.settings.setValue('export/gif_loop', self.gif_loop.isChecked())

    def accept_and_save(self):
        self.save_settings()
        self.accept()

    def apply_settings(self):
        self.save_settings()
        # Notify main window to update display
        if self.parent():
            self.parent().update_display()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Dixon MRI Viewer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            # Set taskbar icon for Windows
            if sys.platform == 'win32':
                import ctypes
                myappid = 'mycompany.dixonviewer.1.0'  # arbitrary string
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Toolbar with controls
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # Create image display area
        self.create_image_display(layout)

        # Status bar with information
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar in status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()

        # Initialize variables
        self.current_folder = None
        self.current_index = 0
        self.scan_folders = []
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.next_scan)
        self.is_playing = False

    def create_toolbar(self):
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar.setStyleSheet("""
            QPushButton {
                min-width: 120px;
                min-height: 30px;
                padding: 5px;
                background-color: #2c2c2c;
                border: none;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
            QPushButton:disabled {
                background-color: #1c1c1c;
                color: #666666;
            }
        """)

        # Navigation buttons with icons and tooltips
        self.prev_button = QPushButton("◄ Previous")
        self.prev_button.setToolTip("View previous scan")
        
        self.next_button = QPushButton("Next ►")
        self.next_button.setToolTip("View next scan")
        
        self.load_button = QPushButton("📂 Load Folder")
        self.load_button.setToolTip("Load a folder containing DICOM images")
        
        # Additional controls
        self.reset_button = QPushButton("↺ Reset View")
        self.reset_button.setToolTip("Reset all view settings to default")
        
        self.settings_button = QPushButton("⚙ Settings")
        self.settings_button.setToolTip("Configure application settings")
        
        # New Export button
        self.export_button = QPushButton("📤 Export")
        self.export_button.setToolTip("Export current images")
        
        # Add play button before the export button
        self.play_button = QPushButton("▶ Play")
        self.play_button.setToolTip("Play/Pause animation")
        self.play_button.clicked.connect(self.toggle_play)
        
        buttons = [self.prev_button, self.load_button, self.next_button, 
                  self.play_button, self.reset_button, self.settings_button, 
                  self.export_button]
        
        for button in buttons:
            button.setFont(QFont("Arial", 10))
            toolbar_layout.addWidget(button)

        toolbar_layout.addStretch()

        # Connect buttons
        self.load_button.clicked.connect(self.load_folder)
        self.prev_button.clicked.connect(self.prev_scan)
        self.next_button.clicked.connect(self.next_scan)
        self.reset_button.clicked.connect(self.reset_view)
        self.settings_button.clicked.connect(self.show_settings)
        self.export_button.clicked.connect(self.export_images)

        return toolbar

    def create_image_display(self, parent_layout):
        # Create image frames in a grid
        images_widget = QWidget()
        self.images_layout = QGridLayout(images_widget)
        self.images_layout.setSpacing(10)
        
        self.image_frames = []
        titles = ['In Phase', 'Out Phase', 'Water Only', 'Fat Only']
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for position, title in zip(positions, titles):
            frame = ImageFrame(title)
            self.images_layout.addWidget(frame, *position)
            self.image_frames.append(frame)

        parent_layout.addWidget(images_widget)


    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_display()  # Refresh display with new settings

    def update_display(self):
        if not self.scan_folders or self.current_index >= len(self.scan_folders):
            return

        settings = QSettings('MRIViewer', 'DixonProcessor')
        current_scan = self.scan_folders[self.current_index]
        
        try:
            # Load DICOM images - keep in native scale
            in_phase_dcm = pydicom.dcmread(current_scan['in_phase'])
            out_phase_dcm = pydicom.dcmread(current_scan['out_phase'])
            
            in_phase_float32 = in_phase_dcm.pixel_array.astype(np.float32)
            out_phase_float32 = out_phase_dcm.pixel_array.astype(np.float32)

            # Get processing settings
            fat_threshold = settings.value('processing/fat_threshold', 0.01, type=float)
            noise_reduction = settings.value('processing/noise_reduction', 'None')
            
            # Get contrast and brightness settings
            contrast = settings.value('display/contrast', 0, type=int) / 50.0  # Convert to range [-1, 1]
            brightness = settings.value('display/brightness', 0, type=int) / 50.0  # Convert to range [-1, 1]
            
            # Keep preprocessing in native scale
            in_phase_preprocessed = self.preprocess_image(in_phase_float32, noise_reduction, keep_scale=True)
            out_phase_preprocessed = self.preprocess_image(out_phase_float32, noise_reduction, keep_scale=True)

            # Normalize for Dixon processing while maintaining scale
            in_phase_norm = self.normalize_image(in_phase_preprocessed)
            out_phase_norm = self.normalize_image(out_phase_preprocessed)

            # Perform fat-water separation in native scale
            water, fat = self.perform_fat_water_separation(
                in_phase_norm, 
                out_phase_norm, 
                fat_threshold=fat_threshold,
            )

            # Apply contrast and brightness adjustments to normalized images
            adjusted_images = []
            for img in [in_phase_norm, out_phase_norm, water, fat]:
                adjusted = self.apply_contrast_brightness(img, contrast, brightness)
                adjusted_images.append(adjusted)

            # Get display settings
            window_size = settings.value('display/window_size', '400x400')
            width, height = map(int, window_size.split('x'))
            
            # Convert to 8-bit for display
            display_images = [self.to_8bit_for_display(img) for img in adjusted_images]
            
            # Display images
            for frame, img_array in zip(self.image_frames, display_images):
                image = QImage(img_array.data, img_array.shape[1], img_array.shape[0], 
                            img_array.shape[1], QImage.Format_Grayscale8)
                pixmap = QPixmap.fromImage(image)
                scaled_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                frame.image_label.setPixmap(scaled_pixmap)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing images: {str(e)}")
            for frame in self.image_frames:
                frame.image_label.clear()
            frame.image_label.setText("Image loading error")

    
    def preprocess_image(self, image, noise_reduction='None', keep_scale=True):
        """Preprocess image with optional noise reduction, maintaining original scale if requested"""

        # Apply noise reduction if specified
        if noise_reduction == 'Gaussian':
            from scipy.ndimage import gaussian_filter
            image = gaussian_filter(image, sigma=1)
        elif noise_reduction == 'Median':
            from scipy.ndimage import median_filter
            image = median_filter(image, size=3)
        elif noise_reduction == 'Bilateral':
            from skimage.restoration import denoise_bilateral
            image = denoise_bilateral(image)
        
        if not keep_scale:
            # Only normalize to 0-255 if specifically requested
            image = (image - np.min(image)) / (np.max(image) - np.min(image))
            image = (image * 255).astype(np.uint8)
        
        return image

    def normalize_image(self, image):
        """Normalize the image to the range [0, 1] while preserving relative intensities"""
        if not isinstance(image, np.ndarray):
            raise ValueError("Input must be a numpy array")
        if image.size == 0:
            raise ValueError("Input array cannot be empty")
        
        image_min = np.min(image)
        image_max = np.max(image)
        
        
        if image_min == image_max:
            raise ValueError("Input array cannot have all identical values")
        
        normalized_image = (image - image_min) / (image_max - image_min)
        return normalized_image

    def gamma_correction(self, image, gamma=0.8):
        """Apply gamma correction to the image"""
        if not isinstance(image, np.ndarray):
            raise ValueError("Input must be a numpy array")
        if image.size == 0:
            raise ValueError("Input array cannot be empty")
        
        corrected_image = np.power(image, gamma)
        return corrected_image

    def perform_fat_water_separation(self, in_phase, out_phase, fat_threshold=0.1, advanced_method=False):
        """Perform fat-water separation using basic or advanced Dixon method"""
        in_phase = in_phase.astype(np.float32)
        out_phase = out_phase.astype(np.float32)

        # Basic Dixon method with signal difference
        # Calculate signal difference
        diff = (in_phase - out_phase)
        
        # Calculate masks for fat predominant regions, water image is the mean image
        mean_signal = (in_phase + out_phase) / 2.0
        
        # initialize fat images
        fat = np.zeros_like(in_phase)
        # Areas where in_phase > out_phase are fat-containing
        fat_mask = (in_phase > out_phase) 
        # Apply masks and enhance contrast
        fat[fat_mask] = diff[fat_mask]

        # Applying Dixon Equation
        water = mean_signal
        
        # Normalize while keeping relative intensities
        water = self.normalize_image(water)
        fat = self.normalize_image(fat)
        
        
        # Apply threshold to fat image, no need for a threshold on water because there is no subtraction
        fat[fat < fat_threshold] = 0
        
        return water, fat

    def to_8bit_for_display(self, image):
        """Convert any scale image to 8-bit for display purposes only"""
        # Ensure we're working with float
        image = image.astype(np.float32)
        
        # Normalize to 0-1 range
        # normalized = (image - np.min(image)) / (np.max(image) - np.min(image))
        
        # Convert to 8-bit
        display_image = (image * 255).astype(np.uint8)
        
        return display_image
    
    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = folder
            self.update_status(f"Loading folder: {folder}")
            
            try:
                self.progress_bar.show()
                self.progress_bar.setRange(0, 0)  # Indeterminate progress
                
                self.scan_folders = self.get_scan_folders(folder)
                
                self.progress_bar.hide()
                
                if len(self.scan_folders) > 0:
                    self.current_index = 0
                    self.update_display()
                    self.update_status(f"Loaded {len(self.scan_folders)} scans successfully")
                else:
                    QMessageBox.warning(self, "Warning", 
                        "No valid scan folders found!\n\nExpected structure:\n"
                        "folder/patient/scan/[inphase.dcm & outphase.dcm]")
            except Exception as e:
                self.progress_bar.hide()
                QMessageBox.critical(self, "Error", f"Error loading folder: {str(e)}")

    def get_scan_folders(self, main_folder):
        scan_folders = []

        print("\nScanning directory structure:")
        for root, dirs, files in os.walk(main_folder):
            print(f"\nChecking directory: {root}")
            print(f"Subdirectories: {dirs}")

            # Ensure the existence of both "inphase" and "outphase" subdirectories
            if 'inphase' in dirs and 'outphase' in dirs:
                print(f"Found inphase and outphase folders in: {root}")

                inphase_path = os.path.join(root, 'inphase')
                outphase_path = os.path.join(root, 'outphase')

                # Find DICOM files with matching prefixes but different suffixes
                inphase_files = [f for f in os.listdir(inphase_path) if f.endswith('.dcm')]
                outphase_files = [f for f in os.listdir(outphase_path) if f.endswith('.dcm')]

                # Check for matching prefixes
                for (in_file, out_file) in zip(inphase_files, outphase_files):
        
                    scan_folders.append({
                        'path': root,
                        'in_phase': os.path.join(inphase_path, in_file),
                        'out_phase': os.path.join(outphase_path, out_file)
                    })                        

        print(f"\nTotal scans found: {len(scan_folders)}")
        return scan_folders


    def prev_scan(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def next_scan(self):
        if self.current_index < len(self.scan_folders) - 1:
            self.current_index += 1
            self.update_display()
        elif self.is_playing:  # If playing and reached the end
            self.current_index = 0  # Loop back to start
            self.update_display()

    def toggle_play(self):
        if not self.scan_folders:
            return
        print("Toggling play")
        print(f"Current playing status: {self.is_playing}")
        if self.is_playing:
            self.play_timer.stop()
            self.play_button.setText("▶ Play")
            self.is_playing = False
        else:
            # Get the speed multiplier from the play_speed combo box
            settings = QSettings('MRIViewer', 'DixonProcessor')
            speed_text = settings.value('display/play_speed', '1x').rstrip('x')

            speed_multiplier = float(speed_text)
            print(f"Playing at {speed_multiplier}x speed")
            base_interval = 500  # Base interval of 500ms (for 1x speed)
            
            # Calculate the actual interval based on the speed multiplier
            interval = int(base_interval / speed_multiplier)
            
            self.play_timer.start(interval)
            self.play_button.setText("⏸ Pause")
            self.is_playing = True

    def export_images(self):
        if not self.scan_folders:
            QMessageBox.warning(self, "Warning", "No images to export!")
            return
            
        settings = QSettings('MRIViewer', 'DixonProcessor')
        export_format = settings.value('export/format', 'DICOM')
        use_compression = settings.value('export/compression', True, type=bool)
        
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not export_dir:
            return
            
        try:
            if export_format == 'GIF':
                self._export_as_gif(export_dir)
            else:
                self.progress_bar.show()
                self.progress_bar.setRange(0, 4)  # Four images to export
                
                frames = ['in_phase', 'out_phase', 'water', 'fat']
                for i, frame in enumerate(self.image_frames):
                    pixmap = frame.image_label.pixmap()
                    if pixmap:
                        image = pixmap.toImage()
                        
                        filename = f"{frames[i]}_{self.current_index}"
                        if export_format == 'DICOM':
                            # Handle DICOM export with metadata
                            file_meta = FileMetaDataset()
                            file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
                            file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
                            file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
                            
                            ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
                            
                            # Required DICOM attributes
                            ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
                            ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
                            ds.StudyDate = datetime.now().strftime('%Y%m%d')
                            ds.ContentDate = ds.StudyDate
                            ds.StudyTime = datetime.now().strftime('%H%M%S')
                            ds.ContentTime = ds.StudyTime
                            ds.Modality = 'MR'
                            
                            
                            # Copy metadata from original DICOM if available
                            if hasattr(self, 'current_dicom') and self.current_dicom:
                                for elem in self.current_dicom:
                                    if elem.keyword not in ['PixelData', 'Rows', 'Columns']:
                                        setattr(ds, elem.keyword, elem.value)
                            
                            # Convert image to array for DICOM
                            buffer = image.bits().asstring(image.width() * image.height() * 4)
                            arr = np.frombuffer(buffer, dtype=np.uint8).reshape(
                                (image.height(), image.width(), 4)
                            )
                            arr = arr[:,:,0]  # Take first channel for grayscale
                            
                            ds.Rows = arr.shape[0]
                            ds.Columns = arr.shape[1]
                            ds.SamplesPerPixel = 1
                            ds.PhotometricInterpretation = "MONOCHROME2"
                            ds.BitsAllocated = 8
                            ds.BitsStored = 8
                            ds.HighBit = 7
                            ds.PixelRepresentation = 0
                            ds.PixelData = arr.tobytes()
                            
                            # Save DICOM
                            filepath = os.path.join(export_dir, f"{filename}.dcm")
                            ds.save_as(filepath, write_like_original=False)
                        else:
                            # Handle other image formats with compression
                            filepath = os.path.join(export_dir, f"{filename}.{export_format.lower()}")
                            if use_compression:
                                # Convert to PIL for better compression control
                                buffer = QBuffer()
                                buffer.open(QBuffer.ReadWrite)
                                image.save(buffer, format='PNG')
                                pil_image = Image.open(io.BytesIO(buffer.data()))
                                
                                if export_format.upper() == 'JPEG':
                                    pil_image.save(filepath, quality=85, optimize=True)
                                elif export_format.upper() == 'PNG':
                                    pil_image.save(filepath, optimize=True)
                                else:
                                    pil_image.save(filepath)
                            else:
                                image.save(filepath)
                        
                        self.progress_bar.setValue(i + 1)
                
                self.progress_bar.hide()
                self.update_status("Images exported successfully")
                        
        except Exception as e:
            self.progress_bar.hide()
            QMessageBox.critical(self, "Error", f"Error exporting images: {str(e)}")

    def _export_as_gif(self, export_dir):
        """Export four separate GIFs, one for each image type (In Phase, Out Phase, Water Only, Fat Only)"""
        from PIL import Image
        import io
        
        # Store current index to restore later
        original_index = self.current_index
        frame_types = ['in_phase', 'out_phase', 'water', 'fat']
        
        try:
            self.progress_bar.show()
            total_frames = len(self.scan_folders) * len(self.image_frames)
            self.progress_bar.setRange(0, total_frames)
            progress = 0
            
            # Dictionary to store frames for each type
            frames_by_type = {
                'in_phase': [],
                'out_phase': [],
                'water': [],
                'fat': []
            }
            
            # Collect frames
            for i in range(len(self.scan_folders)):
                self.current_index = i
                self.update_display()
                
                # Capture each view separately
                for frame_type, frame in zip(frame_types, self.image_frames):
                    pixmap = frame.image_label.pixmap()
                    if pixmap:
                        # Convert QPixmap to PIL Image
                        buffer = QBuffer()
                        buffer.open(QBuffer.ReadWrite)
                        pixmap.save(buffer, "PNG")
                        pil_img = Image.open(io.BytesIO(buffer.data()))
                        frames_by_type[frame_type].append(pil_img)
                    
                    progress += 1
                    self.progress_bar.setValue(progress)
            
            # Get GIF settings
            settings = QSettings('MRIViewer', 'DixonProcessor')
            duration = settings.value('export/gif_duration', 500, type=int)
            loop = 0 if settings.value('export/gif_loop', True, type=bool) else 1
            
            # Save each type as a separate GIF
            for frame_type, frames in frames_by_type.items():
                if frames:
                    output_path = os.path.join(export_dir, f"{frame_type}_animation.gif")
                    frames[0].save(
                        output_path,
                        save_all=True,
                        append_images=frames[1:],
                        duration=duration,
                        loop=loop,
                        optimize=True  # Enable optimization for smaller file size
                    )
            
            self.update_status("GIFs exported successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting GIFs: {str(e)}")
        finally:
            # Restore original state
            self.current_index = original_index
            self.update_display()
            self.progress_bar.hide()

    def apply_contrast_brightness(self, image, contrast, brightness):
        """
        Apply contrast and brightness adjustments to an image.
        
        Args:
            image: Input image normalized to [0, 1]
            contrast: Contrast adjustment factor in range [-1, 1]
            brightness: Brightness adjustment factor in range [-1, 1]
        
        Returns:
            Adjusted image normalized to [0, 1]
        """
        # Convert contrast to multiplicative factor (0.5 to 2.0)
        contrast_factor = 1.0 + contrast
        
        # Apply contrast adjustment (centered around 0.5)
        result = (image - 0.5) * contrast_factor + 0.5
        
        # Apply brightness adjustment
        result = result + brightness
        
        # Clip values to [0, 1] range
        result = np.clip(result, 0, 1)
        
        return result

  
    def reset_view(self):
        # Reset view to default state
        if hasattr(self, 'current_index'):
            self.update_display()

    def update_status(self, message):
        self.status_bar.showMessage(message, 3000)  # Show for 3 seconds


    def _save_as_dicom(self, qimage, filepath):
        # Get the original DICOM metadata from the current scan
        current_scan = self.scan_folders[self.current_index]
        original_dcm = pydicom.dcmread(current_scan['in_phase'])
        
        # Create new dataset with original metadata
        ds = original_dcm.copy()
        
        # Update necessary UIDs to make it a unique instance
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
        
        # Convert QImage to numpy array
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        
        # Convert to grayscale if needed
        if len(arr.shape) > 2:
            arr = np.mean(arr[:,:,:3], axis=2).astype(np.uint16)
        
        # Update image-specific attributes if dimensions changed
        ds.Rows = height
        ds.Columns = width
        
        # Convert pixel data to match original bit depth
        max_val = (2 ** ds.BitsStored) - 1
        pixel_data = ((arr / arr.max()) * max_val).astype(np.uint16)
        ds.PixelData = pixel_data.tobytes()
        
        # Add processing information to series description
        ds.SeriesDescription = f"{original_dcm.SeriesDescription}_processed" if hasattr(original_dcm, 'SeriesDescription') else "Processed"
        
        # Save the file
        ds.save_as(filepath)

def main():
    app = QApplication(sys.argv)
    
    # Set app icon for all windows
    icon_path = os.path.join(os.path.dirname(__file__), 'Icon\medical-viewer-icon.svg')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Apply dark style
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
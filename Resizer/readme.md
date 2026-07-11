# Image Resizer GUI

A simple yet powerful desktop application that allows users to resize images through an intuitive graphical interface. The application supports custom resolutions, multiple output formats, progress tracking, and estimated completion time.

---

## Features

*  **Graphical File Selection**

  * Browse and select an input image using a file picker dialog.

*  **Custom Image Size**

  * Resize images to any custom resolution.
  * Supported range:

    * **Minimum:** 32 × 32 pixels
    * **Maximum:** 8192 × 8192 pixels
  * Examples:

    * 128 × 128
    * 256 × 256
    * 512 × 512
    * 1024 × 1024
    * Any custom size within the supported range

*  **Multiple Output Formats**

  * Save the resized image in various formats, including:

    * PNG
    * JPG / JPEG
    * BMP
    * TIFF
    
    * (Additional formats supported by the installed image library.)

*  **Output Folder Selection**

  * Choose the destination folder using a folder picker dialog.

*  **Live Progress Tracking**

  * Displays a real-time progress bar while processing.

*  **Time Information**

  * Shows:

    * Time elapsed
    * Estimated time remaining (ETA)

*  **Simple Workflow**

  1. Select an image.
  2. Enter the desired resolution.
  3. Choose the output format.
  4. Select the destination folder.
  5. Click **Start** to process the image.

---

# Requirements

* Python 3.10 or later

Required libraries:

```text
Pillow
tkinter (included with most Python installations)
```

Install Pillow:

```bash
pip install pillow
```

---

# Usage

1. Launch the application.

2. Click **Browse** to select the source image.

3. Enter the desired dimensions.

Example:

```
512 x 512
```

or

```
2048 x 1024
```

4. Choose the desired output format.

5. Select the output directory.

6. Click **Start Processing**.

7. Wait for the progress bar to complete.

8. The resized image will be saved in the selected output folder.

---

# Supported Resolution Limits

| Property       |   Value |
| -------------- | ------: |
| Minimum Width  |   32 px |
| Minimum Height |   32 px |
| Maximum Width  | 8192 px |
| Maximum Height | 8192 px |

Any values outside these limits will be rejected.

---

# Supported Output Formats

* PNG
* JPG
* JPEG
* BMP
* TIFF


Additional formats may be available depending on your Pillow installation.

---

# Progress Display

During processing, the application displays:

* Current progress percentage
* Progress bar
* Elapsed processing time
* Estimated time remaining (ETA)

This provides clear feedback for longer processing tasks.

---

# Error Handling

The application validates user input and displays informative error messages for situations such as:

* No input image selected
* Invalid width or height
* Resolution outside the supported range
* Unsupported output format
* Missing output folder
* File read/write errors

---

# Example Workflow

```
Input Image
        │
        ▼
Select Image File
        │
        ▼
Enter Width & Height
        │
        ▼
Choose Output Format
        │
        ▼
Select Output Folder
        │
        ▼
Start Processing
        │
        ▼
Progress Bar + ETA
        │
        ▼
Saved Resized Image
```

---

# Notes

* The original image is never modified.
* A new resized copy is created in the selected output folder.
* Image quality is preserved as much as possible based on the chosen output format.
* Large output resolutions may require additional processing time and memory.

---

# Future Improvements

Potential enhancements include:

* Batch image processing
* Drag-and-drop support
* Aspect ratio lock
* Multiple interpolation methods
* Image preview
* Compression quality slider
* Dark mode interface
* Metadata preservation
* GPU acceleration (where supported)

---

# License

This project is provided for educational and personal use. You are free to modify and extend it to suit your own requirements.

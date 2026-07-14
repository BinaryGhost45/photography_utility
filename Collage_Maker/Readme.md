# Collage Maker

A desktop GUI application that creates photo collages from images located in a selected folder. The application is designed to be fast, configurable, and responsive by using multithreading for image processing.

## Features

- Select an input folder containing photos.
- Select an output folder where the finished collage will be saved.
- Create collages using between **1 and 200 images**.
- Adjustable spacing (padding) between photos.
- Configurable RAM allocation for processing.
- Background processing using worker threads so the GUI remains responsive.
- Real-time progress bar.
- Displays:
  - Processing progress
  - Elapsed time
  - Estimated remaining time (ETA)
- Prevents selecting more than 200 images.
- Supports common image formats such as:
  - JPG
  - JPEG
  - PNG
  - BMP
  - WEBP (optional)

## User Interface

The application includes the following controls:

### Input Folder

Allows the user to browse and select the folder containing source images.

### Output Folder

Allows the user to choose where the generated collage will be saved.

### Maximum Images

A numeric input that accepts values from **1 to 200**.

Example:

```
Images to Use: 120
```

### Photo Spacing

A numeric input allowing the user to manually specify the spacing between photos.

Example:

```
Spacing: 8 pixels
```

### RAM Allocation

A numeric input allowing the user to specify how much RAM the application may use while processing.

Example:

```
RAM Limit: 4096 MB
```

The application should automatically manage memory usage to stay within the selected limit whenever possible.

### Progress Section

Displays:

- Progress bar
- Percentage complete
- Images processed
- Elapsed time
- Estimated time remaining (ETA)

Example:

```
Processed:
104 / 200 images

Elapsed:
00:01:18

Remaining:
00:01:12
```

## Performance

Image processing runs in one or more worker threads.

This ensures:

- The GUI never freezes during processing.
- Progress updates remain smooth.
- Users can move or resize the window while processing.
- Time estimates update continuously.

## Validation

The application should validate the following:

- Input folder exists.
- Output folder exists.
- At least one image is available.
- Maximum image count is between 1 and 200.
- RAM allocation is greater than zero.
- Spacing is zero or greater.

Meaningful error messages should be shown for invalid input.

## Processing Workflow

1. Select the input folder.
2. Select the output folder.
3. Choose the number of images (1–200).
4. Set the spacing between photos.
5. Set the RAM allocation.
6. Click **Create Collage**.
7. Watch the live progress and timing information.
8. The finished collage is saved to the output folder.

## Technical Design

Recommended architecture:

- GUI Thread
  - Handles user interaction.
  - Updates progress.
  - Displays elapsed and remaining time.

- Worker Thread(s)
  - Loads images.
  - Resizes images.
  - Creates the collage.
  - Writes the output file.

Communication between worker threads and the GUI should use thread-safe mechanisms such as signals, events, or queues.

## Future Improvements

- Drag-and-drop folder selection.
- Automatic collage layout optimization.
- Multiple collage templates.
- Border customization.
- Background color selection.
- Image rotation.
- Image quality adjustment.
- GPU acceleration.
- Batch collage generation.
- Thumbnail preview before processing.

## Requirements

- Python 3.10 or newer
- Pillow
- Tkinter or PySide6/PyQt6
- NumPy (optional for optimization)

## Example Usage

1. Launch the application.
2. Choose an input folder containing photos.
3. Select an output folder.
4. Set:
   - Number of images
   - Photo spacing
   - RAM allocation
5. Click **Create Collage**.
6. Wait for processing to complete while monitoring the progress bar and time estimates.
7. Open the output folder to view the generated collage.

## License

This project is intended for educational and personal use. Modify and distribute according to your chosen license.
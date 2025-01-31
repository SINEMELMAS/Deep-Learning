import os
import png
import pydicom
import numpy as np

def mri_to_png(mri_file, png_file):

    # Extracting data from the MRI file
    try:
        plan = pydicom.dcmread(mri_file, force=True)  # Force reading non-standard files
    except Exception as e:
        raise ValueError(f"Failed to read DICOM file {mri_file}: {e}")

    # Verify if pixel_array exists
    if not hasattr(plan, 'pixel_array'):
        raise ValueError(f"The file {mri_file} does not contain image data.")

    pixel_array = plan.pixel_array

    # Handle rescaling if necessary
    if hasattr(plan, 'RescaleIntercept') and hasattr(plan, 'RescaleSlope'):
        intercept = plan.RescaleIntercept
        slope = plan.RescaleSlope
        pixel_array = pixel_array * slope + intercept

    # Normalize pixel values to 0-255 range
    pixel_array = pixel_array.astype(float)
    min_val = np.min(pixel_array)
    max_val = np.max(pixel_array)

    if max_val == min_val:
        raise ValueError(f"The file {mri_file} contains uniform pixel values.")

    # Scale pixel values to 0-255
    pixel_array = (pixel_array - min_val) / (max_val - min_val) * 255.0
    pixel_array = pixel_array.astype(np.uint8)

    # Writing the PNG file
    shape = pixel_array.shape
    w = png.Writer(shape[1], shape[0], greyscale=True)
    w.write(png_file, pixel_array.tolist())

def convert_file(mri_file_path, png_file_path):
    # Making sure that the MRI file exists
    if not os.path.exists(mri_file_path):
        raise Exception(f'File "{mri_file_path}" does not exist')

    # Making sure the PNG file does not exist
    if os.path.exists(png_file_path):
        raise Exception(f'File "{png_file_path}" already exists')

    with open(mri_file_path, 'rb') as mri_file, open(png_file_path, 'wb') as png_file:
        mri_to_png(mri_file, png_file)

def convert_folder(mri_folder, png_folder):

    # Create the folder for the PNG directory structure
    os.makedirs(png_folder, exist_ok=True)

    # Recursively traverse all sub-folders in the path
    for mri_sub_folder, _, files in os.walk(mri_folder):
        for mri_file in files:
            mri_file_path = os.path.join(mri_sub_folder, mri_file)

            # Make sure path is an actual file
            if os.path.isfile(mri_file_path):

                # Replicate the original file structure
                rel_path = os.path.relpath(mri_sub_folder, mri_folder)
                png_folder_path = os.path.join(png_folder, rel_path)
                os.makedirs(png_folder_path, exist_ok=True)
                png_file_path = os.path.join(png_folder_path, f'{os.path.splitext(mri_file)[0]}.png')

                try:
                    # Convert the actual file
                    convert_file(mri_file_path, png_file_path)
                    print(f'SUCCESS> {mri_file_path} --> {png_file_path}')
                except Exception as e:
                    print(f'FAIL> {mri_file_path} --> {png_file_path} : {e}')

if __name__ == '__main__':
    # Manually set paths for conversion
    dicom_path = "C:\\Users\\***\\****\\***"
    png_path = "C:\\Users\\***\\***\\***"

    try:
        # Convert folder
        convert_folder(dicom_path, png_path)
    except Exception as e:
        print(f'Error: {e}')

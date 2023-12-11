
# Emotional Heatmap Generation GUI for iMotion for Image-Based Experiment - User Guide

## Introduction

This guide outlines the steps to use the Emotional Heatmap Generation GUI. The interface is designed to be user-friendly and effective, catering to users with varying levels of technical expertise.

## Preliminary Steps Before Using the GUI

### Download Raw Data

1. **Download Raw Data Zip**: Make sure to download the `raw_data.zip` file containing the necessary raw data files.
2. **Unzip the Data**: Extract the contents of `raw_data.zip` to a known directory on your computer.

### Install Required Libraries

Before running the code, it's essential to install the required libraries. You can do this by creating a conda environment using the `environment.yml` file.

1. Save the `environment.yml` content provided in a file.
2. Open a terminal and navigate to the folder containing `environment.yml`.
3. Run the following command to create the conda environment:

    ```bash
    conda env create -f environment.yml
    ```

4. Activate the conda environment:

    ```bash
    conda activate my_env
    ```

### Download Experiment Images

1. **Download Experiment Images Zip**: Download the `experiment_images.zip` file containing all images used in the experiment.
2. **Unzip the Images**: Extract the contents of `experiment_images.zip` to a known directory on your computer.

## Steps to Use the GUI

### Step 1: Select Raw Data Folder and Output Folder

1. **Select Raw Data Folder**: Navigate to the 'iMotions Raw Data Folder' section in the GUI and click the 'Browse' button to select the folder containing raw data exported from iMotions.
2. **Select Output Folder**: Choose an 'Output Folder' for cleaned CSV files by clicking another 'Browse' button.
3. **Notification**: Upon each successful folder selection, a notification popup and an audible alert signal to the user that they can proceed to the next step.

### Step 2: Select Cleaned CSV File

1. The GUI presents an option for the 'Cleaned CSV File' selection.
2. Click on the 'Browse' button in this section and pick the specific cleaned CSV file you wish to analyze.
3. A popup notification and sound confirm the successful selection.

### Step 3: Select XLS File, Image File, and Enter Sheet Name

1. **Select XLS File**: Click the 'Browse' button in the 'XLS File' section to select an XLS file for heatmap generation.
2. **Select Image File**: Click the 'Browse' button in the 'Image File' section to select an image for heatmap generation.
3. **Enter Sheet Name**: Manually enter the name of the Excel sheet you intend to analyze in a 'Sheet Name' field.
4. **Generate Plot**: Click the 'Generate Plot' button to initiate the emotional heatmap generation.

## Conclusion

A final notification popup and sound will affirm the successful creation of the heatmap. These steps, accompanied by real-time notifications and sounds, make the GUI exceptionally user-friendly and effective.

Thank you for using the Emotional Heatmap Generation GUI. We hope it enhances your data analysis process.

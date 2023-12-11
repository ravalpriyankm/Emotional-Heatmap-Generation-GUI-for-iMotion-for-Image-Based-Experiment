import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from openpyxl import Workbook
import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

# Declare figs list in the global scope
# Declare global variables here
figs = []
plot_index = 0
plot_queue = deque()
plot_window = None
canvas = None
base_dir = "Output"
seen_plots = [] # Images that were already displayed
pending_plots = []  # Images in the queue to be displayed

# Function definitions for Step 1

def file_clean(df, filename):
    df = df[df[df[0] == "Row"].index[0]:]
    df = df.reset_index(drop=True)
    df.columns = df.iloc[0].tolist()
    df = df[1:]
    df["SlideEvent"] = df["SlideEvent"].ffill()
    df = df.loc[df.SlideEvent == "StartMedia"]

    columns_to_drop = ["EventSource", "GSR Resistance CAL", "GSR Conductance CAL", "Heart Rate PPG ALG"]
    df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

    df = df.reset_index(drop=True)
    df["Participant"] = filename
    return df

def browse_raw_folder():
    folder_path = filedialog.askdirectory()
    raw_entry.delete(0, tk.END)
    raw_entry.insert(0, folder_path)

def browse_output_folder():
    folder_path = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, folder_path)

def clean_files(raw_path, output_path):
        columns_to_keep = ['Timestamp', 'Row', 'StimType', 'Duration', 'SourceStimuliName', 'CollectionPhase',
                    'SlideEvent', 'Participant', 'SampleNumber', 'Anger',
                    'Contempt', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 
                    'Engagement', 'Valence', 'Sentimentality', 'Confusion', 'Neutral', 'ET_GazeLeftx', 'ET_GazeLefty', 'ET_GazeRightx',
                    'ET_GazeRighty', 'ET_PupilLeft', 'ET_PupilRight' ]
        os.makedirs(output_path, exist_ok=True)
        for file in os.listdir(raw_path):
            file_path = os.path.join(raw_path, file)
            try:
                df = pd.read_csv(file_path, header=None, low_memory=False)
            except pd.errors.ParserError as e:
                messagebox.showerror("Error", f"Error reading CSV file: {file_path}\n{e}")
                continue
            filename = file.split(".")[0].split("_")[1]
            cleaned_df = file_clean(df, filename)
            if cleaned_df is not None:
                cleaned_df = cleaned_df[columns_to_keep]
                cleaned_csv_filename = f"{filename}_cleaned.csv"
                cleaned_csv_path = os.path.join(output_path, cleaned_csv_filename)
                cleaned_df.to_csv(cleaned_csv_path, index=False)

def execute_cleaning():
    raw_path = raw_entry.get()
    output_path = output_entry.get()
    if not raw_path or not output_path:
        messagebox.showerror("Error", "Please select both input and output directories.")
        return
    clean_files(raw_path, output_path)
    messagebox.showinfo("Info", "Files cleaned successfully!")

# Function definitions for Step 2
def read_csv_file():
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    csv_entry.delete(0, tk.END)
    csv_entry.insert(0, file_path)

def save_excel(df, participant_name, base_path):
        save_path = os.path.join(base_path, f"{participant_name}.xlsx")
        
        workbook = Workbook()

        emotion_columns = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Joy', 
                        'Sadness', 'Surprise', 'Engagement', 'Valence', 
                        'Sentimentality', 'Confusion', 'Neutral']

        for source_stimuli_name in df['SourceStimuliName'].unique():
            sheet = workbook.create_sheet(title=source_stimuli_name[:31])  # Excel sheet names have a maximum length of 31 characters
            
            filtered_df = df[df['SourceStimuliName'] == source_stimuli_name]
            
            # Replace empty strings and NaN with 0 in the specific columns of the filtered DataFrame
            filtered_df[emotion_columns] = filtered_df[emotion_columns].replace("", 0).fillna(0)

            # Select the desired columns
            columns = ['Timestamp', 'Row', 'StimType', 'Duration', 'SourceStimuliName',
                'CollectionPhase', 'SlideEvent', 'Participant', 'SampleNumber',
                'SampleNumber.1', 'SampleNumber.2', 'Anger', 'Contempt', 'Disgust',
                'Fear', 'Joy', 'Sadness', 'Surprise', 'Engagement', 'Valence',
                'Sentimentality', 'Confusion', 'Neutral', 'ET_GazeLeftx', 'ET_GazeLefty', 'ET_GazeRightx',
                    'ET_GazeRighty', 'ET_PupilLeft', 'ET_PupilRight' ]
            
            #filtered_df[columns] = filtered_df[columns].replace("", 0).fillna(0)
            
            sheet.append(columns)
            for row in filtered_df[columns].itertuples(index=False):
                sheet.append(row)

        workbook.remove(workbook['Sheet'])
        workbook.save(save_path)
        
def main_process():
    file_path = csv_entry.get()
    if file_path:
        df = pd.read_csv(file_path)
        participant_name = df['Participant'].iloc[0]  # Extracting the participant's name from the first row
        base_path = os.path.dirname(file_path)
        save_excel(df, participant_name, base_path)
        messagebox.showinfo("Success", f"Excel file has been generated and saved as {participant_name}.xlsx!")
    else:
        messagebox.showwarning("Error", "Unable to read CSV file.")

# Function definitions for Step 
def select_excel_file():
    excel_file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if excel_file_path:
        entry_excel_file.delete(0, tk.END)
        entry_excel_file.insert(0, excel_file_path)

# Function to select the image file
def select_image_file():
    image_file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    if image_file_path:
        entry_image_file.delete(0, tk.END)
        entry_image_file.insert(0, image_file_path)

# Function to create and save individual plots for each emotion
def create_and_save_plot():
    global plot_index
    # Get the file paths and sheet name from the entry fields
    excel_file_path = entry_excel_file.get()
    sheet_name = entry_sheet_name.get()
    image_file_path = entry_image_file.get()

    if not excel_file_path or not sheet_name or not image_file_path:
        print("Please select all required files and enter the sheet name.")
        return

    # Load the data from the Excel file
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    df.dropna(subset=['ET_GazeLeftx', 'ET_GazeLefty', 'ET_GazeRightx', 'ET_GazeRighty'], inplace=True)

    # Calculate the normalized x and y coordinates
    df['norm_x'] = ((df['ET_GazeLeftx'] + df['ET_GazeRightx']) / 2) / 1920
    df['norm_y'] = ((df['ET_GazeLefty'] + df['ET_GazeRighty']) / 2) / 1080

    # Sort data by y-coordinate
    df = df.sort_values('norm_y')
    
    # Rest of the code for data processing and plotting...

    emotions = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Engagement', 'Valence', 'Sentimentality', 'Confusion', 'Neutral']
    # Create a dictionary to store alpha values for each emotion
    
    emotion_alpha = {
            'Anger': 0.02,
            'Contempt': 0.09,
            'Disgust': 0.15,
            'Fear': 0.21,
            'Joy': 0.32,
            'Sadness': 0.4,
            'Surprise': 0.52,
            'Engagement': 0.6,
            'Valence': 0.7,
            'Sentimentality': 0.8,
            'Confusion': 0.9,
            'Neutral': 1.0
        }

        # Create a custom colormap that transitions from white to red
    cdict = {'red':   [[0.0, 1.0, 1.0], [1.0, 1.0, 1.0]],
                'green': [[0.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
                'blue':  [[0.0, 1.0, 1.0], [1.0, 0.0, 0.0]]}
    red_to_white_cmap = LinearSegmentedColormap('RedToWhite', cdict)

        # Function to get emotion color based on value and alpha
    def get_emotion_color_alpha(value, emotion):
            alpha_val = emotion_alpha[emotion]
            color = red_to_white_cmap(value)
            return color[:3] + (alpha_val,)


    for emotion1 in emotions:
        # Create the figure and subplots for each emotion comparison
        fig, axs = plt.subplots(1, 2, figsize=(15, 6))
        figs.append(fig)

        # Left subplot - Scatter plot for the current emotion
        sc = axs[0].scatter(df['norm_x'], df['norm_y'], c=df[emotion1], cmap=red_to_white_cmap, label=f'{emotion1} Emotion Points', alpha=0.8, s=100)
        axs[0].set_title(f'{emotion1} Emotion Points')
        axs[0].set_xlabel('Normalized X-coordinate')
        axs[0].set_ylabel('Normalized Y-coordinate')

        # Set the axis ticks for the left subplot
        axs[0].set_xticks([0, 0.5, 1])
        axs[0].set_yticks([0, 0.5, 1])

        # Right subplot - Heatmap of eye gaze points with the current emotion levels
        sns.kdeplot(data=df, x='norm_x', y='norm_y', fill=True, thresh=0.05, levels=10, cmap=red_to_white_cmap, ax=axs[1], alpha=0.4)
        axs[1].set_title(f'Eye Gaze Heatmap with {emotion1} Emotion')
        axs[1].set_xlabel('Normalized X-coordinate')
        axs[1].set_ylabel('Normalized Y-coordinate')

        # Create a custom colorbar for the current emotion
        cbar_emotion = plt.colorbar(sc, ax=axs[1])
        cbar_emotion.set_label(f'{emotion1} Level')

        # Add the current emotion points as scatter points overlaid on the heatmap
        sc = axs[1].scatter(df['norm_x'], df['norm_y'], c=df[emotion1], cmap=red_to_white_cmap, label=f'{emotion1} Emotion Points', alpha=0.8, s=100)

        # Update the color and alpha values for the scatter points based on emotion values
        sc.set_array(df[emotion1])
        sc.set_cmap(red_to_white_cmap)
        sc.set_color([get_emotion_color_alpha(val, emotion1) for val in df[emotion1]])

        # Add legend on the right subplot
        axs[1].legend()

        # Load the image
        image = Image.open(image_file_path)

        # Resize the image to match the figure size
        fig_width, fig_height = fig.get_size_inches()
        resized_image = image.resize((int(fig_width * image.width), int(fig_height * image.height)))

        # Overlay the resized image with transparency (alpha) on both subplots
        axs[0].imshow(resized_image, extent=[0, 1, 0, 1], alpha=0.9, aspect='auto')
        axs[1].imshow(resized_image, extent=[0, 1, 0, 1], alpha=0.9, aspect='auto')

        plot_queue.append(fig)

        # Create a canvas widget in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=root)  
        canvas.draw()  # Draw the plot onto the canvas
        canvas.get_tk_widget().pack()  # Add the canvas widget to the window
        participant_name = df['Participant'].iloc[0]
        output_folder = os.path.join("Output", participant_name, sheet_name)
        os.makedirs(output_folder, exist_ok=True)
        output_file_path = os.path.join(output_folder, f"{sheet_name}_{emotion1}_{plot_index}_plot.png")
        fig.savefig(output_file_path)

        plot_index += 1

        messagebox.showinfo("Info", "Plot generated and saved!")

def show_plot():
    global plot_window, canvas

    if plot_window:  # Check and destroy the previous plot_window if it exists
        plot_window.destroy()
        plot_window = None
        canvas = None

    if experiment.get() == "New":
        for root, dirs, _ in os.walk("Output"):
            for dir_name in dirs:
                plot_dir = os.path.join(root, dir_name)
                show_image_from_dir(plot_dir)
    else:
        participant = participant_menu.get()
        sheet = sheet_menu.get()
        if participant and sheet:
            plot_dir = os.path.join("Output", participant, sheet)
            if os.path.exists(plot_dir):
                show_image_from_dir(plot_dir)
            else:
                print(f"Directory {plot_dir} does not exist.")

def on_closing():
    global plot_window
    plot_window.destroy()
    plot_window = None

def show_image_from_figure(input_data):
    global plot_window, canvas

    plt.close('all')

    if isinstance(input_data, np.ndarray):
        fig, ax = plt.subplots()
        ax.imshow(input_data)
    else:
        fig = input_data

    ax.axis('off')

    if not plot_window:  # If the plot window hasn't been created yet
        plot_window = tk.Toplevel(root)
        plot_window.protocol("WM_DELETE_WINDOW", on_closing)

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

        # Create the buttons only once (assuming you've defined show_previous_plot and show_next_plot functions)
        previous_plot_button = ttk.Button(plot_window, text="Previous Plot", command=show_previous_plot)
        previous_plot_button.pack(side=tk.LEFT, padx=10, pady=10)

        next_plot_button = ttk.Button(plot_window, text="Next Plot", command=show_next_plot)
        next_plot_button.pack(side=tk.RIGHT, padx=10, pady=10)

    else:  # If the plot window already exists
        canvas.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

def show_image_from_dir(directory):
    global pending_plots

    # Gather all the images from the directory and add to the pending queue
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.png'):
            img_path = os.path.join(directory, filename)
            pending_plots.append(img_path)

    # If there are any images in the queue, show the first one
    if pending_plots:
        next_image = pending_plots.pop(0)
        img = plt.imread(next_image)
        seen_plots.append(next_image)
        show_image_from_figure(img)

def show_previous_plot():
    global seen_plots, pending_plots

    if len(seen_plots) > 1:  # If there is more than one image in seen_plots
        # Move the last shown image to pending_plots and remove it from seen_plots
        pending_image = seen_plots.pop()
        pending_plots.insert(0, pending_image)

        # Load and display the previous image
        prev_image_path = seen_plots[-1]
        img = plt.imread(prev_image_path)
        show_image_from_figure(img)

def show_next_plot():
    global seen_plots, pending_plots

    if pending_plots:  # If there are images left to be shown
        next_image_path = pending_plots.pop(0)
        img = plt.imread(next_image_path)
        seen_plots.append(next_image_path)
        show_image_from_figure(img)

def update_sheets_dropdown(*args):
    selected_participant = participant_var.get()
    if selected_participant:
        participant_dir = os.path.join(base_dir, selected_participant)
        sheets = [name for name in os.listdir(participant_dir) 
                if os.path.isdir(os.path.join(participant_dir, name))]
        sheet_var.set('')  # reset sheet value
        sheet_menu["values"] = sheets

def update_participants_and_sheets():
    participants = [name for name in os.listdir(base_dir) 
                    if os.path.isdir(os.path.join(base_dir, name))]
    participant_var.set('')  # reset participant value
    participant_menu["values"] = participants
    sheet_var.set('')  # reset sheet value

def update_gui(*args):
    selection = experiment.get()

    if selection == "New":
        # Show widgets for "New" option
        # Show widgets for "New" option
        new_experiment_frame.pack(fill='both', padx=20, pady=10)
    # Hide widgets for "Existing" option
        existing_experiment_frame.pack_forget()
        button_select_excel.pack(pady=10)
        entry_excel_file.pack(pady=20)
        label_sheet_name.pack(pady=10)
        entry_sheet_name.pack(pady=10)
        button_select_image.pack(pady=10)
        entry_image_file.pack(pady=20)
        generate_button.pack(pady=20)
        # Hide widgets for "Existing" option
        participant_menu.pack_forget()
        sheet_menu.pack_forget()
    else:
    # Show widgets for "Existing" option
        existing_experiment_frame.pack(fill='both', padx=20, pady=10)
        # Hide widgets for "New" option
        new_experiment_frame.pack_forget()
        participant_menu.pack(pady=10)
        sheet_menu.pack(pady=10)
        # Hide widgets for "New" option
        button_select_excel.pack_forget()
        entry_excel_file.pack_forget()
        label_sheet_name.pack_forget()
        entry_sheet_name.pack_forget()
        button_select_image.pack_forget()
        entry_image_file.pack_forget()
        generate_button.pack_forget()

# Main function to run the app
def run_app():
    global raw_entry, output_entry, csv_entry  # Declare as global so they can be accessed in the other functions

    # Initialize the root Tkinter window
    root = tk.Tk()
    root.title("Multi-step GUI")
    root.geometry("600x400")

    # Create the notebook (tab controller)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Step 1: CSV Cleaner
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Step 1 - CSV Cleaner")

    # File selection frame for Step 1
    file_selection_frame1 = ttk.LabelFrame(tab1, text="File Selection", padding=(10, 5))
    file_selection_frame1.pack(pady=20, padx=20, fill=tk.X)

    ttk.Label(file_selection_frame1, text="Raw Data Folder:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    raw_entry = ttk.Entry(file_selection_frame1)
    raw_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(file_selection_frame1, text="Browse", command=browse_raw_folder).grid(row=0, column=2, padx=5, pady=5)

    ttk.Label(file_selection_frame1, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    output_entry = ttk.Entry(file_selection_frame1)
    output_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(file_selection_frame1, text="Browse", command=browse_output_folder).grid(row=1, column=2, padx=5, pady=5)

    ttk.Button(tab1, text="Execute Cleaning", command=execute_cleaning).pack(pady=20)

    # Ensure the entry fields expand horizontally
    file_selection_frame1.columnconfigure(1, weight=1)

    # Step 2: CSV to Excel Converter
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Step 2 - CSV to Excel Converter")

    # File selection frame for Step 2
    file_selection_frame2 = ttk.LabelFrame(tab2, text="File Selection", padding=(10, 5))
    file_selection_frame2.pack(pady=20, padx=20, fill=tk.X)

    ttk.Label(file_selection_frame2, text="CSV File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    csv_entry = ttk.Entry(file_selection_frame2)
    csv_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(file_selection_frame2, text="Browse", command=read_csv_file).grid(row=0, column=2, padx=5, pady=5)

    ttk.Button(tab2, text="Convert to Excel", command=main_process).pack(pady=20)

    # Ensure the entry fields expand horizontally
    file_selection_frame2.columnconfigure(1, weight=1)

    # Tab 3: Eye Gaze Plot with Emotions Overlay
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Step 3 - Eye Gaze Plot with Emotions Overlay")

    selected_option = tk.StringVar(value="New")

    # File selection frame
    file_selection_frame = ttk.LabelFrame(tab3, text="File Selection", padding=(10, 5))
    file_selection_frame.pack(pady=20, padx=20, fill=tk.X)

    ttk.Label(file_selection_frame, text="Excel File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    entry_excel_file = ttk.Entry(file_selection_frame)
    entry_excel_file.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
    button_select_excel = ttk.Button(file_selection_frame, text="Select", command=select_excel_file)
    button_select_excel.grid(row=0, column=2, padx=5, pady=5)

    ttk.Label(file_selection_frame, text="Image File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    entry_image_file = ttk.Entry(file_selection_frame)
    entry_image_file.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
    button_select_image = ttk.Button(file_selection_frame, text="Select", command=select_image_file)
    button_select_image.grid(row=1, column=2, padx=5, pady=5)

    ttk.Label(file_selection_frame, text="Sheet Name:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    entry_sheet_name = ttk.Entry(file_selection_frame)
    entry_sheet_name.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

    # Control frame for actions
    control_frame = ttk.Frame(tab3, padding=(10, 5))
    control_frame.pack(pady=20, padx=20, fill=tk.X)

    generate_button = ttk.Button(control_frame, text="Generate Plot", command=create_and_save_plot)
    generate_button.pack(pady=10)

    # Ensure the entry fields expand horizontally
    file_selection_frame.columnconfigure(1, weight=1)

    root.mainloop()

# Run the app
run_app()

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os # Added for file path operations and existence checks
import datetime # Added for dummy data generation if parse_dataset is not available
import numpy as np # Added for dummy data generation if parse_dataset is not available
import seaborn as sns # Added for compare_glycaemic_measures figure extraction

from libs.visualisation import get_individual_plot, get_daily_glycaemic_variation, get_group_daily_glycaemic_variation, compare_glycaemic_measures, compare_measures
from src.dataset.parse_dataset import get_pIDs, prepare_data, get_profiles

# Import visualisation functions


class GlucoseVisualisationApp:
    def __init__(self, master):
        self.master = master
        master.title("T1DM Glucose Explorer")

        self.df = None
        self.profiles = None
        self.pIDs = []

        # Default dataset name and directory for auto-building
        # self.dataset_name = 'OhioT1DM'
        self.dataset_dir = './datasets/'

        # --- Frames ---
        self.file_frame = ttk.LabelFrame(master, text="Data Selection")
        self.file_frame.pack(padx=10, pady=10, fill=tk.X)

        self.plot_frame = ttk.LabelFrame(master, text="Plot Configuration")
        self.plot_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.canvas_frame = ttk.Frame(master)
        self.canvas_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- Widgets for File Selection ---
        ttk.Label(self.file_frame, text="Dataset Name:").grid(row=0, column=0, padx=5, pady=5)
        self.dataset_name_var = tk.StringVar(value="OhioT1DM") # Default value
        self.dataset_name_entry = ttk.Entry(self.file_frame, width=50, textvariable=self.dataset_name_var)
        self.dataset_name_entry.grid(row=0, column=1, padx=0, pady=5, columnspan=2)

        ttk.Label(self.file_frame, text="Glucose Data CSV:").grid(row=1, column=0, padx=5, pady=5)
        self.glucose_file_path = ttk.Entry(self.file_frame, width=50)
        self.glucose_file_path.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.file_frame, text="Browse", command=self.load_glucose_data).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(self.file_frame, text="Auto-Load/Build Glucose", command=lambda: self._ensure_data_loaded(data_type='glucose')).grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(self.file_frame, text="Profiles Data CSV:").grid(row=2, column=0, padx=5, pady=5)
        self.profiles_file_path = ttk.Entry(self.file_frame, width=50)
        self.profiles_file_path.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.file_frame, text="Browse", command=self.load_profiles_data).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(self.file_frame, text="Auto-Load/Build Profiles", command=lambda: self._ensure_data_loaded(data_type='profiles')).grid(row=2, column=3, padx=5, pady=5)

        
        # --- Plot Selection and Configuration ---
        ttk.Label(self.plot_frame, text="Select Plot:").grid(row=0, column=0, padx=5, pady=5)
        self.plot_type = ttk.Combobox(self.plot_frame,
                                      values=["Individual Plot", "Daily Glycaemic Variation", "Group Daily Glycaemic Variation", "Glycaemic Metrics Comparison", "Glycaemic Distribution Comparison", "CEG Analysis Comparison"])
        self.plot_type.grid(row=0, column=1, padx=5, pady=5)
        self.plot_type.bind("<<ComboboxSelected>>", self.update_plot_options)

        self.plot_options_frame = ttk.Frame(self.plot_frame)
        self.plot_options_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5) # Adjusted columnspan

        self.draw_button = ttk.Button(self.plot_frame, text="Draw Plot", command=self.draw_plot)
        self.draw_button.grid(row=2, column=0, columnspan=4, pady=10) # Adjusted columnspan

        # --- Canvas for Plotting ---
        self.fig = plt.Figure(figsize=(8, 6)) # Initialize with an empty Figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.clear_canvas() # Initialise with empty plot

    def _ensure_data_loaded(self, data_type=None):
        """
        Ensures glucose and/or profiles data is loaded, attempting to build from scratch if files are not found.
        """
        if not os.path.exists(self.dataset_dir):
            os.makedirs(self.dataset_dir)

        current_dataset_name = self.dataset_name_var.get()

        if data_type is None or data_type == 'glucose':
            if self.df is None:
                glucose_csv_path = os.path.join(self.dataset_dir, f'{current_dataset_name}.csv')
                if os.path.exists(glucose_csv_path):
                    try:
                        self.df = pd.read_csv(glucose_csv_path)
                        self.pIDs = list(self.df['pID'].unique())
                        print(f"Loaded glucose data from {glucose_csv_path}")
                    except Exception as e:
                        tk.messagebox.showwarning("Warning", f"Could not load {glucose_csv_path}: {e}. Attempting to build.")
                        self._build_glucose_data()
                else:
                    self._build_glucose_data()

        if data_type is None or data_type == 'profiles':
            if self.profiles is None:
                profiles_csv_path = os.path.join(self.dataset_dir, f'{current_dataset_name}_profile.csv')
                if os.path.exists(profiles_csv_path):
                    try:
                        self.profiles = pd.read_csv(profiles_csv_path)
                        print(f"Loaded profiles data from {profiles_csv_path}")
                    except Exception as e:
                        tk.messagebox.showwarning("Warning", f"Could not load {profiles_csv_path}: {e}. Attempting to build.")
                        self._build_profiles_data()
                else:
                    self._build_profiles_data()

    def _build_glucose_data(self):
        """Builds glucose data using prepare_data and saves it to CSV."""
        try:
            # get_pIDs might need a real dataset_path depending on its implementation
            # For dummy functions, a placeholder path is fine.
            current_dataset_name = self.dataset_name_var.get()
            dataset_path = './datasets/{}/raw/'.format(current_dataset_name)
            pIDs_for_build = get_pIDs(dataset_path)
            self.df = prepare_data(dataset_path, pIDs_for_build, True)
            self.df.to_csv(os.path.join(self.dataset_dir, f'{current_dataset_name}.csv'), index=False)
            self.pIDs = list(self.df['pID'].unique())
            print(f"Built and saved glucose data to {self.dataset_dir}/{current_dataset_name}.csv")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to build glucose data: {e}. "
                                     "Please ensure 'src.dataset.parse_dataset' is correctly set up "
                                     "and raw data is accessible if not using dummy functions.")
            self.df = None # Ensure df is None if building fails

    def _build_profiles_data(self):
        """Builds profiles data using get_profiles and saves it to CSV."""
        try:
            # get_profiles might need a real dataset_path depending on its implementation
            current_dataset_name = self.dataset_name_var.get()
            dataset_path = './datasets/{}/raw/'.format(current_dataset_name)
            profiles_df = get_profiles(dataset_path)
            profiles_df.to_csv(os.path.join(self.dataset_dir, f'{current_dataset_name}_profile.csv'), index=False)
            self.profiles = profiles_df
            print(f"Built and saved profiles data to {self.dataset_dir}/{current_dataset_name}_profile.csv")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to build profiles data: {e}. "
                                     "Please ensure 'src.dataset.parse_dataset' is correctly set up "
                                     "and raw data is accessible if not using dummy functions.")
            self.profiles = None # Ensure profiles is None if building fails

    def load_glucose_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.glucose_file_path.delete(0, tk.END)
            self.glucose_file_path.insert(0, file_path)
            try:
                self.df = pd.read_csv(file_path)
                self.pIDs = list(self.df['pID'].unique())
                print("Glucose data loaded successfully from selected file.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Could not load glucose data from selected file: {e}")
                self.df = None

    def load_profiles_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.profiles_file_path.delete(0, tk.END)
            self.profiles_file_path.insert(0, file_path)
            try:
                self.profiles = pd.read_csv(file_path)
                print("Profiles data loaded successfully from selected file.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Could not load profiles data from selected file: {e}")
                self.profiles = None

    def update_plot_options(self, event=None):
        self.clear_plot_options()
        selected_plot = self.plot_type.get()

        # Ensure profiles data is loaded if a category-dependent plot is selected
        if selected_plot in ["Group Daily Glycaemic Variation", "Glycaemic Metrics Comparison", "Glycaemic Distribution Comparison", "CEG Analysis Comparison"]:
            self._ensure_data_loaded(data_type='profiles') # Attempt to load/build profiles data

        if selected_plot == "Individual Plot":
            self.add_individual_plot_options()
        elif selected_plot == "Daily Glycaemic Variation":
            self.add_daily_variation_options()
        elif selected_plot == "Group Daily Glycaemic Variation":
            self.add_group_variation_options()
        elif selected_plot == "Glycaemic Metrics Comparison":
            self.add_compare_glycaemic_options()
        elif selected_plot == "Glycaemic Distribution Comparison":
            self.add_compare_glycaemic_distributions()
        elif selected_plot == "CEG Analysis Comparison":
            self.add_compare_measures_options()

    def clear_plot_options(self):
        for widget in self.plot_options_frame.winfo_children():
            widget.destroy()

    def add_individual_plot_options(self):
        ttk.Label(self.plot_options_frame, text="Select pID:").grid(row=0, column=0, padx=5, pady=5)
        self.pID_var = tk.IntVar(value= self.pIDs[0])
        self.pID_entry = ttk.Combobox(self.plot_options_frame, textvariable=self.pID_var, values = self.pIDs)
        self.pID_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.plot_options_frame, text="Start Day:").grid(row=1, column=0, padx=5, pady=5)
        self.start_day_var = tk.IntVar(value=0)
        self.start_day_entry = ttk.Entry(self.plot_options_frame, textvariable=self.start_day_var)
        self.start_day_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.plot_options_frame, text="End Day:").grid(row=2, column=0, padx=5, pady=5)
        self.end_day_var = tk.IntVar(value=1000)
        self.end_day_entry = ttk.Entry(self.plot_options_frame, textvariable=self.end_day_var)
        self.end_day_entry.grid(row=2, column=1, padx=5, pady=5)

    def add_daily_variation_options(self):
        ttk.Label(self.plot_options_frame, text="Select pID:").grid(row=0, column=0, padx=5, pady=5)
        self.daily_pID_var = tk.IntVar(value= self.pIDs[0])
        self.daily_pID_entry = ttk.Combobox(self.plot_options_frame, textvariable=self.daily_pID_var, values = self.pIDs)
        self.daily_pID_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.plot_options_frame, text="Interval Type:").grid(row=1, column=0, padx=5, pady=5)
        self.interval_type_var = tk.StringVar(value="sparse")
        self.interval_type_combo = ttk.Combobox(self.plot_options_frame, textvariable=self.interval_type_var, values=["sparse", "dense"])
        self.interval_type_combo.grid(row=1, column=1, padx=5, pady=5)

    def add_group_variation_options(self):
        ttk.Label(self.plot_options_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        categories = []
        if self.profiles is not None:
          categories = list(self.profiles.columns)[1:]
        self.group_category_var = tk.StringVar()
        self.group_category_combo = ttk.Combobox(self.plot_options_frame, textvariable=self.group_category_var, values=categories)
        self.group_category_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.plot_options_frame, text="Interval Type:").grid(row=1, column=0, padx=5, pady=5)
        self.group_interval_type_var = tk.StringVar(value="sparse")
        self.group_interval_type_combo = ttk.Combobox(self.plot_options_frame, textvariable=self.group_interval_type_var, values=["sparse", "dense"])
        self.group_interval_type_combo.grid(row=1, column=1, padx=5, pady=5)

    def add_compare_glycaemic_options(self):
        ttk.Label(self.plot_options_frame, text="Measure:").grid(row=0, column=0, padx=5, pady=5)
        measures = ['SD', 'CV', 'CONGA24', 'GMI', 'j-index', 'MODD', 'eA1c', 'HBGI', 'LBGI', 'ADDR']
        self.compare_measure_var = tk.StringVar()
        self.compare_measure_combo = ttk.Combobox(self.plot_options_frame, textvariable=self.compare_measure_var, values=measures)
        self.compare_measure_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.plot_options_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        categories = []
        if self.profiles is not None:
          categories = list(self.profiles.columns)[1:]
        self.compare_category_var = tk.StringVar()
        self.compare_category_combo = ttk.Combobox(self.plot_options_frame, textvariable=self.compare_category_var, values=categories)
        self.compare_category_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.plot_options_frame, text="Hue:").grid(row=2, column=0, padx=5, pady=5)
        hue_categories = ["None"] + categories
        self.compare_hue_var = tk.StringVar(value="None")
        self.compare_hue_combo = ttk.Combobox(self.plot_options_frame, textvariable=self.compare_hue_var, values=hue_categories)
        self.compare_hue_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.plot_options_frame, text="Start Day:").grid(row=3, column=0, padx=5, pady=5)
        self.compare_start_day_var = tk.IntVar(value=0)
        self.compare_start_day_entry = ttk.Entry(self.plot_options_frame, textvariable=self.compare_start_day_var)
        self.compare_start_day_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.plot_options_frame, text="End Day:").grid(row=4, column=0, padx=5, pady=5)
        self.compare_end_day_var = tk.IntVar(value=1000)
        self.compare_end_day_entry = ttk.Entry(self.plot_options_frame, textvariable=self.compare_end_day_var)
        self.compare_end_day_entry.grid(row=4, column=1, padx=5, pady=5)

    def add_compare_glycaemic_distributions(self):
        ttk.Label(self.plot_options_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        categories = []
        if self.profiles is not None:
          categories = list(self.profiles.columns)[1:]
        self.hist_category_var = tk.StringVar()
        self.hist_category_combo = ttk.Combobox(self.plot_options_frame, textvariable=self.hist_category_var, values=categories)
        self.hist_category_combo.grid(row=0, column=1, padx=5, pady=5)

    def add_compare_measures_options(self):
        ttk.Label(self.plot_options_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        categories = []
        if self.profiles is not None:
          categories = list(self.profiles.columns)[1:]
        self.clarke_category_var = tk.StringVar()
        self.clarke_category_combo = ttk.Combobox(self.plot_options_frame, textvariable=self.clarke_category_var, values=categories)
        self.clarke_category_combo.grid(row=0, column=1, padx=5, pady=5)

    def draw_plot(self):
        self.clear_canvas() # Clear the existing plot before drawing a new one

        # Ensure data is loaded or attempt to build it before plotting
        self._ensure_data_loaded(data_type='glucose')
        selected_plot = self.plot_type.get()

        if selected_plot in ["Group Daily Glycaemic Variation", "Glycaemic Metrics Comparison", "Glycaemic Distribution Comparison", "CEG Analysis Comparison"]:
            self._ensure_data_loaded(data_type='profiles')

        if self.df is None:
            tk.messagebox.showerror("Error", "Glucose data is not available. Please load or build it.")
            return
        if selected_plot in ["Group Daily Glycaemic Variation", "Glycaemic Metrics Comparison", "Glycaemic Distribution Comparison", "CEG Analysis Comparison"] and self.profiles is None:
            tk.messagebox.showerror("Error", "Profiles data is not available for this plot type. Please load or build it.")
            return

        new_fig = None # Variable to hold the Figure object returned by plotting functions

        try:
            if selected_plot == "Individual Plot":
                pID_str = self.pID_entry.get()
                try:
                    pID = int(pID_str) # Convert pID to integer
                except ValueError:
                    tk.messagebox.showerror("Input Error", f"Invalid pID: '{pID_str}'. Please select a valid patient ID.")
                    return
                start_day = self.start_day_var.get()
                end_day = self.end_day_var.get()
                current_dataset_name = self.dataset_name_var.get()

                # Assumes get_individual_plot returns a Figure object
                new_fig = get_individual_plot(self.df, current_dataset_name, pID, start_day, end_day)


            elif selected_plot == "Daily Glycaemic Variation":
                pID_str = self.daily_pID_entry.get()
                try:
                    pID = int(pID_str) # Convert pID to integer
                except ValueError:
                    tk.messagebox.showerror("Input Error", f"Invalid pID: '{pID_str}'. Please select a valid patient ID.")
                    return
                interval_type = self.interval_type_var.get()
                current_dataset_name = self.dataset_name_var.get()
                # Assumes get_daily_glycaemic_variation returns a Figure object

                new_fig = get_daily_glycaemic_variation(self.df, current_dataset_name, pID, interval_type)

            elif selected_plot == "Group Daily Glycaemic Variation":
                category = self.group_category_var.get()
                interval_type = self.group_interval_type_var.get()
                # Assumes get_group_daily_glycaemic_variation returns a Figure object
                new_fig = get_group_daily_glycaemic_variation(self.df, self.profiles, category, interval_type)

            elif selected_plot == "Glycaemic Metrics Comparison":
                measure = self.compare_measure_var.get()
                category = self.compare_category_var.get()
                hue = self.compare_hue_var.get()
                start_day = self.compare_start_day_var.get()
                end_day = self.compare_end_day_var.get()
                if hue == "None":
                    hue = None
                pIDs_for_comparison = list(self.df['pID'].unique())
                # Assumes compare_glycaemic_measures returns a seaborn FacetGrid/Axes object,
                # from which we can extract the Figure.
                sns_plot_object = compare_glycaemic_measures(self.df, self.profiles.copy(), pIDs_for_comparison, measure, category, hue, start_day, end_day)
                if hasattr(sns_plot_object, 'fig'):
                    new_fig = sns_plot_object.fig
                elif hasattr(sns_plot_object, 'figure'): # For some seaborn functions, it might be 'figure'
                    new_fig = sns_plot_object.figure
                else:
                    tk.messagebox.showerror("Error", "Could not extract Figure from seaborn plot object.")
                    return
                
            elif selected_plot == "Glycaemic Distribution Comparison":
                category = self.hist_category_var.get()
                cat_array = self.profiles.copy()[category].unique()
                df_group = self.df
                for cat in cat_array:
                    mask = self.profiles[category] == cat
                    inc  = self.profiles.loc[mask, 'pID']
                    select_pIDs = inc.unique()

                    df_group.loc[df_group['pID'].isin(select_pIDs), category] = cat

                sns_plot_object = sns.histplot(data=df_group, x='CGM' ,bins=30, stat = 'density', hue=category, kde=True, legend=True, common_norm=False)

                if hasattr(sns_plot_object, 'fig'):
                    new_fig = sns_plot_object.fig
                elif hasattr(sns_plot_object, 'figure'): # For some seaborn functions, it might be 'figure'
                    new_fig = sns_plot_object.figure
                else:
                    tk.messagebox.showerror("Error", "Could not extract Figure from seaborn plot object.")
                    return


            elif selected_plot == "CEG Analysis Comparison":
                category = self.clarke_category_var.get()
                cat_array = self.profiles.copy()[category].unique()

                new_fig, axs = plt.subplots(ncols= len(cat_array), figsize = (len(cat_array) * 5,6))

                for ax, cat in zip(axs, cat_array):
                    mask = self.profiles[category] == cat
                    inc  = self.profiles.loc[mask, 'pID']
                    select_pIDs = inc.unique()
                    # Assumes compare_measures returns a Figure object (and potentially other data)
                    ax, zone, zone_index = compare_measures(self.df, select_pIDs, ax)
                    ax.set_title('[{cat}] Safe Regions: {per:.1f}%'.format(cat = cat, per = zone[0] + zone[1]))

                new_fig.tight_layout()
                new_fig.suptitle(f'Clarke Error Grid stratified by {category}')
                   
            if new_fig:
                # Destroy the old canvas widget
                if self.canvas_widget:
                    self.canvas_widget.destroy()
                # Only close the figure if it's a valid matplotlib Figure object
                if hasattr(self, 'fig') and isinstance(self.fig, plt.Figure):
                    plt.close(self.fig) # Close the old matplotlib figure to free memory

                # Create a new canvas widget with the new figure
                self.fig = new_fig # Update the instance's figure reference
                self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
                self.canvas.draw()
                self.canvas_widget = self.canvas.get_tk_widget()
                self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            else:
                tk.messagebox.showerror("Error", "Plot generation failed or no figure was returned.")

        except Exception as e:
            tk.messagebox.showerror("Plotting Error", f"An error occurred during plotting: {e}")
            self.clear_canvas() # Clear canvas on error

    def clear_canvas(self):
        """Clears the current canvas and replaces it with an empty plot."""
        if self.canvas_widget:
            self.canvas_widget.destroy()
        # Only attempt to close if self.fig is actually a Figure object
        if hasattr(self, 'fig') and isinstance(self.fig, plt.Figure):
            plt.close(self.fig) # Close the previous figure to free memory

        self.fig = plt.Figure(figsize=(8, 6)) # Create a new empty figure
        self.ax = self.fig.add_subplot(111) # Add an axes to it
        self.ax.set_xlabel("")
        self.ax.set_ylabel("")
        self.ax.set_title("Load data and select plot type")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = GlucoseVisualisationApp(root)
    root.mainloop()

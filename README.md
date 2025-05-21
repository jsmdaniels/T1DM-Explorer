# T1DM Glucose Explorer: Exploratory Data Analysis Tool

This tool provides a user-friendly interface for exploring and visualizing glucose data from publicly available datasets related to Type 1 Diabetes Mellitus (T1DM). It includes both a Jupyter Notebook for direct code interaction and a standalone GUI application for interactive data visualization.

![Example plot](https://raw.githubusercontent.com/jsmdaniels/T1DM-Explorer/refs/heads/main/examples/T1DM-Explorer-individual-plot.png)

## Features

  * **Dataset Loading and Preparation**: Easily load pre-processed glucose and profiles data, or automatically build them from raw files for supported datasets.
  * **Individual Patient Data Visualization**: Plot time-series glucose, carbohydrate, and insulin data for individual patients over specified date ranges.
  * **Daily Glycaemic Variation Analysis**: Visualize the mean and standard deviation of daily glucose levels, showing typical glucose patterns throughout a 24-hour cycle for individuals.
  * **Grouped Glycaemic Variation**: Compare daily glycaemic variations across different demographic or clinical categories (e.g., Age, Gender).
  * **Glycaemic Metrics Comparison**: Analyze various glycaemic risk measures (e.g., SD, CV, CONGA24, GMI, j-index, MODD, eA1c, HBGI, LBGI, ADDR) across different patient groups or categories.
  * **Glycaemic Distribution Comparison**: Visualize and compare the distribution of glucose values for different patient categories using histograms.
  * **Clarke Error Grid Analysis (CEG)**: Evaluate the clinical accuracy of glucose measurements by plotting reference versus BGM (Blood Glucose Meter) readings and calculating points in different error zones, stratified by chosen categories.

## Getting Started

### Prerequisites

  * Python 3.7+
  * Required Python packages (will be installed via `requirements.txt`):
      * `numpy`
      * `pandas`
      * `seaborn`
      * `matplotlib`
      * `scikit-learn` (for `OrdinalEncoder` in `data_visualizer.ipynb`)
      * `tk` (usually comes with Python, but ensure `tkinter` is available)

### Installation

1.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

2.  **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

### Data Setup

The tool expects raw dataset files to be organized in a specific structure for automatic loading and processing.
Create a `datasets` folder in the root directory of the project. Within `datasets`, create subfolders for each dataset (e.g., `OhioT1DM`, `Replace_BG`). Inside each dataset folder, there should be a `raw` folder where the original raw data files are located.

Example structure:

```
.
├── datasets/
│   ├── OhioT1DM/
│   │   └── raw/
│   │       ├── patient_data_files...
│   ├── Replace_BG/
│   │   └── raw/
│   │       ├── patient_data_files...
├── src/
│   └── dataset/
│       ├── parse_dataset.py
│       ├── dataset_OhioT1DM.py
│       ├── dataset_replaceBG.py
├── libs/
│   ├── visualisation.py
│   ├── CEG.py
├── main.py
├── data_visualizer.ipynb
├── README.md
├── requirements.txt
```

The tool can then automatically load or build the processed `.csv` files (e.g., `OhioT1DM.csv`, `OhioT1DM_profile.csv`) into the `datasets/` directory.

## Usage

### 1\. Using the GUI Application

To launch the interactive GUI application:

```bash
python main.py
```

**GUI Usage Steps:**

1.  **Dataset Name**: Enter the name of the dataset (e.g., "OhioT1DM").
2.  **Load Data**:
      * Click "Browse" to manually select pre-processed `_glucose.csv` and `_profile.csv` files.
      * Click "Auto-Load/Build Glucose" and "Auto-Load/Build Profiles" to attempt to load existing CSVs from `./datasets/` or build them from raw data if they don't exist.
3.  **Select Plot**: Choose a plot type from the "Select Plot" dropdown menu (e.g., "Individual Plot", "Daily Glycaemic Variation").
4.  **Configure Plot Options**: Depending on the selected plot, relevant configuration options will appear (e.g., pID, start/end day, category for grouping).
5.  **Draw Plot**: Click the "Draw Plot" button to generate and display the visualization.

![T1DM-Explorer-daily-glycaemic-plot](https://raw.githubusercontent.com/jsmdaniels/T1DM-Explorer/refs/heads/main/examples/T1DM-Explorer-daily-glycaemic-plot.PNG)

![T1DM-Explorer-glycaemic-comparison-plot-1](https://raw.githubusercontent.com/jsmdaniels/T1DM-Explorer/refs/heads/main/examples/T1DM-Explorer-glycaemic-comp-plot-1.PNG)

![T1DM-Explorer-glycaemic-comparison-plot-2](https://raw.githubusercontent.com/jsmdaniels/T1DM-Explorer/refs/heads/main/examples/T1DM-Explorer-glycaemic-comp-plot-2.PNG)

![T1DM-Explorer-glycaemic-histogram-plo](https://raw.githubusercontent.com/jsmdaniels/T1DM-Explorer/refs/heads/main/examples/T1DM-Explorer-glycaemic-hist-plot.PNG)

![T1DM-Explorer-CEG-plot](https://raw.githubusercontent.com/jsmdaniels/T1DM-Explorer/refs/heads/main/examples/T1DM-Explorer-ceg-plot.PNG)

### 2\. Using the Jupyter Notebook

Open `data_visualizer.ipynb` in a Jupyter environment (e.g., Jupyter Lab, Jupyter Notebook, VS Code with Jupyter extension).

```bash
jupyter notebook data_visualizer.ipynb
```

The notebook provides a step-by-step example of how to load data and generate different visualizations programmatically. You can modify the `dataset` variable and `pID`, `start_day`, `end_day` parameters in the cells to explore different aspects of the data.

Follow the cells sequentially:

  * **Initialization**: Imports necessary libraries.
  * **Dataset Selection**: Define the `dataset` and `dataset_path`.
  * **Data Loading/Preparation**: Cells are set up to load pre-existing CSVs or run `prepare_data` to generate them from raw data.
  * **Visualization Calls**: Cells demonstrate how to call the visualization functions directly with specific parameters (e.g., `get_individual_plot`, `get_daily_glycaemic_variation`, `get_group_daily_glycaemic_variation`, `compare_measures`, `compare_glycaemic_measures`).

## Modules

  * `main.py`: The main script for the Tkinter GUI application.
  * `data_visualizer.ipynb`: A Jupyter Notebook demonstrating the usage of visualization functions.
  * `src/dataset/parse_dataset.py`: Handles parsing raw dataset files and preparing dataframes. It includes functions to get patient IDs (`get_pIDs`), read dataframes (`read_df`), get record times (`get_record_time`), get profiles (`get_profiles`), and prepare complete datasets (`prepare_data`).
  * `libs/visualisation.py`: Contains functions for generating various plots and glycaemic measures.
      * `get_individual_plot()`: Plots individual patient glucose, carbohydrate, and insulin data.
      * `get_daily_glycaemic_variation()`: Shows mean and std deviation of daily glucose for an individual.
      * `get_group_daily_glycaemic_variation()`: Displays mean and std deviation of daily glucose for patient groups based on a category.
      * `compare_measures()`: Implements Clarke Error Grid Analysis.
      * `compare_glycaemic_measures()`: Compares selected glycaemic metrics across categories.
      * `get_glycaemic_measures()`: Calculates various glycaemic metrics (e.g., SD, CV, ADDR).
  * `libs/CEG.py`: Implements the Clarke Error Grid algorithm.
  * `libs/cg_ega/cg_ega.py`: Contains code for Control Variability Grid Analysis (CVGA) (though not explicitly used in the provided `visualisation.py` code snippet, it's part of the `libs` structure).

## Contributing

Contributions are welcome\! Please feel free to open issues or submit pull requests.

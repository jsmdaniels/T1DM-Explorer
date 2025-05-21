'''
CLARKE ERROR GRID ANALYSIS      ClarkeErrorGrid.py

The Clarke Error Grid shows the differences between a blood glucose predictive measurement and a reference measurement,
and it shows the clinical significance of the differences between these values.
The x-axis corresponds to the reference value and the y-axis corresponds to the prediction.
The diagonal line shows the prediction value is the exact same as the reference value.
This grid is split into five zones. Zone A is defined as clinical accuracy while
zones C, D, and E are considered clinical error.

Zone A: Clinically Accurate
    This zone holds the values that differ from the reference values no more than 20 percent
    or the values in the hypoglycemic range (<70 mg/dl).
    According to the literature, values in zone A are considered clinically accurate.
    These values would lead to clinically correct treatment decisions.
Zone B: Clinically Acceptable
    This zone holds values that differe more than 20 percent but would lead to
    benign or no treatment based on assumptions.
Zone C: Overcorrecting
    This zone leads to overcorrecting acceptable BG levels.
Zone D: Failure to Detect
    This zone leads to failure to detect and treat errors in BG levels.
    The actual BG levels are outside of the acceptable levels while the predictions
    lie within the acceptable range
Zone E: Erroneous treatment
    This zone leads to erroneous treatment because prediction values are opposite to
    actual BG levels, and treatment would be opposite to what is recommended.

SYNTAX:
        fig, ax, zone, zone_index = clarke_error_grid(ref_values, pred_values, title_string)

INPUT:
        ref_values          List of n reference values.
        pred_values         List of n prediciton values.
        title_string        String of the title.

OUTPUT:
        fig                 The Matplotlib figure object.
        ax                  The Matplotlib axes (subplot) object.
        zone                List of counts of values in each zone.
                            [count_A, count_B, count_C, count_D, count_E]
        zone_index          List of lists containing indices of points in each zone.
                            [indices_A, indices_B, indices_C, indices_D, indices_E]

EXAMPLE:
        import matplotlib.pyplot as plt # Import pyplot for showing the plot

        ref_values = [i for i in range(50, 350, 5)]
        pred_values = [i + (5 - i % 10) * (-1)**(i//10) for i in range(50, 350, 5)] # Example data
        title = "Sample Clarke Error Grid"

        fig, ax, zone, zone_index = clarke_error_grid(ref_values, pred_values, title)
        
        # To display the plot
        plt.show() 

        print(f"Zone A points: {zone[0]}")
        print(f"Zone B points: {zone[1]}")
        print(f"Zone C points: {zone[2]}")
        print(f"Zone D points: {zone[3]}")
        print(f"Zone E points: {zone[4]}")

References:
[1]     Clarke, WL. (2005). "The Original Clarke Error Grid Analysis (EGA)."
        Diabetes Technology and Therapeutics 7(5), pp. 776-779.
[2]     Maran, A. et al. (2002). "Continuous Subcutaneous Glucose Monitoring in Diabetic
        Patients" Diabetes Care, 25(2).
[3]     Kovatchev, B.P. et al. (2004). "Evaluating the Accuracy of Continuous Glucose-
        Monitoring Sensors" Diabetes Care, 27(8).
[4]     Guevara, E. and Gonzalez, F. J. (2008). Prediction of Glucose Concentration by
        Impedance Phase Measurements, in MEDICAL PHYSICS: Tenth Mexican
        Symposium on Medical Physics, Mexico City, Mexico, vol. 1032, pp.
        259261.
[5]     Guevara, E. and Gonzalez, F. J. (2010). Joint optical-electrical technique for
        noninvasive glucose monitoring, REVISTA MEXICANA DE FISICA, vol. 56,
        no. 5, pp. 430434.

Modified to use Figure and Axes objects.
'''

import matplotlib.pyplot as plt

def clarke_error_grid(ref_values, pred_values, ax):
    """
    Generates a Clarke Error Grid plot using Matplotlib's Figure and Axes objects.

    Args:
        ref_values (list or array-like): Reference glucose values.
        pred_values (list or array-like): Predicted glucose values.
        title_string (str): Title for the plot.

    Returns:
        tuple: (fig, ax, zone, zone_index)
            fig (matplotlib.figure.Figure): The figure object.
            ax (matplotlib.axes.Axes): The axes object.
            zone (list): Count of points in each zone [A, B, C, D, E].
            zone_index (list of lists): Indices of points in each zone.
    """

    # Checking to see if the lengths of the reference and prediction arrays are the same
    assert (len(ref_values) == len(pred_values)), \
        "Unequal number of values (reference : {}) (prediction : {})".format(len(ref_values), len(pred_values))

    # Checks to see if the values are within the normal physiological range, otherwise it gives a warning
    if max(ref_values) > 400 or max(pred_values) > 400:
        print("Input Warning: the maximum reference value {} or the maximum prediction value {} exceeds the normal "
              "physiological range of glucose (<400 mg/dl)".format(max(ref_values), max(pred_values)))
    if min(ref_values) < 0 or min(pred_values) < 0:
        print("Input Warning: the minimum reference value {} or the minimum prediction value {} is less than 0 mg/dl"
              .format(min(ref_values),  min(pred_values)))


    # Scatter plot of the data
    ax.scatter(ref_values, pred_values, marker='o', color='red', s=8, label="Data Points")

    # Set up plot labels and title
    # ax.set_title(title_string + " Clarke Error Grid")
    ax.set_xlabel("Reference Glucose Concentration (mg/dl)")
    ax.set_ylabel("Predicted Glucose Concentration (mg/dl)")

    # Set ticks for x and y axes
    ticks = [0, 50, 100, 150, 200, 250, 300, 350, 400]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)

    # Set facecolor of the plot area
    ax.set_facecolor('white')

    # Set axes limits and aspect ratio
    ax.set_xlim([0, 400])
    ax.set_ylim([0, 400])
    ax.set_aspect('equal', adjustable='box') # Ensures the plot is square

    # Plot zone lines
    # These lines define the boundaries of the different zones in the Clarke Error Grid.
    ax.plot([0,400], [0,400], ':', c='black')                      # Theoretical 45 regression line (perfect agreement)
    
    # Zone A/B boundaries
    ax.plot([0, 175/3], [70, 70], '-', c='black')
    ax.plot([175/3, 400/1.2], [70, 400], '-', c='black') # Upper B boundary
    
    # Zone A/C boundaries (more complex, involves multiple segments)
    ax.plot([70, 70], [84, 400],'-', c='black') # Lower C boundary for y > 84 when x = 70
    
    # Zone A/D boundaries
    ax.plot([0, 70], [180, 180], '-', c='black') # Upper D boundary for x < 70
    ax.plot([70, 290],[180, 400],'-', c='black') # Upper D boundary for x > 70
    
    # Zone A/E boundaries (symmetric to C and D)
    ax.plot([70, 70], [0, 56], '-', c='black') # Upper E boundary for y < 56 when x = 70
    ax.plot([70, 400], [56, 320],'-', c='black') # Lower E boundary

    # Other internal zone lines
    ax.plot([180, 180], [0, 70], '-', c='black') # Separates D and E for y < 70
    ax.plot([180, 400], [70, 70], '-', c='black') # Separates B and D for y = 70
    
    ax.plot([240, 240], [70, 180],'-', c='black') # Separates B and D
    ax.plot([240, 400], [180, 180], '-', c='black') # Separates B and C
    
    # This line seems to be an older or alternative C/E boundary, keeping for consistency if it was intentional
    # ax.plot([130, 180], [0, 70], '-', c='black') 
    # Based on the original logic, the line below is more consistent with the zones:
    # This line defines a part of the lower boundary of C or upper boundary of E for low reference values
    # For example, if ref_values[i] is between 130 and 180, and pred_values[i] is very low (e.g., < 70),
    # it could fall into zone C or E.
    # The original code had plt.plot([130, 180], [0, 70], '-', c='black')
    # This implies a line from (130,0) to (180,70). Let's keep it.
    ax.plot([130, 180], [0, 70], '-', c='black')


    # Add zone labels (text annotations on the plot)
    ax.text(30, 15, "A", fontsize=15)
    ax.text(370, 260, "B", fontsize=15) # Upper B
    ax.text(280, 370, "B", fontsize=15) # Right B
    ax.text(160, 370, "C", fontsize=15) # Upper C
    ax.text(160, 15, "C", fontsize=15)  # Lower C
    ax.text(30, 140, "D", fontsize=15)  # Left D
    ax.text(370, 120, "D", fontsize=15) # Right D
    ax.text(30, 370, "E", fontsize=15)  # Upper E
    ax.text(370, 15, "E", fontsize=15)  # Lower E

    # Initialize zone counters and lists for indices
    zone = [0] * 5  # A, B, C, D, E
    
    # Lists to store indices of points falling into each zone
    indicesSZ_A, indicesSZ_B = [], [] 
    indicesHZ_C, indicesHZ_D, indicesHZ_E = [], [], []

    # Iterate through each data point to determine its zone
    for i in range(len(ref_values)):
        r, p = ref_values[i], pred_values[i] # Current reference and prediction values

        # Zone A: Clinically accurate
        # Points are in Zone A if they are within 20% of the reference value,
        # or if both reference and prediction are <= 70 mg/dL (hypoglycemic range).
        if (r <= 70 and p <= 70) or (p <= 1.2 * r and p >= 0.8 * r):
            zone[0] += 1
            indicesSZ_A.append(i)
        
        # Zone E: Erroneous treatment
        # Points are in Zone E if one value is in the hyperglycemic range (>= 180)
        # and the other is in the hypoglycemic range (<= 70), indicating a dangerous misclassification.
        elif (r >= 180 and p <= 70) or (r <= 70 and p >= 180):
            zone[4] += 1
            indicesHZ_E.append(i)

        # Zone C: Overcorrection
        # These conditions define regions where the prediction would lead to overcorrection.
        # (r >= 70 and r <= 290 and p >= r + 110): Prediction is significantly higher than reference.
        # (r >= 130 and r <= 180 and p <= (7/5)*r - 182): Prediction is significantly lower in a specific range.
        elif ((r >= 70 and r <= 290) and p >= r + 110) or \
             ((r >= 130 and r <= 180) and (p <= (7/5)*r - 182)): # This is equivalent to p <= 1.4*r - 182
            zone[2] += 1
            indicesHZ_C.append(i)
            
        # Zone D: Failure to detect
        # These conditions define regions where clinically significant deviations are missed.
        # (r >= 240 and (p >= 70 and p <= 180)): High reference, but prediction is in acceptable/low range.
        # (r <= 175/3 and p >= 70 and p <= 180): Low reference, prediction in acceptable range. (175/3 is approx 58.33)
        # ((r > 175/3 and r < 70) and p >= (6/5)*r): Reference is low-ish, prediction is higher but still potentially missing hypoglycemia.
        elif (r >= 240 and (p >= 70 and p <= 180)) or \
             (r <= 175/3 and p <= 180 and p >= 70) or \
             ((r > 175/3 and r < 70) and p >= (6/5)*r): # This is p >= 1.2*r
            zone[3] += 1
            indicesHZ_D.append(i)
            
        # Zone B: Clinically acceptable (all other points)
        # If a point doesn't fall into A, C, D, or E, it's classified as Zone B.
        else:
            zone[1] += 1
            indicesSZ_B.append(i)

    zone_indices = [indicesSZ_A, indicesSZ_B, indicesHZ_C, indicesHZ_D, indicesHZ_E]

    return ax, zone, zone_indices


import pandas as pd
import string
import matplotlib.pyplot as plt

# Generate a list of column names if there are more than 26 columns
column_names = list(string.ascii_uppercase) + ["A" + letter for letter in string.ascii_uppercase[:26]]
print(column_names)

# Load the CSV with the appropriate number of column names
avgBalance = pd.read_csv("Experiment_Result_CSVs/Experiment_1/FIVE_INSDR/bse_d000_i05_0001_avg_balance.csv", header=None, \
                         names=column_names[:52],  # Adjust the number based on the actual count
                         index_col=False)

# Update column names mapping
newNames = {"H":"GVWY", "L":"INSDR", "P":"PRSK", "T":"SHVR", "X":"ZIC", "AB":"ZIP"}
avgBalance.rename(columns=newNames, inplace=True)

# Plotting
avgBalance.plot(x="B",y=["GVWY","INSDR","PRSK","SHVR","ZIC","ZIP"], kind="line")
avgBalance.plot(x="B", y=["C","D"], kind="line")
plt.show(block=True)


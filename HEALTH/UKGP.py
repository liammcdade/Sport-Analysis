import pandas as pd

# Replace 'appointments.csv' with your actual CSV filename
df = pd.read_csv(r'C:\Users\liam\Pictures\apple its glowtime\iPhone 16\Practice_Level_Crosstab_Apr_25\Practice_Level_Crosstab_Apr_25.csv')

# Filter out unknown APPT_STATUS values
df_filtered = df[df['APPT_STATUS'].isin(['Attended', 'DNA'])]

# Sum counts by status
total_attended = df_filtered[df_filtered['APPT_STATUS'] == 'Attended']['COUNT_OF_APPOINTMENTS'].sum()
total_did_not_attend = df_filtered[df_filtered['APPT_STATUS'] == 'DNA']['COUNT_OF_APPOINTMENTS'].sum()

# Calculate totals and percentages
total_known = total_attended + total_did_not_attend

percent_attended = (total_attended / total_known) * 100 if total_known > 0 else 0
percent_did_not_attend = (total_did_not_attend / total_known) * 100 if total_known > 0 else 0

print(f"Total appointments: {total_known:,}")
print(f"Percent attended: {percent_attended:.2f}& & {total_attended:,}")
print(f"Percent did not attend: {percent_did_not_attend:.2f}% & {total_did_not_attend:,}")

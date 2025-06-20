import numpy as np

# Constants
omega = 7.292115e-5  # Earth's angular velocity (rad/s)
latitude_deg = 40  # Approximate NFL stadium latitude
latitude = np.radians(latitude_deg)


def yards_to_meters(yards):
    return yards * 0.9144


def flight_time(distance_m):
    speed = 25  # m/s, rough average kick speed
    return distance_m / speed if distance_m > 0 else 0


def coriolis_displacement(v, t, lat):
    # d = omega * v * sin(lat) * t^2
    return omega * v * np.sin(lat) * t**2  # meters


kick_distances_yards = np.arange(1, 71)  # 1 to 70 yards

displacements_cm = []

for yards in kick_distances_yards:
    d_m = yards_to_meters(yards)
    t = flight_time(d_m)
    d_lat = coriolis_displacement(25, t, latitude)
    displacements_cm.append(d_lat * 100)  # cm

print("Kick Distance (yards) | Coriolis Deflection (cm)")
for yd, d_cm in zip(kick_distances_yards, displacements_cm):
    print(f"{yd:>20} | {d_cm:.4f}")

avg_deflection_cm = np.mean(displacements_cm)
print(f"\nAverage Coriolis deflection over 1-70 yard kicks: {avg_deflection_cm:.4f} cm")


percent_increases = []
for i in range(1, len(displacements_cm)):
    prev = displacements_cm[i - 1]
    curr = displacements_cm[i]
    if prev == 0:
        pct_inc = float("inf")  # Handle division by zero at 1 yard
    else:
        pct_inc = ((curr - prev) / prev) * 100
    percent_increases.append(pct_inc)

# Find biggest percentage increase (ignore infinity at start)
filtered_increases = [p for p in percent_increases if p != float("inf")]
max_increase = max(filtered_increases)
max_index = percent_increases.index(max_increase) + 2  # +2 to get yard number after 1

avg_increase = np.mean(filtered_increases)

print(
    f"\nBiggest percentage increase: {max_increase:.2f}% from yard {max_index-1} to {max_index}"
)
print(f"Average percentage increase per yard: {avg_increase:.2f}%")

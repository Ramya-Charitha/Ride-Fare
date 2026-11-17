# RideFare: Dynamic Surge Pricing Engine for Ride-Hailing
# A simple menu-driven console program (no classes, no libraries).


# ---------------------------------------------------------------
# HELPER FUNCTIONS (used for EVERY input in the program)
# ---------------------------------------------------------------

# Keeps asking until the user types something that is not blank.
# It also removes extra spaces from the start and end of the text.
def get_text(prompt):
    while True:
        text = input(prompt).strip()
        if text == "":
            print("  Please type something, it cannot be blank.")
        else:
            return text


# Keeps asking until the user types a valid number between
# min_value and max_value. Letters and symbols are rejected.
def get_number(prompt, min_value, max_value=1000000):
    while True:
        text = input(prompt).strip()
        try:
            number = float(text)
        except ValueError:
            print("  That is not a number. Please type digits only (example: 12.5).")
            continue
        # This check also rejects "nan" and "inf" because they fail comparisons.
        if not (min_value <= number <= max_value):
            print("  Please enter a number from", min_value, "to", max_value, ".")
            continue
        return number


# ---------------------------------------------------------------
# DATA (stored in memory using a list of dictionaries)
# ---------------------------------------------------------------

# Each record is one vehicle type with its three rates.
vehicles = [
    {"name": "Mini", "base_fare": 50, "per_km": 12, "per_min": 2},
    {"name": "Sedan", "base_fare": 80, "per_km": 15, "per_min": 3},
    {"name": "SUV", "base_fare": 120, "per_km": 20, "per_min": 4},
]

# Each record is one fare estimate that the user has made.
trip_history = []


# ---------------------------------------------------------------
# CALCULATION HELPERS
# ---------------------------------------------------------------

# Works out the surge multiplier from requests and drivers.
def get_surge(requests, drivers):
    # If there are no drivers at all, surge is the highest.
    if drivers == 0:
        return 2.5
    ratio = requests / drivers
    if ratio > 2.0:
        return 2.0
    elif ratio > 1.5:
        return 1.5
    elif ratio > 1.0:
        return 1.2
    else:
        return 1.0


# Returns True if the hour is between 11 PM (23) and 5 AM.
def is_night(hour):
    return hour >= 23 or hour < 5


# Looks for a vehicle by name, ignoring capital/small letters.
# Returns the vehicle dictionary, or None if it is not found.
def find_vehicle(name):
    for v in vehicles:
        if v["name"].lower() == name.lower():
            return v
    return None


# Asks the user for all trip details and returns them together.
def ask_trip_details():
    distance = get_number("Enter trip distance in km: ", 0)
    minutes = get_number("Enter expected time in minutes: ", 0)
    requests = int(get_number("Enter current ride requests (whole number): ", 0))
    drivers = int(get_number("Enter available drivers (whole number): ", 0))
    hour = int(get_number("Enter current hour in 24-hour format (0-23): ", 0, 23))
    return distance, minutes, requests, drivers, hour


# ---------------------------------------------------------------
# MENU FEATURES
# ---------------------------------------------------------------

# Feature 1: show all stored vehicle types and their rates.
def view_vehicles():
    # Stop early if there is no data to show.
    if len(vehicles) == 0:
        print("\nNo vehicle types stored yet. Please add one first.")
        return
    print("\n--- Vehicle Types and Rates ---")
    for v in vehicles:
        print(v["name"], "| Base: Rs", v["base_fare"],
              "| Per km: Rs", v["per_km"],
              "| Per min: Rs", v["per_min"])


# Adds a new vehicle type to the list.
def add_vehicle():
    print("\n--- Add a Vehicle Type ---")
    name = get_text("Enter vehicle name: ")
    # Do not allow two vehicles with the same name.
    if find_vehicle(name) is not None:
        print("That vehicle type already exists.")
        return
    base = get_number("Enter base fare (Rs): ", 0)
    per_km = get_number("Enter rate per km (Rs): ", 0)
    per_min = get_number("Enter rate per minute (Rs): ", 0)
    vehicles.append({"name": name, "base_fare": base,
                     "per_km": per_km, "per_min": per_min})
    print("Vehicle type added!")


# Features 2, 3, 4, 5: estimate one fare and show the breakdown.
def estimate_fare():
    # Stop early if there are no vehicles to calculate with.
    if len(vehicles) == 0:
        print("\nNo vehicle types stored yet. Please add one first.")
        return
    print("\n--- Estimate Ride Fare ---")
    view_vehicles()

    # Ask which vehicle, then find it (case-insensitive).
    name = get_text("Enter vehicle name: ")
    vehicle = find_vehicle(name)
    if vehicle is None:
        print("Sorry, that vehicle type was not found.")
        return

    distance, minutes, requests, drivers, hour = ask_trip_details()

    # Base fare = base + distance part + time part.
    base_cost = vehicle["base_fare"] + distance * vehicle["per_km"] + minutes * vehicle["per_min"]

    # Apply the surge multiplier.
    surge = get_surge(requests, drivers)
    surged_cost = base_cost * surge

    # Add 20% night charge if it is between 11 PM and 5 AM.
    night_charge = 0.0
    if is_night(hour):
        night_charge = surged_cost * 0.20

    total = surged_cost + night_charge

    # Save this estimate in the history list.
    trip_history.append({"vehicle": vehicle["name"], "distance": distance, "fare": total})

    # Show the fare breakdown.
    print("\n========== FARE BREAKDOWN ==========")
    print("Vehicle:", vehicle["name"])
    print("Distance:", distance, "km | Time:", minutes, "min")
    print("Base fare + distance + time: Rs", round(base_cost, 2))
    print("Surge multiplier:", surge, "x -> Rs", round(surged_cost, 2))
    if night_charge > 0:
        print("Night charge (20%): + Rs", round(night_charge, 2))
    else:
        print("Night charge: None")
    print("------------------------------------")
    print("FINAL FARE: Rs", round(total, 2))
    print("====================================")


# Feature 5 (part 2): compare all vehicle types for one trip.
def compare_vehicles():
    # Stop early if there are no vehicles to compare.
    if len(vehicles) == 0:
        print("\nNo vehicle types stored yet. Please add one first.")
        return
    print("\n--- Compare All Vehicles ---")
    distance, minutes, requests, drivers, hour = ask_trip_details()

    # Work out surge once because it is the same for every vehicle.
    surge = get_surge(requests, drivers)

    print("\nTrip:", distance, "km,", minutes, "min | Surge:", surge, "x")
    print("-" * 40)
    # Go through every vehicle and calculate its final fare.
    for v in vehicles:
        base_cost = v["base_fare"] + distance * v["per_km"] + minutes * v["per_min"]
        cost = base_cost * surge
        if is_night(hour):
            cost = cost * 1.20
        print(v["name"], ": Rs", round(cost, 2))
    print("-" * 40)


# Shows all fare estimates made so far.
def view_history():
    # Stop early if no estimates have been made.
    if len(trip_history) == 0:
        print("\nNo trips estimated yet.")
        return
    print("\n--- Trip History ---")
    number = 1
    for trip in trip_history:
        print(number, ".", trip["vehicle"], "|", trip["distance"], "km | Rs", round(trip["fare"], 2))
        number = number + 1


# ---------------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------------

# Shows the menu again and again until the user chooses Exit.
def main():
    while True:
        print("\n=== RideFare Surge Pricing Menu ===")
        print("1. View Vehicle Rates")
        print("2. Add a Vehicle Type")
        print("3. Estimate Fare")
        print("4. Compare All Vehicles")
        print("5. View Trip History")
        print("6. Exit")

        choice = int(get_number("Enter your choice (1-6): ", 1, 6))

        # Run the feature that matches the choice.
        if choice == 1:
            view_vehicles()
        elif choice == 2:
            add_vehicle()
        elif choice == 3:
            estimate_fare()
        elif choice == 4:
            compare_vehicles()
        elif choice == 5:
            view_history()
        else:
            print("Goodbye!")
            break


# Start the program.
main()

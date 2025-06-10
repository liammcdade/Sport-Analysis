import csv
import sys
from collections import defaultdict

def _read_csv_data(csv_file_path):
    cars_data = []
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            required_headers = ['Model', 'Price', 'Rate']
            if not all(header in reader.fieldnames for header in required_headers):
                print(f"Error: CSV file must contain the following headers: {', '.join(required_headers)}")
                return []

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Clean up price: remove $ and commas, strip whitespace
                    price_str = row['Price'].replace('$', '').replace(',', '').strip()
                    # Clean up rating: use 'Rate' column, fallback to 'Rating' if present
                    rating_str = row.get('Rate', row.get('Rating', '')).strip()
                    car = {
                        "Model": row['Model'],
                        "Price": int(price_str),
                        "Rating": float(rating_str)
                    }
                    cars_data.append(car)
                except ValueError as e:
                    print(f"Warning: Skipping row {row_num} due to data type conversion error: {e}. Row data: {row}")
                except KeyError as e:
                    print(f"Warning: Skipping row {row_num} due to missing expected column: {e}. Row data: {row}")
    except FileNotFoundError:
        print(f"Error: The CSV file '{csv_file_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the CSV file: {e}")
        sys.exit(1)
    
    if not cars_data:
        print("No valid car data found in the CSV file after processing.")
    
    return cars_data

def _perform_analysis(cars_data):
    analysis_results = {}

    if not cars_data:
        return analysis_results

    total_price = sum(car['Price'] for car in cars_data)
    analysis_results['average_price'] = total_price / len(cars_data)

    total_rating = sum(car['Rating'] for car in cars_data)
    analysis_results['average_rating'] = total_rating / len(cars_data)

    analysis_results['most_expensive'] = max(cars_data, key=lambda x: x['Price'])
    analysis_results['least_expensive'] = min(cars_data, key=lambda x: x['Price'])
    analysis_results['highest_rated'] = max(cars_data, key=lambda x: x['Rating'])
    analysis_results['lowest_rated'] = min(cars_data, key=lambda x: x['Rating'])

    analysis_results['sorted_by_price'] = sorted(cars_data, key=lambda x: x['Price'])
    analysis_results['sorted_by_rating'] = sorted(cars_data, key=lambda x: x['Rating'], reverse=True)

    # --- Average dollar price per rating ---
    # This is the total price divided by the total rating (not grouped)
    if total_rating > 0:
        analysis_results['average_price_per_rating'] = total_price / total_rating
    else:
        analysis_results['average_price_per_rating'] = None

    # --- Average price per rating point (grouped, as before) ---
    ratings_grouped_by_price = defaultdict(lambda: {'sum_price': 0, 'count': 0})
    for car in cars_data:
        rounded_rating = round(car['Rating'] * 10) / 10.0
        ratings_grouped_by_price[rounded_rating]['sum_price'] += car['Price']
        ratings_grouped_by_price[rounded_rating]['count'] += 1
    
    average_price_per_rating = {}
    for rating, data in sorted(ratings_grouped_by_price.items()):
        average_price_per_rating[rating] = data['sum_price'] / data['count']
    
    analysis_results['average_price_per_rating_point'] = average_price_per_rating

    return analysis_results

def _print_results(cars_data, analysis_results):
    print("--- Mercedes Car Analysis ---")

    print("\nAvailable Car Models (Model, Rate, Price):")
    for car in cars_data:
        print(f"  - {car['Model']}, Rate: {car['Rating']}/10, Price: ${car['Price']:,}")

    if not analysis_results:
        print("\nNo analysis results to display.")
        return

    print(f"\nAverage Price: ${analysis_results['average_price']:,.2f}")
    print(f"Average Rate: {analysis_results['average_rating']:.2f}/10")

    print(f"\nMost Expensive: {analysis_results['most_expensive']['Model']} (${analysis_results['most_expensive']['Price']:,})")
    print(f"Least Expensive: {analysis_results['least_expensive']['Model']} (${analysis_results['least_expensive']['Price']:,})")
    print(f"Highest Rated: {analysis_results['highest_rated']['Model']} ({analysis_results['highest_rated']['Rating']}/10)")
    print(f"Lowest Rated: {analysis_results['lowest_rated']['Model']} ({analysis_results['lowest_rated']['Rating']}/10)")



    print("\n--- Average Price per Rating Point (0.1 increments) ---")
    if analysis_results['average_price_per_rating_point']:
        for rating, avg_price in analysis_results['average_price_per_rating_point'].items():
            print(f"  - Rating {rating:.1f}/10: Average Price = ${avg_price:,.2f}")
    else:
        print("  No data to calculate average price per rating point.")

    print("\n--- Sorted Lists ---")

    print("\nSorted by Price (Ascending):")
    for car in analysis_results['sorted_by_price']:
        print(f"  - {car['Model']}, Price: ${car['Price']:,}")

    print("\nSorted by Rate (Descending):")
    for car in analysis_results['sorted_by_rating']:
        print(f"  - {car['Model']}, Rate: {car['Rating']}/10")

def analyze_mercedes_cars(csv_file_path='kaggle/car.csv'):
    cars_data = _read_csv_data(csv_file_path)
    if not cars_data:
        return

    analysis_results = _perform_analysis(cars_data)

    _print_results(cars_data, analysis_results)

    # Print the average dollar price per rating at the bottom
    if analysis_results.get('average_price_per_rating') is not None:
        print(f"\n[Summary] Average Dollar Price Per Rating (all cars): ${analysis_results['average_price_per_rating']:,.2f} per rating point")
    else:
        print("\n[Summary] Average Dollar Price Per Rating (all cars): N/A")

if __name__ == "__main__":
    analyze_mercedes_cars()

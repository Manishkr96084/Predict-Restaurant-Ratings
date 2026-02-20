from flask import Flask, render_template, request

app = Flask(__name__)


restaurant_types = [
    "Casual Dining",
    "Fine Dining",
    "Cafe",
    "Quick Bites",
    "Buffet",
    "Delivery"
]

cuisines_list = [
    "North Indian",
    "South Indian",
    "Chinese",
    "Italian",
    "Continental",
    "Biryani",
    "Fast Food",
    "Desserts"
]

locations_list = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Pune",
    "Bihar",
    "UP"
]

yes_no_options = ["Yes", "No"]

cost_ranges = [
    "0-500",
    "500-1000",
    "1000-2000",
    "2000+"
]

vote_ranges = [
    "0-50",
    "50-100",
    "100-200",
    "200+"
]


# Home Page
@app.route('/')
def home():
    return render_template("index.html")


# Predictor Page
@app.route('/predictor')
def predictor():
    return render_template(
        "predictor.html",
        restaurant_types=restaurant_types,
        cuisines_list=cuisines_list,
        locations_list=locations_list,
        yes_no_options=yes_no_options,
        cost_ranges=cost_ranges,
        vote_ranges=vote_ranges
    )
# About Page
@app.route('/about')
def about():
    return render_template("about.html")


# Prediction Route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        restaurant_type = request.form.get("restaurant_type")
        cuisines = request.form.get("cuisines")
        online_order = request.form.get("online_order")
        book_table = request.form.get("book_table")
        location = request.form.get("location")
        cost_range = request.form.get("cost")
        vote_range = request.form.get("votes")

        rating = 3.0

        # Restaurant Type Logic
        if restaurant_type == "Fine Dining":
            rating += 0.6
        elif restaurant_type == "Buffet":
            rating += 0.5
        elif restaurant_type == "Casual Dining":
            rating += 0.4
        elif restaurant_type == "Cafe":
            rating += 0.3
        elif restaurant_type == "Quick Bites":
            rating += 0.2
        else:
            rating += 0.1

        # Cuisine Logic
        if cuisines in ["North Indian", "Chinese", "Biryani"]:
            rating += 0.4
        else:
            rating += 0.2

        # Online Order
        if online_order == "Yes":
            rating += 0.3

        # Book Table
        if book_table == "Yes":
            rating += 0.3

        # Cost Logic
        if cost_range == "2000+":
            rating += 0.4
        elif cost_range == "1000-2000":
            rating += 0.2

        # Votes Logic
        if vote_range == "200+":
            rating += 0.7
        elif vote_range == "100-200":
            rating += 0.5
        elif vote_range == "50-100":
            rating += 0.3

        rating = min(max(rating, 1), 5)
        prediction = f"{round(rating, 1)} ⭐"

        return render_template(
            "predictor.html",
            prediction=prediction,
            restaurant_types=restaurant_types,
            cuisines_list=cuisines_list,
            locations_list=locations_list,
            yes_no_options=yes_no_options,
            cost_ranges=cost_ranges,
            vote_ranges=vote_ranges
        )

    except:
        return render_template(
            "predictor.html",
            prediction="Error in input values",
            restaurant_types=restaurant_types,
            cuisines_list=cuisines_list,
            locations_list=locations_list,
            yes_no_options=yes_no_options,
            cost_ranges=cost_ranges,
            vote_ranges=vote_ranges
        )


if __name__ == "__main__":
    app.run(debug=True)
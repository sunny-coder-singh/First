# test edit: verifying write access
from flask import Flask, request, jsonify, render_template
import pandas as pd

print("sunny")
app = Flask(__name__)

# Load dataset
df = pd.read_csv("Starbucks_Synthetic_Beverage_Dataset_3000.csv")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    question = request.json["message"].lower().strip()
    from datetime import datetime

    with open("user_queries.txt", "a") as file:
     file.write(f"{datetime.now()} : {question}\n")

    # Highest calories
    if "highest calories" in question:
        item = df.loc[df["Calories"].idxmax()]
        answer = f"{item['Beverage_Name']} has the highest calories ({item['Calories']})."

    # Highest caffeine
    elif "highest caffeine" in question:
        item = df.loc[df["Caffeine_mg"].idxmax()]
        answer = f"{item['Beverage_Name']} has the highest caffeine ({item['Caffeine_mg']} mg)."

    # Lowest calories
    elif "lowest calories" in question:
        item = df.loc[df["Calories"].idxmin()]
        answer = f"{item['Beverage_Name']} has the lowest calories ({item['Calories']})."

    # Search beverage by any field
    else:

        result = df[
            df.astype(str)
              .apply(lambda row: row.str.lower().str.contains(question, na=False).any(), axis=1)
        ]

        if not result.empty:

            item = result.iloc[0]

            answer = f"""
Beverage : {item['Beverage_Name']}
Category : {item['Category']}
Size : {item['Size']}
Hot/Cold : {item['Hot_Cold']}
Calories : {item['Calories']}
Caffeine : {item['Caffeine_mg']} mg
Sugar : {item['Sugar_g']} g
Protein : {item['Protein_g']} g
Fat : {item['Fat_g']} g
Price : ₹{item['Price_INR']}
Rating : {item['Customer_Rating']}
Flavor : {item['Flavor_Profile']}
"""

        else:
            answer = "Sorry, I couldn't find that beverage."

    return jsonify({"response": answer})


if __name__ == "__main__":
    app.run(debug=True)

print("sunny")

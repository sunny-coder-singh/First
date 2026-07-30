
from flask import Flask, request, jsonify, render_template
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# -------------------------
# LOAD DATASET
# -------------------------

df = pd.read_csv("Starbucks_Synthetic_Beverage_Dataset_3000.csv")


# -------------------------
# GROQ API INITIALIZATION
# -------------------------

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found in the .env file."
    )

client = Groq(api_key=api_key)


# -------------------------
# RETRIEVE RELEVANT DATA
# -------------------------

def retrieve_data(question):

    question_words = question.lower().split()

    # Search every column for matching words
    mask = df.astype(str).apply(
        lambda row: any(
            word in " ".join(row.astype(str)).lower()
            for word in question_words
        ),
        axis=1
    )

    result = df[mask]

    # If nothing relevant is found,
    # send a small sample to the model.
    if result.empty:
        return df.head(20)

    return result.head(20)


# -------------------------
# AI FUNCTION
# -------------------------

def ask_llm(question):

    relevant_data = retrieve_data(question)

    prompt = f"""
You are a Starbucks Beverage Assistant.

Answer ONLY using the dataset provided below.

Dataset:
{relevant_data.to_string(index=False)}

Question:
{question}

Rules:

1. Answer ONLY from the dataset.
2. Do NOT make up information.
3. If the answer is not present, say:
   "I couldn't find that information in the dataset."
4. Keep answers short and accurate.
5. If the user asks for recommendations,
   use the available beverages from the dataset only.
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": "You are a helpful Starbucks Beverage Assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3

    )

    return response.choices[0].message.content


# -------------------------
# HOME PAGE
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# CHAT ROUTE
# -------------------------

@app.route("/chat", methods=["POST"])
def chat():

    question = request.json["message"].lower().strip()


    # Highest Calories
    if "highest calories" in question:

        item = df.loc[df["Calories"].idxmax()]

        answer = (
            f"{item['Beverage_Name']} has the highest "
            f"calories ({item['Calories']})."
        )


    # Highest Caffeine
    elif "highest caffeine" in question:

        item = df.loc[df["Caffeine_mg"].idxmax()]

        answer = (
            f"{item['Beverage_Name']} has the highest "
            f"caffeine ({item['Caffeine_mg']} mg)."
        )


    # Lowest Calories
    elif "lowest calories" in question:

        item = df.loc[df["Calories"].idxmin()]

        answer = (
            f"{item['Beverage_Name']} has the lowest "
            f"calories ({item['Calories']})."
        )


    # Everything else goes to the AI model
    else:

        answer = ask_llm(question)


    return jsonify({"response": answer})


# -------------------------
# RUN APP
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)

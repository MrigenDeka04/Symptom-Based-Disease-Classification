import tkinter as tk
from tkinter import ttk
import random
import pandas as pd
import joblib
import numpy as np
import google.generativeai as genai
import os
# from google.colab import userdata
from sklearn.preprocessing import LabelEncoder

# --- Configuration ---
DATA_PATH = "E:\Project\Dataset\Disease symptom Dataset\cleaned_diseases_and_symptoms.csv"  # Update path if needed
MODEL_PATH = "E:\Project\Dataset\Disease symptom Dataset\Models\best_disease_model.joblib"    # Update path if needed
# Ensure you have a GOOGLE_API_KEY set up in your environment variables
# or replace userdata.get('GOOGLE_API_KEY') with your actual API key (not recommended for security)

# --- Load Resources (Model, Label Encoder, Symptom Names) ---
model = None
label_encoder = None
symptom_names = []

try:
    model = joblib.load(MODEL_PATH)
    df_full = pd.read_csv(DATA_PATH)
    df_full.fillna(0, inplace=True)
    label_encoder = LabelEncoder()
    label_encoder.fit(df_full['diseases'])
    symptom_names = df_full.drop('diseases', axis=1).columns.tolist()
    print("Model, label encoder, and symptom names loaded successfully.")
except FileNotFoundError:
    print(f"Error: File not found. Ensure '{DATA_PATH}' and '{MODEL_PATH}' exist in the same directory or provide correct paths.")
except Exception as e:
    print(f"An unexpected error occurred while loading resources: {e}")

# --- Configure Gemini API ---
try:
    # In a local script, you might load the API key from a .env file or similar
    # For demonstration, we'll try to get it from environment variable
    # Replace with your actual API key if not using environment variables (not recommended)
    api_key = os.environ.get('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key="AIzaSyBf2WG3IghlBmHu_lDmnVGTitWKoH3UYfY")
        print("Gemini API configured.")
    else:
        print("Warning: GOOGLE_API_KEY environment variable not set. Gemini API features will not work.")

except Exception as e:
    print(f"Error configuring Gemini API: {e}")

# --- Gemini API Interaction Function ---
def get_precautions_from_gemini(disease_name: str) -> str:
    """
    Searches for precautions for a given disease using the Gemini API.

    Args:
        disease_name: The name of the disease to search precautions for.

    Returns:
        A string containing the precautions, or an error message if not found.
    """
    try:
        # Check if Gemini API is configured
        if not genai.get_client().api_key:
            return "Gemini API not configured. Cannot fetch precautions."

        model_gemini = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"What are the precautions for {disease_name}?"
        response = model_gemini.generate_content(prompt)

        if response and response.text:
            return response.text
        else:
            return f"Could not find precautions for {disease_name}."

    except Exception as e:
        return f"An error occurred while fetching precautions: {e}"

# --- Prediction Function ---
def predict_disease_with_precautions(symptoms, model, label_encoder, symptom_names):
    """
    Predicts the disease based on symptoms using the saved model and gets precautions from Gemini API.

    Args:
        symptoms: A list or array of symptoms (binary: 1 if symptom is present, 0 otherwise).
        model: The trained machine learning model.
        label_encoder: The LabelEncoder fitted on the disease names.
        symptom_names: A list of symptom names in the correct order.


    Returns:
        A tuple containing the predicted disease name, a dictionary of confidence percentages for all diseases,
        and the precautions from the Gemini API.
    """
    if model is None or label_encoder is None or not symptom_names:
        return "Error: Model, label encoder, or symptom names not loaded.", None, "Error: Cannot fetch precautions."

    if len(symptoms) != len(symptom_names):
         return f"Error: Input symptoms length ({len(symptoms)}) does not match expected number of features ({len(symptom_names)}).", None, "Error: Cannot fetch precautions."

    symptoms_reshaped = np.array(symptoms).reshape(1, -1)

    if model is None:
         return "Error: Model not loaded.", None, "Error: Cannot fetch precautions."

    predicted_encoded_label = model.predict(symptoms_reshaped)[0]

    confidence_percentages = {}
    try:
        if hasattr(model, 'predict_proba'):
            confidence_scores = model.predict_proba(symptoms_reshaped)[0]
            for i, score in enumerate(confidence_scores):
                 disease_name = label_encoder.inverse_transform([i])[0]
                 confidence_percentages[disease_name] = score * 100
        else:
            predicted_disease = label_encoder.inverse_transform([predicted_encoded_label])[0]
            confidence_percentages[predicted_disease] = 100.0

    except Exception as e:
        print(f"Could not get confidence scores: {e}")
        confidence_percentages = {"Error fetching confidence": None}

    predicted_disease = label_encoder.inverse_transform([predicted_encoded_label])[0]

    precautions = get_precautions_from_gemini(predicted_disease)

    return predicted_disease, confidence_percentages, precautions

# --- Function to collect symptoms from checkboxes and trigger prediction ---
def predict_disease_from_checkboxes(symptom_vars, symptom_names, model, label_encoder,
                                     predicted_disease_label, confidence_label, precautions_text, health_tips_label):
    """
    Collects selected symptoms from Tkinter variables, predicts disease, and updates GUI.

    Args:
        symptom_vars: A list of tk.IntVar objects associated with symptom checkboxes.
        symptom_names: A list of symptom names corresponding to symptom_vars order.
        model: The trained machine learning model.
        label_encoder: The LabelEncoder fitted on the disease names.
        predicted_disease_label: Tkinter Label to display predicted disease.
        confidence_label: Tkinter Label to display confidence level.
        precautions_text: Tkinter Text widget to display precautions.
        health_tips_label: Tkinter Label to display health tips.
    """
    predicted_disease, confidence_scores_dict, precautions = predict_disease_with_precautions(
        [var.get() for var in symptom_vars], symptom_names, model, label_encoder
    )

    predicted_disease_label.config(text=f"Predicted Disease: {predicted_disease}")

    if confidence_scores_dict and predicted_disease in confidence_scores_dict:
        predicted_confidence = confidence_scores_dict[predicted_disease]
        confidence_label.config(text=f"Confidence Level: {predicted_confidence:.2f}%")
    else:
        confidence_label.config(text="Confidence Level: N/A")

    precautions_text.delete(1.0, tk.END)
    precautions_text.insert(tk.END, precautions)

    # Placeholder for health awareness tips (can be expanded)
    health_tips = "General Health Tip: Remember to stay hydrated and get enough sleep!"
    health_tips_label.config(text=health_tips)


# --- Tkinter GUI Setup ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("Disease Prediction GUI")

        # --- Frames ---
        greeting_frame = tk.Frame(root)
        quote_frame = tk.Frame(root)
        symptoms_frame = tk.Frame(root)
        results_frame = tk.Frame(root)
        disclaimer_frame = tk.Frame(root)

        greeting_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        quote_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        symptoms_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        results_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        disclaimer_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)

        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=0)
        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=1)
        root.grid_rowconfigure(4, weight=0)

        # --- Greetings and Quote ---
        health_quotes = [
            "The greatest wealth is health.",
            "Take care of your body. It's the only place you have to live.",
            "A healthy outside starts from the inside.",
            "Your body hears everything your mind says.",
            "To keep the body in good health is a duty...",
            "Health is not valued till sickness comes.",
            "The first wealth is health.",
            "It is health that is real wealth and not pieces of gold or silver.",
            "The groundwork for all happiness is good health.",
            "Physical fitness is not only one of the most important keys to a healthy body, it is the basis of dynamic and creative intellectual activity.",
            "The only way to keep your health is to eat what you don't want, drink what you don't like, and do what you'd rather not.",
            "Walking is the best possible exercise. Habituate yourself to walk very far.",
            "An apple a day keeps the doctor away.",
            "Healthy habits are your building blocks to a healthy life.",
            "Health is a state of complete harmony of the body, mind and spirit.",
            "Eat, sleep, and swim. That's a pretty good day.",
            "The best doctor gives the least medicines.",
            "A vigorous five-mile walk will do more good for an unhappy but otherwise healthy man than all the medicine and psychology in the world.",
            "The human body is the best picture of the human soul.",
            "To enjoy the glow of good health, you must exercise.",
            "Early to bed and early to rise makes a man healthy, wealthy, and wise.",
            "Healthy citizens are the greatest asset any country can have.",
            "Healing is a matter of time, but it is sometimes also a matter of opportunity.",
            "It's not the loads that break you down, it's the way you carry them.",
            "The art of medicine consists of amusing the patient while nature cures the disease.",
            "Our bodies are our gardens – our wills are our gardeners.",
            "Take care of your body with steadfast fidelity. The soul must see through these eyes alone, and if they are dim, the whole world is dim.",
            "Be careful about reading health books. You may die of a misprint.",
            "A wise man should consider that health is the greatest of human blessings.",
            "The doctor of the future will give no medicine, but will interest his patients in the care of the human frame, in diet, and in the cause and prevention of disease."
        ]

        greeting_label = tk.Label(greeting_frame, text="Hello! Welcome to the Disease Prediction GUI.", font=("Arial", 14))
        greeting_label.pack(pady=10)

        quote_heading_label = tk.Label(quote_frame, text="Quote of the Day:", font=("Arial", 12, "bold"))
        quote_heading_label.pack(pady=5)

        random_quote = random.choice(health_quotes)
        quote_label = tk.Label(quote_frame, text=random_quote, font=("Arial", 10), wraplength=400)
        quote_label.pack(pady=5)

        # --- Symptom Selection Checkboxes (Horizontal) ---
        symptoms_label = tk.Label(symptoms_frame, text="Select your symptoms:", font=("Arial", 12, "bold"))
        symptoms_label.pack(pady=5)

        checkbox_frame = tk.Frame(symptoms_frame)
        checkbox_frame.pack(expand=True, fill="both")

        canvas = tk.Canvas(checkbox_frame)
        scrollbar = ttk.Scrollbar(checkbox_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")

        symptom_vars = []
        if symptom_names:
            for symptom in symptom_names:
                var = tk.IntVar()
                symptom_vars.append(var)
                chk = ttk.Checkbutton(scrollable_frame, text=symptom, variable=var)
                chk.pack(side=tk.LEFT, padx=5, pady=2)
        else:
            no_symptoms_label = tk.Label(scrollable_frame, text="Symptom names not loaded. Please check data file.")
            no_symptoms_label.pack()


        # --- Predict Button ---
        predict_button = tk.Button(symptoms_frame, text="Predict Disease", command=lambda: predict_disease_from_checkboxes(
            symptom_vars, symptom_names, model, label_encoder,
            predicted_disease_label, confidence_label, precautions_text, health_tips_label
        ))
        predict_button.pack(pady=10)

        # --- Display Results Section ---
        results_heading_label = tk.Label(results_frame, text="Prediction Results:", font=("Arial", 12, "bold"))
        results_heading_label.pack(pady=5)

        predicted_disease_label = tk.Label(results_frame, text="Predicted Disease: ", font=("Arial", 10), wraplength=500, justify="left")
        predicted_disease_label.pack(pady=2, anchor="w")

        confidence_label = tk.Label(results_frame, text="Confidence Level: ", font=("Arial", 10), justify="left")
        confidence_label.pack(pady=2, anchor="w")

        precautions_heading_label = tk.Label(results_frame, text="Precautions:", font=("Arial", 10, "bold"), justify="left")
        precautions_heading_label.pack(pady=5, anchor="w")

        precautions_text = tk.Text(results_frame, font=("Arial", 10), wrap="word", height=10, width=60)
        precautions_text.pack(pady=2, anchor="w")

        health_tips_heading_label = tk.Label(disclaimer_frame, text="Health Awareness Tip:", font=("Arial", 10, "bold"), justify="left")
        health_tips_heading_label.pack(pady=5, anchor="w")

        health_tips_label = tk.Label(disclaimer_frame, text="Loading health tip...", font=("Arial", 10), wraplength=500, justify="left")
        health_tips_label.pack(pady=2, anchor="w")

        # --- Disclaimer Section ---
        disclaimer_heading_label = tk.Label(disclaimer_frame, text="Disclaimer:", font=("Arial", 10, "bold"), justify="left")
        disclaimer_heading_label.pack(pady=5, anchor="w")

        disclaimer_text_label = tk.Label(disclaimer_frame, text="This prediction is for informational purposes only and should not be considered a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.",
                                         font=("Arial", 10, "italic"), fg="red", wraplength=600, justify="left")
        disclaimer_text_label.pack(pady=5, anchor="w")

        # --- Start GUI ---
        print("Tkinter GUI script generated. Copy and paste this code into a local Python file to run it.")
        root.mainloop() # Uncomment this line when running locally

    except tk.TclError as e:
        print(f"Tkinter Error: {e}. Cannot run GUI in this environment.")
    except Exception as e:
        print(f"An unexpected error occurred during GUI setup: {e}")
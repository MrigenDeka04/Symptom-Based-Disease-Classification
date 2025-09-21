import tkinter as tk
from tkinter import ttk
import random
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder

# --- Configuration ---
DATA_PATH = r"E:\Project\Dataset\Disease symptom Dataset\cleaned_diseases_and_symptoms.csv"  
MODEL_PATH = r"E:\Project\Dataset\Disease symptom Dataset\Models\best_disease_model.joblib"    

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

# --- Prediction Function ---
def predict_disease(symptoms, model, label_encoder, symptom_names):
    if model is None or label_encoder is None or not symptom_names:
        return "Error: Model, label encoder, or symptom names not loaded.", None

    if len(symptoms) != len(symptom_names):
        return f"Error: Input symptoms length ({len(symptoms)}) does not match expected number of features ({len(symptom_names)}).", None

    symptoms_reshaped = np.array(symptoms).reshape(1, -1)
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
    return predicted_disease, confidence_percentages

# --- Function to collect symptoms and trigger prediction ---
def predict_disease_from_checkboxes(symptom_vars, symptom_names, model, label_encoder,
                                     predicted_disease_label, confidence_label, health_tips_label,
                                     top5_label):
    predicted_disease, confidence_scores_dict = predict_disease(
        [var.get() for var in symptom_vars], model, label_encoder, symptom_names
    )

    predicted_disease_label.config(text=f"Predicted Disease: {predicted_disease}")

    if confidence_scores_dict and predicted_disease in confidence_scores_dict:
        predicted_confidence = confidence_scores_dict[predicted_disease]
        confidence_label.config(text=f"Confidence Level: {predicted_confidence:.2f}%")
    else:
        confidence_label.config(text="Confidence Level: N/A")

    # --- Show Top 5 Predicted Diseases ---
    if confidence_scores_dict:
        sorted_confidences = sorted(confidence_scores_dict.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_text = "Top 5 Predicted Diseases:\n"
        for disease, score in sorted_confidences:
            top5_text += f"- {disease}: {score:.2f}%\n"
        top5_label.config(text=top5_text)
    else:
        top5_label.config(text="Top 5 Predicted Diseases: N/A")

    # --- Show Random Health Tip ---
    health_tips_list = [
        "Drink at least 8 glasses of water daily.",
        "Get 7–8 hours of quality sleep each night.",
        "Eat more fruits and vegetables for better immunity.",
        "Exercise at least 30 minutes a day.",
        "Wash your hands regularly to prevent infections.",
        "Limit sugary foods and drinks to protect your health.",
        "Take short breaks from screens to rest your eyes.",
        "Manage stress with meditation or deep breathing.",
        "Avoid smoking and limit alcohol consumption.",
        "Go for regular health check-ups, even if you feel fine."
    ]
    health_tip = random.choice(health_tips_list)
    health_tips_label.config(text=f"Health Tip: {health_tip}")

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

        # --- Greetings and Quote ---
        health_quotes = [
            "The greatest wealth is health.",
            "Take care of your body. It's the only place you have to live.",
            "A healthy outside starts from the inside.",
            "Your body hears everything your mind says.",
            "Health is not valued till sickness comes."
        ]

        greeting_label = tk.Label(greeting_frame, text="Hello! Welcome to the Disease Prediction GUI.", font=("Arial", 14))
        greeting_label.pack(pady=10)

        quote_heading_label = tk.Label(quote_frame, text="Quote of the Day:", font=("Arial", 12, "bold"))
        quote_heading_label.pack(pady=5)

        random_quote = random.choice(health_quotes)
        quote_label = tk.Label(quote_frame, text=random_quote, font=("Arial", 10), wraplength=400)
        quote_label.pack(pady=5)

        # --- Symptom Selection Checkboxes ---
        symptoms_label = tk.Label(symptoms_frame, text="Select your symptoms:", font=("Arial", 12, "bold"))
        symptoms_label.pack(pady=5)

        checkbox_frame = tk.Frame(symptoms_frame)
        checkbox_frame.pack(expand=True, fill="both")

        canvas = tk.Canvas(checkbox_frame)
        scrollbar = ttk.Scrollbar(checkbox_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
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
            predicted_disease_label, confidence_label, health_tips_label, top5_label
        ))
        predict_button.pack(pady=10)

        # --- Display Results Section ---
        results_heading_label = tk.Label(results_frame, text="Prediction Results:", font=("Arial", 12, "bold"))
        results_heading_label.pack(pady=5)

        predicted_disease_label = tk.Label(results_frame, text="Predicted Disease: ", font=("Arial", 10), wraplength=500, justify="left")
        predicted_disease_label.pack(pady=2, anchor="w")

        confidence_label = tk.Label(results_frame, text="Confidence Level: ", font=("Arial", 10), justify="left")
        confidence_label.pack(pady=2, anchor="w")

        top5_label = tk.Label(results_frame, text="Top 5 Predicted Diseases: ", font=("Arial", 10), justify="left")
        top5_label.pack(pady=2, anchor="w")

        # --- Health Tips Section ---
        health_tips_heading_label = tk.Label(disclaimer_frame, text="Health Tips:", font=("Arial", 10, "bold"), justify="left")
        health_tips_heading_label.pack(pady=5, anchor="w")

        health_tips_label = tk.Label(disclaimer_frame, text="Loading health tip...", font=("Arial", 10), wraplength=500, justify="left")
        health_tips_label.pack(pady=2, anchor="w")

        # --- Disclaimer Section ---
        disclaimer_heading_label = tk.Label(disclaimer_frame, text="Disclaimer:", font=("Arial", 10, "bold"), justify="left")
        disclaimer_heading_label.pack(pady=5, anchor="w")

        disclaimer_text_label = tk.Label(disclaimer_frame, text="This prediction is for informational purposes only and should not be considered a substitute for professional medical advice.",
                                         font=("Arial", 10, "italic"), fg="red", wraplength=600, justify="left")
        disclaimer_text_label.pack(pady=5, anchor="w")

        # --- Start GUI ---
        root.mainloop()

    except tk.TclError as e:
        print(f"Tkinter Error: {e}. Cannot run GUI in this environment.")
    except Exception as e:
        print(f"An unexpected error occurred during GUI setup: {e}")

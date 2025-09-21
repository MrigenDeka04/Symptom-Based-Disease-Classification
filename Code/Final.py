import tkinter as tk
from tkinter import ttk, messagebox
import random

# ------------------------
# Sample Symptoms (Replace with your full list)
# ------------------------
symptoms_list = [
    "fever", "cough", "headache", "fatigue", "nausea",
    "vomiting", "chest pain", "shortness of breath", "dizziness",
    "sore throat", "abdominal pain", "loss of appetite",
    "joint pain", "rash", "sweating", "chills", "runny nose",
    "back pain", "arm pain", "hand or finger swelling",
    "wrist swelling", "arm stiffness or tightness"
]

# ------------------------
# Health Tips (30 total)
# ------------------------
health_tips = [
    "Exercise at least 30 minutes a day.",
    "Drink at least 8 glasses of water daily.",
    "Get 7-8 hours of quality sleep.",
    "Eat more fruits and vegetables.",
    "Limit processed and junk food.",
    "Take short breaks while working.",
    "Wash hands regularly with soap.",
    "Practice deep breathing or meditation.",
    "Avoid excessive sugar intake.",
    "Maintain good posture while sitting.",
    "Do stretching exercises daily.",
    "Spend time outdoors in sunlight.",
    "Keep a consistent sleep schedule.",
    "Avoid smoking and alcohol.",
    "Don’t skip breakfast.",
    "Include protein in every meal.",
    "Do regular health checkups.",
    "Stay socially connected.",
    "Limit screen time before bed.",
    "Eat slowly and mindfully.",
    "Practice gratitude daily.",
    "Take the stairs instead of the lift.",
    "Do strength training twice a week.",
    "Reduce salt in your diet.",
    "Have a hobby for relaxation.",
    "Avoid eating late at night.",
    "Stay hydrated during workouts.",
    "Use proper ergonomics at your desk.",
    "Do yoga or stretching in the morning.",
    "Laugh more and stay positive."
]

# ------------------------
# Main GUI Class
# ------------------------
class DiseasePredictionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Disease Prediction GUI")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f5f5")

        # Title
        title = tk.Label(root, text="Hello! Welcome to the Disease Prediction GUI.",
                         font=("Helvetica", 14, "bold"), bg="#f0f5f5", fg="#003366")
        title.pack(pady=10)

        # Quote
        quote_label = tk.Label(root, text="Quote of the Day:",
                               font=("Helvetica", 12, "bold"), bg="#f0f5f5")
        quote_label.pack()
        quote = tk.Label(root, text="The greatest wealth is health.",
                         font=("Helvetica", 11, "italic"), bg="#f0f5f5")
        quote.pack(pady=(0, 10))

        # Symptom selection frame with scrollbar
        symptom_frame = tk.LabelFrame(root, text="Select your symptoms:",
                                      font=("Helvetica", 12, "bold"), bg="#e6f2ff", padx=10, pady=10)
        symptom_frame.pack(fill="both", padx=20, pady=10, expand=True)

        canvas = tk.Canvas(symptom_frame, bg="#e6f2ff", highlightthickness=0)
        scrollbar = tk.Scrollbar(symptom_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#e6f2ff")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add symptom checkboxes
        self.symptom_vars = {}
        for i, symptom in enumerate(symptoms_list):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(scrollable_frame, text=symptom, variable=var,
                                 font=("Helvetica", 10), bg="#e6f2ff", anchor="w")
            chk.grid(row=i // 3, column=i % 3, sticky="w", padx=5, pady=3)
            self.symptom_vars[symptom] = var

        # Predict Button
        predict_btn = tk.Button(root, text="Predict Disease", command=self.predict_disease,
                                font=("Helvetica", 11, "bold"), bg="#3399ff", fg="white",
                                relief="raised", padx=10, pady=5)
        predict_btn.pack(pady=15)

        # Result Section
        self.result_frame = tk.LabelFrame(root, text="Prediction Results:",
                                          font=("Helvetica", 12, "bold"), bg="#f0f5f5", padx=10, pady=10)
        self.result_frame.pack(fill="both", padx=20, pady=10, expand=True)

        self.result_text = tk.Text(self.result_frame, height=12, wrap="word",
                                   font=("Helvetica", 10), bg="white", relief="sunken")
        self.result_text.pack(fill="both", expand=True)

        # Disclaimer Section
        disclaimer_frame = tk.LabelFrame(root, text="Disclaimer:",
                                         font=("Helvetica", 11, "bold"), bg="#f0f5f5", padx=10, pady=10)
        disclaimer_frame.pack(fill="x", padx=20, pady=5)

        disclaimer = tk.Label(disclaimer_frame,
                              text="This prediction system is for educational purposes only and "
                                   "should not be used as a substitute for professional medical advice.",
                              font=("Helvetica", 9), wraplength=750, justify="left", bg="#f0f5f5", fg="red")
        disclaimer.pack()

    # ------------------------
    # Dummy Disease Prediction Function
    # ------------------------
    def predict_disease(self):
        selected_symptoms = [symptom for symptom, var in self.symptom_vars.items() if var.get()]

        if not selected_symptoms:
            messagebox.showwarning("No Symptoms", "Please select at least one symptom.")
            return

        # Dummy logic: just show selected symptoms as a fake prediction
        disease = "fracture of the hand"
        confidence = random.uniform(80, 99)

        # Fake Top 5 predictions
        top5 = [
            (disease, confidence),
            ("fracture of the arm", random.uniform(1, 5)),
            ("injury to the arm", random.uniform(0.5, 2)),
            ("rotator cuff injury", random.uniform(0.1, 0.5)),
            ("carpal tunnel syndrome", random.uniform(0.01, 0.1))
        ]

        # Randomly pick 3 health tips
        tips = random.sample(health_tips, 3)

        # Show results
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Predicted Disease: {disease}\n")
        self.result_text.insert(tk.END, f"Confidence Level: {confidence:.2f}%\n\n")

        self.result_text.insert(tk.END, "Top 5 Predicted Diseases:\n")
        for d, c in top5:
            self.result_text.insert(tk.END, f"- {d}: {c:.2f}%\n")

        self.result_text.insert(tk.END, "\nHealth Tips:\n")
        for tip in tips:
            self.result_text.insert(tk.END, f"- {tip}\n")


# ------------------------
# Run the App
# ------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DiseasePredictionGUI(root)
    root.mainloop()

import tkinter as tk
import random
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os

# --- Configuration ---
DATA_PATH = r"E:\Project\Dataset\Disease symptom Dataset\cleaned_diseases_and_symptoms.csv"
MODEL_PATH = r"E:\Project\Dataset\Disease symptom Dataset\Models\best_disease_model.joblib"

# Toggle search behavior
# True = hide non-matching symptoms when typing; False = only highlight matches
FILTER_MODE = True

# --- Load Resources ---
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
except Exception as e:
    print(f"Error loading resources: {e}")

# --- Disease-specific Health Tips ---
disease_health_tips = {
    "Diabetes": ["Monitor your blood sugar regularly.", "Avoid high sugar foods.", "Exercise daily."],
    "Hypertension": ["Reduce salt intake.", "Manage stress with meditation.", "Check BP regularly."],
    "Flu": ["Drink warm fluids.", "Rest well.", "Wash hands frequently."],
    "Asthma": ["Avoid smoke/pollution.", "Carry inhaler.", "Do breathing exercises."],
    "default": ["Maintain a balanced diet.", "Get enough sleep.", "Drink 8 glasses of water."]
}

# --- Prediction Logic ---
def predict_disease(symptoms, model, label_encoder, symptom_names):
    if model is None:
        return "Error: Model not loaded.", None
    symptoms_reshaped = np.array(symptoms).reshape(1, -1)
    predicted_encoded_label = model.predict(symptoms_reshaped)[0]

    confidence_percentages = {}
    if hasattr(model, 'predict_proba'):
        confidence_scores = model.predict_proba(symptoms_reshaped)[0]
        for i, score in enumerate(confidence_scores):
            disease_name = label_encoder.inverse_transform([i])[0]
            confidence_percentages[disease_name] = float(score) * 100.0

    predicted_disease = label_encoder.inverse_transform([predicted_encoded_label])[0]
    return predicted_disease, confidence_percentages

# --- GUI Colors ---
BG_COLOR = "#1e1e1e"
FG_COLOR = "#ffffff"
BTN_COLOR = "#2e8b57"
BTN_CLEAR_COLOR = "#b22222"

# --- GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("🧑‍⚕️ Disease Prediction GUI")
    root.geometry("1100x750")
    root.configure(bg=BG_COLOR)

    # Header
    greeting_label = tk.Label(root, text="Hello! Welcome to the Disease Prediction GUI.",
                              font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg="#00ffff")
    greeting_label.pack(pady=10)

    quote_label = tk.Label(root, text=random.choice([
        "The greatest wealth is health.",
        "Take care of your body. It's the only place you have to live.",
        "A healthy outside starts from the inside."
    ]), font=("Helvetica", 12), bg=BG_COLOR, fg="#aaaaaa")
    quote_label.pack(pady=5)

    # Symptoms Section with Search + Scroll
    symptoms_frame = tk.LabelFrame(root, text="Select your Symptoms", font=("Helvetica", 12, "bold"),
                                   bg=BG_COLOR, fg="#00bfff", labelanchor="n")
    symptoms_frame.pack(fill="both", expand=True, padx=15, pady=10)

    # Search bar
    search_var = tk.StringVar()
    search_row = tk.Frame(symptoms_frame, bg=BG_COLOR)
    search_row.pack(fill="x", padx=8, pady=(8, 4))
    tk.Label(search_row, text="Search symptom:", bg=BG_COLOR, fg="#bbbbbb",
             font=("Helvetica", 10)).pack(side="left", padx=(2, 8))
    search_entry = tk.Entry(search_row, textvariable=search_var, bg="#2b2b2b", fg="#ffffff",
                            insertbackground="#ffffff", relief="flat", font=("Helvetica", 10))
    search_entry.pack(side="left", fill="x", expand=True)

    # Scrollable area
    container = tk.Frame(symptoms_frame, bg=BG_COLOR)
    container.pack(fill="both", expand=True, padx=8, pady=8)

    canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
    vscroll = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vscroll.set)

    grid_holder = tk.Frame(canvas, bg=BG_COLOR)
    grid_window = canvas.create_window((0, 0), window=grid_holder, anchor="nw")

    canvas.pack(side="left", fill="both", expand=True)
    vscroll.pack(side="right", fill="y")

    def _on_frame_configure(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event):
        # Make inner frame width follow the canvas width
        canvas.itemconfigure(grid_window, width=event.width)

    grid_holder.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_canvas_configure)

    # Cross‑platform mouse wheel bindings
    def _bind_mousewheel(widget):
        widget.bind_all("<MouseWheel>", _on_mousewheel_windows)   # Windows/macOS
        widget.bind_all("<Button-4>", _on_mousewheel_linux_up)    # Linux (X11)
        widget.bind_all("<Button-5>", _on_mousewheel_linux_down)  # Linux (X11)

    def _unbind_mousewheel(widget):
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")

    def _on_enter(_):
        _bind_mousewheel(canvas)

    def _on_leave(_):
        _unbind_mousewheel(canvas)

    def _on_mousewheel_windows(event):
        delta = int(-1 * (event.delta / 120))
        canvas.yview_scroll(delta, "units")

    def _on_mousewheel_linux_up(event):
        canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(event):
        canvas.yview_scroll(1, "units")

    container.bind("<Enter>", _on_enter)
    container.bind("<Leave>", _on_leave)

    # Checkboxes Grid
    symptom_vars = []
    check_widgets = []  # (name_lower, chk_widget, var)
    if symptom_names:
        columns = 5
        for c in range(columns):
            grid_holder.grid_columnconfigure(c, weight=1, uniform="symcols")
        for idx, symptom in enumerate(symptom_names):
            var = tk.IntVar()
            symptom_vars.append(var)
            chk = tk.Checkbutton(grid_holder, text=symptom, variable=var,
                                 bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR,
                                 activebackground=BG_COLOR, activeforeground="#00ff00",
                                 font=("Helvetica", 10), anchor="w")
            r, c = divmod(idx, columns)
            chk.grid(row=r, column=c, sticky="w", padx=10, pady=6)
            check_widgets.append((symptom.lower(), chk, var))

    # Live search: highlight + (optional) filter
    def on_search_change(*_):
        q = search_var.get().casefold().strip()
        any_changed = False
        for name, chk, var in check_widgets:
            is_match = q != "" and q in name
            if FILTER_MODE:
                if q and not is_match:
                    if chk.winfo_ismapped():
                        chk.grid_remove()
                        any_changed = True
                else:
                    if not chk.winfo_ismapped():
                        chk.grid()
                        any_changed = True
                if is_match:
                    var.set(1)
                chk.configure(fg="#00ff88" if is_match else FG_COLOR)
            else:
                chk.configure(fg="#00ff88" if is_match else FG_COLOR)
                if is_match:
                    var.set(1)
        if any_changed:
            grid_holder.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

    search_var.trace_add("write", on_search_change)

    # Buttons and actions
    button_frame = tk.Frame(root, bg=BG_COLOR)
    button_frame.pack(pady=10)

    def predict_disease_from_checkboxes():
        predicted_disease, confidence_scores_dict = predict_disease(
            [var.get() for var in symptom_vars], model, label_encoder, symptom_names
        )

        predicted_disease_label.config(text=f"🩺 Predicted Disease: {predicted_disease}")

        if confidence_scores_dict and predicted_disease in confidence_scores_dict:
            predicted_confidence = confidence_scores_dict[predicted_disease]
            confidence_label.config(text=f"📊 Confidence Level: {predicted_confidence:.2f}%")
        else:
            confidence_label.config(text="📊 Confidence Level: N/A")

        if confidence_scores_dict:
            sorted_confidences = sorted(confidence_scores_dict.items(), key=lambda x: x[1], reverse=True)[:5]
            name_w = max((len(d) for d, _ in sorted_confidences), default=10)
            lines = ["🏆 Top 5 Predicted Diseases:"]
            for disease, score in sorted_confidences:
                lines.append(f"{disease:<{name_w}}  :  {score:6.2f}%")
            top5_label.configure(font=("Courier New", 11))
            top5_label.config(text="\n".join(lines))
        else:
            top5_label.configure(font=("Helvetica", 11))
            top5_label.config(text="Top 5 Predicted Diseases: (no probabilities available)")

        # ALWAYS refresh health tips for the current disease
        tips = disease_health_tips.get(predicted_disease, disease_health_tips["default"])
        health_tips_label.config(text="💡 Health Tips:\n- " + "\n- ".join(tips))

    def clear_symptoms():
        for name, chk, var in check_widgets:
            var.set(0)
            chk.configure(fg=FG_COLOR)
            if FILTER_MODE and not chk.winfo_ismapped():
                chk.grid()  # show all again
        search_var.set("")
        grid_holder.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    predict_button = tk.Button(button_frame, text="🔍 Predict Disease",
                               bg=BTN_COLOR, fg="white", font=("Helvetica", 11, "bold"),
                               relief="groove", bd=2, padx=15, pady=5,
                               command=predict_disease_from_checkboxes)
    predict_button.grid(row=0, column=0, padx=10)

    clear_button = tk.Button(button_frame, text="🧹 Clear Selection",
                             bg=BTN_CLEAR_COLOR, fg="white", font=("Helvetica", 11, "bold"),
                             relief="groove", bd=2, padx=15, pady=5,
                             command=clear_symptoms)
    clear_button.grid(row=0, column=1, padx=10)

    # Results Section
    results_frame = tk.LabelFrame(root, text="Prediction Results", font=("Helvetica", 12, "bold"),
                                  bg=BG_COLOR, fg="#00ffff", labelanchor="n")
    results_frame.pack(fill="x", padx=15, pady=10)

    predicted_disease_label = tk.Label(results_frame, text="Predicted Disease: ",
                                       bg=BG_COLOR, fg="#00ff7f", font=("Helvetica", 11))
    predicted_disease_label.pack(anchor="w", pady=5)

    confidence_label = tk.Label(results_frame, text="Confidence Level: ",
                                bg=BG_COLOR, fg="#1e90ff", font=("Helvetica", 11))
    confidence_label.pack(anchor="w", pady=5)

    top5_label = tk.Label(results_frame, text="Top 5 Predicted Diseases: ",
                          bg=BG_COLOR, fg="#ffcc00", font=("Helvetica", 11), justify="left")
    top5_label.pack(anchor="w", pady=5)

    health_tips_label = tk.Label(results_frame, text="Health Tips will appear here after prediction.",
                                 bg=BG_COLOR, fg="#ffa500", font=("Helvetica", 11),
                                 wraplength=1000, justify="left")
    health_tips_label.pack(anchor="w", pady=5)

    # Disclaimer
    disclaimer_frame = tk.Frame(root, bg="#111")
    disclaimer_frame.pack(side="bottom", fill="x")
    disclaimer_label = tk.Label(disclaimer_frame,
        text="⚠️ This prediction is for informational purposes only and should not replace professional medical advice.",
        bg="#111", fg="red", font=("Helvetica", 10, "italic"), wraplength=1000, justify="center")
    disclaimer_label.pack(pady=5)

    root.mainloop()

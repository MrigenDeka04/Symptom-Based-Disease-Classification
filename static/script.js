document.addEventListener('DOMContentLoaded', function() {
    const symptomCheckboxesDiv = document.getElementById('symptom-checkboxes');
    const symptomForm = document.getElementById('symptom-form');
    const predictedDiseaseElement = document.getElementById('predicted-disease');
    const confidenceLevelElement = document.getElementById('confidence-level');
    const precautionsElement = document.getElementById('precautions');
    const randomQuoteElement = document.getElementById('random-quote');


    // Function to fetch and display symptoms
    function fetchAndDisplaySymptoms() {
        fetch('/symptoms')
            .then(response => response.json())
            .then(symptoms => {
                symptomCheckboxesDiv.innerHTML = ''; // Clear loading message

                // Dynamically generate checkboxes
                symptoms.forEach(symptom => {
                    const checkboxDiv = document.createElement('div');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = symptom;
                    checkbox.name = 'symptoms';
                    checkbox.value = symptom;

                    const label = document.createElement('label');
                    label.htmlFor = symptom;
                    label.textContent = symptom;

                    checkboxDiv.appendChild(checkbox);
                    checkboxDiv.appendChild(label);
                    symptomCheckboxesDiv.appendChild(checkboxDiv);
                });
            })
            .catch(error => {
                console.error('Error fetching symptoms:', error);
                symptomCheckboxesDiv.innerHTML = '<p>Error loading symptoms.</p>';
            });
    }

    // Function to fetch and display a random quote
    function fetchAndDisplayQuote() {
        const quotes = [
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
        ];
        const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
        randomQuoteElement.textContent = randomQuote;
    }


    // Function to collect selected symptoms
    function getSelectedSymptoms() {
        const selectedSymptoms = [];
        symptomCheckboxesDiv.querySelectorAll('input[name="symptoms"]:checked').forEach(checkbox => {
            selectedSymptoms.push(checkbox.value);
        });
        return selectedSymptoms;
    }

    // Handle form submission
    symptomForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const selectedSymptoms = getSelectedSymptoms();
        console.log("Selected Symptoms:", selectedSymptoms);

        // Send selected symptoms to the backend
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms: selectedSymptoms }),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Prediction Results:", data);
            // Display results to the user
            predictedDiseaseElement.textContent = `Predicted Disease: ${data.predicted_disease}`;
            // Check if confidence is available before formatting
            if (data.confidence !== null && data.confidence !== undefined) {
                 confidenceLevelElement.textContent = `Confidence Level: ${data.confidence.toFixed(2)}%`;
            } else {
                 confidenceLevelElement.textContent = 'Confidence Level: N/A';
            }
            precautionsElement.textContent = `Precautions: ${data.precautions}`;
        })
        .catch(error => {
            console.error('Error during prediction:', error);
            predictedDiseaseElement.textContent = 'Predicted Disease: Error predicting disease.';
            confidenceLevelElement.textContent = 'Confidence Level: N/A';
            precautionsElement.textContent = 'Precautions: Error fetching precautions.';
        });
    });

    // Initial load
    fetchAndDisplaySymptoms();
    fetchAndDisplayQuote();
});

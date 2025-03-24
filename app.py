from flask import Flask, jsonify, request, session
import pandas as pd
import os
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Path to your treatments CSV file
TREATMENTS_FILE = 'treatments_24.csv'
LLM_FULL_RESULTS_FILE = 'llm_responses.csv'
HUMAN_CURRENT_RESULTS_FILE = 'human_current_results.csv'
LLM_CURRENT_RESULTS_FILE = 'llm_current_results.csv'

# Load treatments data once at startup
def load_treatments():
    if not os.path.exists(TREATMENTS_FILE):
        raise FileNotFoundError(f"Treatments file {TREATMENTS_FILE} not found")
    
    df = pd.read_csv(TREATMENTS_FILE)
    treatments = {}
    
    # Group by treatment_id
    for treatment_id, group in df.groupby('treatment_id'):
        treatments[treatment_id] = group.to_dict('records')
    
    return treatments

# Initialize treatments
try:
    all_treatments = load_treatments()
except Exception as e:
    print(f"Error loading treatments: {e}")
    all_treatments = {}


@app.route('/initialize', methods=['GET'])
def initialize():
    """
    Initialize a new treatment session by selecting the next treatment ID
    and returning its headlines.
    """
    # Read existing results if file exists
    human_current_results = []
    if os.path.exists(HUMAN_CURRENT_RESULTS_FILE):
        try:
            human_current_results = pd.read_csv(HUMAN_CURRENT_RESULTS_FILE)
        except pd.errors.EmptyDataError:
            pass
    if os.path.exists(LLM_CURRENT_RESULTS_FILE):
        try:
            llm_current_results = pd.read_csv(LLM_CURRENT_RESULTS_FILE)
        except pd.errors.EmptyDataError:
            pass
    if os.path.exists(LLM_FULL_RESULTS_FILE):
        try:
            llm_full_results = pd.read_csv(LLM_FULL_RESULTS_FILE)
        except pd.errors.EmptyDataError:
            pass

    # Determine next treatment ID
    if len(human_current_results) == 0:
        next_treatment = 1
    else:
        # Count occurrences of each treatment_id
        treatment_counts = human_current_results['treatment_id'].value_counts()
        
        # Find the first treatment that hasn't been done twice
        next_treatment = 1
        while next_treatment in treatment_counts and treatment_counts[next_treatment] >= 2:
            next_treatment += 1

    # Determine which AI model to use
    ai_models = llm_full_results['expert_id'].unique()
    ai_model = random.choice(ai_models)
    
        
    

    # Get headlines for the next treatment
    if next_treatment not in all_treatments:
        return jsonify({"error": "No more treatments available"}), 404

    headlines = [{"id": item["id"], "headline": item["headline"]} 
                for item in all_treatments[next_treatment]]
    for h in headlines:
        ai_response = llm_full_results[(llm_full_results['headline'] == h['headline']) & (llm_full_results['expert_id'] == ai_model)]["advice"].values[0]
        h['ai_response'] = ai_response
    return jsonify({
        "treatment_id": next_treatment,
        "headlines": headlines,
        "ai_model": ai_model,
    })

@app.route('/submit', methods=['POST'])
def submit():
    """
    Submit the results of a treatment.
    """
    data = request.json
    if not data or 'treatment_id' not in data or 'answers' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    treatment_id = data['treatment_id']
    answers = data['answers']

    # Validate answers
    if len(answers) != 24:
        return jsonify({"error": "Must provide answers for all 24 headlines"}), 400

    # Create DataFrame with results
    results = []
    for answer in answers:
        results.append({
            'treatment_id': treatment_id,
            'headline_id': answer['id'],
            'answer': answer['answer']
        })
    
    results_df = pd.DataFrame(results)

    # Append to existing results or create new file
    if os.path.exists(HUMAN_CURRENT_RESULTS_FILE):
        human_current_results = pd.read_csv(HUMAN_CURRENT_RESULTS_FILE)
        results_df = pd.concat([human_current_results, results_df], ignore_index=True)
    
    # Save results
    results_df.to_csv(HUMAN_CURRENT_RESULTS_FILE, index=False)
    
    return jsonify({"message": "Results saved successfully"})

if __name__ == '__main__':
    app.run(debug=True)
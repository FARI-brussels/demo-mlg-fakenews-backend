# Fake News demo backend

## API Documentation

### Endpoints

#### 1. Initialize Session
```http
GET /initialize
```

Initializes a new session by selecting the next available treatment and returning its headlines along with AI model responses.

**Response Format:**
```json
{
    "treatment_id": 1,
    "headlines": [
        {
            "id": 1,
            "headline": "Example headline 1",
            "ai_response": 0.25
        },
        // ... 24 headlines total
    ],
    "ai_model": "model_identifier"
}
```
The ai response range from 0 for very unlikely to 1 for very likely.

**Error Responses:**
- `404 Not Found`: When no more treatments are available
```json
{
    "error": "No more treatments available"
}
```

#### 2. Submit Treatment Results
```http
POST /submit
```

Submits the human responses for a treatment session. The 

**Request Format:**
```json
{
    "treatment_id": 1,
    "headlines": [
        {
            "id": 1,
            "headline": "Example headline 1",
            "ai_response": 0.25,
            "human_response" :  1
        },
        // ... 24 headlines total
    ],
    "ai_model": "model_identifier"
}
```

**Response Format:**
```json
{
    "graph":  "to do later"
}
```

**Error Responses:**
- `400 Bad Request`: When required fields are missing or invalid
```json
{
    "error": "Missing required fields"
}
```
or
```json
{
    "error": "Must provide answers for all 24 headlines"
}
```

## Data Files

The backend uses several CSV files to manage data:

1. `treatments_24.csv`: Contains all treatments and their headlines
2. `llm_responses.csv`: Contains AI model responses for all headlines
3. `human_current_results.csv`: Stores current human responses
4. `llm_current_results.csv`: Stores current AI model responses

## Treatment Selection Logic

The backend implements the following logic for selecting treatments:

1. If no results exist, treatment 1 is selected
2. For existing results:
   - Counts how many times each treatment has been completed
   - Selects the first treatment that hasn't been completed twice
3. When all treatments have been completed twice, returns a 404 error

## Setup and Running

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

## Testing

Run the test suite:
```bash
pytest test_app.py -v
```

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all origins to allow frontend applications to interact with the API.
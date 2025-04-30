from flask import Flask, jsonify, render_template, request
from fuzzywuzzy import process

def read_responses_from_file(filename):
    responses = {}
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if ':' in line:
                question, answers = line.split(':', 1)
                responses[question.strip()] = [answer.strip() for answer in answers.split('|')]
    return responses

app = Flask(__name__)

RESPONSES_FILE = 'GetBot_Kel4/GetBot_Kel4/responses.txt'
responses = read_responses_from_file(RESPONSES_FILE)

user_state = {}

def get_response(user_input, responses, user_id='default_user'):
    questions = list(responses.keys())
    
    # Mengambil beberapa kandidat pertanyaan
    candidates = process.extract(user_input, questions, limit=5)

    # Menyaring kandidat berdasarkan threshold
    filtered_candidates = [candidate for candidate in candidates if candidate[1] > 70]  # Misalnya threshold 70
    
    if not filtered_candidates:
        return "Maaf, saya tidak mengerti pertanyaan Anda."

    # Memilih kandidat dengan confidence tertinggi
    closest_match, confidence = max(filtered_candidates, key=lambda x: x[1])
    
    # Menangani pertanyaan mirip
    if confidence > 75:
        question = closest_match
        if user_id not in user_state:
            user_state[user_id] = {question: 0}
        if question not in user_state[user_id]:
            user_state[user_id][question] = 0

        answer_index = user_state[user_id][question]
        response = responses[question][answer_index]

        user_state[user_id][question] = (answer_index + 1) % len(responses[question])

        return response
    else:
        return "Maaf, saya tidak mengerti pertanyaan Anda."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['user_input']
    bot_response = get_response(user_input, responses)
    return jsonify({'bot_response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)

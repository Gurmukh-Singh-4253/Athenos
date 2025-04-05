from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import os
import json
from datetime import  datetime

app = Flask(__name__)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Load datasets
env_df = pd.read_csv('data/environment_science_QA.csv')
geo_df = pd.read_csv('data/geography_rivers_QA.csv')
hist_df = pd.read_csv('data/history_ww2_QA.csv')

def save_result_json(subject, result, user_id="anonymous"):
    """Saves evaluation result to a JSON file for future tracking."""
    filename = f"results/{subject}_results.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Add metadata
    record = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "total_score": result['total_score'],
        "out_of": result['out_of'],
        "grade": result['grade'],
        "feedback": result['final_feedback']
    }

    # Load existing data or create new
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    data.append(record)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def assign_grade(score, out_of):
    percent = (score / out_of) * 100
    if percent >= 90:
        return "A", "Excellent!"
    elif percent >= 75:
        return "B", "Good work!"
    elif percent >= 60:
        return "C", "Fair, needs improvement"
    elif percent >= 40:
        return "D", "Weak, review needed"
    else:
        return "F", "Poor, please revisit"


def evaluate_quiz(df, answers):
    q_map = df.set_index("Question")["Answer"].to_dict()
    results = []
    for item in answers:
        q = item['question']
        student_ans = item['answer']
        correct_ans = q_map.get(q, "")

        emb = model.encode([student_ans, correct_ans], convert_to_tensor=True)
        sim = util.pytorch_cos_sim(emb[0], emb[1]).item()

        if sim >= 0.8:
            score, fb = 1, "Great job!"
        elif sim >= 0.5:
            score, fb = 0.5, "Almost correct"
        else:
            score, fb = 0, "Not quite, review the concept"

        results.append({
            "question": q,
            "your_answer": student_ans,
            "correct_answer": correct_ans,
            "score": score,
            "similarity": round(sim, 2),
            "feedback": fb
        })

    total = sum(r['score'] for r in results)
    grade, final_fb = assign_grade(total, len(results))
    return {
        "total_score": total,
        "out_of": len(results),
        "grade": grade,
        "final_feedback": final_fb,
        "details": results
    }


# ---------- Frontend Pages ----------
@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/environment')
def env_page():
    return render_template('environment.html')

@app.route('/geography')
def geo_page():
    return render_template('geography.html')

@app.route('/history')
def hist_page():
    return render_template('history.html')


# ---------- API Endpoints ----------
@app.route('/environment/generate')
def generate_env_quiz():
    n = int(request.args.get('n', 5))
    quiz = env_df.sample(n=min(n, len(env_df))).to_dict(orient='records')
    return jsonify(quiz)

@app.route('/environment/evaluate', methods=['POST'])
def evaluate_env_quiz():
    data = request.json
    answers = data['answers']
    user_id = data.get('user_id', 'anonymous')
    result = evaluate_quiz(env_df, answers)
    save_result_json("environment", result, user_id)
    return jsonify(result)


@app.route('/geography/generate')
def generate_geo_quiz():
    n = int(request.args.get('n', 5))
    quiz = geo_df.sample(n=min(n, len(geo_df))).to_dict(orient='records')
    return jsonify(quiz)

@app.route('/geography/evaluate', methods=['POST'])
def evaluate_geo_quiz():
    data = request.json
    answers = data['answers']
    user_id = data.get('user_id', 'anonymous')
    result = evaluate_quiz(geo_df, answers)
    save_result_json("geography", result, user_id)
    return jsonify(result)

@app.route('/history/generate')
def generate_hist_quiz():
    n = int(request.args.get('n', 5))
    quiz = hist_df.sample(n=min(n, len(hist_df))).to_dict(orient='records')
    return jsonify(quiz)

@app.route('/history/evaluate', methods=['POST'])
def evaluate_hist_quiz():
    data = request.json
    answers = data['answers']
    user_id = data.get('user_id', 'anonymous')
    result = evaluate_quiz(hist_df, answers)
    save_result_json("history", result, user_id)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)


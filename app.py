from flask import Flask, render_template, jsonify
import detect_fp  # Assuming detect_fp.py is in the same directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results')
def results_page():
    return render_template('results.html')

@app.route('/api/results', methods=['GET'])
def get_results():
    results = detect_fp.main()  # Assuming detect_fp.main() returns a dictionary with the results
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)

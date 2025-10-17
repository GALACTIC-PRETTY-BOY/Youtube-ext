from flask import Flask, request, jsonify
import testing_models # rename imported script accordingly

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    video_id = request.json['videoId']
    output = testing_models.run_analysis(video_id)  # You must write this function to wrap your script's logic
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)



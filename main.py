from flask import Flask, request, jsonify
import subprocess, os, uuid

app = Flask(__name__)
os.makedirs("source", exist_ok=True)
os.makedirs("result", exist_ok=True)

@app.route('/')
def home():
    return '✅ Audio Splitter is running!'

@app.route('/split-audio', methods=['POST'])
def split_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    file_id = str(uuid.uuid4())
    input_path = f"source/{file_id}.mp3"
    output_template = f"result/{file_id}_%03d.mp3"

    file.save(input_path)

    try:
        subprocess.run([
            "ffmpeg", "-i", input_path,
            "-f", "segment", "-segment_time", "600", "-c", "copy", output_template
        ], check=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    chunks = sorted(f for f in os.listdir("result") if f.startswith(file_id))
    return jsonify({"chunks": chunks, "count": len(chunks)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

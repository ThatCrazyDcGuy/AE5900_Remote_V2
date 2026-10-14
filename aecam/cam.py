import os
from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

if os.environ.get('WERKZEUG_RUN_MAIN') or not app.debug:
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
else:
    camera = None

def generate_frames():
    if camera is None:
        yield b"Camera not initialized"
        return
        
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5005, debug=True, use_reloader=False)

   

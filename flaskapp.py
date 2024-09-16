from flask import Flask, render_template, Response,jsonify,request,session
from flask import Flask, render_template, Response, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from psutil import users
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import InputRequired
import os
import cv2
from ultralytics import YOLO
import math

#FlaskForm--> it is required to receive input from the user
# Whether uploading a video file  to our object detection model

from flask_wtf import FlaskForm


from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange
import os


# Required to run the YOLOv8 model
import cv2

# YOLO_Video is the python file which contains the code for our object detection model
#Video Detection is the Function which performs Object Detection on Input Video
from YOLO_Video import video_detection
app = Flask(__name__)

app.config['SECRET_KEY'] = 'muhammadmoin'
app.config['UPLOAD_FOLDER'] = 'static/files'


#Use FlaskForm to get input video file  from user
class UploadFileForm(FlaskForm):
    #We store the uploaded video file path in the FileField in the variable file
    #We have added validators to make sure the user inputs the video in the valid format  and user does upload the
    #video when prompted to do so
    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Run")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = StringField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password", 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#dummy user and password

users = {
    'admin': 'password',
    'user1': 'password1',
    'user2': 'password2'
}


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = StringField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


def generate_frames(path_x = ''):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    session.clear()
    return render_template('indexproject.html')
# Rendering the Webcam Rage
#Now lets make a Webcam page for the application
#Use 'app.route()' method, to render the Webcam page at "/webcam"
@app.route("/webcam", methods=['GET','POST'])

def webcam():
    session.clear()
    return render_template('ui.html')
@app.route('/FrontPage', methods=['GET','POST'])
def front():
    # Upload File Form: Create an instance for the Upload File Form
    form = UploadFileForm()
    if form.validate_on_submit():
        # Our uploaded video file path is saved here
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))  # Then save the file
        # Use session storage to save video file path
        session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                             secure_filename(file.filename))
    return render_template('videoprojectnew.html', form=form)
@app.route('/video')
def video():
    #return Response(generate_frames(path_x='static/files/bikes.mp4'), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames(path_x = session.get('video_path', None)),mimetype='multipart/x-mixed-replace; boundary=frame')

# To display the Output Video on Webcam page
@app.route('/webapp')
def webapp():
    #return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames_web(path_x=0), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
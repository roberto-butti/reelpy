import os
import pprint
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug import secure_filename


app = Flask(__name__)

app.secret_key = 'skfjsfkfklfjlsfjfklfjks'
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['mp4', 'mov'])

app.config['config_size']=300, 168
app.config['config_fps']=8
app.config['config_maxframes']=80




# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route("/")
def index():
  listfiles = os.listdir(os.path.join(app.config['UPLOAD_FOLDER']+"videos/"))
  pprint.pprint(listfiles)

  return render_template("index.html", listfiles=listfiles)

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER']+"videos/", filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        flash("File: "+filename+" caricato")
        return redirect(url_for('index'))
        #return redirect(url_for('uploaded_file',
        #                        filename=filename))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER']+'videos/',
                               filename)

@app.route('/uploads_thumb/<filename>')
def uploaded_thumb(filename):
    basepath= os.path.splitext(filename)[0]
    return send_from_directory(app.config['UPLOAD_FOLDER']+'/thumbs/'+basepath+'/', 'test_0001.png')

@app.route('/generate/<filename>')
def generate_file(filename):
  path=app.config['UPLOAD_FOLDER']+'videos/'+filename
  basepath= os.path.splitext(filename)[0]
  paththumb=app.config['UPLOAD_FOLDER']+'thumbs/'+basepath+"/"
  if not os.path.exists(paththumb):
    os.makedirs(paththumb)
  command = "ffmpeg -i "+path+" -vf fps="+str(app.config['config_fps'])+" "+paththumb+"test_%04d.png"
  print command
  os.system(command)
  return "AAAA"

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )

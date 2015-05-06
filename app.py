import os
import pprint
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug import secure_filename
from PIL import Image
from files import Files



app = Flask(__name__)

app.secret_key = 'skfjsfkfklfjlsfjfklfjks'
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['mp4', 'mov'])

app.config['config_size']=300, 168
app.config['config_fps']=1
app.config['config_maxframes']=80





# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def resize(path_thumbs_original, path_thumbs_resized):
    outfiles=[]
    outfilesrow=[]
    i=0
    list_files = os.listdir(path_thumbs_original)

    for infile in list_files:
        outfile = os.path.splitext(infile)[0] + "_thumbnail.png"
        outfile = os.path.join(path_thumbs_resized,outfile)
        outfilesrow.append(outfile)
        if infile != outfile:
            try:
                im = Image.open(os.path.join(path_thumbs_original,infile))
                im.thumbnail(app.config['config_size'], Image.ANTIALIAS)
                im.save(outfile, "PNG")
                #print(outfile)
            except IOError as e:
                print "cannot create thumbnail for '%s'" % infile
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
        i=i+1
        if (i == app.config['config_maxframes']):
            outfiles.append(outfilesrow)
            outfilesrow=[]
            i=0
    if (len(outfilesrow) > 0):
        outfiles.append(outfilesrow)
    return outfiles

def get_path_videos():
    return os.path.join(app.config['UPLOAD_FOLDER'], "videos")

def get_path_generated_thumbs(filename, create_if_no_exists = False):
    path_base= os.path.splitext(filename)[0]
    path = os.path.join(app.config['UPLOAD_FOLDER'], "generated", path_base)
    if create_if_no_exists:
        if not os.path.exists(path):
            os.makedirs(path)
    return  path


def get_path_generated_thumbs_original(filename, create_if_no_exists = False):
    path=os.path.join(get_path_generated_thumbs(filename, create_if_no_exists), "original")
    if create_if_no_exists:
        if not os.path.exists(path):
            os.makedirs(path)
    return  path

def get_path_generated_thumbs_resize(filename, create_if_no_exists = False):
    path=os.path.join(get_path_generated_thumbs(filename), "resize")
    if create_if_no_exists:
        if not os.path.exists(path):
            os.makedirs(path)
    return  path

def get_path_generated_reels(filename, create_if_no_exists = False):
    path=os.path.join(get_path_generated_thumbs(filename), "reels")
    if create_if_no_exists:
        if not os.path.exists(path):
            os.makedirs(path)
    return  path

def generate_reels(filename, outfiles):
    howmany = 0
    path_reels = get_path_generated_reels(filename, True)
    for outfilesrow in outfiles:
        images = map(Image.open, outfilesrow)
        w = sum(i.size[0] for i in images)
        mh = max(i.size[1] for i in images)
        result = Image.new("RGBA", (w, mh))
        x = 0
        for i in images:
            result.paste(i, (x, 0))
            x += i.size[0]
        result.save(os.path.join(path_reels,  "reel_" + str(howmany) + ".jpg"),  "JPEG", quality=15, optimize=True, progressive=True )
        howmany += 1


@app.route("/")
def index():
    path_videos = get_path_videos()
    list_files = []
    if os.path.exists(path_videos):
        list_files = os.listdir(path_videos)
    list_obj_files = [Files(f) for f in list_files]

    pprint.pprint(list_obj_files)
    return render_template("index.html", listfiles=list_obj_files)

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
        path_videos=get_path_videos()
        if not os.path.exists(path_videos):
            os.makedirs(path_videos)
        file.save(os.path.join(path_videos, filename))
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
    return send_from_directory(get_path_videos(), filename)

@app.route('/uploads_thumb/<filename>')
def uploaded_thumb(filename):
    path_file = get_path_generated_thumbs_original(filename)
    return send_from_directory(path_file, 'test_0001.png')

@app.route('/generate/<filename>')
def generate_file(filename):
    file_video = os.path.join(get_path_videos(), filename)
    path_thumbs = get_path_generated_thumbs_original(filename, True)
    path_thumbs_resized = get_path_generated_thumbs_resize(filename, True)
    command = "avconv -i "+file_video+" -vf fps="+str(app.config['config_fps'])+" "+path_thumbs+"/test_%04d.png"
    print command
    os.system(command)
    outfiles = resize(path_thumbs, path_thumbs_resized)
    generate_reels(filename, outfiles)
    flash("Frames extracted")
    return redirect(url_for('index'))

@app.route('/resizethumb/<filename>')
def resize_thumb(filename):
    path_thumbs = get_path_generated_thumbs_original(filename, True)
    path_thumbs_resized = get_path_generated_thumbs_resize(filename, True)
    resize(path_thumbs, path_thumbs_resized)
    flash("Thumbs resized")
    return redirect(url_for('index'))

@app.route('/delete/<filename>')
def delete_file(filename):
    file_video = os.path.join(get_path_videos(), filename)

@app.route('/view_reel/<filename>')
def view_reel(filename):
    file_video = os.path.join(get_path_videos(), filename)



if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )

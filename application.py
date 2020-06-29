import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from detector import Detector

UPLOAD_FOLDER = 'static/data/uploads'
DETECTED_FOLDER = 'static/data/detected'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(application.config['UPLOAD_FOLDER'], exist_ok=True)
application.config['DETECTED_FOLDER'] = DETECTED_FOLDER
os.makedirs(application.config['DETECTED_FOLDER'], exist_ok=True)

detector = Detector()
entries = {"category": list(detector.category_map.values()),}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@application.route('/', methods=['GET', 'POST'])
def upload_file_by_folder():
    if request.method == 'POST':
        entries["files"] = list()
        images = request.files.getlist('file')

        for folder in ('UPLOAD_FOLDER', 'DETECTED_FOLDER'):
            for root, dirs, files in os.walk(application.config[folder]):
                for file in files:
                    os.remove(os.path.join(root, file))

        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))

                detector.run(os.path.join(application.config['UPLOAD_FOLDER'], filename),
                             os.path.join(application.config['DETECTED_FOLDER'], filename))

                entries['files'].append({
                    'filename': filename,
                    'path': os.path.join(application.config['UPLOAD_FOLDER'], filename)
                })

        return render_template("images.html", entries=entries)

    return render_template("index.html", entries=entries)


@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    application.run("0.0.0.0", port=80)

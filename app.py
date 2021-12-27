import os
from flask import Flask, flash, request, redirect, url_for ,render_template, send_from_directory
from werkzeug.utils import secure_filename
from PyPDF2 import PdfFileReader, PdfFileWriter
import time
from flask import after_this_request

UPLOAD_FOLDER = 'Transformed PDF'
ALLOWED_EXTENSIONS = { 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') 

app.add_url_rule(
    "/rotation/<name>", endpoint="download_file") # , build_only=True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Redirect to the home page
@app.route('/',methods=['GET', 'POST'])
def home():
    
    return render_template('index.html')

#getting data from form
@app.route('/pdf', methods=['GET', 'POST'])
def upload_file()->str:
    if request.method == "POST":
        
        #getting the pdf page number
        page_number = int(request.form['page_number'])
        
        #getting angle of rotation
        degree_of_rotation = int(request.form['degree_of_rotation'])
        
    #getting the pdf file
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = file.filename
        # filename = secure_filename(file.filename)
        
        pdf_writer = PdfFileWriter()
        pdf_reader = PdfFileReader(file)
        #getting pdf page count
        pdf_size = pdf_reader.getNumPages()
        # print(f'pdf size:{pdf_size}')
        
        
        #getting the pdf page
        basedir = os.path.abspath(os.path.dirname(__file__))
        file.save(os.path.join(basedir,app.config['UPLOAD_FOLDER'],file.filename))
        trf_path = os.path.join(basedir,app.config['UPLOAD_FOLDER'],file.filename)
        
        #checker for page number
        if page_number > pdf_size-1:
            flash("Page number doesn't exist!")
            return redirect(request.url)
        time.sleep(1)
        
        #rotating pages
        for page in range(pdf_size):
            if page == page_number:
                
                page_obj = pdf_reader.getPage(page)
                page_obj.rotateClockwise(degree_of_rotation)
                pdf_writer.addPage(page_obj)
                
                # saving the transformed pdf
                with open(trf_path, 'wb') as file:
                    pdf_writer.write(file)
            else:
                pdf_writer.addPage(pdf_reader.getPage(page))
                with open(trf_path, 'wb') as file:
                    pdf_writer.write(file)
        return redirect(url_for('download_file', name=filename))

#Redirecting transformed file into new tab    
@app.route('/rotation/<name>')
def download_file(name):
    # deleting file after the rotation
    @after_this_request
    def delete(response):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], name))
        return response
    return send_from_directory(directory='Transformed PDF',path=name)

 
if __name__ == "__main__":
    app.run(debug=True)

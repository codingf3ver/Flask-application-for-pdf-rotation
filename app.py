import os
from flask import Flask, flash, request, redirect, url_for ,render_template, send_from_directory
from flask import after_this_request
from PyPDF2 import PdfFileReader, PdfFileWriter
import time


UPLOAD_FOLDER = 'Transformed PDF'
ALLOWED_EXTENSIONS = { 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] ="ccqeeejfeydqwdwndwdcec" #os.environ.get('SECRET_KEY') # this is temp security key

#Opening in new tab
app.add_url_rule(
    "/rotation/<name>", endpoint="download_file") # , build_only=True

#allowed file type
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
    try:
        if request.method == "POST":
        
            #getting the pdf page number
            page_number = int(request.form['page_number'])
            
            #getting angle of rotation
            degree_of_rotation = int(request.form['degree_of_rotation'])
            
            #checker for valid file type
            if 'file' not in request.files:
                flash('No file part')
                return redirect(url_for('home'))
            
            file = request.files['file']
            
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(url_for('home'))
            
            if file and allowed_file(file.filename):
                filename = file.filename
            
            # pdf writer object    
            pdf_writer = PdfFileWriter()
            pdf_reader = PdfFileReader(file)
            pdf_size = pdf_reader.getNumPages()
            
            #getting the pdf page
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir,app.config['UPLOAD_FOLDER'],file.filename))
            trf_path = os.path.join(basedir,app.config['UPLOAD_FOLDER'],file.filename)
            
            #checker for page number
            if page_number > pdf_size-1:
                flash("Page number doesn't exist!")
                return redirect(request.url)
            time.sleep(0.5)
            
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

    except Exception as e:
        pass     
    
    # if exception it will redirect to home page
    return render_template('index.html')
        
        
            
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

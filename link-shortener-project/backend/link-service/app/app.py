from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask, jsonify , request , redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import shortuuid
# instance of the Flask class
app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)

#--add this section for database configuration ---
# for now we are using a local SQLite database but later we will chamnge it to PostgreSQL .
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///links.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Create the SQLAlchemy database object
db = SQLAlchemy(app)

#---end of database configuration section---

#-----  ADD THIS MODEL CLASS ------
# this class will define the "links" table in your database
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(512), nullable=False)
    short_code = db.Column(db.String(8), unique=True, nullable=False)

    def __repr__(self):
        return f'<Link {self.short_code}>'
    
#----- END OF MODEL CLASS -------

@app.route('/')
def health_check():
    """
    This route is a health check to confirm the service is running.
    """
    return jsonify({"status": "healthy", "message": "Link service is up and running!"}), 200

@app.route('/api/shorten', methods = ['POST'])
def shorten_url():
    """
    This route accepts a JSON payload with a 'long_url' field and returns a shortened URL.
    """
    data = request.get_json()

    if not data or 'long_url' not in data:
        return jsonify({"error": "invalid request the 'long URL' is required"}), 400
    
    long_url = data['long_url']

    #check if the long_url already exist or not in the database
    existing_link = Link.query.filter_by(long_url=long_url).first()
    if existing_link:
        short_url = request.host_url +'r/' + existing_link.short_code
        return jsonify({
            "message" : "link already exist",
            "long_url" : long_url,
            "short_url" : short_url,
            "short_code" : existing_link.short_code
        }), 200
    
    # if not exist , create a new link
    short_code = shortuuid.uuid()[:8]
    new_link = Link(long_url = long_url , short_code = short_code)
    
    #add this new link to database session and commit 
    db.session.add(new_link)
    db.session.commit()

    short_url = request.host_url +'r/' + short_code

    return jsonify({
        "message" : "New link Created successfully",
        "long_url" : long_url,
        "short_url" : short_url,
        "short_code" : short_code
    }) , 201

@app.route('/r/<short_code>')
def redirect_to_long_url(short_code):
    """
    This route redirects to the original long URL based on the provided short code.
    """
    # look for the original_link (long_url) in the database by the short_code
    link = Link.query.filter_by(short_code=short_code).first_or_404()

    #if found redirect to long url
    return redirect(link.long_url)

#Method to get all the link 
@app.route('/api/links', methods = ['GET'])
def get_all_links():
    """
    Returns a  list of all stored links in the database
    """
    links = Link.query.all()
    
    output = []
    for link in links:
        short_url = request.host_url + 'r/' + link.short_code
        output.append({
            "long_url" : link.long_url,
            "short_url" : short_url,
            "short_code" : link.short_code
        })
    return jsonify({"links" : output})
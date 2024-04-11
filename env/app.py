from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, unset_jwt_cookies

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_repositori'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  

db = SQLAlchemy(app)
jwt = JWTManager(app)

class DataDokumen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.String(10), db.ForeignKey('data_dosen.nip'), nullable=False)
    type_dokumen = db.Column(db.Enum('file', 'url'), nullable=False)
    nama_dokumen = db.Column(db.String(100), nullable=False)
    nama_file = db.Column(db.String(100), nullable=False)

class DataDosen(db.Model):
    nip = db.Column(db.String(10), primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    prodi_id = db.Column(db.Integer, db.ForeignKey('data_prodi.id'), nullable=False)

class DataProdi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kode_prodi = db.Column(db.String(10), unique=True, nullable=False)
    nama_prodi = db.Column(db.String(100), nullable=False)


#LOGIN LOGOUT
@app.route('/login', methods=['POST'])
def login():
    nama_lengkap = request.json.get('nama_lengkap', None)
    nip = request.json.get('nip', None)

    # Periksa kredensial pengguna
    user = DataDosen.query.filter_by(nama_lengkap=nama_lengkap, nip=nip).first()
    if user:
        # Jika kredensial valid, buat token JWT
        access_token = create_access_token(identity=user.nip)
        return jsonify(message='Login Successful', access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid nama_lengkap or nip"}), 401
    

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    unset_jwt_cookies()
    return{'message': 'Logged out successfully'}, 200
    


#DOSEN
@app.route('/dosen', methods=['GET'])
@jwt_required()
def get_all_dosen():
    dosen = DataDosen.query.all()
    if dosen:
        result = []
        for d in dosen:
            result.append({'nip': d.nip, 'nama_lengkap': d.nama_lengkap, 'prodi_id': d.prodi_id})
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No dosen found'}), 404

@app.route('/dosen/<nip>', methods=['GET'])
@jwt_required()
def get_dosen(nip):
    dosen = DataDosen.query.get(nip)
    if dosen:
        return jsonify({'nip': dosen.nip, 'nama_lengkap': dosen.nama_lengkap, 'prodi_id': dosen.prodi_id}), 200
    else:
        return jsonify({'message': 'Dosen not found'}), 404
    
@app.route('/dosen', methods=['POST'])
@jwt_required()
def create_dosen():
    if request.method == 'POST':
        data = request.json
        new_dosen = DataDosen(nip=data['nip'], nama_lengkap=data['nama_lengkap'], prodi_id=data['prodi_id'])
        db.session.add(new_dosen)
        db.session.commit()
        return jsonify({'message': 'Dosen created successfully'}), 201

@app.route('/dosen/<nip>', methods=['PUT'])
@jwt_required()
def update_dosen(nip):
    if request.method == 'PUT':
        data = request.json
        dosen = DataDosen.query.get(nip)
        if dosen:
            dosen.nama_lengkap = data['nama_lengkap']
            dosen.prodi_id = data['prodi_id']
            db.session.commit()
            return jsonify({'message': 'Dosen updated successfully'}), 200
        else:
            return jsonify({'message': 'Dosen not found'}), 404

@app.route('/dosen/<nip>', methods=['DELETE'])
@jwt_required()
def delete_dosen(nip):
    dosen = DataDosen.query.get(nip)
    if dosen:
        db.session.delete(dosen)
        db.session.commit()
        return jsonify({'message': 'Dosen deleted successfully'}), 200
    else:
        return jsonify({'message': 'Dosen not found'}), 404
    


#DOCUMENT
@app.route('/document', methods=['GET'])
@jwt_required()
def get_all_documen():
    dokumen = DataDokumen.query.all()
    if dokumen:
        result = []
        for d in dokumen:
            result.append({'nip': d.nip, 'type_dokumen': d.type_dokumen, 'nama_dokumen': d.nama_dokumen, 'nama_file': d.nama_file})
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No documents found'}), 404

@app.route('/document/<id>', methods=['GET'])
@jwt_required()
def get_document(id):
    doc = DataDokumen.query.get(id)
    if doc :
        return jsonify({'id:' : doc.id, 'type_document': doc.type_dokumen, 'nama_dokumen': doc.nama_dokumen, 'nama_file': doc.nama_dokumen })
    else :
        return jsonify({'message': 'Document not found'}), 404

@app.route('/document', methods=['POST'])
@jwt_required()
def create_dokumen():
    if request.method == 'POST':
        data = request.json
        new_doc = DataDokumen(nip=data["nip"], type_dokumen=data["type_dokumen"], nama_dokumen=data["nama_dokumen"], nama_file=data["nama_file"])
        db.session.add(new_doc)
        db.session.commit()
        return jsonify({"message": 'Document created succusfully'})
    
@app.route('/document/<nip>', methods=['PUT'])
@jwt_required()
def update_dokumen(nip):
    if request.method == 'PUT':
        data = request.json
        doc = DataDokumen.query.get(nip)
        if doc:
            doc.nip = data['nip']
            doc.type_dokumen = data['type_dokumen']
            doc.nama_dokumen = data['nama_dokumen']
            doc.nama_file = data['nama_file']
            db.session.commit()
            return jsonify({'message': 'Document updated successfully'}), 200
        else:
            return jsonify({'message': 'Document not found'}), 404

@app.route('/document/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_dokumen(id):
    doc = DataDokumen.query.get(id)
    if doc:
        db.session.delete(doc)
        db.session.commit()
        return jsonify({'message': 'Document deleted successfully'}), 200
    else:
        return jsonify({'message': 'Document not found'}), 404



#PRODI
@app.route('/prodi', methods=['GET'])
@jwt_required()
def get_all_prodi():
    prodi_list = DataProdi.query.all()
    if prodi_list:
        result = []
        for prodi in prodi_list:
            result.append({'kode_prodi': prodi.kode_prodi, 'nama_prodi': prodi.nama_prodi})
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No program studi found'}), 404

@app.route('/prodi/<int:kode_prodi>', methods=['GET'])
@jwt_required()
def get_prodi(kode_prodi):
    prodi = DataProdi.query.get(kode_prodi)
    if prodi:
        return jsonify({'kode_prodi': prodi.kode_prodi, 'nama_prodi': prodi.nama_prodi}), 200
    else:
        return jsonify({'message': 'Prodi not found'}), 404
    
@app.route('/prodi', methods=['POST'])
@jwt_required()
def create_prodi():
    if request.method == 'POST':
        data = request.json
        new_prodi = DataProdi(kode_prodi=data['kode_prodi'], nama_prodi=data['nama_prodi'])
        db.session.add(new_prodi)
        db.session.commit()
        return jsonify({'message': 'Prodi created successfully'}), 201

@app.route('/prodi/<int:id>', methods=['PUT'])
@jwt_required()
def update_prodi(id):
    data = request.json
    prodi = DataProdi.query.get(id)
    if prodi:
        prodi.nama_prodi = data['nama_prodi']
        prodi.kode_prodi = data['kode_prodi']
        db.session.commit()
        return jsonify({'message': 'Prodi updated successfully'}), 200
    else:
        return jsonify({'message': 'Prodi not found'}), 404

@app.route('/prodi/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_prodi(id):
    prodi = DataProdi.query.get(id)
    if prodi:
        db.session.delete(prodi)
        db.session.commit()
        return jsonify({'message': 'Prodi deleted successfully'}), 200
    else:
        return jsonify({'message': 'Prodi not found'}), 404



if __name__ == '__main__':
    app.run(debug=True)
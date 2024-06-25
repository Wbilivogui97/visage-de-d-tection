import os
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

def get_recommendations(client_index, similarity_matrix, services, top_n=3):
    similar_clients = np.argsort(-similarity_matrix[client_index])[1:top_n]
    similar_clients_services = services.iloc[similar_clients]
    service_scores = similar_clients_services.sum(axis=0)
    client_services = services.iloc[client_index]
    recommended_services = service_scores[client_services == 0]
    recommended_services = recommended_services.sort_values(ascending=False)

    specific_voix = 'voix_nationale'
    specific_internationale = 'voix_internationale'
    specific_sms = 'sms'
    specific_data = 'data'

    if specific_voix not in recommended_services.index:
        return ['choco_malin']
    elif specific_sms not in recommended_services.index:
        return ['pack_sms', 'choco_magic']
    elif specific_data not in recommended_services.index:
        return ['choco_magic', 'choco_maxi']
    elif specific_internationale not in recommended_services.index:
        return ['choco_afrique', 'choco_monde']
    elif all(s not in recommended_services.index for s in [specific_sms, specific_voix, specific_data]):
        return ['choco_maxi', 'choco_magic']
    elif all(s not in recommended_services.index for s in [specific_sms, specific_voix, specific_data, specific_internationale]):
        return ['choco_maxi', 'choco_afrique', 'choco_monde']
    elif all(s not in recommended_services.index for s in [specific_sms, specific_voix]):
        return ['choco_malin']
    elif all(s not in recommended_services.index for s in [specific_sms, specific_data]):
        return ['choco_magic', 'choco_maxi']
    elif all(s not in recommended_services.index for s in [specific_voix, specific_data]):
        return ['choco_magic', 'choco_maxi', 'choco_malin']
    elif all(s not in recommended_services.index for s in [specific_internationale, specific_sms]):
        return ['pack_sms', 'choco_afrique', 'choco_monde']
    else:
        return recommended_services.index.tolist()

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    try:
        # Lecture du fichier CSV ou Excel
        if file.filename.endswith('.csv'):
            data = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            data = pd.read_excel(file)
        else:
            return jsonify({'error': 'le type de fichier insurportable,veuillez importer le bon fichier'})
        
        # Vérification des colonnes nécessaires
        required_columns = ['client', 'voix_nationale', 'voix_internationale', 'sms', 'data', 
                            'pack_sms', 'choco_malin', 'choco_magic', 'choco_maxi', 
                            'choco_afrique', 'choco_monde']
        
        if not set(required_columns).issubset(data.columns):
            missing_columns = list(set(required_columns) - set(data.columns))
            return jsonify({'error': f'Il manque la(es) colonne(e) {", ".join(missing_columns)} dans le fichier'})
        
        services = data.drop(columns=['client'])
        similarity_matrix = cosine_similarity(services)
        recommendations = {}
        
        # Pour chaque client, obtenir les recommandations
        for client_id in data['client']:
            client_index = data.index[data['client'] == client_id].tolist()[0]
            recommendations[client_id] = get_recommendations(client_index, similarity_matrix, services)
        
        return jsonify({'Les differentes recommandations en fonction du comportement de chaque client': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

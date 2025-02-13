import pandas as pd
import streamlit as st
import time
import datetime

def main():

    # Créer le nom du fichier avec la date et l'heure
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

    # Fonction pour transformer les numéros
    def transform_number(number):
        """Appliquer les règles de transformation des numéros."""
        if number.startswith('00'):
            return '0' + number[2:]  # Remplacer '00' par '0'
        elif number.startswith('0'):
            return number  # Aucun changement si le numéro commence par 0
        elif number.startswith('212'):
            return '0' + number[3:]  # Remplacer '212' par '0'
        else:
            return '0' + number  # Ajouter un 0 si le numéro ne commence ni par 0 ni par 212 ni par 00

    # Fonction pour charger et nettoyer les données d'appels et SMS
    def load_and_clean_data(file):
        df = pd.read_csv(file, sep='\t', encoding='latin1',dtype={'Cgi': str,'IMEI': str})    
        if 'Date Naissance' in df.columns:
            df['Date Naissance'] = pd.to_datetime(df['Date Naissance'], errors='coerce')
        df.columns = [col if not col.endswith('Identification') else 'Numero Identification' for col in df.columns]
        
        if df.columns[0] != 'Telephone Origine' or df.columns[1] != 'Telephone Destination':
            df.rename(columns={
                df.columns[0]: 'Telephone Origine',
                df.columns[1]: 'Telephone Destination'
            }, inplace=True)
        
        if pd.api.types.is_integer_dtype(df['Telephone Origine']):
            df['Telephone Origine'] = '0' + df['Telephone Origine'].astype(str).str.strip()
        if pd.api.types.is_integer_dtype(df['Telephone Destination']):
            df['Telephone Destination'] = '0' + df['Telephone Destination'].astype(str).str.strip()
        
        df['Telephone Origine'] = df['Telephone Origine'].apply(transform_number)
        df['Telephone Destination'] = df['Telephone Destination'].apply(transform_number)
    
        if 'Secondes Reelles' in df.columns:
            df['Secondes Reelles'] = df['Secondes Reelles'].astype(str).str.replace(',', '.').astype(float)
        if 'Cgi' in df.columns:
            df['Cgi'] = df['Cgi'].astype(str).str.replace(r'^604000', '60400', regex=True)
        return df
    
    # Charger les données de localisation
    @st.cache_data
    def load_location_data(file):
        location_df = pd.read_excel(file, dtype={'Cells': str})
        location_df = location_df.drop_duplicates(subset='Cells')
        return location_df
    
    # Titre de l'application
    st.title("Réquisition des appels et SMS")   
    
    # Téléchargement du fichier num.txt
    st.subheader("1️⃣ Charger le fichier des numéros (num.txt)")
    num_file = st.file_uploader("Charger le fichier num.txt", type='txt')
    if num_file:
        numeros_list = num_file.read().decode('latin1').strip().split(';')
        numeros_list = [transform_number(numero) for numero in numeros_list]
        numeros_df = pd.DataFrame(numeros_list, columns=['numeros'])
        with st.expander("📂 Afficher le contenu du fichier num.txt"):
            st.write("Numéros chargés :", numeros_df)
    
    # Téléchargement des autres fichiers TXT
    st.subheader("2️⃣ Charger les autres fichiers de données (Appels/SMS)")
    other_files = st.file_uploader("Charger les autres fichiers TXT", accept_multiple_files=True, type='txt')
    dataframes = {}
    if other_files:
        with st.expander("📂 Afficher le contenu des fichiers chargés"):
            for file in other_files:
                file_key = file.name.split('.')[0]
                dataframes[file_key] = load_and_clean_data(file)
                st.write(f"Contenu de {file_key} :", dataframes[file_key])
    
    # Téléchargement du fichier de localisation
    st.subheader("3️⃣ Charger le fichier de localisation (format .xlsx)")
    location_file = st.file_uploader("Charger le fichier de localisation", type='xlsx')
    location_df = None
    if location_file:
        location_df = load_location_data(location_file)
        st.write("Détails de localisation chargés :", location_df.head())
    
    # Bouton pour exécuter le script
    if st.button("🚀 Lancer l'analyse maintenant") and num_file and other_files:
        with st.spinner('🔍 Analyse en cours...'):
            start_time = time.time()
            
            # Liste pour stocker les résultats
            results = []     

            def search_in_df(df, file_name, has_duration=True):
                for numero in numeros_df['numeros']:
                    found = df[(df['Telephone Origine'] == numero) | (df['Telephone Destination'] == numero)]
                    
                    for _, row in found.iterrows():
                        Type = 'Émis' if file_name in ['s_c', 's', 'sms_e'] else 'Reçu'
                        Type_comm = 'SMS' if file_name.lower().startswith('sms') else 'Voix' if file_name != 'interco' or float(row['Secondes Reelles']) != 0 else 'SMS'
                                  
                        results.append({
                            'Type': Type,
                            'Type comm': Type_comm,
                            'Appelant': row['Telephone Origine'],
                            'Appelé': row['Telephone Destination'],
                            'Date / Heure':  row.iloc[2],
                            'Durée': row['Secondes Reelles'] if has_duration else None,
                            'Nom': row.get('Nom', None),
                            'CIN': row.get('Numero Identification', None),
                            'Date Naissance': row.get('Date Naissance', None),
                            'Adresse': row.get('Adresse', None),
                            'IMEI': row.get('IMEI', None),
                            'Cell ID': row.get('Cgi', None),
                            
                        })

            if 's_c' in dataframes: search_in_df(dataframes['s_c'], 's_c')
            if 's' in dataframes: search_in_df(dataframes['s'], 's')
            if 'interco' in dataframes: search_in_df(dataframes['interco'], 'interco')
            if 'sms_e' in dataframes: search_in_df(dataframes['sms_e'], 'sms_e', has_duration=False)
            if 'sms_r' in dataframes: search_in_df(dataframes['sms_r'], 'sms_r', has_duration=False)
            if 'e_c' in dataframes: search_in_df(dataframes['e_c'], 'e_c')
            if 'e_p' in dataframes: search_in_df(dataframes['e_p'], 'e_p')

            # Création du DataFrame de résultats
            results_df = pd.DataFrame(results)
            results_df = results_df.drop_duplicates()
            results_df = results_df.replace("#EMPTY", "") ############################################################

            
            # Filtrer et supprimer les numéros commençant par "06576" ou dans la plage "0663977000 - 0663978000"
            results_df = results_df[~results_df['Appelé'].str.startswith('06576')]  # Exclure les numéros commençant par "06576"
            results_df = results_df[~(results_df['Appelé'].str.startswith('06577') & (results_df['Appelé'].str.len() > 10))]
            results_df = results_df[~results_df['Appelé'].isin(['0663977000', '0663978000', '0771086627'])]  # Exclure les numéros 
            results_df = results_df[~results_df['Appelant'].isin(['0346', '0600000001', '0771086627'])]  # Exclure les numéros 
            
            # Exclure les lignes où 'Appelant' ou 'Appelé' contient une lettre
            results_df = results_df[~results_df['Appelant'].str.contains(r'[a-zA-Z]', na=False)]
            results_df = results_df[~results_df['Appelé'].str.contains(r'[a-zA-Z]', na=False)]

    
            # Fusion avec les détails de localisation
            results_df = results_df.merge(location_df, left_on='Cell ID', right_on='Cells', how='left')
            results_df.drop(columns='Cells', inplace=True, errors='ignore')

            # Sauvegarde des résultats
            output_file = f'Canevas_{current_time}.xlsx'
            results_df.to_excel(output_file, index=False)

            # Temps d'exécution
            end_time = time.time()
            execution_time = end_time - start_time
            st.success(f"Analyse terminée en {execution_time:.2f} secondes")
            
            # Aperçu des résultats
            st.subheader("📋 Aperçu des résultats")
            st.dataframe(results_df.head(20))

            # Lien de téléchargement
            with open(output_file, "rb") as f:
                st.download_button(
                    label="💾 Télécharger le fichier Excel",
                    data=f,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

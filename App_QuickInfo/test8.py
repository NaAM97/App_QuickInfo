import pandas as pd
import streamlit as st
import time
import datetime

def main():

    # Titre de l'application
    st.title("Recherche d'IMEI dans les données d'appels")
    # Créer le nom du fichier avec la date et l'heure
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Téléchargement des fichiers
    fichier_donnees = st.file_uploader("Téléversez le fichier de données d'appels (.txt)", type="txt")
    fichier_imei = st.file_uploader("Téléversez le fichier de liste d'IMEI (.txt)", type="txt")
    
    # Traitement lorsque les deux fichiers sont téléchargés
    if fichier_donnees is not None and fichier_imei is not None:
        start_time = time.time()  # Temps de début de l'exécution
    
        # Lecture du fichier de données d'appels
        donnees_df = pd.read_csv(fichier_donnees, sep='\t', names=['Telephone Origine', 'Telephone Destination', 'Date Appel', 'Secondes Reelles', 'IMEI'],dtype={'IMEI':str})
               
        # Lecture du fichier d'IMEI
        imei_contenu = fichier_imei.read().decode("latin1").strip()
        imei_liste = [imei.strip() for imei in imei_contenu.split(';') if imei.strip()]
    
        # Filtrage des données pour récupérer les lignes correspondant aux IMEI
        resultats_df = donnees_df[donnees_df['IMEI'].isin(imei_liste)]
    

    
        # Bouton de téléchargement
        if not resultats_df.empty:
            # Enregistrement des résultats dans un fichier Excel en mémoire
           
            output_file = f'IMEI_search_{current_time}.xlsx'
            resultats_df.to_excel(output_file, index=False)
            
            # Temps d'exécution
            end_time = time.time()
            execution_time = end_time - start_time
            st.success(f"Analyse terminée en {execution_time:.2f} secondes")
            
            # Aperçu des résultats
            st.subheader("📋 Aperçu des résultats")
            st.dataframe(resultats_df.head(20))
            
            
            # Lien de téléchargement
            with open(output_file, "rb") as f:
                st.download_button(
                    label="💾 Télécharger le fichier Excel",
                    data=f,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

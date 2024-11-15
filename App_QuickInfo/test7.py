import pandas as pd
import streamlit as st
import datetime

def main():
    
    # Interface de l'application
    st.title(" Séparation par numéro")
    # Créer le nom du fichier avec la date et l'heure
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Fonction pour transformer les numéros
    def transform_number(number):
        """Appliquer les règles de transformation des numéros."""
        if number.startswith('00'):
            return  '0' + number[2:]  # Remplacer '00' par '0'
        elif number.startswith('0'):
            return number  # Aucun changement si le numéro commence par 0
        elif number.startswith('212'):
            return '0' + number[3:]  # Remplacer '212' par '0'

        else:
            return '0' + number  # Ajouter un 0 si le numéro ne commence ni par 0 ni par 212 ni par 00
    
    
    # Téléchargement du fichier Excel contenant les détails
    st.subheader("1️⃣ Charger le fichier Excel contenant les détails des appels et SMS")
    excel_file = st.file_uploader("Charger le fichier Excel", type="xlsx")
    
    # Téléchargement du fichier texte contenant les numéros
    st.subheader("2️⃣ Charger le fichier texte contenant les numéros")
    num_file = st.file_uploader("Charger le fichier des numéros (num.txt)", type="txt")
    
    # Vérification que les deux fichiers sont téléchargés
    if excel_file and num_file:
        # Lecture du fichier Excel
        try:
            details_df = pd.read_excel(excel_file, dtype={'Appelant': str, 'Appelé': str})
            # Afficher l'aperçu du fichier Excel chargé
            st.write("Aperçu du fichier Excel chargé :")
            st.write(details_df.head())
    
            # Afficher le nombre de lignes dans le fichier Excel initial
            st.subheader(f"Nombre total de lignes dans le fichier Excel : {len(details_df)}")
            
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
        # Vérification de la colonne 'Appelant' et 'Appelé'
        if 'Appelant' not in details_df.columns or 'Appelé' not in details_df.columns:
            st.error("Les colonnes 'Appelant' ou 'Appelé' ne sont pas présentes dans le fichier Excel.")
        else:
            # Vérification de la colonne 'Type'
            if 'Type' not in details_df.columns:
                st.error("La colonne 'Type' n'est pas présente dans le fichier Excel.")
            else:
                # Si le type est "Reçu", échanger les colonnes 'Appelant' et 'Appelé'
                details_df.loc[details_df['Type'] == 'Reçu', ['Appelant', 'Appelé']] = \
                    details_df.loc[details_df['Type'] == 'Reçu', ['Appelé', 'Appelant']].values
            
            # Appliquer les règles de transformation des numéros pour les numéros dans le fichier texte
            numeros_list = num_file.read().decode('latin1').strip().split(';')
            
            # Appliquer la fonction transform_number sur chaque numéro dans la liste
            numeros_list = [transform_number(numero) for numero in numeros_list]
        
            # Afficher le nombre total de numéros dans le fichier texte après transformation
            st.subheader(f"Nombre total de numéros : {len(numeros_list)}")
            # Appliquer la transformation sur les colonnes 'Appelant' et 'Appelé' dans le DataFrame
            details_df['Appelant'] = details_df['Appelant'].apply(transform_number)
            details_df['Appelé'] = details_df['Appelé'].apply(transform_number)

    
            # Initialisation du writer pour créer un fichier Excel avec une feuille par numéro
            output_file = f'Details_par_numero_{current_time}.xlsx'
            line_counts = []  # Liste pour stocker le nombre de lignes par numéro
            non_found_numbers = []  # Liste pour stocker les numéros non trouvés
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                for numero in numeros_list:
                    # Filtrer les données pour chaque numéro
                    numero_df = details_df[(details_df['Appelant'] == numero) | (details_df['Appelé'] == numero)]
    
                    # Si des données sont trouvées, les écrire dans une feuille dédiée
                    if not numero_df.empty:
                        numero_df.to_excel(writer, sheet_name=str(numero), index=False)
                        line_counts.append({"Numéro": numero, "Nombre d'opérations": str(len(numero_df))})  # Ajouter aux résultats
                    else:
                        non_found_numbers.append(numero)  # Ajouter le numéro à la liste des non trouvés
    
            # Convertir les résultats en DataFrame pour un affichage sous forme de tableau
            line_counts_df = pd.DataFrame(line_counts).sort_values(by="Nombre d'opérations", ascending=False, ignore_index=True)
    
            # Afficher le tableau avec le nombre d'opérations par numéro
            st.subheader("Nombre d'opérations par numéro :")
            st.write(line_counts_df)
            
            # Calculer la somme totale des opérations
            total_operations = line_counts_df["Nombre d'opérations"].astype(int).sum()
            
            # Afficher la somme totale des opérations
            st.subheader(f"Total des opérations : {total_operations}")
    
            # Afficher la liste des numéros pour lesquels aucune donnée n'a été trouvée
            if non_found_numbers:
                st.subheader("Numéros non trouvés :")
                st.write(non_found_numbers)
    
            # Bouton pour télécharger le fichier Excel généré
            st.subheader("Télécharger le fichier Excel avec les détails par numéro")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="💾 Télécharger le fichier Excel",
                    data=f,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("Veuillez télécharger les deux fichiers pour lancer l'analyse.")

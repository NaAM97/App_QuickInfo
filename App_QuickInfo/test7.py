import pandas as pd
import streamlit as st
import datetime

def main():
    # Interface de l'application
    st.title("Séparation par numéro")
    # Créer le nom du fichier avec la date et l'heure
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
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
    
    # Téléchargement des fichiers
    st.subheader("1️⃣ Charger le fichier Excel contenant les détails des appels et SMS")
    excel_file = st.file_uploader("Charger le fichier Excel", type="xlsx")
    
    st.subheader("2️⃣ Charger le fichier texte contenant les numéros")
    num_file = st.file_uploader("Charger le fichier des numéros (num.txt)", type="txt")
    
    if excel_file and num_file:
        try:
            details_df = pd.read_excel(excel_file, dtype={'Appelant': str, 'Appelé': str, 'Type': str})
            st.write("Aperçu du fichier Excel chargé :")
            st.write(details_df.head())
            st.subheader(f"Nombre total de lignes dans le fichier Excel : {len(details_df)}")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
            return
        
        if {'Appelant', 'Appelé', 'Type'}.issubset(details_df.columns):
            numeros_list = num_file.read().decode('latin1').strip().split(';')
            numeros_list = [transform_number(numero) for numero in numeros_list]
            st.subheader(f"Nombre total de numéros dans le fichier texte : {len(numeros_list)}")
            
            # Appliquer la transformation sur les colonnes
            details_df['Appelant'] = details_df['Appelant'].apply(transform_number)
            details_df['Appelé'] = details_df['Appelé'].apply(transform_number)
            
            # Initialisation des résultats
            output_file = f'Details_par_numero_{current_time}.xlsx'
            line_counts = []
            non_found_numbers = []
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                for numero in numeros_list:
                    # Filtrer les données selon le type
                    if details_df['Type'] == 'Émis' :
                        numero_df=details_df[details_df['Appelant'] == numero]
                    else :
                        numero_df=details_df[details_df['Appelant'] == numero)]
                                       
                    if not numero_df.empty:
                        numero_df.to_excel(writer, sheet_name=str(numero), index=False)
                        line_counts.append({"Numéro": numero, "Nombre d'opérations": len(numero_df)})
                    else:
                        non_found_numbers.append(numero)
            
            # Afficher les résultats
            line_counts_df = pd.DataFrame(line_counts).sort_values(by="Nombre d'opérations", ascending=False, ignore_index=True)
            st.subheader("Nombre d'opérations par numéro :")
            st.write(line_counts_df)
            
            total_operations = line_counts_df["Nombre d'opérations"].sum()
            st.subheader(f"Total des opérations : {total_operations}")
            
            if non_found_numbers:
                st.subheader("Numéros non trouvés :")
                st.write(non_found_numbers)
            
            # Bouton pour télécharger le fichier
            st.subheader("Télécharger le fichier Excel avec les détails par numéro")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="💾 Télécharger le fichier Excel",
                    data=f,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("Les colonnes 'Appelant', 'Appelé', ou 'Type' sont absentes du fichier Excel.")
    else:
        st.info("Veuillez télécharger les deux fichiers pour lancer l'analyse.")

if __name__ == "__main__":
    main()

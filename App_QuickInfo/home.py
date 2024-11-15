import streamlit as st


st.image("logo.png", width=300)
# Titre de la page d'accueil
st.title("Bienvenue sur l'application QuickInfo ")

# Menu principal avec trois options
option = st.selectbox("Choisissez le script à exécuter :", ("Accueil", "Réquisition par numéros", "Séparation de données par numéro", "Réquisition par IMEI"))

# Charger les scripts selon l'option sélectionnée
if option == "Accueil":
    st.write("Bienvenue ! Sélectionnez un script pour commencer.")
elif option == "Réquisition par numéros":
    # Appel du script 1
    import test666
    test666.main()  # Lancer la fonction main() de script1
elif option == "Séparation de données par numéro":
    # Appel du script 2
    import test7
    test7.main()  # Lancer la fonction main() de script2
elif option == "Réquisition par IMEI":
    # Appel du script 3
    import test8
    test8.main()  # Lancer la fonction main() de script3

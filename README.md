# Système de Gestion des Présences avec Reconnaissance Faciale

Une application de gestion des présences utilisant la reconnaissance faciale, développée avec Python, Streamlit et OpenCV.

## 📋 Prérequis

- Python 3.8 ou plus récent
- Une webcam fonctionnelle
- Git

## 🎥 Démonstration

https://github.com/Lmati01/Presence_Management/assets/test_video.mp4

Regardez la vidéo de démonstration ci-dessus pour voir l'application en action !

## 🚀 Installation

1. Clonez le repository :
```bash
git clone https://github.com/Lmati01/Presence_Management.git
cd Presence_Management
```

2. Créez et activez l'environnement virtuel :
```bash
# Sur Linux/Mac
python -m venv dlib_venv
source dlib_venv/bin/activate

# Sur Windows
python -m venv dlib_venv
.\dlib_venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install streamlit opencv-python face-recognition numpy pandas
```

## 💻 Utilisation

1. Créez un dossier `ImagesAttendance` à la racine du projet (s'il n'existe pas déjà)

2. Lancez l'application :
```bash
streamlit run app.py
```

3. L'application sera accessible dans votre navigateur à l'adresse : http://localhost:8501

## 🎯 Fonctionnalités

- **Ajouter un Étudiant** : Ajoutez un nouvel étudiant avec sa photo (upload ou capture webcam)
- **Liste des Étudiants** : Visualisez tous les étudiants enregistrés
- **Prendre Présence** : Marquez les présences via reconnaissance faciale
- **Voir Présences** : Consultez l'historique des présences par date

## 📁 Structure du Projet

```
Presence_Management/
│
├── app.py                 # Application principale
├── ImagesAttendance/     # Dossier des photos des étudiants
├── Assets/               # Ressources du projet
└── daily_attendance.csv  # Fichier des présences
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📝 License

Ce projet est sous licence MIT.

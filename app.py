import streamlit as st
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import pandas as pd
import time
import base64

# Configuration de la page
st.set_page_config(page_title="Système de Présence", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        padding: 0;
        min-width: 250px !important;
        box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
    }
    
    .sidebar-title {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        padding: 1.5rem;
        text-align: center;
        background: rgba(255, 255, 255, 0.1);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .menu-item {
        display: block;
        padding: 0.75rem 1.5rem;
        text-decoration: none;
        color: #93c5fd !important;
        transition: all 0.2s ease;
        border-left: 3px solid transparent;
        margin: 0.25rem 0;
        cursor: pointer;
    }
    
    .menu-item:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff !important;
        border-left: 3px solid #60a5fa;
    }
    
    .menu-item.active {
        background: rgba(255, 255, 255, 0.15);
        color: #ffffff !important;
        border-left: 3px solid #3b82f6;
        font-weight: 500;
    }
    
    /* Cacher les éléments de Streamlit par défaut */
    #MainMenu, footer, header {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la session state
if 'page' not in st.session_state:
    st.session_state.page = 'Accueil'
if 'camera' not in st.session_state:
    st.session_state.camera = None

def load_known_faces():
    path = 'ImagesAttendance'
    images = []
    classNames = []
    myList = os.listdir(path)
    
    for cls in myList:
        curImg = cv2.imread(f'{path}/{cls}')
        images.append(curImg)
        classNames.append(os.path.splitext(cls)[0])
    return images, classNames

def findEncodings(images):
    encodingsList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodingsList.append(encode)
    return encodingsList

def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')

def initialize_attendance_file():
    if not os.path.exists('daily_attendance.csv'):
        # Create file with headers
        with open('daily_attendance.csv', 'w') as f:
            f.write('Date,Name,Status,Time\n')

def mark_all_students_absent():
    current_date = get_current_date()
    _, students = load_known_faces()
    
    # Read existing attendance to avoid duplicates
    existing_records = set()
    if os.path.exists('daily_attendance.csv'):
        df = pd.read_csv('daily_attendance.csv')
        # Normaliser les noms dans les enregistrements existants
        df['Name'] = df['Name'].str.title()
        existing_records = set(zip(df['Date'], df['Name']))
    
    # Mark absent for students not already marked today
    with open('daily_attendance.csv', 'a') as f:
        for student in students:
            # Normaliser le nom de l'étudiant
            student = student.title()
            if (current_date, student) not in existing_records:
                f.write(f'{current_date},{student},Absent,\n')

def markAttendance(name):
    current_date = get_current_date()
    current_time = datetime.now().strftime('%H:%M:%S')
    
    # Normaliser le nom
    name = name.title()
    
    # Read the CSV file
    if os.path.exists('daily_attendance.csv'):
        df = pd.read_csv('daily_attendance.csv')
        # Normaliser tous les noms dans le DataFrame
        df['Name'] = df['Name'].str.title()
        # Update the status for the current student on the current date
        mask = (df['Date'] == current_date) & (df['Name'] == name)
        if len(df[mask]) > 0:
            df.loc[mask, 'Status'] = 'Present'
            df.loc[mask, 'Time'] = current_time
            df.to_csv('daily_attendance.csv', index=False)
        else:
            # Add new record if not exists
            with open('daily_attendance.csv', 'a') as f:
                f.write(f'{current_date},{name},Present,{current_time}\n')
    else:
        # Create new file if doesn't exist
        initialize_attendance_file()
        with open('daily_attendance.csv', 'a') as f:
            f.write(f'{current_date},{name},Present,{current_time}\n')

def init_camera():
    if st.session_state.camera is None:
        st.session_state.camera = cv2.VideoCapture(0)
        time.sleep(0.5)  # Wait for camera to initialize
    return st.session_state.camera

def release_camera():
    if st.session_state.camera is not None:
        st.session_state.camera.release()
        st.session_state.camera = None

def main():
    # Initialize attendance system
    initialize_attendance_file()
    mark_all_students_absent()  # Mark all students absent at the start
    
    # Sidebar avec navigation
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Gestion des Présences</div>', unsafe_allow_html=True)
        
        # Navigation avec des boutons simples
        menu_items = {
            "Accueil": "Accueil",
            "Prendre Présence": "Prendre Présence",
            "Voir Présences": "Voir Présences",
            "Liste des Étudiants": "Liste des Étudiants",
            "Ajouter Étudiant": "Ajouter Étudiant"
        }

        # Style pour cacher les éléments de bouton par défaut
        st.markdown("""
            <style>
                .stButton button {
                    width: 100%;
                    padding: 0.75rem 1.5rem;
                    background: none;
                    border: none;
                    color: #93c5fd;
                    text-align: left;
                    font-size: 0.875rem;
                    transition: all 0.2s ease;
                    border-left: 3px solid transparent;
                    margin: 0.25rem 0;
                    cursor: pointer;
                }
                
                .stButton button:hover {
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                    border-left: 3px solid #60a5fa;
                }
                
                .stButton button:active, .stButton button:focus {
                    background: rgba(255, 255, 255, 0.15);
                    color: white;
                    border-left: 3px solid #3b82f6;
                    font-weight: 500;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Créer les boutons de navigation
        for label, page in menu_items.items():
            if st.button(label, key=f"nav_{page}"):
                if st.session_state.page != page:
                    release_camera()
                st.session_state.page = page
                st.rerun()

    # Contenu principal
    if st.session_state.page == "Accueil":
        release_camera()  # Ensure camera is released on home page
        st.title("Système de Gestion des Présences")
        st.subheader("Bienvenue dans le Système de Gestion des Présences")
        st.write("Ce système utilise la reconnaissance faciale pour gérer les présences.")
        st.write("Utilisez le menu à gauche pour naviguer dans l'application.")
        
    elif st.session_state.page == "Prendre Présence":
        st.title("Prendre Présence")
        
        # Style personnalisé pour les boutons de présence
        st.markdown("""
            <style>
                div[data-testid="column"]:nth-child(1) button,
                div[data-testid="column"]:nth-child(2) button {
                    background-color: #38bdf8 !important;
                    color: white !important;
                    border: none !important;
                    padding: 0.5rem 1rem !important;
                    border-radius: 0.375rem !important;
                    font-size: 0.875rem !important;
                    font-weight: 500 !important;
                    width: auto !important;
                    margin: 0 !important;
                }
                
                div[data-testid="column"] button:hover {
                    background-color: #0ea5e9 !important;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        images, classNames = load_known_faces()
        encodeListKnown = findEncodings(images)
        
        FRAME_WINDOW = st.image([])
        camera = init_camera()
        
        # Colonnes pour les boutons avec espacement
        col1, space, col2 = st.columns([1, 3, 1])
        with col1:
            stop = st.button("Arrêter", use_container_width=True)
        with col2:
            mark_presence = st.button("Marquer Présence", use_container_width=True)
        
        current_name = None  # Variable to store current detected name
        
        if camera is not None and camera.isOpened():
            while not stop:
                ret, frame = camera.read()
                if ret:
                    imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
                    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                    
                    facesCurFrame = face_recognition.face_locations(imgS)
                    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
                    
                    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                        
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                        
                        if len(faceDis) > 0:
                            matchIndex = np.argmin(faceDis)
                            if matches[matchIndex]:
                                name = classNames[matchIndex].upper()
                                current_name = name
                                color = (0, 255, 0)
                            else:
                                name = "INCONNU"
                                current_name = None
                                color = (0, 0, 255)
                                
                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                            cv2.rectangle(frame, (x1, y2-35), (x2, y2), color, cv2.FILLED)
                            cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    FRAME_WINDOW.image(frame)
                    
                    if mark_presence and current_name and current_name != "INCONNU":
                        markAttendance(current_name)
                        st.success(f"Présence marquée pour {current_name}")
                        st.balloons()
                        break
                else:
                    st.error("Erreur lors de la capture vidéo")
                    break
        else:
            st.error("Impossible d'accéder à la webcam")
        
        if stop:
            release_camera()
            
    elif st.session_state.page == "Liste des Étudiants":
        st.title("Liste des Étudiants")
        
        # Get list of students from ImagesAttendance directory
        students = []
        if os.path.exists('ImagesAttendance'):
            for img_file in os.listdir('ImagesAttendance'):
                if img_file.endswith(('.jpg', '.jpeg', '.png')):
                    name = os.path.splitext(img_file)[0]
                    img_path = os.path.join('ImagesAttendance', img_file)
                    students.append({'name': name, 'image_path': img_path})
        
        if students:
            # CSS pour les cartes d'étudiants
            st.markdown("""
                <style>
                    .student-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                        gap: 1rem;
                        padding: 1rem;
                    }
                    .student-card {
                        background: white;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                        transition: transform 0.2s;
                        position: relative;
                    }
                    .student-card:hover {
                        transform: translateY(-5px);
                    }
                    .student-image {
                        width: 100%;
                        height: 200px;
                        object-fit: cover;
                    }
                    .student-name {
                        padding: 1rem;
                        text-align: center;
                        font-weight: bold;
                        color: #1F2937;
                    }
                    .card-buttons {
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        display: flex;
                        gap: 5px;
                        opacity: 0;
                        transition: opacity 0.2s;
                    }
                    .student-card:hover .card-buttons {
                        opacity: 1;
                    }
                    .card-button {
                        width: 30px;
                        height: 30px;
                        border-radius: 50%;
                        border: none;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        cursor: pointer;
                        transition: transform 0.2s;
                        color: white;
                        font-size: 16px;
                    }
                    .edit-button {
                        background: rgba(59, 130, 246, 0.9);
                    }
                    .delete-button {
                        background: rgba(239, 68, 68, 0.9);
                    }
                    .card-button:hover {
                        transform: scale(1.1);
                    }
                    .edit-button:hover {
                        background: rgb(59, 130, 246);
                    }
                    .delete-button:hover {
                        background: rgb(239, 68, 68);
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Créer la grille d'étudiants
            cols = st.columns(4)
            for idx, student in enumerate(students):
                col = cols[idx % 4]
                with col:
                    # Afficher la carte avec les boutons
                    st.markdown(f"""
                        <div class="student-card">
                            <img src="data:image/jpeg;base64,{get_image_base64(student['image_path'])}" 
                                 class="student-image" alt="{student['name']}">
                            <div class="student-name">{student['name'].replace('_', ' ')}</div>
                            <div class="card-buttons">
                                <button class="card-button edit-button" onclick="document.getElementById('edit_{student['name']}').click()">✎</button>
                                <button class="card-button delete-button" onclick="delete_student('{student['name']}')">×</button>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Bouton caché pour la suppression
                    st.markdown(f"""
                        <div style="display: none;">
                            <button id="delete_{student['name']}" onclick="delete_student('{student['name']}')"></button>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Aucun étudiant enregistré pour le moment.")
    
    elif st.session_state.page == "Voir Présences":
        st.title("Historique des Présences")
        if os.path.exists('daily_attendance.csv'):
            df = pd.read_csv('daily_attendance.csv')
            
            # Add date filter
            dates = sorted(df['Date'].unique(), reverse=True)
            selected_date = st.selectbox("Sélectionner une date", dates)
            
            # Filter by selected date
            filtered_df = df[df['Date'] == selected_date].copy()
            
            # Add color coding to status
            def color_status(status):
                if status == 'Present':
                    return 'background-color: #4ade80; color: white'  # Green
                else:
                    return 'background-color: #f87171; color: white'  # Red
            
            # Style the dataframe
            styled_df = filtered_df.style.applymap(
                color_status, subset=['Status']
            )
            
            st.dataframe(
                styled_df,
                column_config={
                    "Date": "Date",
                    "Name": "Nom",
                    "Status": "Statut",
                    "Time": "Heure d'arrivée"
                },
                hide_index=True
            )
        else:
            st.warning("Aucune présence enregistrée pour le moment.")
            
    elif st.session_state.page == "Ajouter Étudiant":
        st.title("Ajouter un Étudiant")
        
        student_name = st.text_input("Nom de l'étudiant")
        
        # Option pour choisir la méthode d'ajout de photo
        photo_method = st.radio("Choisir la méthode d'ajout de photo", 
                              ["Uploader une photo", "Prendre une photo avec la webcam"])
        
        if photo_method == "Uploader une photo":
            release_camera()  # Release camera when switching to upload
            
            photo = st.file_uploader("Photo de l'étudiant", type=['jpg', 'jpeg', 'png'])
            
            if st.button("Ajouter") and student_name and photo:
                try:
                    os.makedirs('ImagesAttendance', exist_ok=True)
                    with open(os.path.join('ImagesAttendance', f'{student_name}.jpg'), 'wb') as f:
                        f.write(photo.getbuffer())
                    st.success(f"Étudiant {student_name} ajouté avec succès!")
                except Exception as e:
                    st.error(f"Erreur lors de l'ajout: {str(e)}")
                    
        else:  # Prendre une photo avec la webcam
            st.write("Webcam active. Positionnez-vous et cliquez sur 'Capturer' quand vous êtes prêt.")
            
            col1, col2 = st.columns(2)
            capture = col1.button("Capturer")
            stop = col2.button("Arrêter")
            
            FRAME_WINDOW = st.image([])
            camera = init_camera()
            
            if camera is not None and camera.isOpened():
                try:
                    while not stop:
                        ret, frame = camera.read()
                        if ret:
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            FRAME_WINDOW.image(frame_rgb)
                            
                            if capture:
                                if student_name:
                                    os.makedirs('ImagesAttendance', exist_ok=True)
                                    save_path = os.path.join('ImagesAttendance', f'{student_name}.jpg')
                                    success = cv2.imwrite(save_path, frame)
                                    
                                    if success:
                                        st.success(f"Photo capturée et étudiant {student_name} ajouté avec succès!")
                                        st.balloons()
                                    else:
                                        st.error("Erreur lors de la sauvegarde de l'image")
                                    break
                                else:
                                    st.warning("Veuillez d'abord entrer le nom de l'étudiant")
                                    break
                        else:
                            st.error("Erreur lors de la capture vidéo")
                            break
                except Exception as e:
                    st.error(f"Erreur avec la webcam: {str(e)}")
                finally:
                    if stop:
                        release_camera()
            else:
                st.error("Impossible d'accéder à la webcam")

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def delete_student(student_name):
    # Supprimer la photo
    image_path = os.path.join('ImagesAttendance', f'{student_name}.jpg')
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # Supprimer les enregistrements de présence
    if os.path.exists('daily_attendance.csv'):
        df = pd.read_csv('daily_attendance.csv')
        df = df[df['Name'] != student_name]
        df.to_csv('daily_attendance.csv', index=False)

def rename_student(old_name, new_name):
    # Renommer la photo
    old_path = os.path.join('ImagesAttendance', f'{old_name}.jpg')
    new_path = os.path.join('ImagesAttendance', f'{new_name}.jpg')
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
    
    # Mettre à jour les enregistrements de présence
    if os.path.exists('daily_attendance.csv'):
        df = pd.read_csv('daily_attendance.csv')
        df.loc[df['Name'] == old_name, 'Name'] = new_name
        df.to_csv('daily_attendance.csv', index=False)

if __name__ == '__main__':
    try:
        main()
    finally:
        # Ensure camera is always released when the app stops
        if 'camera' in st.session_state and st.session_state.camera is not None:
            st.session_state.camera.release()
            st.session_state.camera = None 
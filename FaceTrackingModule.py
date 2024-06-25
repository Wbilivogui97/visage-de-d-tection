import cv2
import mediapipe as mp
import time

# Initialisation de la capture vidéo
cap = cv2.VideoCapture(0) 

# Initialisation de la variable pour le temps précédent
pTime = 0

# Initialisation des outils de dessin de MediaPipe
mpDraw = mp.solutions.drawing_utils
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(max_num_faces=2)
drawSpec = mpDraw.DrawingSpec(thickness=2, circle_radius=2)

# Définition de la largeur et de la hauteur du cadre vidéo
frameWidth = 960
frameHeight = 800
cap.set(3, frameWidth)
cap.set(4, frameHeight)

# Définition de la luminosité de la vidéo (facultatif)
cap.set(10, 150)

while True:
    # Lecture d'une frame de la vidéo
    success, img = cap.read()
    
    # Vérification si la lecture de la frame est réussie
    if not success:
        print("La lecture de la frame a échoué.")
        break
    
    # Conversion de l'image en RGB (MediaPipe travaille avec des images RGB)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Traitement du maillage du visage
    results = faceMesh.process(imgRGB)
    
    # Vérification si des visages ont été détectés
    if results.multi_face_landmarks:
        for faceLms in results.multi_face_landmarks:
            # Dessin du maillage du visage
            mpDraw.draw_landmarks(img, faceLms, mpFaceMesh.FACEMESH_CONTOURS, drawSpec, drawSpec)
    
    # Calcul du FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    # Affichage du FPS
    cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    
    # Affichage de l'image
    cv2.imshow("Image", img)
    
    # Attente de l'appui sur la touche 'Esc' pour quitter
    if cv2.waitKey(1) == 27:
        break

# Libération des ressources de la capture vidéo
cap.release()






import cv2
import mediapipe as mp
import time
import os

from database_setup import criar_banco_de_dados
from core_functions import verificar_pessoa

criar_banco_de_dados()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rostos_dir = os.path.join(BASE_DIR, 'rostos_cadastrados')
capturas_dir = os.path.join(BASE_DIR, 'capturas_log')
if not os.path.exists(rostos_dir):
    os.makedirs(rostos_dir)
if not os.path.exists(capturas_dir):
    os.makedirs(capturas_dir)

video_capture = cv2.VideoCapture(0) 

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

INTERVALO_VERIFICACAO = 3.0
ultimo_tempo_verificacao = 0

print("\n[INFO] Sistema de reconhecimento facial contínuo iniciado.")
print("Pressione 'Q' na janela da câmera para sair.")

# --- LOOP PRINCIPAL ---
with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.6) as face_detection:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERRO] Não foi possível capturar frame da câmera. Tentando novamente...")
            time.sleep(2)
            continue

        # Converte a imagem para RGB para o MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        rosto_detectado_na_frame = bool(results.detections)
        if rosto_detectado_na_frame:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)

        cv2.imshow('Sistema de Reconhecimento Facial - Pressione Q para Sair', frame)

        # Lógica de verificação automática com temporizador
        tempo_atual = time.time()
        if rosto_detectado_na_frame and (tempo_atual - ultimo_tempo_verificacao > INTERVALO_VERIFICACAO):
            print("\n[INFO] Rosto detectado. Iniciando verificação...")
            
            # Extrai a imagem do rosto para verificação
            detection = results.detections[0]
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(iw, x + w), min(ih, y + h)
            
            rosto_img_recortado = frame[y1:y2, x1:x2]

            if rosto_img_recortado.size != 0:
                verificar_pessoa(rosto_img_recortado)
            
            # Atualiza o tempo da última verificação
            ultimo_tempo_verificacao = tempo_atual

        # Verifica se a tecla 'q' foi pressionada para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# --- FINALIZAÇÃO ---
print("\n[INFO] Encerrando o sistema...")
video_capture.release()
cv2.destroyAllWindows()
print("[INFO] Sistema finalizado.")

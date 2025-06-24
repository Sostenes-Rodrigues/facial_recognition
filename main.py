import cv2
import mediapipe as mp
import sqlite3
import os
import time
from deepface import DeepFace

# diretórios e banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rostos_dir = os.path.join(BASE_DIR, 'rostos')
if not os.path.exists(rostos_dir):
    os.makedirs(rostos_dir)

db_path = os.path.join(BASE_DIR, 'database.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

# criar tabela caso n exista
c.execute('''
    CREATE TABLE IF NOT EXISTS rostos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT,
        curso TEXT,
        advertencia TEXT,
        arquivo TEXT NOT NULL
    )
''')
conn.commit()

# função para salvar uma nova pessoa
def cadastrar_pessoa(nome, categoria, curso, advertencia, imagem):
    numero = obter_proximo_numero()
    filename = os.path.join(rostos_dir, f"pessoa_{numero}.jpg")
    cv2.imwrite(filename, imagem)

    c.execute('''
        INSERT INTO rostos (nome, categoria, curso, advertencia, arquivo)
        VALUES (?, ?, ?, ?, ?)
    ''', (nome, categoria, curso, advertencia, filename))
    conn.commit()
    print(f"[INFO] {nome} cadastrado com sucesso em {filename}!")

# função para verificar pessoa
def verificar_pessoa(imagem_teste):
    c.execute("SELECT nome, categoria, curso, advertencia, arquivo FROM rostos")
    registros = c.fetchall()

    for nome, categoria, curso, advertencia, arquivo in registros:
        if not os.path.exists(arquivo):
            continue
        result = DeepFace.verify(imagem_teste, arquivo, model_name='Facenet', enforce_detection=False)
        if result['verified']:
            print(f"✅ Pessoa reconhecida: {nome}")
            print(f"Categoria: {categoria}, Curso: {curso}, Advertência: {advertencia}")
            print(f"Distância: {result['distance']:.4f}, Tempo: {result['time']:.2f}s")
            return
    print("❌ Pessoa não reconhecida no banco.")

# função para obter o próximo número de arquivo
def obter_proximo_numero():
    c.execute("SELECT MAX(id) FROM rostos")
    row = c.fetchone()
    return (row[0] or 0) + 1

# iniciar captura
CAMERA_URL = "http://192.168.18.45:8080/video" # atualmente usando o ip da câmera do meu celular
video_capture = cv2.VideoCapture(CAMERA_URL)

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

print("Pressione C para CADASTRAR, V para VERIFICAR, Q para sair.")

with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERRO] Não foi possível capturar frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)

        cv2.imshow('Reconhecimento Facial', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            # cadastro
            if results.detections:
                nome = input("Nome: ")
                categoria = input("Categoria (discente/docente/servidor): ")
                curso = input("Curso (ou N/A): ")
                advertencia = input("Advertência (ou Nenhuma): ")

                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x1 = max(0, int(bboxC.xmin * iw))
                    y1 = max(0, int(bboxC.ymin * ih))
                    x2 = min(iw, x1 + int(bboxC.width * iw))
                    y2 = min(ih, y1 + int(bboxC.height * ih))
                    rosto_img = frame[y1:y2, x1:x2]

                    cadastrar_pessoa(nome, categoria, curso, advertencia, rosto_img)
            else:
                print("[INFO] Nenhum rosto detectado para cadastro.")

        elif key == ord('v'):
            # verificação
            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x1 = max(0, int(bboxC.xmin * iw))
                    y1 = max(0, int(bboxC.ymin * ih))
                    x2 = min(iw, x1 + int(bboxC.width * iw))
                    y2 = min(ih, y1 + int(bboxC.height * ih))
                    rosto_img = frame[y1:y2, x1:x2]

                    temp_img_path = os.path.join(BASE_DIR, "temp_verificacao.jpg")
                    cv2.imwrite(temp_img_path, rosto_img)

                    verificar_pessoa(temp_img_path)
                    os.remove(temp_img_path)
            else:
                print("[INFO] Nenhum rosto detectado para verificação.")

        elif key == ord('q'):
            break

video_capture.release()
cv2.destroyAllWindows()
conn.close()

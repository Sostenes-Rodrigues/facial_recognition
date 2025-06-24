import cv2
import mediapipe as mp
import sqlite3
import os

# pega o diretório onde o script está rodando
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# cria a pasta 'rostos' dentro do diretório do script
rostos_dir = os.path.join(BASE_DIR, 'rostos')
if not os.path.exists(rostos_dir):
    os.makedirs(rostos_dir)

# caminho do banco de dados dentro da pasta do script
db_path = os.path.join(BASE_DIR, 'database.db')

# banco de dados
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS rostos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        arquivo TEXT
    )
''')
conn.commit()

# url da câmera do celular (atualmente usando o do meu celular (ph))
CAMERA_URL = "http://192.168.18.45:8080/video" # possível integração com o front-end pra configurar melhor isso?
video_capture = cv2.VideoCapture(CAMERA_URL)

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# função para contar arquivos na pasta da pessoa para continuar a numeração
def proximo_indice_pessoa(pasta_pessoa):
    arquivos = [f for f in os.listdir(pasta_pessoa) if f.endswith('.jpg')]
    indices = []
    for nome_arquivo in arquivos:
        try:
            i = int(nome_arquivo.split('_')[-1].split('.')[0])
            indices.append(i)
        except:
            pass
    return max(indices) + 1 if indices else 0

# lista para controlar as pastas das pessoas detectadas (inicialmente separando como "pessoa_1, pessoa_2..." necessário implementação com o front-end pra melhor configuração
pessoa_atual = 0
pasta_pessoa_atual = os.path.join(rostos_dir, f'Pessoa_{pessoa_atual}')
if not os.path.exists(pasta_pessoa_atual):
    os.makedirs(pasta_pessoa_atual)

contador = proximo_indice_pessoa(pasta_pessoa_atual)

with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERRO] Não foi possível capturar frame da câmera.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)

        cv2.imshow('Reconhecimento Facial', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            # fecha após apertar q
            break

        elif key == ord('s'):
            # salvar rosto detectado assim que apertar s
            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x1 = int(bboxC.xmin * iw)
                    y1 = int(bboxC.ymin * ih)
                    w = int(bboxC.width * iw)
                    h = int(bboxC.height * ih)

                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(iw, x1 + w)
                    y2 = min(ih, y1 + h)

                    rosto = frame[y1:y2, x1:x2]
                    filename = os.path.join(pasta_pessoa_atual, f'rosto_{contador}.jpg')
                    cv2.imwrite(filename, rosto)

                    # salva no banco
                    c.execute("INSERT INTO rostos (nome, arquivo) VALUES (?, ?)", (f'Pessoa_{pessoa_atual}', filename))
                    conn.commit()

                    print(f"[INFO] Rosto salvo: {filename}")

                    contador += 1

print("Finalizando...")
video_capture.release()
cv2.destroyAllWindows()
conn.close()

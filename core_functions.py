import sqlite3
import os
import cv2
from datetime import datetime
from deepface import DeepFace

# --- CONFIGURAÇÕES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'database.db')
capturas_dir = os.path.join(BASE_DIR, 'capturas_log')
if not os.path.exists(capturas_dir):
    os.makedirs(capturas_dir)

def registrar_log_acesso(status, usuario_id=None, caminho_foto_capturada=None):
    """
    Insere um registro na tabela LogsAcesso com o fuso horário local.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    timestamp_local = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        c.execute('''
            INSERT INTO LogsAcesso (timestamp_acesso, status, usuario_id, caminho_foto_capturada)
            VALUES (?, ?, ?, ?)
        ''', (timestamp_local, status, usuario_id, caminho_foto_capturada))
        conn.commit()
        print(f"[LOG] Evento de acesso '{status}' registrado às {timestamp_local}.")
    except Exception as e:
        print(f"[ERRO DE LOG] Não foi possível registrar o acesso: {e}")
    finally:
        conn.close()

def verificar_pessoa(imagem_rosto_detectado):
    """
    Compara o rosto detectado com o banco de dados e registra o log de acesso.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Salva a imagem capturada para o log
    timestamp = int(datetime.now().timestamp())
    log_img_filename = f"captura_{timestamp}.jpg"
    log_img_path = os.path.join(capturas_dir, log_img_filename)
    cv2.imwrite(log_img_path, imagem_rosto_detectado)

    try:
        c.execute("SELECT id, nome_completo, tipo, situacao, caminho_foto_rosto FROM Usuarios")
        registros = c.fetchall()

        if not registros:
            print("[AVISO] Nenhum usuário cadastrado para verificação.")
            registrar_log_acesso('Não Encontrado', caminho_foto_capturada=log_img_path)
            return

        pessoa_encontrada = False
        for user_id, nome, tipo_usuario, situacao, arquivo_rosto_db in registros:
            if not os.path.exists(arquivo_rosto_db):
                continue
            
            try:
                result = DeepFace.verify(
                    img1_path=log_img_path,
                    img2_path=arquivo_rosto_db,
                    model_name='Facenet512',
                    enforce_detection=False
                )
                
                if result['verified']:
                    pessoa_encontrada = True
                    print("-" * 30)
                    if situacao == 'Suspenso':
                        print(f"❌ ACESSO NEGADO: {nome}")
                        print(f"   - Motivo: Usuário com situação '{situacao}'")
                        registrar_log_acesso('Negado', user_id, log_img_path)
                    else:
                        print(f"✅ ACESSO ACEITO: {nome}")
                        print(f"   - Tipo: {tipo_usuario}")
                        print(f"   - Situação: {situacao}")
                        registrar_log_acesso('Aceito', user_id, log_img_path)
                    print("-" * 30)
                    return

            except Exception as e:
                print(f"[ERRO] Verificação falhou para {nome}. Detalhe: {e}")

        if not pessoa_encontrada:
            print("❌ Pessoa não reconhecida no banco de dados.")
            registrar_log_acesso('Não Encontrado', caminho_foto_capturada=log_img_path)

    finally:
        conn.close()

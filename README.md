## Projeto

Código base para funcionamento de um sistema de reconhecimento e análise facial

## Instalação

PYTHON 3.7 OU SUPERIOR NECESSÁRIO

1. Clone ou baixe este repositório.
2. Navegue até a pasta do projeto no terminal. (Comando cd)
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. No celular Android, instale e abra o app [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam).
5. Inicie a câmera no app e pegue o endereço IP mostrado (ex: `http://192.168.18.45:8080/video`).
6. No arquivo `main.py`, configure a variável `CAMERA_URL` com o endereço obtido. (necessário ter o /video no final)

---

## Uso

No terminal, dentro da pasta do projeto, rode o main.py

- Uma janela vai abrir mostrando o vídeo da câmera com rostos detectados.
- Pressiona a tecla `c` para cadastrar o rosto capturado com os dados necessários
- Pressiona a tecla `v` para verificar se o rosto capturado está cadastrado
- Pressione a tecla `q` para fechar o programa.
- As imagens dos rostos detectados estarão na pasta `rostos/`
- O banco de dados `database.db` terá os registros das imagens salvas com os dados da pessoa cadastrada.

---

## Observações

- Certifique-se de que o celular e o computador estejam conectados na mesma rede Wi-Fi.
- Para melhores resultados, utilize boa iluminação.

---
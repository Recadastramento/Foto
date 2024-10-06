import flet as ft
import os
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Função para autenticar e enviar a imagem para o Google Drive
def upload_to_drive(file_path):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    # Autenticação via OAuth2
    creds = None
    if os.path.exists("Gtoken.json"):
        print("Carregando credenciais de Gtoken.json...")
        creds = Credentials.from_authorized_user_file("Gtoken.json", SCOPES)
    
    if not creds or not creds.valid:
        print("Credenciais não encontradas ou inválidas. Iniciando o processo de autenticação...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Credenciais expiradas, renovando...")
        else:
            flow = InstalledAppFlow.from_client_secrets_file("Gcredentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            print("Autenticação concluída, credenciais salvas.")

        with open("Gtoken.json", 'w') as token:
            token.write(creds.to_json())
            print("Token salvo em Gtoken.json.")
    
    print("Construindo o serviço do Google Drive...")
    service = build('drive', 'v3', credentials=creds)

    # Carregar o arquivo para o Google Drive
    print(f"Carregando o arquivo {file_path} para o Google Drive...")
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaIoBaseUpload(io.FileIO(file_path, 'rb'), mimetype='image/jpeg')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("Arquivo carregado com sucesso.")

    # Obter o link de compartilhamento
    file_id = file.get('id')
    print(f"Arquivo ID: {file_id}, configurando permissões...")
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    link = f"https://drive.google.com/uc?id={file_id}&export=download"
    print(f"Link gerado: {link}")
    return link

# Função do botão para upload e salvar a imagem
def main(page: ft.Page):
    # Criando o FilePicker e adicionando-o à página
    file_dialog = ft.FilePicker(on_result=lambda result: on_file_picked(result))
    page.overlay.append(file_dialog)
    
    # Função executada após o arquivo ser selecionado
    def on_file_picked(result):
        if result.files:
            file_path = result.files[0].path
            print(f"Arquivo selecionado: {file_path}")
            page.snack_bar = ft.SnackBar(ft.Text("Upload in progress..."), open=True)
            page.update()
            link = upload_to_drive(file_path)
            page.snack_bar = ft.SnackBar(ft.Text(f"Link gerado: {link}"), open=True)
            page.update()

    # Função chamada ao clicar no botão
    def on_upload(e):
        print("Botão de upload clicado, abrindo o seletor de arquivos...")
        file_dialog.pick_files(allow_multiple=False)

    upload_button = ft.ElevatedButton("Enviar foto", on_click=on_upload)
    page.add(upload_button)

ft.app(target=main)

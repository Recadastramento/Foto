import flet as ft
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configure as credenciais e o serviço do Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'aa.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=credentials)

def main(pagina):
    Rc = ft.Text("Selecione uma foto")
    foto = ft.FilePicker(on_result=file_picker_result)
    
    # Botão para abrir o seletor de arquivos
    botao = ft.ElevatedButton("Selecionar Foto", on_click=lambda e: foto.pick_files())

    pagina.add(Rc)
    pagina.add(botao)
    pagina.add(foto)

def file_picker_result(event):
    if event.files:
        file_path = event.files[0].path
        upload_file_to_drive(file_path)

def upload_file_to_drive(file_path):
    file_metadata = {
        'name': os.path.basename(file_path),
        'mimeType': 'image/jpeg'  # ou outro tipo de imagem
    }
    media = MediaFileUpload(file_path, mimetype='image/jpeg')

    # Fazer o upload do arquivo
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    # Gerar link de compartilhamento
    drive_service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'},
        fields='id'
    ).execute()

    link = f"https://drive.google.com/file/d/{file_id}/view"
    print("Link da foto:", link)

ft.app(main)

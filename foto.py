import flet as ft
import os
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def authenticate(page):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    cod_token = "token.json"
    CLIENT_SECRET_FILE = "credentials.json"

    creds = None
    
    # Verificar se o token de acesso já existe
    if os.path.exists(cod_token):
        print("Carregando credenciais...")
        page.snack_bar = ft.SnackBar(ft.Text("Carregando credenciais..."), open=True)
        page.update()
        creds = Credentials.from_authorized_user_file(cod_token, SCOPES)
    else:
        print("Iniciando autenticação...")
        page.snack_bar = ft.SnackBar(ft.Text("Iniciando autenticação..."), open=True)
        page.update()
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        print("Autenticação concluída.")
        page.snack_bar = ft.SnackBar(ft.Text("Autenticação concluída."), open=True)
        page.update()

        # Salvar as credenciais para a próxima execução
        with open(cod_token, 'w') as token:
            token.write(creds.to_json())
            print("Token salvo.")
            page.snack_bar = ft.SnackBar(ft.Text("Token salvo."), open=True)
            page.update()
    
    return creds


def upload_to_drive(file_path, page, creds):
    print("Construindo o serviço do Google Drive...")
    page.snack_bar = ft.SnackBar(ft.Text("Construindo o serviço do Google Drive..."), open=True)
    page.update()
    
    service = build('drive', 'v3', credentials=creds)
    print("Serviço criado com sucesso.")
    page.snack_bar = ft.SnackBar(ft.Text("Serviço criado com sucesso."), open=True)
    page.update()

    print(f"Carregando {file_path}...")
    page.snack_bar = ft.SnackBar(ft.Text(f"Carregando {file_path}..."), open=True)
    page.update()
    
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaIoBaseUpload(io.FileIO(file_path, 'rb'), mimetype='image/jpeg')

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("Arquivo carregado com sucesso!")

    file_id = file.get('id')
    print(f"Arquivo ID: {file_id}, configurando permissões...")
    page.snack_bar = ft.SnackBar(ft.Text(f"Arquivo ID: {file_id}, configurando permissões..."), open=True)
    page.update()

    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    link = f"https://drive.google.com/uc?id={file_id}&export=download"
    print(f"Link gerado: {link}")
    page.snack_bar = ft.SnackBar(ft.Text(f"Link gerado: {link}"), open=True)
    page.update()
    return link


def main(page: ft.Page):
    file_dialog = ft.FilePicker(on_result=lambda result: on_file_picked(result, page))
    page.overlay.append(file_dialog)

    def on_file_picked(result, page):
        if result.files:
            file_path = result.files[0].path
            print("Iniciando upload...")
            page.snack_bar = ft.SnackBar(ft.Text("Iniciando upload..."), open=True)
            page.update()

            creds = authenticate(page)
            if creds:
                link = upload_to_drive(file_path, page, creds)
                print(f"Upload concluído. Link: {link}")
                page.snack_bar = ft.SnackBar(ft.Text(f"Upload concluído. Link: {link}"), open=True)
                page.update()

    def on_upload(e):
        print("Abrindo seletor de arquivos...")
        page.snack_bar = ft.SnackBar(ft.Text("Abrindo seletor de arquivos..."), open=True)
        page.update()
        file_dialog.pick_files(allow_multiple=False)
    SOCORRO = ft.Text("aaaaaa")
    upload_button = ft.ElevatedButton("Enviar foto", on_click=on_upload)
    page.add(SOCORRO)
    page.add(upload_button)

ft.app(target=main)

import os
import io
import flet as ft
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Escopos de acesso
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Caminho para o arquivo de credenciais JSON
cod_token = "token.json"
cod_cred = "credentials.json"
CLIENT_SECRET_FILE = cod_cred  # Altere para o seu caminho

# Verificar se o token de acesso já existe
if os.path.exists(cod_token):
    creds = Credentials.from_authorized_user_file(cod_token, SCOPES)
else:
    # Se não tiver, faça o login
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Salvar as credenciais para a próxima execução
    with open(cod_token, 'w') as token:
        token.write(creds.to_json())

# Construir o serviço
service = build('drive', 'v3', credentials=creds)

# Função para fazer o upload de uma imagem
def upload_image(file_path, page):
    if not file_path:
        page.snack_bar = ft.SnackBar(ft.Text("Nenhum arquivo foi selecionado."), open=True)
        page.update()
        return

    page.snack_bar = ft.SnackBar(ft.Text(f"Iniciando o upload do arquivo: {file_path}..."), open=True)
    page.update()

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaIoBaseUpload(io.FileIO(file_path, 'rb'), mimetype='image/jpeg')
    
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        page.snack_bar = ft.SnackBar(ft.Text(f"Arquivo carregado com sucesso! ID do arquivo: {file.get('id')}"), open=True)
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao carregar o arquivo: {str(e)}"), open=True)
    
    page.update()

def main(page: ft.Page):
    file_dialog = ft.FilePicker(on_result=lambda result: on_file_picked(result, page))
    page.overlay.append(file_dialog)

    def on_file_picked(result, page):
        if result.files:
            file_path = result.files[0].path
            page.snack_bar = ft.SnackBar(ft.Text(f"Arquivo selecionado: {file_path}"), open=True)
            page.update()

            # Chamar a função de upload
            upload_image(file_path, page)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Nenhum arquivo selecionado."), open=True)
            page.update()

    def on_upload(e):
        page.snack_bar = ft.SnackBar(ft.Text("Abrindo seletor de arquivos..."), open=True)
        page.update()
        file_dialog.pick_files(allow_multiple=False)

    upload_button = ft.ElevatedButton("Enviar foto", on_click=on_upload)
    page.add(upload_button)

ft.app(target=main)

import os
import sys
import tempfile
import base64
import threading
import webbrowser
import webview
from converter import convert_document
from i18n import TRANSLATIONS

class Api:
    def __init__(self, window_holder):
        self.window_holder = window_holder

    def get_translation(self, lang_code):
        return TRANSLATIONS.get(lang_code, TRANSLATIONS.get('el'))

    def open_url(self, url):
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print("Error opening URL:", e)
            return False

    def select_file(self):
        window = self.window_holder['window']
        file_types = ('Document Files (*.pdf;*.docx;*.doc;*.odt)', 'All Files (*.*)')
        result = window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        
        if result and len(result) > 0:
            file_path = result[0]
            return self.convert_file_by_path(file_path)
        return {'status': 'cancelled'}

    def convert_file_by_path(self, file_path):
        try:
            md_content = convert_document(file_path)
            base_name = os.path.basename(file_path)
            return {
                'status': 'success',
                'file_name': base_name,
                'content': md_content
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def convert_file_by_data(self, file_name, base64_data):
        try:
            # Decode base64 data to temporary file
            data_bytes = base64.b64decode(base64_data.split(',')[-1])
            ext = os.path.splitext(file_name)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(data_bytes)
                tmp_path = tmp.name

            md_content = convert_document(tmp_path)
            
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except Exception:
                pass

            return {
                'status': 'success',
                'file_name': file_name,
                'content': md_content
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def save_file(self, content):
        window = self.window_holder['window']
        file_types = ('Markdown File (*.md)', 'All Files (*.*)')
        save_path = window.create_file_dialog(webview.SAVE_DIALOG, save_filename='document.md', file_types=file_types)
        
        if save_path:
            if isinstance(save_path, (list, tuple)):
                save_path = save_path[0]
            
            if save_path:
                if not save_path.endswith('.md'):
                    save_path += '.md'
                try:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return {'status': 'success', 'path': save_path}
                except Exception as e:
                    return {'status': 'error', 'message': str(e)}
        return {'status': 'cancelled'}

def main():
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    web_dir = os.path.join(base_dir, 'web')
    index_path = os.path.join(web_dir, 'index.html')

    window_holder = {}
    api = Api(window_holder)

    window = webview.create_window(
        title='Doc2MD - Kidmedia',
        url=index_path,
        js_api=api,
        width=740,
        height=620,
        resizable=True,
        min_size=(680, 560)
    )
    window_holder['window'] = window
    webview.start(debug=False)

if __name__ == '__main__':
    main()

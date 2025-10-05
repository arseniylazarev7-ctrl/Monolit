from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from monolit_local_app.other import del_garbage, get_tag_positions

class Monolit(Flask):
    index_path = None
    process_request = None

server = Monolit(__name__)

@server.route("/")
def index():
    from monolit_local_app.other import sum_paths
    from os.path import dirname

    try:
        with open(server.index_path, "r") as f:
            pass
    except FileNotFoundError as e:
        raise FileNotFoundError(f"not found the main html-file, on path '{server.index_path}'\nError: {e}")

    with open(server.index_path, "r") as f:
        text = f.read()
        lines = text.split("\n")
        out = text

        html = BeautifulSoup(text, features="html.parser")

        for tag in html.find_all("link"):
            if tag.get("rel") == ["stylesheet"] and tag.get("type") == "text/css":
                try:
                    with open(tag.get("href"), "r") as f:
                        begin, end = get_tag_positions(text, lines, tag)

                        out = out.replace(del_garbage(text[begin:end]), f"\t\t<style>\n{f.read()}\n\t\t</style>")
                except FileNotFoundError:
                    with open(sum_paths(dirname(server.index_path), tag.get("href")), "r") as f:
                        begin, end = get_tag_positions(text, lines, tag)

                        out = out.replace(del_garbage(text[begin:end]), f"\t\t<style>\n{f.read()}\n\t\t</style>")         
            
        for tag in html.find_all("script"):
            try:
                with open(tag.get("src"), "r") as f:
                    begin, end = get_tag_positions(text, lines, tag)

                    out = out.replace(del_garbage(text[begin:end]), f"\t\t<script>\n{f.read()}\n\t\t</script>")
            except FileNotFoundError:
                with open(sum_paths(dirname(server.index_path), tag.get("src"))) as f:
                    begin, end = get_tag_positions(text, lines, tag)

                    out = out.replace(del_garbage(text[begin:end]), f"\t\t<script>\n{f.read()}\n\t\t</script>")

        return out, 200
    
@server.route("/favicon.ico")
def icon():
    return ""
    
@server.route('/process', methods=['POST']) # Слушаем POST-запросы на /process
def process_json_from_client():
    if request.method == 'POST':
        if request.is_json:
            try:
                return server.process_request(request)
            except Exception as e:
                print(f"[SERVER] Ошибка при обработке JSON: {e}")
                return jsonify({"error": "Не удалось обработать JSON"}), 400 # Bad Request
        else:
            return jsonify({"error": "Запрос должен быть в формате JSON"}), 415 # Unsupported Media Type
    else:
        return jsonify({"error": "Метод не поддерживается"}), 405 # Method Not Allowed
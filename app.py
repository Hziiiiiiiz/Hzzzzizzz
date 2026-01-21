from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # 解决跨域问题
import os
from demo7 import render_multiplication

app = Flask(__name__)
CORS(app)  # 允许所有域名访问 API（生产环境可限制）

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/api/render', methods=['POST'])
def api_render():
    try:
        data = request.get_json()
        num1 = int(data['num1'])
        num2 = int(data['num2'])
        high_quality = bool(data.get('high_quality', False))

        if num1 <= 0 or num2 <= 0:
            return jsonify({'error': '数字必须为正整数'}), 400
        if num1 > 99999 or num2 > 99999:
            return jsonify({'error': '数字过大，请小于 100000'}), 400

        quality = "high_quality" if high_quality else "low_quality"
        video_path = render_multiplication(num1, num2, OUTPUT_DIR, quality)

        filename = os.path.basename(video_path)
        return jsonify({
            'video_url': f'/video/{filename}',
            'download_url': f'/download/{filename}'
        })

    except Exception as e:
        print("渲染错误:", str(e))
        return jsonify({'error': f'渲染失败: {str(e)}'}), 500

@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/download/<filename>')
def download_video(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    print("🚀 后端 API 服务启动中... 访问 http://0.0.0.0:5000/api/render")
    app.run(host='0.0.0.0', port=5000, debug=False)
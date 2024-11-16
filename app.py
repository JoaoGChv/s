from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import base64
import numpy as np
from PIL import Image, ImageDraw
import json
import torch
import cv2

# Importações do modelo SAM2
from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

app = Flask(__name__, static_folder='static')
CORS(app)

# Configurações do modelo SAM2
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CHECKPOINT = "/workspace/segment-anything-2/checkpoints/sam2_hiera_tiny.pt"
CONFIG = "sam2_hiera_t.yaml"

# Carregar o modelo SAM2
def load_model():
    global sam2_model, mask_generator
    sam2_model = build_sam2(CONFIG, CHECKPOINT, device=DEVICE,
                            apply_postprocessing=False)
    mask_generator = SAM2AutomaticMaskGenerator(sam2_model)

load_model()

# Variáveis globais
image_rgb = None
sam2_result = None
annotations = []
image_width = 0
image_height = 0
current_image = None  # Armazena a imagem atual com as anotações

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/process_point', methods=['POST'])
def process_point():
    global image_rgb, sam2_result, current_image
    data = request.json
    x_click = int(data['x'])
    y_click = int(data['y'])

    if image_rgb is None or sam2_result is None:
        return jsonify({'error': 'Nenhuma imagem carregada.'}), 400

    result = process_single_point((x_click, y_click), sam2_result,
                                  image_rgb)
    if result is None:
        return jsonify({'error': 'Nenhuma segmentação encontrada para '
                                 'o ponto clicado.'}), 400

    result_image, bbox = result

    # Atualizar a imagem atual com as novas anotações
    current_image = result_image
    
    # Converter a imagem para base64
    buffered = BytesIO()
    result_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return jsonify({'image': img_str, 'bbox': bbox})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global image_rgb, sam2_result, annotations, image_width, image_height, current_image
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nenhuma imagem selecionada.'}), 400

    # Salvar a imagem em memória
    img_bytes = file.read()
    image = Image.open(BytesIO(img_bytes)).convert('RGB')
    image_rgb = np.array(image)
    image_width, image_height = image.size

    # Iniciar a imagem atual
    current_image = Image.fromarray(image_rgb.astype('uint8'))

    # Gerar as segmentações para a nova imagem
    sam2_result = generate_masks(image_rgb)

    # Limpar as anotações anteriores
    annotations = []

    return jsonify({'message': 'Imagem carregada com sucesso.'}), 200

@app.route('/save_annotation', methods=['POST'])
def save_annotation():
    global annotations
    data = request.json
    label = data.get('label')
    class_number = data.get('class_number')
    bbox = data.get('bbox')

    if label is None or class_number is None or bbox is None:
        return jsonify({'error': 'Dados da anotação incompletos.'}), 400

    # Salvar a anotação
    annotation = {
        'label': label,
        'class_number': class_number,
        'bbox': bbox
    }
    annotations.append(annotation)

    return jsonify({'message': 'Anotação salva com sucesso.'}), 200

@app.route('/export_annotations', methods=['GET'])
def export_annotations():
    global annotations, image_width, image_height

    if not annotations:
        return jsonify({'error': 'Nenhuma anotação disponível para '
                                 'exportação.'}), 400

    # Obter o formato selecionado pelo usuário
    bbox_format = request.args.get('format', 'yolo')

    # Validar o formato
    if bbox_format not in ['xywh', 'xyxy', 'yolo']:
        return jsonify({'error': 'Formato de bounding box inválido.'}), 400

    if bbox_format == 'yolo':
        # Gerar o conteúdo para o formato YOLO
        yolo_lines = []
        for ann in annotations:
            class_number = ann['class_number']
            bbox = ann['bbox']
            x_min, y_min, width, height = bbox
            x_center = x_min + width / 2.0
            y_center = y_min + height / 2.0

            # Normalizar as coordenadas
            x_center_norm = x_center / image_width
            y_center_norm = y_center / image_height
            width_norm = width / image_width
            height_norm = height / image_height

            line = f"{class_number} {x_center_norm} {y_center_norm} {width_norm} {height_norm}"
            yolo_lines.append(line)

        yolo_content = "\n".join(yolo_lines)

        return send_file(
            BytesIO(yolo_content.encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name='annotations.txt'
        )
    else:
        # Converter as anotações para o formato selecionado
        formatted_annotations = []
        for ann in annotations:
            label = ann['label']
            class_number = ann['class_number']
            bbox = ann['bbox']
            if bbox_format == 'xyxy':
                x_min, y_min, width, height = bbox
                x_max = x_min + width
                y_max = y_min + height
                formatted_bbox = [x_min, y_min, x_max, y_max]
            else:  # 'xywh'
                formatted_bbox = bbox
            formatted_annotations.append({
                'label': label,
                'class_number': class_number,
                'bbox': formatted_bbox
            })

        # Exportar as anotações em formato JSON
        annotations_json = json.dumps(formatted_annotations, indent=4)

        return send_file(
            BytesIO(annotations_json.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name='annotations.json'
        )

def generate_masks(image_rgb):
    # Gerar as segmentações usando o modelo SAM2
    return mask_generator.generate(image_rgb)

def process_single_point(point, sam2_result, image_rgb):
    x_click, y_click = point
    print(f"Processing point: ({x_click}, {y_click})")

    global current_image

    found = False
    for data in sam2_result:
        segmentation = data['segmentation']
        bbox = data['bbox']  # [x_min, y_min, width, height]

        # Converter a máscara de segmentação para um array numpy
        segmentation_mask = segmentation.astype(bool)

        if (0 <= y_click < segmentation_mask.shape[0] and
            0 <= x_click < segmentation_mask.shape[1]):
            if segmentation_mask[y_click, x_click]:
                # Atualizar a imagem atual com a nova segmentação
                current_image = update_current_image(
                    current_image, segmentation_mask, bbox, point)
                found = True
                return current_image, bbox  # Retorna a imagem atualizada e o bbox

    if not found:
        print(f"No segmentation found for point: ({x_click}, {y_click})")
        return None

def update_current_image(current_image, segmentation_mask, bbox, point):
    # Converter a imagem atual para PIL Image (se não for)
    if not isinstance(current_image, Image.Image):
        current_image = Image.fromarray(current_image.astype('uint8'))

    overlay = Image.new('RGBA', current_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Aplicar a segmentação como uma máscara vermelha
    red_mask = Image.new('RGBA', current_image.size,
                         (255, 0, 0, int(255 * 0.5)))  # Alpha 50%
    segmentation_pil = Image.fromarray(
        (segmentation_mask * 255).astype('uint8'))
    overlay.paste(red_mask, (0, 0), mask=segmentation_pil)

    # Desenhar o bounding box
    x_min, y_min, width, height = bbox
    x_max = x_min + width
    y_max = y_min + height
    draw.rectangle([(x_min, y_min), (x_max, y_max)],
                   outline='yellow', width=2)

    # Marcar o ponto clicado
    draw.ellipse([(point[0] - 5, point[1] - 5),
                  (point[0] + 5, point[1] + 5)],
                 fill='blue', outline='blue')

    # Combinar a imagem atual com o overlay
    updated_image = Image.alpha_composite(current_image.convert('RGBA'),
                                          overlay)

    return updated_image.convert('RGB')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

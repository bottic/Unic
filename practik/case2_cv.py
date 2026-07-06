import cv2
import numpy as np
import matplotlib.pyplot as plt

def generate_synthetic_steel(defect_type=None):
    """
    Генерирует синтетическое изображение поверхности стали.
    """
    # Создаем базовый серый фон с шумом (текстура металла)
    img = np.ones((400, 400), dtype=np.uint8) * 180
    noise = np.random.normal(0, 10, img.shape).astype(np.float64)
    img = np.clip(img + noise, 0, 255).astype(np.uint8)
    
    # Применяем легкое размытие для сглаживания текстуры
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    # Наносим дефекты в зависимости от типа
    if defect_type == 'scratch':  # Царапина (темная тонкая линия)
        cv2.line(img, (50, 80), (350, 320), (50), 3)
        # Добавим немного неровности царапине
        cv2.line(img, (100, 120), (250, 270), (40), 2)
    elif defect_type == 'scale':  # Окалина (темное бесформенное пятно)
        pts = np.array([[120, 150], [180, 130], [250, 180], [200, 250], [140, 220]], np.int32)
        cv2.fillPoly(img, [pts], (60))
        # Размоем края окалины
        img = cv2.GaussianBlur(img, (3, 3), 0)
    elif defect_type == 'dent':  # Вмятина (округлое пятно с тенью)
        # Тень
        cv2.circle(img, (200, 200), 40, (100), -1)
        # Блик
        cv2.circle(img, (190, 190), 38, (160), -1)
        img = cv2.GaussianBlur(img, (15, 15), 0)
        
    return img

def detect_defects(img):
    """
    Пайплайн детекции дефектов с использованием классических методов CV.
    """
    # 1. Сглаживание для удаления текстурного шума металла
    blurred = cv2.GaussianBlur(img, (9, 9), 0)
    
    # 2. Пороговая сегментация (дефекты темнее основного фона)
    # Используем простую бинаризацию с порогом
    _, thresh = cv2.threshold(blurred, 130, 255, cv2.THRESH_BINARY_INV)
    
    # 3. Морфологические операции для объединения частей дефекта
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # 4. Поиск контуров
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Рисуем результаты
    result = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    detected_count = 0
    
    for cnt in contours:
        # Фильтруем слишком мелкие шумы по площади
        area = cv2.contourArea(cnt)
        if area > 100:
            detected_count += 1
            # Получаем координаты ограничивающего прямоугольника
            x, y, w, h = cv2.boundingRect(cnt)
            # Рисуем рамку вокруг дефекта (красный цвет)
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 0, 255), 2)
            # Добавляем надпись
            cv2.putText(result, f"Defect #{detected_count}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
    return thresh, morphed, result

def main():
    # Генерируем изображения для разных типов дефектов
    defects = ['scratch', 'scale', 'dent']
    
    plt.figure(figsize=(15, 10))
    
    for i, def_type in enumerate(defects):
        # Генерация
        img = generate_synthetic_steel(def_type)
        
        # Детекция
        thresh, morphed, result = detect_defects(img)
        
        # Визуализация
        plt.subplot(3, 3, i*3 + 1)
        plt.imshow(img, cmap='gray')
        plt.title(f"Original ({def_type})")
        plt.axis('off')
        
        plt.subplot(3, 3, i*3 + 2)
        plt.imshow(thresh, cmap='gray')
        plt.title("Thresholded")
        plt.axis('off')
        
        plt.subplot(3, 3, i*3 + 3)
        plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        plt.title("Detection Result")
        plt.axis('off')
        
    plt.tight_layout()
    plt.savefig('case2_defect_detection.png', dpi=300)
    print("Результаты визуализации сохранены в 'case2_defect_detection.png'")

if __name__ == "__main__":
    main()

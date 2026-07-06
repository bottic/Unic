import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Список сменных рапортов (русский язык)
logs = [
    # Категория 1: Проблемы с подшипниками и конвейерами (Механика)
    "заклинило подшипник на конвейере №2",
    "замена изношенного подшипника транспортера",
    "люфт подшипника приводного вала конвейера",
    "свист подшипника на конвейерной ленте №1",
    "застревание ленты конвейера из-за поломки подшипника",
    
    # Категория 2: Перегрев и электрика (Моторы)
    "перегрев мотора на главном приводе",
    "высокая температура электродвигателя насоса",
    "сработала тепловая защита двигателя вентилятора",
    "мотор сильно перегрелся, аварийная остановка",
    "задымление в районе коробки передач электродвигателя",
    
    # Категория 3: Автоматика и датчики (КИПиА)
    "сбой в системе автоматики АСУ ТП",
    "ошибка контроллера PLC на узле дозирования",
    "потеря связи с датчиком давления",
    "зависание панели оператора, перезапуск системы",
    "некорректные показания температурного датчика дуговой печи"
]

def preprocess_text(text):
    """
    Простая токенизация и стемминг (обрезание окончаний для русского языка),
    чтобы объединить формы слов (подшипник/подшипника, мотор/мотора и т.д.)
    """
    words = text.lower().split()
    processed = []
    for w in words:
        # Удаляем знаки препинания и спецсимволы
        w = "".join([c for c in w if c.isalnum()])
        if not w:
            continue
        # Обрезаем слова длиннее 5 символов для псевдо-стемминга
        if len(w) > 5:
            w = w[:5]
        processed.append(w)
    return " ".join(processed)

def main():
    # Применяем псевдо-стемминг к логам
    processed_logs = [preprocess_text(log) for log in logs]
    
    # Простые стоп-слова (в обрезанном виде)
    russian_stopwords = [
        "и", "в", "во", "на", "под", "за", "с", "из", "о", "об", "обо", "у", "к", "ко", 
        "по", "для", "при", "а", "но", "да", "или", "бы", "ли", "же", "это", "что", "этот",
        "изза"
    ]
    
    # 1. Векторизация текста с помощью TF-IDF
    vectorizer = TfidfVectorizer(stop_words=russian_stopwords)
    X = vectorizer.fit_transform(processed_logs)
    
    # 2. Инициализация центроидов с расширенным набором тематических ключевых слов (псевдо-разметка)
    init_docs = [
        "подшипник конвейер лента вал транспортер заклинило люфт поломка свист застревание износ", # Механика
        "перегрев мотор электродвигатель температура нагрев двигатель тепловая защита вентилятор задымление", # Электрика
        "автоматика датчик сбой ошибка связь контроллер панель система давление показания зависание plc асу" # Автоматика
    ]
    processed_init = [preprocess_text(d) for d in init_docs]
    init_vectors = vectorizer.transform(processed_init).toarray()
    
    # 3. Кластеризация методом K-Means (3 кластера)
    num_clusters = 3
    kmeans = KMeans(n_clusters=num_clusters, init=init_vectors, n_init=1, random_state=42)
    kmeans.fit(X)
    labels = kmeans.labels_
    
    # Создаем DataFrame для анализа результатов
    df = pd.DataFrame({
        'original_log': logs, 
        'cluster': labels
    })
    
    cluster_labels_map = {
        0: "Механические неисправности (подшипники, конвейеры)",
        1: "Электрическая часть и перегревы (моторы, вентиляторы)",
        2: "Сбои автоматики и датчиков (АСУ ТП, PLC)"
    }
    
    print("--- Результаты кластеризации ---")
    for i in range(num_clusters):
        print(f"\nКластер {i} ({cluster_labels_map[i]}):")
        # Выводим логи этого кластера
        cluster_logs = df[df['cluster'] == i]['original_log'].tolist()
        for log in cluster_logs:
            print(f"    - {log}")
            
    # 4. Визуализация кластеров (Проекция на 2D с помощью PCA)
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X.toarray())
    
    plt.figure(figsize=(12, 9))
    colors = ['#66B2FF', '#FF9999', '#99FF99']
    
    for i in range(num_clusters):
        points = coords[labels == i]
        plt.scatter(
            points[:, 0], 
            points[:, 1], 
            s=250, 
            c=colors[i], 
            label=cluster_labels_map[i], 
            edgecolors='black',
            zorder=3
        )
        
        # Добавляем аккуратные подписи к каждой точке
        for idx, text in enumerate(logs):
            if labels[idx] == i:
                plt.annotate(
                    text, 
                    (coords[idx, 0] + 0.02, coords[idx, 1] + 0.01), 
                    fontsize=8, 
                    alpha=0.9,
                    zorder=4,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=0.5, alpha=0.85)
                )
                
    plt.title("Результаты автоматической кластеризации сменных рапортов (K-Means)", fontsize=14, fontweight='bold', pad=15)
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel("Главная компонента 1")
    plt.ylabel("Главная компонента 2")
    
    # Настройка осей для лучшего отображения меток
    plt.xlim(coords[:, 0].min() - 0.2, coords[:, 0].max() + 0.5)
    plt.ylim(coords[:, 1].min() - 0.2, coords[:, 1].max() + 0.2)
    
    plt.tight_layout()
    plt.savefig('case3_nlp_clustering.png', dpi=300)
    print("\nВизуализация сохранена в 'case3_nlp_clustering.png'")

if __name__ == "__main__":
    main()

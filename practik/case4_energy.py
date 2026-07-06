import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Установка seed для воспроизводимости
np.random.seed(42)

def generate_synthetic_energy_data(n_hours=720):
    """
    Генерирует временной ряд энергопотребления дуговой печи за n_hours часов.
    """
    hours = np.arange(n_hours)
    
    # 1. Признаки
    hour_of_day = hours % 24
    day_of_week = (hours // 24) % 7
    
    # Вес плавки стали (в тоннах), от 40 до 120 тонн
    steel_weight = np.random.uniform(40, 120, size=n_hours)
    
    # Температура печи (в градусах Цельсия), от 1400 до 1680 C
    furnace_temp = np.random.uniform(1400, 1680, size=n_hours)
    
    # Режим работы печи (1 - Нагрев, 2 - Плавление, 3 - Выпуск металла)
    op_mode = np.random.choice([1, 2, 3], size=n_hours, p=[0.4, 0.4, 0.2])
    
    # Базовый тренд энергопотребления (МВт*ч) на основе режима и веса стали
    # Плавление (режим 2) расходует больше всего энергии, выпуск (режим 3) - меньше всего
    base_energy = np.zeros(n_hours)
    for idx in range(n_hours):
        if op_mode[idx] == 1:
            base_energy[idx] = 40 + 0.3 * steel_weight[idx] + 0.01 * furnace_temp[idx]
        elif op_mode[idx] == 2:
            base_energy[idx] = 70 + 0.5 * steel_weight[idx] + 0.02 * furnace_temp[idx]
        else:
            base_energy[idx] = 10 + 0.1 * steel_weight[idx]
            
    # Добавляем суточную цикличность (днем потребление выше)
    daily_pattern = 10 * np.sin(2 * np.pi * hour_of_day / 24)
    
    # Случайный шум (непредсказуемые колебания нагрузки)
    noise = np.random.normal(0, 5, size=n_hours)
    
    # Целевая переменная: энергопотребление
    target_energy = base_energy + daily_pattern + noise
    # Энергия не может быть отрицательной
    target_energy = np.clip(target_energy, 0, None)
    
    # Создаем DataFrame
    df = pd.DataFrame({
        'HourOfDay': hour_of_day,
        'DayOfWeek': day_of_week,
        'SteelWeight_Tons': steel_weight,
        'FurnaceTemp_C': furnace_temp,
        'OperatingMode': op_mode,
        'Energy_MWh': target_energy
    })
    
    # Добавляем лаговый признак (потребление энергии за прошлый час)
    df['PrevHour_Energy'] = df['Energy_MWh'].shift(1)
    # Заполняем первую строку средним значением
    df.loc[0, 'PrevHour_Energy'] = df['Energy_MWh'].mean()
    
    return df

def main():
    # 1. Генерация данных
    df = generate_synthetic_energy_data(n_hours=720)
    
    # Разделяем на признаки (X) и целевую переменную (y)
    X = df.drop(columns=['Energy_MWh'])
    y = df['Energy_MWh']
    
    # Разделяем на обучающую и тестовую выборки
    # Так как это временной ряд, разделим хронологически
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # 2. Обучение модели Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Прогнозирование
    y_pred = model.predict(X_test)
    
    # 3. Метрики качества
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print("--- Метрики качества модели ---")
    print(f"Mean Absolute Error (MAE): {mae:.3f} МВт*ч")
    print(f"Root Mean Squared Error (RMSE): {rmse:.3f} МВт*ч")
    print(f"Коэффициент детерминации R^2: {r2:.3f}")
    
    # 4. Важность признаков
    importances = model.feature_importances_
    features = X.columns
    print("\n--- Важность признаков для прогноза ---")
    for feat, imp in zip(features, importances):
        print(f"  {feat}: {imp:.3f}")
        
    # 5. Визуализация результатов (сравнение факта и прогноза за 48 часов)
    plt.figure(figsize=(12, 6))
    
    # Возьмем первые 48 часов из тестовой выборки
    hours_to_plot = 48
    plt.plot(np.arange(hours_to_plot), y_test.iloc[:hours_to_plot].values, label="Фактическое потребление", color='blue', marker='o')
    plt.plot(np.arange(hours_to_plot), y_pred[:hours_to_plot], label="Прогноз ML-модели", color='orange', linestyle='--', marker='x')
    
    plt.title("Прогнозирование расхода энергии дуговой печи на 48 часов вперед")
    plt.xlabel("Время (часы)")
    plt.ylabel("Потребление энергии (МВт*ч)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('case4_energy_prediction.png', dpi=300)
    print("\nГрафик прогноза сохранен в 'case4_energy_prediction.png'")

if __name__ == "__main__":
    main()

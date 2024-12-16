import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import tkinter as tk
from tkinter import messagebox

# 1. Збір та підготовка даних
data = {
    'hours_studied': [10, 9, 8, 6, 4, 2, 1, 7, 8, 3],         # Години навчання
    'missed_classes': [1, 0, 2, 2, 5, 7, 8, 0, 3, 5],        # Пропущені заняття
    'homework_score': [90, 85, 80, 60, 70, 50, 40, 75, 80, 55],  # Оцінка за домашні завдання
    'hours_sleep': [8, 7, 6, 5, 5, 4, 3, 6, 7, 4],           # Години сну перед іспитом
    'passed_exam': [1, 1, 1, 1, 0, 0, 0, 1, 1, 0]            # Результат іспиту (1 - здав, 0 - не здав)
}

df = pd.DataFrame(data)

# Розділяємо на ознаки та цільову змінну
X = df[['hours_studied', 'missed_classes', 'homework_score', 'hours_sleep']]
y = df['passed_exam']

# Розділяємо на тренувальний та тестовий набори
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Масштабування даних
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Навчання моделі
model = LogisticRegression()
model.fit(X_train, y_train)

# Оцінка точності моделі
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Точність моделі: {accuracy:.2f}')


# Функція для прогнозування
def predict_exam():
    try:
        # Отримання значень від користувача
        hours = float(entry_hours.get())
        missed = float(entry_missed.get())
        homework = float(entry_homework.get())
        sleep = float(entry_sleep.get())

        # Підготовка даних до масштабування
        input_data = np.array([[hours, missed, homework, sleep]])
        input_data_scaled = scaler.transform(input_data)

        # Прогнозування результату
        prediction = model.predict(input_data_scaled)

        # Виведення результату
        if prediction == 1:
            messagebox.showinfo("Результат", "Студент здасть іспит!")
        else:
            messagebox.showinfo("Результат", "Студент НЕ здасть іспит.")

    except ValueError:
        # Якщо введені нечислові дані
        messagebox.showerror("Помилка", "Будь ласка, введіть коректні числа.")


# Створення вікна програми
root = tk.Tk()
root.title("Прогноз успішності студента")
root.geometry("400x300")  # Задаємо більший розмір вікна

# Підписи та поля для введення даних
label_hours = tk.Label(root, text="Години навчання:")
label_hours.grid(row=0, column=0, padx=10, pady=5)

entry_hours = tk.Entry(root)
entry_hours.grid(row=0, column=1, padx=10, pady=5)

label_missed = tk.Label(root, text="Пропущені заняття:")
label_missed.grid(row=1, column=0, padx=10, pady=5)

entry_missed = tk.Entry(root)
entry_missed.grid(row=1, column=1, padx=10, pady=5)

label_homework = tk.Label(root, text="Оцінка за домашні завдання:")
label_homework.grid(row=2, column=0, padx=10, pady=5)

entry_homework = tk.Entry(root)
entry_homework.grid(row=2, column=1, padx=10, pady=5)

label_sleep = tk.Label(root, text="Години сну перед іспитом:")
label_sleep.grid(row=3, column=0, padx=10, pady=5)

entry_sleep = tk.Entry(root)
entry_sleep.grid(row=3, column=1, padx=10, pady=5)

# Кнопка для прогнозування
button_predict = tk.Button(root, text="Прогнозувати", command=predict_exam)
button_predict.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

# Запуск програми
root.mainloop()

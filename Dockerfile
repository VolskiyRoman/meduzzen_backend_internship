FROM python:3.8
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости проекта (файлы requirements.txt) в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости, указанные в requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . /app/

# Создаем и применяем миграции Django
RUN python manage.py migrate

# Запускаем Django-приложение при запуске контейнера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
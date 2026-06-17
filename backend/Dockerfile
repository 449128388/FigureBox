FROM demisto/python3:3.11.9.103842

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

CMD ["sh", "entrypoint.sh"]
FROM python

WORKDIR /app

COPY . .

RUN pip3 install pipreqs
RUN pipreqs . --force

RUN pip3 install -r requirements.txt
RUN pip3 install python-dotenv

CMD [ "python3", "main.py" ]
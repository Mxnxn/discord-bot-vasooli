FROM python:3.10
WORKDIR /usr/src/vasooli
COPY requirements.txt ./
RUN python -m pip install -r requirements.txt
COPY . ./ 
EXPOSE 10001
ENV PORT=10001
CMD [ "python", "script.py" ]
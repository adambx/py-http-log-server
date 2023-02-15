docker build -t logserver .
docker run -p 8000:8000 \
-e FILE_PATHS=\
/app/logserver.py \
-e TAIL_LENGTH=2048 \
logserver
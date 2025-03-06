## Guide setup

```bash
ubuntu@ip-172-31-68-179:~/aidev/fintech-chatbot-research/vietqa-demo$ docker compose up -d 
WARN[0000] /home/ubuntu/aidev/fintech-chatbot-research/vietqa-demo/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
[+] Running 3/3
 ✔ Container vietqa-demo-streamlit-1           Started                                                 1.1s 
 ✔ Container vietqa-demo-fastapi-1             Started                                                 0.8s 
 ✔ Container vietqa-demo-vietnamese-embedor-1  Started     


docker exec -it vietqa-demo-vietnamese-embedor-1 bash 


uvicorn main:app --reload --host 0.0.0.0 --port 80
 ```
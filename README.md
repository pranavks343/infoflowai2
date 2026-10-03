# InfoFlow AI

Streamlit interface with an internal FastAPI document assistant.

## Deploy to Render

[Open the Render deployment setup](https://render.com/deploy?repo=https%3A%2F%2Fgithub.com%2Fpranavks343%2Finfoflowai2%2Ftree%2Fcodex%2Frender-deployment)

The `render.yaml` Blueprint deploys a Docker web service with a 1 GB persistent
disk. This uses a paid Starter service and paid storage; review Render's pricing
before creating the service.

1. In Render, select **New → Blueprint** and connect this GitHub repository.
2. Select the branch containing `render.yaml`.
3. Enter `OPENAI_API_KEY` when prompted. Keep it in Render's environment settings,
   never in the repository or Docker image.
4. Review the proposed resources and deploy.
5. Open the service's Render URL, sign up, and upload a document as HR.

Only Streamlit is exposed publicly; FastAPI runs inside the container on
`127.0.0.1:8000`. Accounts, uploaded files and the FAISS index are stored under
`/var/data` on the persistent disk. Existing local documents and accounts are not
included in the image; upload documents again after deployment.

This is a prototype deployment. Signup permits users to choose HR/IT roles and
passwords are stored without hashing. Use test accounts and non-sensitive data
until authentication and document permissions are hardened.

## Run locally

Use Python 3.12 and install `requirements.txt` in a virtual environment. Set
`OPENAI_API_KEY` in `backend/.env` (ignored by Git).

```sh
# Terminal 1, from backend/
../.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2, from frontend/
../.venv/bin/python -m streamlit run home.py
```

For Docker, provide the key via an environment variable and persist `/var/data`:

```sh
docker build -t infoflow-ai .
docker run --rm -p 10000:10000 --env-file backend/.env \
  -v infoflow-data:/var/data infoflow-ai
```

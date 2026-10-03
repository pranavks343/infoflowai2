# InfoFlow AI

Streamlit interface with an internal FastAPI document assistant.

## Deploy to Render

[Open the Render deployment setup](https://render.com/deploy?repo=https%3A%2F%2Fgithub.com%2Fpranavks343%2Finfoflowai2%2Ftree%2Fcodex%2Frender-deployment)

The `render.yaml` Blueprint deploys a free Docker web service without a persistent
disk. Render can spin it down after inactivity; accounts, documents and the index
are lost on spin-down, restart or redeploy. OpenAI API usage is billed separately.

1. In Render, select **New → Blueprint** and connect this GitHub repository.
2. Select the branch containing `render.yaml`.
3. Enter `OPENAI_API_KEY` when prompted. Keep it in Render's environment settings,
   never in the repository or Docker image.
4. Review the proposed resources and deploy.
5. Open the service's Render URL and sign in with Clerk.

Only Streamlit is exposed publicly; FastAPI runs inside the container on
`127.0.0.1:8000`. Accounts, uploaded files and the FAISS index are stored under
`/tmp/infoflow-data` on ephemeral storage. Existing local documents and accounts are not
included in the image; upload documents again after deployment.

Clerk manages authentication; passwords are no longer read from `users.json`.
Every API request verifies Clerk's signature, issuer, expiry and application
origin. Each sign-in asks users to select an Employee, HR, IT, or Admin workspace.
The selection does not grant permissions: new users have Employee access until
an administrator assigns a different role in Clerk. Users can select Employee
or their assigned role; Admin users can select any workspace. Uploads and management endpoints require
HR or Admin, and the IT endpoint requires IT or Admin. Documents still share one
knowledge base; department-level document filtering is not implemented.

## Clerk configuration

The included publishable key belongs to the InfoFlow AI development instance.
It is public and is safe to ship to browsers. No Clerk secret key is required.
For a production Clerk instance, replace `CLERK_PUBLISHABLE_KEY` in Render and
the Blueprint with that instance's publishable key and complete Clerk's domain
setup. Keep `CLERK_AUTHORIZED_PARTIES` set to the exact application origin.

To grant a user a role:

1. In Clerk, go to **Configure → Sessions → Customize session token** and set:

   ```json
   {"role": "{{user.public_metadata.role}}"}
   ```

2. In **Users**, select the user and set their **Public metadata** to
   `{"role": "HR"}`, `{"role": "IT"}`, or `{"role": "Admin"}`.
3. Sign out and back in, or wait for the session token to refresh.

Only administrators should edit public metadata. User-editable unsafe metadata
is never used for permissions. Existing local accounts must register with Clerk.
Clerk users persist independently of Render's ephemeral filesystem.

For local development, also set `CLERK_PUBLISHABLE_KEY` in `backend/.env`.
Local origins default to `http://localhost:8501` and `http://127.0.0.1:8501` when
`CLERK_AUTHORIZED_PARTIES` is not set. Refreshing authentication does not resubmit
questions or uploads; those require explicit form/button submissions.

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

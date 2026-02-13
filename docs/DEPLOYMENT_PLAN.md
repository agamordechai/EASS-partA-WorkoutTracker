# Deployment Guide: AWS Free Tier

## Overview

Deploy to AWS EC2 free tier: **t2.micro** (1 vCPU, 1 GB RAM, 30 GB storage).
Free for 12 months. We add 4 GB swap to handle all services comfortably.

---

## Step 1: Create an AWS Account

1. Go to https://aws.amazon.com and click **Create an AWS Account** (top right)
2. Enter your email and choose an account name
3. Verify your email, set a password
4. Choose **Personal** account type, fill in your details
5. Enter credit card (verification hold only, like Oracle — won't be charged for free tier usage)
6. Verify your phone number
7. Select the **Basic Support — Free** plan
8. Click **Complete sign up**
9. Wait for the activation email (can take a few minutes)

## Step 2: Generate an SSH Key Pair (on your Mac)

```bash
ssh-keygen -t ed25519 -f ~/.ssh/aws-vm -N ""
```

Copy the public key to clipboard:
```bash
cat ~/.ssh/aws-vm.pub | pbcopy
```

## Step 3: Launch an EC2 Instance

1. Log in to https://console.aws.amazon.com
2. In the top-right, select a **Region** close to you (e.g., `eu-central-1` Frankfurt, `us-east-1` Virginia)
3. Search for **EC2** in the top search bar and click it
4. Click **Launch Instance** (orange button)
5. Configure:
   - **Name:** `workout-tracker`
   - **Application and OS Images:**
     - Click **Ubuntu**
     - Select **Ubuntu Server 24.04 LTS** (free tier eligible)
     - Architecture: **64-bit (x86)**
   - **Instance type:** `t2.micro` (should say "Free tier eligible")
   - **Key pair:**
     - Click **Create new key pair**
     - OR click **Import key pair** → paste your `~/.ssh/aws-vm.pub` contents
     - If you create a new one in AWS: download the `.pem` file and save it to `~/.ssh/`
   - **Network settings:**
     - Click **Edit**
     - **Auto-assign public IP:** Enable
     - **Security group:** Create a new one
     - Keep the default SSH rule (port 22, from 0.0.0.0/0)
     - Click **Add security group rule**:
       - Type: **HTTP**
       - Source: **0.0.0.0/0**
       - (This opens port 80)
   - **Storage:** Change to **30 GB** gp3 (free tier allows up to 30 GB)
6. Click **Launch Instance**
7. Click **View all instances**
8. Wait for **Instance state** to show **Running** and **Status check** to show **2/2 checks passed**
9. Click on your instance → **copy the Public IPv4 address**

## Step 4: SSH into the VM

If you imported your own key:
```bash
ssh -i ~/.ssh/aws-vm ubuntu@<YOUR-PUBLIC-IP>
```

If you created a key pair in AWS and downloaded the `.pem`:
```bash
chmod 400 ~/.ssh/your-key.pem
ssh -i ~/.ssh/your-key.pem ubuntu@<YOUR-PUBLIC-IP>
```

Type `yes` if prompted about the fingerprint.

## Step 5: Set Up Swap Space (important — only 1 GB RAM)

On the VM, run:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Verify with `free -h` — you should see 4 GB swap.

## Step 6: Clone the Repo and Deploy

```bash
# Clone the repo
git clone https://github.com/<your-username>/eass_a_workouttracker.git
cd eass_a_workouttracker

# Run the setup script (first run installs Docker and copies .env template)
bash deploy/setup.sh
```

The script will install Docker and copy the `.env` template, then **exit** telling you to fill in secrets.

Edit the `.env` file:
```bash
nano .env
```

Fill in:
- **PUBLIC_IP** — your EC2 public IP from Step 3
- **JWT_SECRET_KEY** — generate with: `openssl rand -hex 32`
- **GOOGLE_CLIENT_ID** — from Step 8 below
- **ANTHROPIC_API_KEY** — your Anthropic key (or leave empty to disable AI coach)
- **POSTGRES_PASSWORD** — generate with: `openssl rand -hex 16`

Save (`Ctrl+O`, Enter, `Ctrl+X`) and run setup again:
```bash
bash deploy/setup.sh
```

First build takes 5-10 minutes on t2.micro. Be patient.

## Step 7: Verify the App

From your local machine:
```bash
# Check API health
curl http://<YOUR-PUBLIC-IP>/api/health

# Open in browser
open http://<YOUR-PUBLIC-IP>
```

## Step 8: Update Google OAuth Redirect URIs

1. Go to https://console.cloud.google.com
2. Select your project
3. Go to **APIs & Services** → **Credentials** (left sidebar)
4. Click your **OAuth 2.0 Client ID**
5. Under **Authorized JavaScript origins**, add:
   - `http://<YOUR-PUBLIC-IP>`
6. Under **Authorized redirect URIs**, add:
   - `http://<YOUR-PUBLIC-IP>`
7. Click **Save**

Now test Google Sign-In on `http://<YOUR-PUBLIC-IP>`.

---

## Files Created

| File | Purpose |
|------|---------|
| `docker-compose.prod.yml` | Production overrides (port 80, no internal ports exposed) |
| `deploy/.env.production` | Environment variable template |
| `deploy/setup.sh` | VM setup automation |
| `deploy/iptables.sh` | Open port 80 (Oracle-specific, not needed for AWS) |

## Architecture

```
Internet → :80 (frontend nginx container)
                → /              → static React files
                → /api/          → api:8000 (internal)
                → /ai-coach/     → ai-coach:8001 (internal)
```

## Useful Commands (on the VM)

```bash
# View logs
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# View specific service logs
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f api

# Restart everything
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart

# Stop everything
docker compose -f docker-compose.yml -f docker-compose.prod.yml down

# Rebuild and restart (after pulling new code)
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Check service status
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Check memory usage
free -h
docker stats --no-stream
```

## Cost Notes

- **Free for 12 months:** 750 hours/month of t2.micro (enough for 1 instance 24/7)
- **Free storage:** 30 GB EBS
- **Free data transfer:** 100 GB/month outbound
- **After 12 months:** ~$8.50/month for t2.micro if you keep it running
- **Important:** Set up a billing alarm (Step 9) to avoid surprises

## Step 9 (Optional): Set Up Billing Alarm

1. Go to https://console.aws.amazon.com/billing
2. Click **Budgets** in the left sidebar
3. Click **Create budget**
4. Select **Zero spend budget** (alerts you if anything is charged)
5. Enter your email → **Create budget**

## Future: Adding HTTPS + Domain

When ready, use a free domain + Let's Encrypt:
- DuckDNS (free subdomain) or Freenom
- Add certbot container for SSL certificates
- Update nginx config for HTTPS

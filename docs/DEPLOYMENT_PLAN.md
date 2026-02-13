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

## Architecture (HTTP-only, before Step 10)

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

## Step 10: Add HTTPS with Cloudflare + Origin Certificate

### 10a: Get a Domain

Buy a domain from any registrar (Cloudflare Registrar, Namecheap, Google Domains, etc.).

### 10b: Add Your Domain to Cloudflare

1. Go to https://dash.cloudflare.com and sign up / log in
2. Click **Add a site** (top bar)
3. Enter your domain name and click **Continue**
4. Select the **Free** plan → click **Continue**
5. Cloudflare will scan existing DNS records — click **Continue**
6. Cloudflare shows you **two nameservers** (e.g. `ada.ns.cloudflare.com`, `bob.ns.cloudflare.com`)
7. Go to your domain registrar and **replace the nameservers** with the two Cloudflare ones
   - If you bought the domain on Cloudflare Registrar, skip this — it's automatic
8. Back in Cloudflare, click **Done, check nameservers**
9. Wait for the email confirming your domain is active (can take up to 24 hours, usually minutes)

### 10c: Create DNS Records Pointing to Your EC2

1. In Cloudflare dashboard, click your domain → **DNS** → **Records**
2. Click **Add record**:
   - **Type:** `A`
   - **Name:** `@` (this means your root domain, e.g. `yourdomain.com`)
   - **IPv4 address:** your EC2 public IP (from Step 3)
   - **Proxy status:** toggle to **Proxied** (orange cloud icon)
   - Click **Save**
3. Click **Add record** again:
   - **Type:** `A`
   - **Name:** `www`
   - **IPv4 address:** same EC2 public IP
   - **Proxy status:** **Proxied** (orange cloud)
   - Click **Save**

### 10d: Set SSL/TLS Mode to Full (Strict)

1. In Cloudflare dashboard, click your domain → **SSL/TLS** (left sidebar)
2. Under **Overview**, find the encryption mode selector
3. Click **Full (Strict)**
   - This tells Cloudflare to encrypt traffic all the way to your server and verify the Origin Certificate

### 10e: Generate a Cloudflare Origin Certificate

1. In Cloudflare dashboard → **SSL/TLS** → **Origin Server**
2. Click **Create Certificate**
3. In the dialog:
   - **Private key type:** RSA (default is fine)
   - **Hostnames:** should already show `yourdomain.com` and `*.yourdomain.com` — leave as-is
   - **Certificate validity:** 15 years (default)
4. Click **Create**
5. You'll see two text boxes:
   - **Origin Certificate** — copy the entire block (including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`)
   - **Private Key** — copy the entire block (including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`)
6. On your **local machine**, save these to files:
   ```bash
   # Paste the Origin Certificate
   nano nginx/certs/cert.pem
   # (paste, Ctrl+O, Enter, Ctrl+X)

   # Paste the Private Key
   nano nginx/certs/key.pem
   # (paste, Ctrl+O, Enter, Ctrl+X)
   ```
7. **IMPORTANT:** Click **OK** in Cloudflare — you cannot see the private key again after closing this dialog

### 10f: Copy Certs to the Server

```bash
scp -i ~/.ssh/aws-vm nginx/certs/cert.pem nginx/certs/key.pem ubuntu@<YOUR-EC2-IP>:~/eass_a_workouttracker/nginx/certs/
```

### 10g: Update `.env` on the Server

SSH into your EC2 and edit `.env`:
```bash
ssh -i ~/.ssh/aws-vm ubuntu@<YOUR-EC2-IP>
cd eass_a_workouttracker
nano .env
```

Add/update:
```
DOMAIN_NAME=yourdomain.com
```

Save and exit.

### 10h: Open Port 443 in AWS Security Group

1. Go to https://console.aws.amazon.com → **EC2** → **Instances**
2. Click your instance → **Security** tab → click the **Security group** link
3. Click **Edit inbound rules**
4. Click **Add rule**:
   - **Type:** HTTPS
   - **Source:** `0.0.0.0/0`
5. Click **Save rules**

### 10i: Redeploy

On the server:
```bash
cd ~/eass_a_workouttracker
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 10j: Update Google OAuth Redirect URIs

1. Go to https://console.cloud.google.com → **APIs & Services** → **Credentials**
2. Click your **OAuth 2.0 Client ID**
3. Under **Authorized JavaScript origins**, add:
   - `https://yourdomain.com`
4. Under **Authorized redirect URIs**, add:
   - `https://yourdomain.com`
5. Click **Save**

### 10k: Verify Everything Works

```bash
# Should redirect to https
curl -I http://yourdomain.com

# Should return the frontend HTML with valid SSL
curl https://yourdomain.com

# API health check
curl https://yourdomain.com/api/health
```

Open `https://yourdomain.com` in your browser — you should see a valid SSL lock icon and Google Sign-In should work.

## Architecture (with HTTPS)

```
Client → Cloudflare (edge SSL) → EC2:443 → nginx-proxy (Origin Cert)
                                                → frontend:80 (static React + reverse proxy)
                                                    → /api/       → api:8000
                                                    → /ai-coach/  → ai-coach:8001
```

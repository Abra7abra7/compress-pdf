# PDF Kompresor - Deployment Dokumentácia

Tento dokument obsahuje podrobné inštrukcie pre nasadenie PDF Kompresor web aplikácie na Linux server pomocou Docker.

## Obsah

1. [Požiadavky](#požiadavky)
2. [Príprava servera](#príprava-servera)
3. [Inštalácia Docker](#inštalácia-docker)
4. [Deployment aplikácie](#deployment-aplikácie)
5. [Konfigurácia](#konfigurácia)
6. [SSL/HTTPS Setup](#sslhttps-setup)
7. [Monitoring a logy](#monitoring-a-logy)
8. [Backup](#backup)
9. [Aktualizácia](#aktualizácia)
10. [Riešenie problémov](#riešenie-problémov)

---

## Požiadavky

### Hardvér
- **CPU**: 2+ jadrá (4 jadrá odporúčané pre 50+ používateľov)
- **RAM**: 2 GB minimum, 4 GB odporúčané
- **Disk**: 20 GB voľného priestoru (viac pre veľa upload/compressed súborov)
- **Network**: 100 Mbps+ pripojenie

### Software
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+, alebo iný s Docker podporou)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Pre klonovanie projektu

---

## Príprava servera

### 1. Aktualizácia systému

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Inštalácia základných nástrojov

```bash
# Ubuntu/Debian
sudo apt install -y git curl wget net-tools

# CentOS/RHEL
sudo yum install -y git curl wget net-tools
```

### 3. Nastavenie firewall

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# FirewallD (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

---

## Inštalácia Docker

### Ubuntu/Debian

```bash
# Odstránenie starých verzií
sudo apt remove docker docker-engine docker.io containerd runc

# Inštalácia závislostí
sudo apt install -y ca-certificates curl gnupg lsb-release

# Pridanie Docker GPG kľúča
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Pridanie Docker repozitára
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Inštalácia Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Pridanie používateľa do docker skupiny
sudo usermod -aG docker $USER

# Reštart pre aktiváciu zmien
newgrp docker
```

### CentOS/RHEL

```bash
# Inštalácia závislostí
sudo yum install -y yum-utils

# Pridanie Docker repozitára
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Inštalácia Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Spustenie Docker
sudo systemctl start docker
sudo systemctl enable docker

# Pridanie používateľa do docker skupiny
sudo usermod -aG docker $USER
```

### Overenie inštalácie

```bash
docker --version
docker compose version
```

---

## Deployment aplikácie

### 1. Klonovanie projektu

```bash
cd /opt
sudo git clone <your-repository-url> pdf-compressor
cd pdf-compressor
sudo chown -R $USER:$USER .
```

### 2. Konfigurácia environment variables

Vytvorte `.env` súbor:

```bash
nano .env
```

Obsah:

```env
# Bezpečnostný kľúč (vygenerujte náhodný string)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Maximum upload size v bytoch (200 MB default)
MAX_UPLOAD_SIZE=209715200

# Čas po ktorom sa vymažú staré súbory (v hodinách)
CLEANUP_AGE=24

# Port (optional, default 80)
PORT=80
```

Generovanie bezpečného SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Vytvorenie SSL adresára (ak plánujete HTTPS)

```bash
mkdir -p ssl
```

### 4. Build a spustenie

```bash
# Build Docker obrazu
docker compose build

# Spustenie v pozadí
docker compose up -d

# Kontrola logu
docker compose logs -f
```

### 5. Overenie

Otvorte prehliadač a prejdite na:

```
http://your-server-ip
```

Mali by ste vidieť PDF Kompresor rozhranie.

---

## Konfigurácia

### Zmena upload limitu

V `docker-compose.yml`:

```yaml
environment:
  - MAX_UPLOAD_SIZE=419430400  # 400 MB
```

Reštartujte aplikáciu:

```bash
docker compose restart
```

### Zmena portu

V `docker-compose.yml` zmeňte port mapping:

```yaml
ports:
  - "8080:80"  # Externý port 8080
```

### Cleanup interval

V `docker-compose.yml`:

```yaml
environment:
  - CLEANUP_AGE=48  # 48 hodín
```

---

## SSL/HTTPS Setup

### Použitie Let's Encrypt (Certbot)

#### 1. Inštalácia Certbot

```bash
# Ubuntu/Debian
sudo apt install -y certbot

# CentOS/RHEL
sudo yum install -y certbot
```

#### 2. Zastavenie Nginx

```bash
docker compose stop nginx
```

#### 3. Získanie certifikátu

```bash
sudo certbot certonly --standalone -d your-domain.com
```

Certifikáty budú v `/etc/letsencrypt/live/your-domain.com/`

#### 4. Kopírovanie certifikátov

```bash
sudo mkdir -p /opt/pdf-compressor/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/pdf-compressor/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/pdf-compressor/ssl/
sudo chown -R $USER:$USER /opt/pdf-compressor/ssl
```

#### 5. Aktualizácia nginx.conf

Odkomentujte HTTPS server blok v `nginx.conf` a aktualizujte `server_name`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    # ... zvyšok konfigurácie
}
```

#### 6. Reštart

```bash
docker compose up -d
```

#### 7. Automatické obnovenie certifikátu

Vytvorte cron job:

```bash
sudo crontab -e
```

Pridajte:

```cron
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/*.pem /opt/pdf-compressor/ssl/ && docker compose -f /opt/pdf-compressor/docker-compose.yml restart nginx
```

---

## Monitoring a logy

### Sledovanie logu

```bash
# Všetky služby
docker compose logs -f

# Len aplikácia
docker compose logs -f app

# Len Nginx
docker compose logs -f nginx

# Posledných 100 riadkov
docker compose logs --tail=100
```

### Kontrola stavu kontajnerov

```bash
docker compose ps
```

### Monitorovanie resources

```bash
docker stats
```

### Health check

```bash
curl http://localhost/health
```

Odpoveď:

```json
{
  "status": "healthy",
  "timestamp": "2024-11-06T09:00:00"
}
```

---

## Backup

### Backup uploads a compressed súborov

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/pdf-compressor"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/pdf-compressor/uploads

# Backup compressed
tar -czf $BACKUP_DIR/compressed_$DATE.tar.gz /opt/pdf-compressor/compressed

# Vymazanie starších ako 7 dní
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Spustenie cez cron (denný backup o 2:00):

```bash
sudo crontab -e
```

```cron
0 2 * * * /opt/pdf-compressor/backup.sh >> /var/log/pdf-backup.log 2>&1
```

---

## Aktualizácia

### Aktualizácia aplikácie

```bash
cd /opt/pdf-compressor

# Backup aktuálnej verzie
docker compose down
cp -r . ../pdf-compressor-backup-$(date +%Y%m%d)

# Pull najnovšej verzie
git pull origin main

# Rebuild a reštart
docker compose build
docker compose up -d

# Kontrola logu
docker compose logs -f
```

### Rollback

```bash
cd /opt/pdf-compressor

# Zastavenie
docker compose down

# Obnovenie zo zálohy
rm -rf *
cp -r ../pdf-compressor-backup-YYYYMMDD/* .

# Reštart
docker compose up -d
```

---

## Riešenie problémov

### Kontajner sa nespustí

```bash
# Kontrola logu
docker compose logs app

# Kontrola portov
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :5000
```

### Chyba "Port already in use"

```bash
# Nájdenie procesu
sudo lsof -i :80

# Zabitie procesu
sudo kill -9 <PID>

# Alebo zmena portu v docker-compose.yml
```

### "Permission denied" pri upload

```bash
# Oprávnenia pre uploads a compressed
sudo chown -R 1000:1000 uploads compressed
chmod 755 uploads compressed
```

### Poppler nie je nainštalovaný

Malo by to byť automatické v Dockerfile, ale ak nie:

```bash
# Vstup do kontajnera
docker compose exec app bash

# Inštalácia Poppler
apt-get update && apt-get install -y poppler-utils

# Exit a reštart
exit
docker compose restart app
```

### Vysoké využitie disku

```bash
# Manuálne vyčistenie starých súborov
find /opt/pdf-compressor/uploads -type f -mtime +1 -delete
find /opt/pdf-compressor/compressed -type f -mtime +1 -delete

# Vyčistenie Docker images
docker system prune -a
```

### Pomalý response

Zvýšte resources:

V `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Logy zabezpečenia

```bash
# Nginx access log
docker compose exec nginx cat /var/log/nginx/access.log

# Nginx error log
docker compose exec nginx cat /var/log/nginx/error.log
```

---

## Produkčné best practices

### 1. Basic Authentication (voliteľné)

Pridajte do `nginx.conf`:

```nginx
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # ... zvyšok konfigurácie
}
```

Vytvorenie htpasswd:

```bash
sudo apt install -y apache2-utils
htpasswd -c .htpasswd admin
docker compose cp .htpasswd nginx:/etc/nginx/.htpasswd
docker compose restart nginx
```

### 2. Rate limiting

V `nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=10r/m;

location /upload {
    limit_req zone=upload_limit burst=5 nodelay;
    # ... zvyšok konfigurácie
}
```

### 3. Monitoring s Prometheus/Grafana

TODO: Pridať integráciu monitoring nástrojov

---

## Kontakt a podpora

Pre problémy alebo otázky:
- GitHub Issues: <repository-url>/issues
- Email: <support-email>

## Licencia

Tento projekt je poskytovaný "ako je" bez záruky.


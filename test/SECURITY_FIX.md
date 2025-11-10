# 🚨 CRITICAL: Security Fix Required

## ⚠️ Problem
Your `.env` file with real credentials may have been committed to Git, exposing:
- Supabase Service Role Key (admin access to your database)
- JWT Secret (can forge authentication tokens)
- Anonymous API Key

## ✅ Immediate Actions Required

### Step 1: Check if `.env` is in Git
```bash
# Check if .env is tracked by git
git ls-files | grep "\.env$"

# If it returns ".env", it's tracked (BAD!)
# If no output, you're safe (GOOD!)
```

### Step 2A: If `.env` IS tracked in Git (URGENT!)

```bash
# 1. Remove .env from Git (keeps local file)
git rm --cached .env

# 2. Commit the removal
git commit -m "Remove .env file from version control"

# 3. Push to remote
git push origin main

# 4. CRITICAL: Rotate all credentials immediately!
#    Go to Supabase dashboard and regenerate:
#    - Service Role Key
#    - JWT Secret
#    - Consider regenerating Anon Key
```

**⚠️ Important**: Even after removing from Git, the credentials are in Git history!
You MUST rotate all keys in Supabase dashboard.

### Step 2B: If `.env` is NOT tracked (Good!)

```bash
# Just verify .env is in .gitignore
grep "^\.env$" .gitignore

# Should return: .env
# If not, add it:
echo ".env" >> .gitignore
```

### Step 3: Verify .gitignore is working
```bash
# Check git status
git status

# .env should NOT appear in the list
# If it does, make sure .gitignore includes .env
```

### Step 4: Update your local .env from .example.env
```bash
# Make sure you have the template
cat .example.env

# Your actual .env should have real values
# But should NEVER be committed
```

## 🔐 How to Handle Secrets Going Forward

### Local Development (Your Machine)
```bash
# 1. Copy template
cp .example.env .env

# 2. Edit with real values
nano .env  # or code .env

# 3. .env stays local, NEVER commit it
```

### Production Deployment (Kubernetes)

```yaml
# k8s/secrets/db-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: court-service-secrets
  namespace: production
type: Opaque
data:
  # Base64 encoded values (use: echo -n "value" | base64)
  SUPABASE_URL: <base64-encoded-url>
  SUPABASE_SERVICE_ROLE_KEY: <base64-encoded-key>
  SUPABASE_ANON_KEY: <base64-encoded-key>
  SUPABASE_JWT_SECRET: <base64-encoded-secret>

---
# Reference in deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: court-service
spec:
  template:
    spec:
      containers:
      - name: court-service
        envFrom:
        - secretRef:
            name: court-service-secrets
```

**Apply secrets separately** (not in Git):
```bash
# Create from file (keep file secure)
kubectl create secret generic court-service-secrets \
  --from-env-file=.env.production \
  --namespace=production

# Or create manually
kubectl create secret generic court-service-secrets \
  --from-literal=SUPABASE_URL="https://..." \
  --from-literal=SUPABASE_SERVICE_ROLE_KEY="eyJ..." \
  --namespace=production
```

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy Court Service

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        env:
          # Stored in GitHub Secrets (Settings > Secrets)
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: |
          # Your deployment script
          ./deploy.sh
```

**Add secrets in GitHub**:
1. Go to repository Settings
2. Secrets and variables > Actions
3. New repository secret
4. Add each secret individually

## 🔍 How to Rotate Supabase Credentials

1. **Go to Supabase Dashboard**
   ```
   https://app.supabase.com/project/YOUR_PROJECT_ID/settings/api
   ```

2. **Generate New Keys**
   - Service role key: Click "Reveal" > Copy > Regenerate
   - JWT Secret: Go to Auth settings > JWT Settings > Generate new secret

3. **Update All Locations**
   - Local `.env` file
   - Kubernetes secrets: `kubectl delete secret court-service-secrets && kubectl create secret...`
   - CI/CD secrets (GitHub/GitLab)
   - Any other deployment locations

4. **Verify Service Still Works**
   ```bash
   # Test the service
   curl http://localhost:8000/health
   ```

## ✅ Verification Checklist

- [ ] `.env` file is NOT in Git (`git ls-files | grep .env` returns nothing)
- [ ] `.env` is in `.gitignore`
- [ ] `.example.env` exists with placeholder values (safe to commit)
- [ ] If credentials were exposed, they have been rotated
- [ ] Production uses secure secret management (not .env files)
- [ ] CI/CD uses repository secrets
- [ ] Local `.env` has real values and works

## 📚 Additional Resources

- [12-Factor App: Config](https://12factor.net/config)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## 🆘 If Credentials Were Leaked

1. **Rotate immediately** (see above)
2. **Check Supabase logs** for suspicious activity
3. **Review database** for unauthorized changes
4. **Consider** reporting to security team
5. **Update** incident response documentation
6. **Review** git history and consider using tools like:
   - [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
   - [git-filter-repo](https://github.com/newren/git-filter-repo)

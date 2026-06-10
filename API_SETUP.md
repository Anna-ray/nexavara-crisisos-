# API Setup Guide

This guide will help you configure AI/ML API keys for the Multi-Agent System.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Getting API Keys](#getting-api-keys)
3. [Configuration Steps](#configuration-steps)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Security Best Practices](#security-best-practices)

---

## Quick Start

**TL;DR:** Copy `.env.example` to `.env`, add your API key, and run the system.

```bash
# 1. Navigate to the multi-agent directory
cd multi-agent

# 2. Copy the example file
cp .env.example .env

# 3. Edit .env and add your API key (use any text editor)
notepad .env  # Windows
nano .env     # Linux/Mac

# 4. Run the system
python main.py
```

---

## Getting API Keys

### Option 1: Featherless AI (Recommended for Testing)

**Best for:** Free tier with generous limits, easy setup

1. Visit [https://featherless.ai/](https://featherless.ai/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Click "Create New API Key"
5. Copy your API key (starts with `sk-...`)

**Free Tier:**
- Generous request limits
- Access to Llama models
- No credit card required

### Option 2: AI/ML API

**Best for:** Production use, advanced models

1. Visit [https://aimlapi.com/](https://aimlapi.com/)
2. Create an account
3. Go to Dashboard → API Keys
4. Generate a new API key
5. Copy your API key

**Free Tier:**
- 100 requests per day
- Access to GPT-4o-mini and other models
- Good for testing

### Option 3: OpenAI (Optional)

**Best for:** Production with OpenAI models

1. Visit [https://platform.openai.com/](https://platform.openai.com/)
2. Sign up and add payment method
3. Go to API Keys section
4. Create new secret key
5. Copy immediately (won't be shown again)

**Note:** OpenAI requires payment setup, no free tier.

### Option 4: Anthropic Claude (Optional)

**Best for:** Claude-specific features

1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Create account
3. Navigate to API Keys
4. Generate new key
5. Copy your key

---

## Configuration Steps

### Step 1: Create .env File

Copy the example template:

**Windows (PowerShell):**
```powershell
cd multi-agent
Copy-Item .env.example .env
```

**Windows (Command Prompt):**
```cmd
cd multi-agent
copy .env.example .env
```

**Linux/Mac:**
```bash
cd multi-agent
cp .env.example .env
```

### Step 2: Edit .env File

Open `.env` in your favorite text editor:

**Windows:**
```powershell
notepad .env
```

**Linux/Mac:**
```bash
nano .env
# or
vim .env
# or
code .env  # VS Code
```

### Step 3: Add Your API Key

Find the appropriate section and replace the placeholder:

```bash
# For Featherless AI
FEATHERLESS_API_KEY=sk-your-actual-key-here

# For AI/ML API
AI_ML_API_KEY=your-actual-key-here
```

**Example:**
```bash
# Before
FEATHERLESS_API_KEY=your-featherless-api-key-here

# After
FEATHERLESS_API_KEY=sk-abc123def456ghi789jkl012mno345pqr678
```

### Step 4: Save and Close

- **Notepad:** File → Save, then close
- **Nano:** Press `Ctrl+O`, then `Enter`, then `Ctrl+X`
- **Vim:** Press `Esc`, type `:wq`, press `Enter`

---

## Verification

### Method 1: Run the System

```bash
cd multi-agent
python main.py
```

**Expected Output:**
```
🤖 Enhanced AI Client initialized
   AI/ML API: ✓
   Featherless API: ✓
```

If you see `✓` next to your configured API, it's working!

### Method 2: Check Environment Variables (Python)

Create a test script `test_env.py`:

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Check API keys
featherless_key = os.getenv("FEATHERLESS_API_KEY")
aiml_key = os.getenv("AI_ML_API_KEY")

print("Featherless API Key:", "✓ Loaded" if featherless_key else "✗ Not found")
print("AI/ML API Key:", "✓ Loaded" if aiml_key else "✗ Not found")

# Show first/last 4 characters for verification
if featherless_key:
    print(f"  Key preview: {featherless_key[:4]}...{featherless_key[-4:]}")
```

Run it:
```bash
python test_env.py
```

### Method 3: Run Demo

```bash
cd multi-agent
python examples/advanced_multi_agent_demo.py
```

Watch for AI-powered analysis in the output.

---

## Troubleshooting

### Issue: "API key not found" or "✗" in output

**Solution:**
1. Verify `.env` file exists in `multi-agent/` directory
2. Check that the file is named exactly `.env` (not `.env.txt`)
3. Ensure no extra spaces around the `=` sign
4. Verify the key is on the correct line

**Check file location:**
```bash
# Should show .env file
ls -la multi-agent/.env  # Linux/Mac
dir multi-agent\.env     # Windows
```

### Issue: "Invalid API key" error

**Solution:**
1. Verify you copied the entire key (no truncation)
2. Check for extra spaces or newlines
3. Regenerate the key from the provider's dashboard
4. Ensure the key hasn't expired

### Issue: .env file not loading

**Solution:**

Install python-dotenv if not already installed:
```bash
pip install python-dotenv
```

Add to your Python script if needed:
```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file
```

### Issue: "Module not found" error

**Solution:**

Install required dependencies:
```bash
cd multi-agent
pip install -r requirements.txt
```

### Issue: API rate limits

**Solution:**
1. Check your provider's dashboard for usage
2. Upgrade to paid tier if needed
3. Add delays between requests
4. Use fallback heuristics (system does this automatically)

### Issue: Windows file visibility

**Solution:**

Show hidden files to see `.env`:
1. Open File Explorer
2. View tab → Options → Change folder and search options
3. View tab → Show hidden files, folders, and drives
4. Apply → OK

Or use PowerShell:
```powershell
Get-ChildItem -Force multi-agent\.env
```

---

## Security Best Practices

### ✅ DO:

- **Keep .env local:** Never commit to Git (it's in `.gitignore`)
- **Use environment variables:** For production deployments
- **Rotate keys regularly:** Every 90 days minimum
- **Use separate keys:** Different keys for dev/staging/production
- **Limit key permissions:** Use read-only keys when possible
- **Monitor usage:** Check API dashboards regularly

### ❌ DON'T:

- **Don't commit .env:** It contains secrets
- **Don't share keys:** Each developer should have their own
- **Don't hardcode keys:** Always use environment variables
- **Don't expose in logs:** Mask keys in error messages
- **Don't use production keys locally:** Use separate dev keys

### Checking .gitignore

Verify `.env` is ignored:

```bash
cd multi-agent
cat .gitignore | grep .env
```

Should show:
```
.env
```

If not, add it:
```bash
echo ".env" >> .gitignore
```

---

## Advanced Configuration

### Using Multiple Providers

Configure multiple API keys for redundancy:

```bash
# Primary provider
FEATHERLESS_API_KEY=sk-primary-key

# Backup provider
AI_ML_API_KEY=backup-key

# Optional providers
OPENAI_API_KEY=openai-key
ANTHROPIC_API_KEY=anthropic-key
```

The system will automatically fall back to available providers.

### Custom Endpoints

Override default endpoints:

```bash
# Custom AI/ML endpoint
AI_ML_ENDPOINT=https://custom.aiml.endpoint/v1/chat/completions

# Custom Featherless endpoint
FEATHERLESS_ENDPOINT=https://custom.featherless.endpoint/v1/chat/completions
```

### Environment-Specific Configuration

Create multiple env files:

```bash
.env.development
.env.staging
.env.production
```

Load specific environment:
```python
from dotenv import load_dotenv
load_dotenv('.env.production')
```

---

## Production Deployment

### Using System Environment Variables

Instead of `.env` file, set system variables:

**Linux/Mac:**
```bash
export FEATHERLESS_API_KEY="your-key"
export AI_ML_API_KEY="your-key"
```

**Windows (PowerShell):**
```powershell
$env:FEATHERLESS_API_KEY="your-key"
$env:AI_ML_API_KEY="your-key"
```

**Windows (Permanent):**
```powershell
[System.Environment]::SetEnvironmentVariable('FEATHERLESS_API_KEY', 'your-key', 'User')
```

### Docker

Add to `docker-compose.yml`:
```yaml
services:
  multi-agent:
    environment:
      - FEATHERLESS_API_KEY=${FEATHERLESS_API_KEY}
      - AI_ML_API_KEY=${AI_ML_API_KEY}
```

### Cloud Platforms

**AWS:**
- Use AWS Secrets Manager
- Set environment variables in Lambda/ECS

**Azure:**
- Use Azure Key Vault
- Set App Settings in App Service

**Google Cloud:**
- Use Secret Manager
- Set environment variables in Cloud Run

---

## Support

### Need Help?

1. Check [QUICKSTART_FOR_JUDGES.md](QUICKSTART_FOR_JUDGES.md) for quick setup
2. Review [README_ADVANCED.md](README_ADVANCED.md) for system details
3. Check provider documentation:
   - [Featherless Docs](https://featherless.ai/docs)
   - [AI/ML API Docs](https://aimlapi.com/docs)

### Common Questions

**Q: Can I run without API keys?**
A: Yes! The system uses fallback heuristics, but AI features will be limited.

**Q: Which provider should I use?**
A: Featherless AI for free testing, AI/ML API for production.

**Q: How much does it cost?**
A: Featherless has generous free tier. AI/ML API has 100 free requests/day.

**Q: Can I use my own models?**
A: Yes! Set custom endpoints in `.env` file.

---

## Quick Reference

### File Locations
```
multi-agent/
├── .env.example          # Template (commit this)
├── .env                  # Your config (DON'T commit)
├── API_SETUP.md         # This file
└── services/
    ├── enhanced_ai_client.py
    ├── featherless_client.py
    └── ai_ml_client.py
```

### Environment Variables
```bash
FEATHERLESS_API_KEY      # Featherless AI key
AI_ML_API_KEY           # AI/ML API key
OPENAI_API_KEY          # OpenAI key (optional)
ANTHROPIC_API_KEY       # Anthropic key (optional)
FEATHERLESS_ENDPOINT    # Custom endpoint (optional)
AI_ML_ENDPOINT          # Custom endpoint (optional)
```

### Quick Commands
```bash
# Setup
cp .env.example .env
notepad .env  # Add your key

# Test
python main.py

# Run demo
python examples/advanced_multi_agent_demo.py

# Verify
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓' if os.getenv('FEATHERLESS_API_KEY') else '✗')"
```

---

**Made with ❤️ by Bob - Your AI Development Assistant**
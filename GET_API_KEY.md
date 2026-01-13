# How to Get Your OpenAI API Key

## Step-by-Step Guide

1. **Visit OpenAI Platform**
   - Go to: https://platform.openai.com/
   - Sign up or log in to your account

2. **Navigate to API Keys**
   - Click on your profile icon (top-right)
   - Select "View API keys" from the dropdown

3. **Create New Key**
   - Click "Create new secret key"
   - Give it a name (e.g., "Inflx Project")
   - Click "Create secret key"

4. **Copy Your Key**
   - **IMPORTANT**: Copy the key immediately - you won't see it again!
   - It will look like: `sk-...` (starts with "sk-")

5. **Set the Environment Variable**

   **Windows PowerShell:**
   ```powershell
   $env:OPENAI_API_KEY="sk-your-actual-key-here"
   ```

   **Windows Command Prompt:**
   ```cmd
   setx OPENAI_API_KEY "sk-your-actual-key-here"
   ```
   (Then restart your terminal)

   **Linux/Mac:**
   ```bash
   export OPENAI_API_KEY="sk-your-actual-key-here"
   ```

6. **Verify It's Set**
   ```powershell
   echo $env:OPENAI_API_KEY
   ```

## Free Trial

OpenAI offers free credits for new accounts. Check your usage at:
https://platform.openai.com/usage

## Security Note

- Never commit your API key to Git
- Never share your API key publicly
- The `.env` file is already in `.gitignore` for safety

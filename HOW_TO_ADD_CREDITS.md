# How to Add Credits to Your OpenAI Account

## Step-by-Step Guide

### Method 1: Add Payment Method and Purchase Credits

1. **Log in to OpenAI Platform**
   - Go to: https://platform.openai.com/
   - Sign in with your account

2. **Navigate to Billing**
   - Click on your profile icon (top-right corner)
   - Select **"Billing"** or **"Settings"** → **"Billing"**
   - Or go directly to: https://platform.openai.com/account/billing

3. **Add Payment Method**
   - Click **"Add payment method"** or **"Set up paid account"**
   - Enter your credit/debit card details
   - Add billing address
   - Click **"Save"** or **"Add payment method"**

4. **Set Usage Limits (Optional)**
   - You can set monthly spending limits
   - This helps control costs
   - Recommended: Start with $5-10 limit for testing

5. **Credits Will Be Available**
   - Once payment method is added, you'll have access to paid API usage
   - Credits are charged as you use the API (pay-as-you-go)
   - Check your usage at: https://platform.openai.com/usage

### Method 2: Free Tier Credits

If you're on a free tier:
- Free tier accounts get limited credits
- Credits may reset monthly
- Check your usage dashboard to see remaining credits
- Visit: https://platform.openai.com/usage

### Method 3: Purchase Prepaid Credits (if available)

Some accounts may have the option to:
- Purchase prepaid credits
- Add credits to your account balance
- Check if this option is available in your billing dashboard

## Quick Links

- **Billing Dashboard**: https://platform.openai.com/account/billing
- **Usage Dashboard**: https://platform.openai.com/usage
- **API Keys**: https://platform.openai.com/api-keys
- **Pricing Information**: https://openai.com/pricing

## Pricing Information

### GPT-4o-mini (What we're using)
- **Input**: ~$0.15 per 1M tokens
- **Output**: ~$0.60 per 1M tokens
- Very affordable for testing!

### Typical Costs
- A conversation with 5-6 turns: ~$0.001-0.01 (less than 1 cent)
- Demo script run: ~$0.01-0.05
- Very cost-effective for development

## After Adding Credits

1. **Verify Credits**
   - Go to: https://platform.openai.com/usage
   - Check your available credits/balance

2. **Test Your Agent**
   ```powershell
   python demo.py
   ```

3. **Monitor Usage**
   - Keep an eye on your usage dashboard
   - Set spending limits to avoid surprises

## Troubleshooting

### "Payment method declined"
- Check card details
- Ensure card has sufficient funds
- Try a different payment method
- Contact your bank if issues persist

### "Credits not showing"
- Wait a few minutes after adding payment method
- Refresh the dashboard
- Check email for confirmation

### "Still getting quota errors"
- Verify payment method is active
- Check if you have any spending limits set
- Ensure you're using the correct API key
- Contact OpenAI support if needed

## Setting Spending Limits

**Recommended for testing:**
1. Go to Billing → Limits
2. Set monthly limit: $5-10
3. This prevents unexpected charges
4. You can increase it anytime

## Support

If you encounter issues:
- OpenAI Support: https://help.openai.com/
- Check status page: https://status.openai.com/
- Community forum: https://community.openai.com/

## Next Steps

Once credits are added:
1. ✅ Verify credits are available
2. ✅ Run `python demo.py` to test
3. ✅ Monitor usage at https://platform.openai.com/usage
4. ✅ Enjoy your working agent!

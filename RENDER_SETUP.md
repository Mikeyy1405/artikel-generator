# WritgoAI v16 - Render Deployment Guide

## 🚀 Quick Deploy to Render

### Environment Variables Required

Add these in Render Dashboard → Environment:

```
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
ORIGINALITY_API_KEY=your_originality_key_here
PIXABAY_API_KEY=your_pixabay_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
DATABASE_URL=(automatically set by Render PostgreSQL)
```

### Build Settings

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Python Version**: 3.11

### Database Setup

1. Create PostgreSQL database in Render
2. Link it to your web service
3. Database will auto-initialize on first run

## ✨ New Features in v16

### Perplexity AI Integration
- Real-time web research before article generation
- Automatic fact-checking and citation gathering
- Toggle on/off per article generation
- Improves content quality and accuracy

### Bug Fixes
- ✅ Fixed "max_tokens" error for GPT-5 models
- ✅ Fixed "best-of-all" model mapping to GPT-4.1
- ✅ All OpenAI calls now use correct parameters

## 📝 How to Use Perplexity Research

1. Enter your article details (anchors, URLs, topic)
2. Check the "🔍 Use Perplexity Research" checkbox
3. Generate article - research happens automatically
4. Article will include researched facts and insights

## 🔧 Technical Details

### Model Parameter Handling
- GPT-5, o1-preview, o1-mini → use `max_completion_tokens`
- GPT-4, GPT-4o, GPT-3.5 → use `max_tokens`
- "best-of-all" → automatically maps to GPT-4.1

### API Integrations
- OpenAI (article generation)
- Anthropic Claude (alternative generation)
- Perplexity AI (web research)
- Originality.AI (plagiarism check)
- Pixabay (image search)

## 📊 Database Schema

PostgreSQL with tables:
- `users` - User accounts
- `articles` - Generated articles
- `wordpress_sites` - Connected WP sites

## 🎯 Deployment Checklist

- [ ] Create Render account
- [ ] Create new Web Service
- [ ] Connect GitHub repo or upload files
- [ ] Add PostgreSQL database
- [ ] Set all environment variables
- [ ] Deploy!

## 🔐 Security Notes

- All API keys stored as environment variables
- Passwords hashed with bcrypt
- Session management with Flask-Login
- CORS enabled for API access

## 📞 Support

For issues or questions, check the logs in Render Dashboard.

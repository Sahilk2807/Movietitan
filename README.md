# 🎬 Telegram Movie Bot

A feature-rich Telegram bot for managing and sharing movie collections through Google Sheets integration.

## 🌟 Features

- **🔍 Smart Search**: Search movies by name, year, or quality
- **📝 Movie Listing**: Paginated view of all available movies
- **🔐 Admin Panel**: Easy management tools for administrators
- **📊 Statistics**: View collection statistics and insights
- **🎥 Direct Downloads**: One-click access to movie links
- **📱 User-Friendly**: Intuitive interface with inline keyboards

## 🚀 Commands

### User Commands
- `/start` - Welcome message and bot introduction
- `/search <query>` - Search for movies
- `/list [page]` - View all movies (paginated)
- `/help` - Show available commands

### Admin Commands
- `/admin` - Access admin panel
- `/addmovie "Name" Year Quality Link` - Add new movie
- `/stats` - View detailed statistics

## 📋 Setup Instructions

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Sheets with public CSV export access

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd telegram-movie-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your bot token, sheet URL, and admin ID

4. **Run the bot**
   ```bash
   python main.py
   ```

### 🌐 Deploy to Render.com

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [Render.com](https://render.com)
   - Create new "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python main.py`
     - **Environment**: Add your environment variables

3. **Environment Variables on Render**
   ```
   BOT_TOKEN=your_bot_token_here
   SHEET_CSV_URL=your_google_sheet_csv_url
   ADMIN_ID=your_telegram_user_id
   ```

## 📊 Google Sheets Setup

Create a Google Sheet with these columns:
- **Movie Name**: Name of the movie
- **Year**: Release year
- **Quality**: Video quality (e.g., HD 1080p, 4K)
- **GP Link**: Google Drive or download link

### Make Sheet Public
1. Open your Google Sheet
2. Click "Share" → "Change to anyone with the link"
3. Set permission to "Viewer"
4. Get the CSV export URL: Replace `/edit` with `/export?format=csv`

## 🛠️ Project Structure

```
telegram-movie-bot/
├── main.py              # Main bot application
├── requirements.txt     # Python dependencies
├── runtime.txt         # Python version for deployment
├── .env                # Environment variables (local)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables
- `BOT_TOKEN`: Your Telegram bot token
- `SHEET_CSV_URL`: Google Sheets CSV export URL
- `ADMIN_ID`: Your Telegram user ID (for admin access)

### Getting Your Admin ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID
3. Use this number as your `ADMIN_ID`

## 🎯 Features in Detail

### Smart Search
- Search by movie name: `/search avengers`
- Search by year: `/search 2023`
- Search by quality: `/search 4K`
- Case-insensitive matching

### Admin Features
- View and edit Google Sheet directly
- Add movies via command
- View collection statistics
- Quality and year distributions

### User Experience
- Paginated movie listings
- Inline download buttons
- Clean, modern interface
- Error handling and feedback

## 🚀 Deployment Options

### Render.com (Recommended)
- Free tier available
- Easy GitHub integration
- Automatic deployments
- Built-in environment variables

### Alternative Platforms
- **Heroku**: Classic choice with good documentation
- **Railway**: Modern platform with simple deployment
- **PythonAnywhere**: Python-focused hosting
- **VPS**: Full control with services like DigitalOcean

## 🔒 Security Notes

- Never commit `.env` file to GitHub
- Use environment variables for sensitive data
- Keep your bot token secure
- Regularly rotate access tokens

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot token validity
   - Verify internet connection
   - Check Render service logs

2. **Sheet access errors**
   - Ensure sheet is public
   - Verify CSV URL format
   - Check sheet permissions

3. **Admin commands not working**
   - Verify your user ID in environment variables
   - Test with [@userinfobot](https://t.me/userinfobot)

### Logs and Debugging
- Check Render service logs for errors
- Enable debug logging if needed
- Monitor bot performance and uptime

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 💬 Support

For support or questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review Telegram Bot API documentation

## 🔄 Updates

Stay updated with new features:
- Watch the GitHub repository
- Check release notes
- Follow deployment best practices

---

**Made with ❤️ for movie enthusiasts**
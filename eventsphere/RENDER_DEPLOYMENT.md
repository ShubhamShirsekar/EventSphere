# Deploying EventSphere to Render

## Prerequisites
- GitHub account
- Render account (sign up at https://render.com)
- Your code pushed to GitHub

## Deployment Steps

### 1. Push Your Code to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Create a New Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (`EventSphere`)
4. Render will detect the `render.yaml` file

### 3. Configure Your Service (if not using render.yaml)

If you prefer manual setup:

- **Name**: `eventsphere`
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn eventsphere.wsgi:application`
- **Plan**: Select **Free**

### 4. Add Environment Variables

Render will auto-populate database variables from `render.yaml`, but you can also set them manually:

- `SECRET_KEY`: Generate a secure key (Render can auto-generate)
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: Your render domain (e.g., `eventsphere.onrender.com`)
- Database variables will be auto-filled if using Render PostgreSQL

### 5. Create PostgreSQL Database

1. From your Render dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name**: `eventsphere-db`
3. **Database**: `eventsphere`
4. **User**: `eventsphere`
5. **Plan**: Select **Free**
6. Click **"Create Database"**

### 6. Link Database to Web Service

In your web service settings:
1. Go to **"Environment"** tab
2. Add environment variables or let `render.yaml` auto-link them
3. Render will provide: `DBNAME`, `DBUSER`, `DBPASSWORD`, `DBHOST`, `DBPORT`

### 7. Deploy

1. Click **"Create Web Service"** or **"Deploy"**
2. Render will:
   - Install dependencies from `requirements.txt`
   - Run `collectstatic` for static files
   - Run database migrations
   - Start your Django app with Gunicorn

### 8. Initial Setup (One-time)

After deployment, create a superuser:

1. Go to your service's **"Shell"** tab
2. Run: `python manage.py createsuperuser`
3. Follow the prompts

Or load test data:
```bash
python manage.py load_test_data
```

## Post-Deployment

### Access Your App
Your app will be available at: `https://eventsphere.onrender.com` (or your chosen name)

### Admin Panel
Access at: `https://your-app.onrender.com/admin`

### Monitor Logs
Check logs in the Render dashboard under the **"Logs"** tab

## Important Notes

### Free Tier Limitations
- Web service spins down after 15 minutes of inactivity
- Cold start takes ~30 seconds on first request
- PostgreSQL database expires after 90 days (you'll need to migrate data)

### Static Files
- Handled by WhiteNoise (no external storage needed)
- Files served from `/staticfiles/`

### Media Files
- For production, consider using cloud storage (AWS S3, Cloudinary)
- Free tier has limited disk space

### Environment Variables
Keep these secure and never commit `.env` file to GitHub!

## Troubleshooting

### Build Fails
- Check `build.sh` has execute permissions
- Verify all dependencies in `requirements.txt`
- Check Python version compatibility

### Database Connection Error
- Verify database environment variables
- Ensure PostgreSQL database is created and linked
- Check database credentials in Render dashboard

### Static Files Not Loading
- Ensure `STATIC_ROOT` is set in settings.py
- Verify `collectstatic` runs in `build.sh`
- Check WhiteNoise is in MIDDLEWARE

### App Not Starting
- Review logs in Render dashboard
- Verify `gunicorn` is in requirements.txt
- Check `ALLOWED_HOSTS` includes your Render domain

## Updating Your App

After making changes:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render will automatically detect changes and redeploy!

## Custom Domain (Optional)

1. Go to your service's **"Settings"**
2. Scroll to **"Custom Domains"**
3. Add your domain and follow DNS instructions

## Need Help?

- Render Docs: https://render.com/docs
- Django on Render: https://render.com/docs/deploy-django
- Check logs for error messages

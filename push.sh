#!/bin/bash

# إعداد بيانات المستخدم في Git
git config --global user.name "alghazaliye"
git config --global user.email "alghazaliye@gmail.com"

# تهيئة مستودع Git محلي
echo "Initializing a new Git repository..."
git init

# ربط المستودع المحلي بمستودع GitHub باستخدام رابط SSH
echo "Connecting to GitHub repository via SSH..."
git remote add origin git@github.com:alghazaliye/ticket_system.git

# إضافة الملفات إلى منطقة الانتظار (Staging Area)
echo "Adding all files to the staging area..."
git add .

# تسجيل أول تغيير (Commit) مع رسالة
echo "Creating the initial commit..."
git commit -m "Initial commit for Ticket System App"

# إنشاء الفرع الرئيسي وتحديده كفرع افتراضي
echo "Setting the main branch..."
git branch -M main

# دفع التغييرات إلى مستودع GitHub
echo "Pushing changes to the GitHub repository..."
git push -u origin main

echo "All done! Your repository is set up successfully."

#!/bin/bash

# إعداد بيانات المستخدم
git config --global user.name "alghazaliye"
git config --global user.email "alghazaliye@gmail.com"

# تهيئة المستودع وربطه عبر SSH بدال HTTPS
git init
git remote add origin git@github.com:alghazaliye/ticket_system.git
git add .
git commit -m "Initial commit for Ticket System App"
git branch -M main
git push -u origin main

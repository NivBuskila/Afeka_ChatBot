# שלב הבנייה
FROM node:20-alpine as builder

# הגדרת תיקיית העבודה
WORKDIR /app

# העתקת קבצי package.json ו-package-lock.json
COPY package*.json ./

# התקנת תלויות
RUN npm ci

# העתקת כל הקבצים מהתיקייה הנוכחית
COPY . .

# בניית האפליקציה
RUN npm run build

# שלב הייצור
FROM nginx:alpine

# העתקת קבצי הבנייה לתיקיית nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# חשיפת פורט 80
EXPOSE 80

# הפקודה להרצת nginx
CMD ["nginx", "-g", "daemon off;"]
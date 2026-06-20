FROM nginx:1.27-alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/public/ /usr/share/nginx/html

EXPOSE 5500

CMD ["nginx", "-g", "daemon off;"]

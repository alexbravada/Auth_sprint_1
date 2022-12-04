FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY config /etc/nginx/conf.d

CMD ["nginx", "-g", "daemon off;"]

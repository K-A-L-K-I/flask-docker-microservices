FROM nginx:1.25-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend files
COPY ../frontend/index.html /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

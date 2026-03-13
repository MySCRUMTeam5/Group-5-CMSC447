# 1. Use Node.js as our "engine"
FROM node:20-slim

# 2. Set the "room" we are working in
WORKDIR /app

# 3. Copy our "recipe list" into the room
COPY package*.json ./

# 4. Install all the tools we need
RUN npm install

# 5. Copy all our code files into the room
COPY . .

# 6. Open a window (port) for the web browser
EXPOSE 5173

# 7. Start the Vite development room
CMD ["npm", "run", "dev", "--", "--host"]

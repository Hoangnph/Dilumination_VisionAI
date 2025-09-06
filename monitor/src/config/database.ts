// Database configuration
export const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'people_counter',
  user: process.env.DB_USER || 'people_counter_user',
  password: process.env.DB_PASSWORD || 'secure_password_123',
};

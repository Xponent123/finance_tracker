import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api', // URL where Flask backend runs
});

export default api;

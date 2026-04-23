import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/style.css'; // Import global styles

const app = createApp(App);
app.use(router);
app.mount('#app');

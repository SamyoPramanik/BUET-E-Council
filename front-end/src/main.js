import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

// 1. Import Toast
import Toast from "vue-toastification";
// 2. Import the CSS (Required for animations)
import "vue-toastification/dist/index.css";

const app = createApp(App)

// 3. Configure Options
const options = {
    position: "bottom-right",
    timeout: 3000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false
};

app.use(router)
app.use(Toast, options) // 4. Tell Vue to use it
app.mount('#app')
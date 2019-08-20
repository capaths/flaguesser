import Vue from 'vue';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';

import Vuex from 'vuex';
import VueNativeSock from 'vue-native-websocket';
import {store} from './_store';

Vue.config.productionTip = false;
Vue.use(Vuex);

const PRODUCTION = process.env.NODE_ENV === 'production';
const socketPort = PRODUCTION ? 8080 : 8081;

Vue.use(VueNativeSock, 'ws://localhost:8000/ws', {
    format: 'json',
});

new Vue({
    store,
    router,
    vuetify,
    render: (h) => h(App),
}).$mount('#app');

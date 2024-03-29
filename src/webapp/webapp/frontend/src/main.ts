import Vue from 'vue';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';

import Vuex from 'vuex';
import VueNativeSock from 'vue-native-websocket';
import {store} from './_store';

Vue.config.productionTip = false;
Vue.use(Vuex);

const GATEWAY_URI = process.env.NODE_ENV === 'production' ? 'flaguesser-gateway.herokuapp.com' : 'localhost:8000';

Vue.use(VueNativeSock, `ws://${GATEWAY_URI}/ws`, {
    format: 'json',
});

new Vue({
    store,
    router,
    vuetify,
    render: (h) => h(App),
}).$mount('#app');

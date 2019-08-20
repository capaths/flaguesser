<template>
    <v-app>
        <v-content>
            <router-view></router-view>
        </v-content>
    </v-app>
</template>

<script lang="ts">
    import Vue from 'vue';
    import HelloWorld from './components/Login.vue';

    export default Vue.extend({
        name: 'App',
    });
</script>

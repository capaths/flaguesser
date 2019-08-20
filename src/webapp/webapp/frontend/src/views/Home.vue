<template>
    <Menu v-if="user"></Menu>
    <Login v-else></Login>
</template>

<script lang="ts">
    import Vue from 'vue';
    import {mapState} from 'vuex';

    import Login from '../components/Login.vue';
    import Menu from '../components/Menu.vue';

    export default Vue.extend({
        components: {
            Login,
            Menu,
        },
        computed: {
            ...mapState('account', ['user']),
        },
    });
</script>

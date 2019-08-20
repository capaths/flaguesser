<template>
    <v-card tile flat :elevation="20" width="100%">
        <v-card-title primary class="headline text-uppercase">
            <span>Flag</span>
            <span class="font-weight-light">uesser</span>
        </v-card-title>
        <v-card-text class="text-center">
            <v-card-text class="text-center">
                <v-avatar class="text-center" size="124">
                    <img src="https://www.belr.com/wp-content/uploads/2017/06/avatar-placeholder-generic-1.jpg"/>
                </v-avatar>
            </v-card-text>
            <p class="title text-center">
                {{user.username}}
            </p>
            <v-btn @click="logout">Log-out</v-btn>
        </v-card-text>
    </v-card>
</template>

<script>
    import {mapState, mapActions} from 'vuex';

    export default {
        name: 'Profile',
        computed: {
            ...mapState('account', ['user']),
        },
        methods: {
            ...mapActions('account', ['logout']),
        },
    };
</script>

<style scoped>

</style>